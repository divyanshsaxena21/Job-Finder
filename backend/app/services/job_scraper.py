"""
Real Job Scraper Service

Scrapes actual job listings from multiple platforms.
Uses Playwright for dynamic sites and BeautifulSoup for static sites.
"""

from typing import List, Optional
from app.models.schemas import JobCreate, UserPreferencesResponse
from datetime import datetime
import logging
import asyncio
import aiohttp
from urllib.parse import quote

logger = logging.getLogger(__name__)


class JobScraperService:
    """Scrapes real job listings from various platforms"""
    
    @staticmethod
    async def scrape_jobs(
        preferences: UserPreferencesResponse,
        max_results: int = 50
    ) -> List[JobCreate]:
        """
        Scrape jobs from multiple platforms based on preferences
        
        Args:
            preferences: User job preferences
            max_results: Maximum jobs to scrape per platform
        
        Returns:
            List of JobCreate objects from all platforms
        """
        logger.info(f"Scraping real jobs for roles: {preferences.roles}, locations: {preferences.location}")
        
        jobs = []
        
        try:
            # Scrape from multiple sources in parallel (6 sources now)
            # Indeed (Playwright), Naukri (BeautifulSoup), Glassdoor (Playwright), 
            # Free APIs, Stack Overflow, Dice
            results = await asyncio.gather(
                JobScraperService.scrape_indeed(
                    preferences.roles,
                    preferences.location,
                    max_results // 6
                ),
                JobScraperService.scrape_naukri(
                    preferences.roles,
                    preferences.location,
                    max_results // 6
                ),
                JobScraperService.scrape_glassdoor(
                    preferences.roles,
                    preferences.location,
                    max_results // 6
                ),
                JobScraperService.scrape_free_api(
                    preferences.roles,
                    preferences.location,
                    max_results // 6
                ),
                JobScraperService.scrape_stack_overflow(
                    preferences.roles,
                    preferences.location,
                    max_results // 6
                ),
                JobScraperService.scrape_dice(
                    preferences.roles,
                    preferences.location,
                    max_results // 6
                ),
                return_exceptions=True
            )
            
            # Combine results, filtering out errors
            for result in results:
                if isinstance(result, list):
                    jobs.extend(result)
                elif isinstance(result, Exception):
                    logger.warning(f"Scraper error: {result}")
            
            # Remove duplicates based on apply_link
            unique_jobs = {job.apply_link: job for job in jobs}.values()
            logger.info(f"Found {len(unique_jobs)} unique jobs across all platforms")
            
        except Exception as e:
            logger.error(f"Error scraping jobs: {str(e)}")
        
        return list(unique_jobs)[:max_results]
    
    @staticmethod
    async def scrape_indeed(
        roles: List[str],
        locations: List[str],
        max_results: int = 25
    ) -> List[JobCreate]:
        """
        Scrape jobs from Indeed using Playwright
        
        Indeed has dynamic content, so we use headless browser automation.
        """
        logger.info(f"Scraping Indeed for {roles}")
        
        jobs = []
        
        try:
            from playwright.async_api import async_playwright
            
            query = " OR ".join(roles)
            location = locations[0] if locations else "United States"
            
            # Indeed URL
            search_url = f"https://www.indeed.com/jobs?q={quote(query)}&l={quote(location)}"
            
            async with async_playwright() as p:
                # Use chromium with minimal resources
                browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
                context = await browser.new_context()
                
                # Add user agent to avoid blocks
                page = await context.new_page()
                await page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                
                try:
                    # Navigate to Indeed search
                    await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
                    await page.wait_for_timeout(2000)  # Wait for JS to render
                    
                    # Extract job listings
                    job_cards = await page.query_selector_all("div.job_seen_beacon")
                    
                    for card in job_cards[:max_results]:
                        try:
                            # Extract job details
                            title_elem = await card.query_selector("h2.jobTitle a")
                            if not title_elem:
                                continue
                            
                            title = await title_elem.text_content()
                            apply_link = await title_elem.get_attribute("href")
                            
                            company_elem = await card.query_selector("span.companyName")
                            company = await company_elem.text_content() if company_elem else "Unknown"
                            
                            location_elem = await card.query_selector("span.job_snippet-location")
                            loc = await location_elem.text_content() if location_elem else location
                            
                            snippet_elem = await card.query_selector("div.job_snippet")
                            description = await snippet_elem.text_content() if snippet_elem else ""
                            
                            # Full Indeed URL
                            if apply_link and not apply_link.startswith("http"):
                                apply_link = f"https://www.indeed.com{apply_link}"
                            
                            if title and apply_link:
                                job = JobCreate(
                                    title=title.strip(),
                                    company=company.strip(),
                                    description=description.strip() if description else title,
                                    location=loc.strip() if loc else location,
                                    job_type="full-time",
                                    source="indeed",
                                    apply_link=apply_link.split("?")[0]  # Remove query params
                                )
                                jobs.append(job)
                        
                        except Exception as e:
                            logger.debug(f"Error extracting Indeed job: {str(e)}")
                            continue
                
                finally:
                    await browser.close()
            
            logger.info(f"Indeed: Extracted {len(jobs)} jobs")
        
        except ImportError:
            logger.warning("Playwright not available for Indeed scraping")
        except Exception as e:
            logger.error(f"Error scraping Indeed: {str(e)}")
        
        return jobs[:max_results]
    
    @staticmethod
    async def scrape_naukri(
        roles: List[str],
        locations: List[str],
        max_results: int = 25
    ) -> List[JobCreate]:
        """
        Scrape jobs from Naukri (popular in India)
        
        Uses BeautifulSoup for HTML parsing + aiohttp for async requests.
        """
        logger.info(f"Scraping Naukri for {roles}")
        
        jobs = []
        
        try:
            from bs4 import BeautifulSoup
            
            query = "+".join(roles)
            location = locations[0].lower().replace(" ", "-") if locations else "india"
            
            search_url = f"https://www.naukri.com/search?keyword={quote(query)}&location={quote(location)}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(search_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                        if resp.status == 200:
                            html = await resp.text()
                            soup = BeautifulSoup(html, "html.parser")
                            
                            # Naukri job cards - look for job list items
                            job_cards = soup.find_all("div", {"class": "srp-jobc-main-wrapper"})[:max_results]
                            
                            if not job_cards:
                                # Try alternative selector
                                job_cards = soup.find_all("article", {"class": "jobCard"})[:max_results]
                            
                            for card in job_cards:
                                try:
                                    # Extract title and link
                                    title_elem = card.find("a", {"class": "jobTitle"}) or card.find("a", {"class": "title"})
                                    if not title_elem:
                                        continue
                                    
                                    title = title_elem.text.strip()
                                    apply_link = title_elem.get("href", "")
                                    
                                    # Fix relative URLs
                                    if apply_link and not apply_link.startswith("http"):
                                        apply_link = f"https://www.naukri.com{apply_link}"
                                    
                                    # Extract company
                                    company_elem = card.find("a", {"class": "companyName"})
                                    company = company_elem.text.strip() if company_elem else "Unknown"
                                    
                                    # Extract location
                                    location_elem = card.find("span", {"class": "location"})
                                    loc = location_elem.text.strip() if location_elem else location
                                    
                                    # Extract brief description
                                    desc_elem = card.find("div", {"class": "job"}) or card.find("p")
                                    description = desc_elem.text.strip() if desc_elem else title
                                    
                                    if title and apply_link:
                                        job = JobCreate(
                                            title=title,
                                            company=company,
                                            description=description[:500],  # Truncate
                                            location=loc,
                                            job_type="full-time",
                                            source="naukri",
                                            apply_link=apply_link.split("?")[0]
                                        )
                                        jobs.append(job)
                                
                                except Exception as e:
                                    logger.debug(f"Error extracting Naukri job: {str(e)}")
                                    continue
                
                except Exception as e:
                    logger.warning(f"HTTP error scraping Naukri: {str(e)}")
        
        except ImportError:
            logger.warning("BeautifulSoup not available for Naukri scraping")
        except Exception as e:
            logger.error(f"Error scraping Naukri: {str(e)}")
        
        return jobs[:max_results]
    
    @staticmethod
    async def scrape_free_api(
        roles: List[str],
        locations: List[str],
        max_results: int = 25
    ) -> List[JobCreate]:
        """
        Scrape jobs from free job APIs (GitHub Jobs, etc.)
        
        These APIs don't require authentication and have good free tiers.
        """
        logger.info(f"Scraping free job APIs for {roles}")
        
        jobs = []
        
        try:
            # Try GitHub Jobs API (deprecated but still works)
            jobs_from_api = await JobScraperService._scrape_github_jobs(roles, locations, max_results)
            jobs.extend(jobs_from_api)
            
            logger.info(f"API: Extracted {len(jobs)} jobs from public APIs")
        
        except Exception as e:
            logger.error(f"Error scraping APIs: {str(e)}")
        
        return jobs[:max_results]
    
    @staticmethod
    async def _scrape_github_jobs(
        roles: List[str],
        locations: List[str],
        max_results: int
    ) -> List[JobCreate]:
        """
        Use GitHub Jobs API (free, no authentication needed)
        """
        jobs = []
        
        try:
            query = " ".join(roles)
            location = locations[0] if locations else ""
            
            # GitHub Jobs API endpoint
            github_jobs_url = f"https://jobs.github.com/positions.json?description={quote(query)}"
            if location:
                github_jobs_url += f"&location={quote(location)}"
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(github_jobs_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            
                            for item in data[:max_results]:
                                try:
                                    job = JobCreate(
                                        title=item.get("title", ""),
                                        company=item.get("company", ""),
                                        description=item.get("description", "")[:500],  # Truncate
                                        location=item.get("location", location or "Remote"),
                                        job_type="full-time" if item.get("type", "").lower() == "full time" else "other",
                                        source="github_jobs",
                                        apply_link=item.get("url", "")
                                    )
                                    
                                    if job.title and job.apply_link:
                                        jobs.append(job)
                                
                                except Exception as e:
                                    logger.debug(f"Error parsing GitHub job: {str(e)}")
                
                except Exception as e:
                    logger.debug(f"GitHub Jobs API error: {str(e)}")
        
        except Exception as e:
            logger.debug(f"API scraping error: {str(e)}")
        
        return jobs[:max_results]
    
    @staticmethod
    async def scrape_glassdoor(
        roles: List[str],
        locations: List[str],
        max_results: int = 25
    ) -> List[JobCreate]:
        """
        Scrape jobs from Glassdoor using Playwright
        
        Note: Glassdoor has strong anti-scraping measures.
        This uses Playwright with proper delays and headers.
        """
        logger.info(f"Scraping Glassdoor for {roles}")
        
        jobs = []
        
        try:
            from playwright.async_api import async_playwright
            
            query = "+".join(roles)
            location = locations[0] if locations else "United States"
            
            search_url = f"https://www.glassdoor.com/Search/jobs.htm?sc.keyword={quote(query)}&locT=C&locId=1&l={quote(location)}"
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                await page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                
                try:
                    await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
                    await page.wait_for_timeout(3000)  # Wait longer for Glassdoor
                    
                    # Extract job listings
                    job_elements = await page.query_selector_all("div.JobCard_jobCardContainer__oJZo7")
                    
                    for elem in job_elements[:max_results]:
                        try:
                            # Job title
                            title_elem = await elem.query_selector("a.JobCard_jobTitle__Y8p8l")
                            title = await title_elem.text_content() if title_elem else None
                            
                            # Job link
                            link = await title_elem.get_attribute("href") if title_elem else None
                            if link and not link.startswith("http"):
                                link = f"https://www.glassdoor.com{link}"
                            
                            # Company
                            company_elem = await elem.query_selector("span.JobCard_companyName__zN92Z")
                            company = await company_elem.text_content() if company_elem else "Unknown"
                            
                            # Location
                            location_elem = await elem.query_selector("span.JobCard_location__eHMFj")
                            loc = await location_elem.text_content() if location_elem else location
                            
                            if title and link:
                                job = JobCreate(
                                    title=title.strip(),
                                    company=company.strip(),
                                    description=title.strip(),
                                    location=loc.strip() if loc else location,
                                    job_type="full-time",
                                    source="glassdoor",
                                    apply_link=link.split("?")[0]
                                )
                                jobs.append(job)
                        
                        except Exception as e:
                            logger.debug(f"Error extracting Glassdoor job: {str(e)}")
                            continue
                
                finally:
                    await browser.close()
            
            logger.info(f"Glassdoor: Extracted {len(jobs)} jobs")
        
        except ImportError:
            logger.warning("Playwright not available for Glassdoor scraping")
        except Exception as e:
            logger.error(f"Error scraping Glassdoor: {str(e)}")
        
        return jobs[:max_results]
    
    @staticmethod
    async def scrape_linkedin(
        roles: List[str],
        locations: List[str],
        max_results: int = 25
    ) -> List[JobCreate]:
        """
        Scrape jobs from LinkedIn
        
        Note: LinkedIn prohibits scraping in Terms of Service.
        Uses official API (requires paid access) or delegates to free alternatives.
        
        For MVP, we skip LinkedIn to avoid legal issues and focus on other sources.
        """
        logger.info(f"LinkedIn scraping requested for {roles}")
        logger.warning("LinkedIn requires paid API access - using alternative sources instead")
        
        return []
    
    @staticmethod
    async def scrape_stack_overflow(
        roles: List[str],
        locations: List[str],
        max_results: int = 25
    ) -> List[JobCreate]:
        """
        Scrape jobs from Stack Overflow Jobs
        
        Uses BeautifulSoup for HTML parsing + aiohttp for async requests.
        Stack Overflow Jobs lists developer opportunities.
        """
        logger.info(f"Scraping Stack Overflow Jobs for {roles}")
        
        jobs = []
        
        try:
            from bs4 import BeautifulSoup
            
            query = " ".join(roles)
            
            search_url = f"https://stackoverflow.com/jobs?q={quote(query)}"
            if locations:
                search_url += f"&l={quote(locations[0])}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(search_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                        if resp.status == 200:
                            html = await resp.text()
                            soup = BeautifulSoup(html, "html.parser")
                            
                            # Stack Overflow job listings
                            job_cards = soup.find_all("div", {"class": "s-job-card"})[:max_results]
                            
                            for card in job_cards:
                                try:
                                    # Extract job title and link
                                    title_elem = card.find("h2", {"class": "s-user-card--top"}) or card.find("a", {"class": "s-link"})
                                    if not title_elem:
                                        title_elem = card.find("a")
                                    
                                    if not title_elem:
                                        continue
                                    
                                    title = title_elem.text.strip()
                                    
                                    # Try to find the actual job link
                                    link = None
                                    link_elem = card.find("a", href=True)
                                    if link_elem:
                                        link = link_elem.get("href", "")
                                    
                                    if link and not link.startswith("http"):
                                        link = f"https://stackoverflow.com{link}"
                                    
                                    # Extract company
                                    company_elem = card.find("a", {"class": "employer"})
                                    if not company_elem:
                                        company_elem = card.find("span", {"class": "-company"})
                                    company = company_elem.text.strip() if company_elem else "Unknown"
                                    
                                    # Extract location
                                    location_elem = card.find("span", {"class": "-location"})
                                    loc = location_elem.text.strip() if location_elem else (locations[0] if locations else "Remote")
                                    
                                    # Extract brief description
                                    desc_elems = card.find_all("p")
                                    description = desc_elems[0].text.strip() if desc_elems else title
                                    
                                    if title and link:
                                        job = JobCreate(
                                            title=title,
                                            company=company,
                                            description=description[:500],
                                            location=loc,
                                            job_type="full-time",
                                            source="stack_overflow",
                                            apply_link=link.split("?")[0]
                                        )
                                        jobs.append(job)
                                
                                except Exception as e:
                                    logger.debug(f"Error extracting Stack Overflow job: {str(e)}")
                                    continue
                
                except Exception as e:
                    logger.warning(f"HTTP error scraping Stack Overflow: {str(e)}")
        
        except ImportError:
            logger.warning("BeautifulSoup not available for Stack Overflow scraping")
        except Exception as e:
            logger.error(f"Error scraping Stack Overflow: {str(e)}")
        
        return jobs[:max_results]
    
    @staticmethod
    async def scrape_dice(
        roles: List[str],
        locations: List[str],
        max_results: int = 25
    ) -> List[JobCreate]:
        """
        Scrape jobs from Dice.com
        
        Uses Playwright for dynamic content + JavaScript rendering.
        Dice focuses on technical jobs (IT, software, hardware).
        """
        logger.info(f"Scraping Dice.com for {roles}")
        
        jobs = []
        
        try:
            from playwright.async_api import async_playwright
            
            query = "+".join(roles)
            location = locations[0] if locations else ""
            
            # Dice search URL
            search_url = f"https://www.dice.com/jobs?q={quote(query)}"
            if location:
                search_url += f"&location={quote(location)}"
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                await page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                
                try:
                    await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
                    await page.wait_for_timeout(2500)  # Wait for JS rendering
                    
                    # Extract job listings
                    # Dice uses diceJobCard class for job listings
                    job_elements = await page.query_selector_all("div[class*='diceJobCard']")
                    
                    if not job_elements:
                        # Try alternative selector
                        job_elements = await page.query_selector_all("div[class*='job-card']")
                    
                    for elem in job_elements[:max_results]:
                        try:
                            # Job title
                            title_elem = await elem.query_selector("a[role='option']") or \
                                        await elem.query_selector("a[class*='job-title']") or \
                                        await elem.query_selector("a")
                            
                            title = await title_elem.text_content() if title_elem else None
                            
                            # Job link
                            link = await title_elem.get_attribute("href") if title_elem else None
                            if link and not link.startswith("http"):
                                link = f"https://www.dice.com{link}"
                            
                            # Company
                            company_elem = await elem.query_selector("div[class*='company']") or \
                                          await elem.query_selector("span[class*='company']")
                            company = await company_elem.text_content() if company_elem else "Unknown"
                            
                            # Location
                            location_elem = await elem.query_selector("div[class*='location']") or \
                                           await elem.query_selector("span[class*='location']")
                            loc = await location_elem.text_content() if location_elem else (location or "Unknown")
                            
                            # Description
                            desc_elem = await elem.query_selector("div[class*='description']") or \
                                       await elem.query_selector("p[class*='summary']")
                            description = await desc_elem.text_content() if desc_elem else title
                            
                            if title and link:
                                job = JobCreate(
                                    title=title.strip(),
                                    company=company.strip() if company else "Unknown",
                                    description=description.strip() if description else title,
                                    location=loc.strip() if loc else "Unknown",
                                    job_type="full-time",
                                    source="dice",
                                    apply_link=link.split("?")[0]
                                )
                                jobs.append(job)
                        
                        except Exception as e:
                            logger.debug(f"Error extracting Dice job: {str(e)}")
                            continue
                
                finally:
                    await browser.close()
            
            logger.info(f"Dice: Extracted {len(jobs)} jobs")
        
        except ImportError:
            logger.warning("Playwright not available for Dice scraping")
        except Exception as e:
            logger.error(f"Error scraping Dice: {str(e)}")
        
        return jobs[:max_results]

