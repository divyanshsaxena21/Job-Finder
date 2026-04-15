"""
Quick test script to verify real job scrapers work
"""

import asyncio
import sys
sys.path.insert(0, '/mnt/d/Project/Job-Finder/backend')

from app.models.schemas import UserPreferencesResponse
from app.services.job_scraper import JobScraperService

async def test_scrapers():
    """Test all job scrapers with real data"""
    
    # Create test preferences
    prefs = UserPreferencesResponse(
        user_id="test_user",
        skills=["Python", "React", "AWS"],
        roles=["Python Developer", "Full Stack Developer"],
        location=["Remote", "United States"],
        experience=3,
        job_type=["full-time", "contract"],
        min_salary=80000,
        max_salary=150000
    )
    
    print("=" * 60)
    print("TESTING REAL JOB SCRAPERS")
    print("=" * 60)
    print(f"\nSearching for: {prefs.roles}")
    print(f"Locations: {prefs.location}")
    print(f"Skills: {prefs.skills}\n")
    
    # Test Indeed scraper
    print("\n[1] Testing Indeed Scraper...")
    indeed_jobs = await JobScraperService.scrape_indeed(
        prefs.roles, prefs.location, 5
    )
    print(f"✓ Found {len(indeed_jobs)} jobs from Indeed")
    for job in indeed_jobs[:2]:
        print(f"  - {job.title} @ {job.company} ({job.source})")
    
    # Test Naukri scraper
    print("\n[2] Testing Naukri Scraper...")
    naukri_jobs = await JobScraperService.scrape_naukri(
        prefs.roles, prefs.location, 5
    )
    print(f"✓ Found {len(naukri_jobs)} jobs from Naukri")
    for job in naukri_jobs[:2]:
        print(f"  - {job.title} @ {job.company} ({job.source})")
    
    # Test Glassdoor scraper
    print("\n[3] Testing Glassdoor Scraper...")
    glassdoor_jobs = await JobScraperService.scrape_glassdoor(
        prefs.roles, prefs.location, 5
    )
    print(f"✓ Found {len(glassdoor_jobs)} jobs from Glassdoor")
    for job in glassdoor_jobs[:2]:
        print(f"  - {job.title} @ {job.company} ({job.source})")
    
    # Test Free APIs
    print("\n[4] Testing Free Job APIs...")
    api_jobs = await JobScraperService.scrape_free_api(
        prefs.roles, prefs.location, 5
    )
    print(f"✓ Found {len(api_jobs)} jobs from Free APIs")
    for job in api_jobs[:2]:
        print(f"  - {job.title} @ {job.company} ({job.source})")
    
    # Test combined scraping
    print("\n[5] Testing Combined Scraper (all sources in parallel)...")
    all_jobs = await JobScraperService.scrape_jobs(prefs, max_results=20)
    print(f"✓ Found {len(all_jobs)} total unique jobs")
    
    # Group by source
    sources = {}
    for job in all_jobs:
        sources[job.source] = sources.get(job.source, 0) + 1
    
    print("\nJobs by source:")
    for source, count in sorted(sources.items()):
        print(f"  - {source}: {count} jobs")
    
    # Show sample jobs
    print("\nSample jobs found:")
    for i, job in enumerate(all_jobs[:5], 1):
        print(f"\n{i}. {job.title}")
        print(f"   Company: {job.company}")
        print(f"   Location: {job.location}")
        print(f"   Source: {job.source}")
        print(f"   Apply: {job.apply_link[:60]}...")

if __name__ == "__main__":
    asyncio.run(test_scrapers())
