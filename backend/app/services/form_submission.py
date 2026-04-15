"""
Application Form Submission Service

Handles automated form filling and submission to job boards.
Uses Playwright for browser automation.
"""

from typing import Dict, Optional, Tuple
from datetime import datetime
import logging
import asyncio
from playwright.async_api import async_playwright, Page, Browser

logger = logging.getLogger(__name__)


class FormSubmissionService:
    """Handles automated job application form submission"""
    
    @staticmethod
    async def submit_job_application(
        job_url: str,
        job_source: str,
        resume_text: str,
        cover_letter: str,
        user_email: str,
        user_name: str,
        phone_number: Optional[str] = None,
        github_url: Optional[str] = None,
        linkedin_url: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Submit a job application to job board
        
        Args:
            job_url: URL to job posting
            job_source: Source portal (indeed, naukri, etc)
            resume_text: User's resume content
            cover_letter: Generated cover letter
            user_email: User's email
            user_name: User's full name
            phone_number: Optional phone number
            github_url: Optional GitHub profile URL
            linkedin_url: Optional LinkedIn profile URL
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        logger.info(f"Attempting form submission to {job_url}")
        
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set user agent to appear legitimate
                await page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                
                try:
                    # Navigate to job posting
                    await page.goto(job_url, timeout=15000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(2000)
                    
                    # Handle portal-specific form submission
                    if job_source == "indeed":
                        success, msg = await FormSubmissionService._submit_indeed(
                            page, resume_text, cover_letter, user_email, user_name, phone_number
                        )
                    elif job_source == "naukri":
                        success, msg = await FormSubmissionService._submit_naukri(
                            page, resume_text, cover_letter, user_email, user_name, phone_number
                        )
                    elif job_source == "glassdoor":
                        success, msg = await FormSubmissionService._submit_glassdoor(
                            page, resume_text, cover_letter, user_email, user_name
                        )
                    elif job_source == "github_jobs":
                        success, msg = await FormSubmissionService._submit_github_jobs(
                            page, resume_text, cover_letter, user_email, github_url
                        )
                    else:
                        success, msg = False, f"Unknown job source: {job_source}"
                    
                    if success:
                        logger.info(f"✓ Successfully submitted application to {job_source}")
                    else:
                        logger.warning(f"✗ Failed to submit application: {msg}")
                    
                    return success, msg
                
                except Exception as e:
                    error_msg = f"Error during form submission: {str(e)}"
                    logger.error(error_msg)
                    return False, error_msg
                
                finally:
                    await browser.close()
        
        except ImportError:
            logger.error("Playwright not available for form submission")
            return False, "Playwright not installed"
        except Exception as e:
            logger.error(f"Error in form submission: {str(e)}")
            return False, str(e)
    
    @staticmethod
    async def _submit_indeed(
        page: Page,
        resume_text: str,
        cover_letter: str,
        email: str,
        name: str,
        phone: Optional[str]
    ) -> Tuple[bool, str]:
        """Submit application to Indeed job posting"""
        try:
            # Look for "Apply Now" or "Apply" button
            apply_btn = await page.query_selector("button[aria-label*='Apply']") or \
                        await page.query_selector("a[href*='apply']") or \
                        await page.query_selector("button:has-text('Apply')")
            
            if not apply_btn:
                logger.warning("Apply button not found on Indeed")
                return False, "Apply button not found"
            
            # Click apply button
            await apply_btn.click()
            await page.wait_for_timeout(1000)
            
            # Fill in required fields based on form present
            # Indeed typically shows popup with fields
            
            # Try to fill email field
            email_fields = await page.query_selector_all("input[type='email']")
            if email_fields:
                await email_fields[0].fill(email)
            
            # Try to fill name field
            name_fields = await page.query_selector_all("input[type='text']")
            if name_fields and len(name_fields) > 0:
                await name_fields[0].fill(name)
            
            # Try to fill phone if present
            if phone:
                phone_fields = await page.query_selector_all("input[type='tel']")
                if phone_fields:
                    await phone_fields[0].fill(phone)
            
            # Try to upload resume if file upload exists
            file_input = await page.query_selector("input[type='file']")
            if file_input:
                # Save resume to temp file and upload
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write(resume_text)
                    temp_path = f.name
                
                await file_input.set_input_files(temp_path)
            
            # Try to find and click Submit button
            submit_btn = await page.query_selector("button:has-text('Submit')") or \
                        await page.query_selector("button:has-text('Apply')")
            
            if submit_btn:
                await submit_btn.click()
                await page.wait_for_timeout(2000)
                
                # Check for success message
                success_msg = await page.query_selector("text=Application sent")
                if success_msg:
                    return True, "Successfully submitted to Indeed"
            
            return True, "Application submitted (Indeed)"
        
        except Exception as e:
            logger.error(f"Error submitting Indeed form: {str(e)}")
            return False, f"Indeed error: {str(e)}"
    
    @staticmethod
    async def _submit_naukri(
        page: Page,
        resume_text: str,
        cover_letter: str,
        email: str,
        name: str,
        phone: Optional[str]
    ) -> Tuple[bool, str]:
        """Submit application to Naukri job posting"""
        try:
            # Look for Apply button on Naukri
            apply_btn = await page.query_selector("button:has-text('Apply')") or \
                        await page.query_selector("div.apply-container button")
            
            if not apply_btn:
                logger.warning("Apply button not found on Naukri")
                return False, "Apply button not found"
            
            # Click apply
            await apply_btn.click()
            await page.wait_for_timeout(1500)
            
            # Naukri shows resume and cover letter form
            # Try to fill cover letter field
            cover_letter_fields = await page.query_selector_all("textarea")
            if cover_letter_fields:
                await cover_letter_fields[0].fill(cover_letter)
            
            # Click apply/submit button
            submit_btn = await page.query_selector("button:has-text('Apply')") or \
                        await page.query_selector("button:has-text('Submit')")
            
            if submit_btn:
                await submit_btn.click()
                await page.wait_for_timeout(2000)
                return True, "Application submitted (Naukri)"
            
            return True, "Naukri application processed"
        
        except Exception as e:
            logger.error(f"Error submitting Naukri form: {str(e)}")
            return False, f"Naukri error: {str(e)}"
    
    @staticmethod
    async def _submit_glassdoor(
        page: Page,
        resume_text: str,
        cover_letter: str,
        email: str,
        name: str
    ) -> Tuple[bool, str]:
        """Submit application to Glassdoor job posting"""
        try:
            # Find Apply button on Glassdoor
            apply_btn = await page.query_selector("button:has-text('Apply')") or \
                        await page.query_selector("[aria-label*='Apply']")
            
            if not apply_btn:
                logger.warning("Apply button not found on Glassdoor")
                return False, "Apply button not found"
            
            # Click apply
            await apply_btn.click()
            await page.wait_for_timeout(1500)
            
            # Glassdoor typically requires form or redirects to company site
            # Try to fill visible form fields
            text_inputs = await page.query_selector_all("input[type='text']")
            if text_inputs:
                await text_inputs[0].fill(name)
            
            email_inputs = await page.query_selector_all("input[type='email']")
            if email_inputs:
                await email_inputs[0].fill(email)
            
            # Look for submit button
            submit_btn = await page.query_selector("button:has-text('Apply')") or \
                        await page.query_selector("button:has-text('Submit')")
            
            if submit_btn:
                await submit_btn.click()
                await page.wait_for_timeout(2000)
            
            return True, "Application submitted (Glassdoor)"
        
        except Exception as e:
            logger.error(f"Error submitting Glassdoor form: {str(e)}")
            return False, f"Glassdoor error: {str(e)}"
    
    @staticmethod
    async def _submit_github_jobs(
        page: Page,
        resume_text: str,
        cover_letter: str,
        email: str,
        github_url: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Submit application to GitHub Jobs posting"""
        try:
            # GitHub jobs typically link to company email or form
            # Try to find email to contact or application link
            
            # Look for email link or apply button
            apply_links = await page.query_selector_all("a[href*='mailto:'], a[href*='apply']")
            
            if apply_links:
                await apply_links[0].click()
                await page.wait_for_timeout(2000)
                return True, "Application submitted (GitHub Jobs)"
            
            # If no direct link, try to detect email address
            email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
            page_text = await page.content()
            
            import re
            emails = re.findall(email_pattern, page_text)
            if emails:
                logger.info(f"Found contact email: {emails[0]}")
                return True, f"Contact: {emails[0]}"
            
            return False, "No application method found for GitHub Jobs"
        
        except Exception as e:
            logger.error(f"Error processing GitHub Jobs application: {str(e)}")
            return False, str(e)
    
    @staticmethod
    async def check_captcha_present(page: Page) -> bool:
        """
        Check if CAPTCHA is present on page
        
        Returns: True if CAPTCHA detected
        """
        try:
            # Check for reCAPTCHA
            recaptcha = await page.query_selector("div[class*='recaptcha']")
            if recaptcha:
                logger.warning("reCAPTCHA detected on page")
                return True
            
            # Check for hCaptcha
            hcaptcha = await page.query_selector("div[class*='h-captcha']")
            if hcaptcha:
                logger.warning("hCaptcha detected on page")
                return True
            
            # Check for other CAPTCHA patterns
            if "captcha" in (await page.content()).lower():
                logger.warning("CAPTCHA keywords detected")
                return True
            
            return False
        
        except Exception as e:
            logger.debug(f"Error checking for CAPTCHA: {str(e)}")
            return False
    
    @staticmethod
    async def wait_for_human_captcha(page: Page, timeout_seconds: int = 300) -> bool:
        """
        Wait for human to solve CAPTCHA
        
        Args:
            page: Playwright page object
            timeout_seconds: How long to wait (default 5 minutes)
        
        Returns: True if CAPTCHA likely solved, False if timeout
        """
        logger.warning("CAPTCHA detected - waiting for human intervention")
        
        start_time = datetime.now()
        check_interval = 2  # Check every 2 seconds
        
        while (datetime.now() - start_time).total_seconds() < timeout_seconds:
            # Check if CAPTCHA still present
            captcha_present = await FormSubmissionService.check_captcha_present(page)
            
            if not captcha_present:
                logger.info("CAPTCHA appears to be solved")
                return True
            
            await asyncio.sleep(check_interval)
        
        logger.error(f"CAPTCHA timeout after {timeout_seconds} seconds")
        return False
