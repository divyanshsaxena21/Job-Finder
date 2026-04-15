# Advanced Features: Quality Scoring, Job Portals & Enhancement

## Overview

Job Finder now includes advanced intelligent features to improve application quality, detect dangerous/spam job postings, expand job discovery, and provide comprehensive insights.

## Feature 1: Job Quality Scoring

### What It Does

Analyzes each job posting to detect:
- **Spam Posts**: Generic, low-effort postings
- **Scams**: Pyramid schemes, visa fraud, upfront fees required
- **Low Quality**: Incomplete descriptions, suspicious details
- **Red Flags**: All-caps text, excessive punctuation, generic language

### How It Works

```
Job Posted
    ↓
Quality Scorer analyzes:
    ├─ Red Flag Keywords (spam, scam, "easy money", etc.)
    ├─ Company Legitimacy (known companies credit: +points)
    ├─ Description Quality (length, professional language)
    ├─ Salary Sanity Check (min/max ratio, unrealistic values)
    ├─ Capitalization Ratio (excessive ALL CAPS)
    ├─ Punctuation Usage (too many !!!)
    ├─ Generic Language ("team player", "work hard")
    └─ Special Scam Detection (relocation fraud, MLM)
    ↓
Score: 0-100
    ├─ 80-100: Excellent ✓ (Apply)
    ├─ 60-79: Good ✓ (Apply)
    ├─ 40-59: Fair ⚠️ (Manual review or skip)
    └─ 0-39: Poor ✗ (Skip)
    ↓
Decision: Apply / Skip / Flag
```

### Implementation

Located in `app/services/quality_scorer.py`:

```python
@staticmethod
def score_job(
    job_title: str,
    company_name: str,
    description: str,
    salary_min: float = None,
    salary_max: float = None
) -> Tuple[int, str, Dict]:
    """
    Score job quality (0-100)
    
    Returns:
        (score, reason, details)
    """
```

### Scoring Criteria

#### 1. Red Flag Detection (-15 points each)

**Spam Keywords**:
- "click here", "call now", "work from home guaranteed"
- "make money fast", "easy money", "no experience needed"
- "too good to be true", "risk free", "guaranteed income"

**Scam Keywords**:
- "wire transfer", "upfront payment", "application fee"
- "money back guarantee", "no interview", "instant hire"

**Low Effort Keywords**:
- "work whenever", "no deadlines", "minimal requirements"

#### 2. Company Legitimacy (+10-30 bonus)

Known Quality Companies (+30):
- Google, Microsoft, Amazon, Apple, Meta, Netflix
- Spotify, Slack, Stripe, Figma, Canva, Notion
- GitHub, GitLab, JetBrains, IBM, Oracle, Salesforce

Unknown Company: +10 (neutral)
Short Name: -20 (suspicious)

#### 3. Description Quality

Length Check:
- Too short (<100 chars): -20 points
- Too long (>50K chars): -10 points
- Normal (100-50K): +20 points

Professional Language:
- Has "responsibilities", "requirements", "qualifications", "benefits": +15 points
- Missing: -15 points

#### 4. Salary Analysis

Valid Salary Range (min < max):
- Ratio > 5x (e.g., $30K-$200K): -20 points (suspicious)
- Minimum < $10K: -25 points (unrealistic)
- Normal range: +25 points

#### 5. Text Style Analysis

Capitalization:
- >20% ALL CAPS words: -15 points

Punctuation:
- >1% exclamation/question marks: -10 points

Generic Language Count:
- 3+ generic phrases: -10 points

### Example Quality Scores

| Job | Score | Reason |
|-----|-------|--------|
| Senior Python Dev at Google | 95 | Known company, detailed description, realistic salary |
| Software Engineer at TechStartup | 75 | Unknown startup, reasonable description, no salary |
| "EARN $5000/WEEK FROM HOME!!!" | 15 | Multiple red flags: spam keywords, all caps, $$ spam |
| Work From Home Data Entry | 35 | Generic description, low effort posting, MLM warning |
| Visa Sponsorship Job Abroad | 40 | Relocation scam detector triggered, risky |

### Integration in Auto-Apply

```python
# In auto_apply.py orchestrator
quality_score, quality_reason, details = JobQualityScorer.score_job(
    job.title, job.company, job.description
)

should_skip, skip_reason = JobQualityScorer.should_skip_job(
    quality_score, 
    min_quality=50  # Skip if <50
)

if should_skip:
    logger.info(f"Skipping low-quality job: {skip_reason}")
    run.jobs_skipped += 1
    continue  # Don't apply to this job
```

### User Configuration

Add to UserPreferences:
```python
min_job_quality: int = 50  # Minimum acceptable quality (0-100)
```

Frontend setting: "Minimum Job Quality" slider (0-100)

## Feature 2: New Job Portals

### Additional Scraping Sources

Updated to scrape from **6 jobs sources** instead of 4:

| Portal | Type | Method | Speed | Quality |
|--------|------|--------|-------|---------|
| Indeed | Aggregator | Playwright (JS) | 8-12s | Excellent |
| Naukri | Aggregator (India) | BeautifulSoup | 3-5s | Good |
| Glassdoor | Aggregator | Playwright (JS) | 10-15s | Good |
| GitHub Jobs | Aggregator | Free API | 1-2s | Good |
| **Stack Overflow** | **Tech-focused** | **BeautifulSoup** | **3-5s** | **Excellent** |
| **Dice.com** | **Tech-focused** | **Playwright (JS)** | **8-12s** | **Good** |

### Stack Overflow Jobs

**URL**: https://stackoverflow.com/jobs?q={query}&l={location}

**Characteristics**:
- Developer-focused (best quality for tech roles)
- No registration required to view
- Long descriptions (typically 500-2000 chars)
- Good salary information
- Rarely spam/scams (vetted by SO community)

**Implementation**:
```python
@staticmethod
async def scrape_stack_overflow(
    roles: List[str],
    locations: List[str],
    max_results: int = 25
) -> List[JobCreate]:
    """Scrape Stack Overflow Jobs using BeautifulSoup"""
    # Uses aiohttp + BeautifulSoup for fast parsing
    # Extracts: Title, company, location, description, apply link
```

**Quality**: 90%+ legitimate developer jobs
**Red Flags**: Rare (<1%)

### Dice.com

**URL**: https://www.dice.com/jobs?q={query}&location={location}

**Characteristics**:
- Specialized in IT/tech roles (system admin, networking, cloud)
- Wide variety of contracts and permanent positions
- Good for both junior and senior roles
- Moderate spam (5-10% MLM/recruiting scams)

**Implementation**:
```python
@staticmethod
async def scrape_dice(
    roles: List[str],
    locations: List[str],
    max_results: int = 25
) -> List[JobCreate]:
    """Scrape Dice.com using Playwright"""
    # JavaScript-heavy site requires headless browser
    # Extracts job cards with detailed tech stack info
```

**Quality**: 85-90% legitimate IT jobs
**Red Flags**: 5-10% recruiting firm spam

### LinkedIn (Future)

**URL**: https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}

**Status**: **Not implemented (requires paid API)**

**Why Not Included**:
1. LinkedIn ToS prohibits scraping
2. Official API requires paid tier ($)
3. High-volume queries get blocked
4. Risk of account suspension

**Future**: When budget allows, integrate LinkedIn API for premium quality job sources.

### Job Distribution Across Sources

With 6 sources, jobs are evenly distributed:

```
scrape_jobs(max_results=60)
    ├─ Indeed: 10 jobs (17%)
    ├─ Naukri: 10 jobs (17%)
    ├─ Glassdoor: 10 jobs (17%)
    ├─ GitHub Jobs: 10 jobs (17%)
    ├─ Stack Overflow: 10 jobs (17%)
    └─ Dice: 10 jobs (17%)
    ↓
    Deduplicate across all sources
    ↓
    Total: 50-60 unique jobs per trigger
```

### Expected Results

| Metric | Previous (4 sources) | Now (6 sources) |
|--------|----------------------|-----------------|
| Jobs Found | 40-80 | 60-120 |
| Dev-Focused Jobs | 20-30 | 40-60 |
| Average Quality | 75% | 80% |
| Spam/Scam Ratio | 10-15% | 5-10% |
| Time to Fetch | 15-20s | 18-25s |

## Feature 3: CAPTCHA Detection & Handling

### What It Does

Detects various CAPTCHA types and provides handling strategies:

```
Form Submission
    ↓
Detect CAPTCHA?
    ├─ Yes → Wait for Human (up to 5 minutes)
    │  ├─ CAPTCHA solved → Continue submission
    │  └─ Timeout → Flag job for manual review
    └─ No → Continue filling form normally
```

### Implementation

Located in `app/services/form_submission.py`:

```python
@staticmethod
async def check_captcha_present(page: Page) -> bool:
    """Check if CAPTCHA is present on page"""
    # Detects: reCAPTCHA, hCaptcha, hcaptcha
    # Returns True if CAPTCHA found

@staticmethod
async def wait_for_human_captcha(
    page: Page, 
    timeout_seconds: int = 300
) -> bool:
    """Wait for human to solve CAPTCHA"""
    # Polls every 2 seconds for up to 5 minutes
    # Returns True if CAPTCHA appears solved
```

### Supported CAPTCHA Types

| Type | Detection | Handling |
|------|-----------|----------|
| **reCAPTCHA v2** | `div[class*='recaptcha']` | Wait for solve (checkbox) |
| **reCAPTCHA v3** | Invisible, no detection possible | Skip job if v3 detected |
| **hCaptcha** | `div[class*='h-captcha']` | Wait for solve |
| **Text CAPTCHA** | Text patterns in HTML | Unsolveable, skip |
| **Image CAPTCHA** | Image blocks in form | Requires OCR, skip |

### Strategy: When CAPTCHA Detected

1. **Detection**: Check page DOM for CAPTCHA elements
2. **Logging**: Log job as "CAPTCHA_BLOCKED"
3. **Wait**: Allow human to solve for up to 5 minutes
4. **Verify**: Check if CAPTCHA gone after solve
5. **Continue**: If verify passes, continue submission
6. **Timeout**: If timeout, flag job and move to next

### Example Flow

```python
# In FormSubmissionService._submit_indeed()
if await FormSubmissionService.check_captcha_present(page):
    logger.warning("CAPTCHA detected - waiting for human")
    
    solved = await FormSubmissionService.wait_for_human_captcha(
        page, 
        timeout_seconds=300  # 5 minute timeout
    )
    
    if solved:
        logger.info("CAPTCHA solved, continuing...")
        # Continue with form submission
    else:
        logger.warning("CAPTCHA timeout")
        return False, "CAPTCHA timeout - requires manual intervention"
```

## Feature 4: Proxy Rotation (Future)

### Why Proxy Rotation?

- **Rate Limiting**: Job sites block IPs after many requests
- **Geographic Variety**: Test with different geo-locations
- **Stealth**: Less detectable as automated scraper

### Implementation Plan

```python
@staticmethod
class ProxyRotator:
    proxies: List[str] = []  # List of proxy URLs
    current_index: int = 0
    
    @staticmethod
    def get_proxy() -> Optional[str]:
        """Get next proxy in rotation"""
        if not ProxyRotator.proxies:
            return None
        
        proxy = ProxyRotator.proxies[ProxyRotator.current_index]
        ProxyRotator.current_index = (
            ProxyRotator.current_index + 1
        ) % len(ProxyRotator.proxies)
        
        return proxy
    
    @staticmethod
    def mark_blocked(proxy: str):
        """Remove blocked proxy from rotation"""
        ProxyRotator.proxies.remove(proxy)
```

### Configuration

```bash
PROXY_LIST=http://proxy1.com:8080,http://proxy2.com:8080,http://proxy3.com:8080
PROXY_USERNAME=user
PROXY_PASSWORD=pass
USE_PROXY_ROTATION=false  # Disable by default
```

### Future Implementation

1. **Free Proxy Lists**: ZenRows, ProxyMesh free tier
2. **Smart Rotation**: Use least-blocked proxy first
3. **Block Recovery**: Rotate after 3 consecutive timeouts
4. **Speed Tradeoff**: Proxy adds 1-2 seconds per request

**Status**: Not implemented in MVP, can be added later for scale.

## Complete Auto-Apply Workflow

Full workflow with all features:

```
User Triggers Auto-Apply
    ↓
Scrape Jobs from 6 Sources (parallel)
    ├─ Indeed: 10-15 jobs
    ├─ Naukri: 5-10 jobs
    ├─ Glassdoor: 10-15 jobs
    ├─ GitHub Jobs: 15-25 jobs
    ├─ Stack Overflow: 10-15 jobs
    └─ Dice: 8-12 jobs
    ↓ (Deduplicate) → 50-100 unique jobs
    
For each job:
    ├─ [1] QUALITY SCORE
    │  ├─ Analyze for spam/scams
    │  ├─ Check company legitimacy
    │  ├─ Validate description quality
    │  └─ Result: Score 0-100, Quality: "Excellent/Good/Fair/Poor"
    │
    ├─ Skip if quality < 50? → YES → Next job
    │
    ├─ [2] SKILL MATCHING
    │  ├─ Extract job keywords
    │  ├─ Compare with user skills
    │  └─ Result: Match score 0-100%
    │
    ├─ Skip if match < 40%? → YES → Next job
    │
    ├─ [3] RESUME CUSTOMIZATION
    │  ├─ Reorder skills by job relevance
    │  ├─ Add relevant GitHub projects
    │  └─ Result: Job-specific resume
    │
    ├─ [4] COVER LETTER GENERATION (Groq AI)
    │  ├─ Create prompt from job details
    │  ├─ Call Groq API (Mixtral 8x7B)
    │  └─ Result: Personalized cover letter
    │
    ├─ [5] APPLICATION SUBMISSION
    │  ├─ Launch Playwright browser
    │  ├─ Navigate to apply link
    │  ├─ Detect job platform (Indeed, Naukri, etc.)
    │  ├─ Fill form fields:
    │  │  ├─ Email
    │  │  ├─ Name
    │  │  ├─ Phone
    │  │  └─ Resume (upload)
    │  ├─ [CHECK CAPTCHA PRESENT?]
    │  │  ├─ Yes → Wait for human (5 min timeout)
    │  │  └─ No → Continue
    │  ├─ Click submit button
    │  └─ Result: Applied / Failed with reason
    │
    └─ Save to applications collection
        ├─ status: applied/failed
        ├─ cover_letter: AI-generated
        ├─ quality_score: 0-100
        ├─ match_score: 0-100
        └─ submit_error: error message if failed
    
↓ (Repeat for all jobs up to max_daily_applications)

Save Run Summary
    ├─ jobs_found: 87
    ├─ jobs_applied: 12
    ├─ jobs_skipped: 72
    │  ├─ 35: Low quality
    │  ├─ 25: Low skill match
    │  ├─ 5: Already applied
    │  └─ 7: Duplicate
    ├─ jobs_failed: 3
    │  ├─ 1: CAPTCHA timeout
    │  ├─ 1: Form not found
    │  └─ 1: Network error
    └─ completed_at: timestamp

Update User Dashboard
    ├─ Show applied jobs with quality scores
    ├─ Display failure reasons for troubleshooting
    ├─ Trend analysis: Quality over time
    └─ Success rate: Applied / Found
```

## Database Integration

### Updated applications Collection

```javascript
{
    user_id: ObjectId,
    job_id: String,
    company: String,
    job_title: String,
    
    // Customization
    resume: String,                    // Customized resume
    cover_letter: String,              // AI-generated letter
    
    // Scoring
    quality_score: Number,             // 0-100 job quality
    match_score: Number,               // 0-100 skill match
    quality_reason: String,            // Why score is X
    
    // Submission
    status: String,                    // applied/failed/manual_review
    submission_status: String,         // "Successfully submitted to Indeed"
    submission_error: String,          // Error message if failed
    submitted_at: Date,
    
    // Metadata
    source: String,                    // indeed/naukri/glassdoor/etc
    created_at: Date,
    updated_at: Date
}
```

## Statistics & Analytics

New dashboard metrics:

```
Statistics Dashboard:

├─ application_quality
│  ├─ average: 72.5%
│  ├─ excellent: 25 (21%)
│  ├─ good: 55 (47%)
│  ├─ fair: 30 (26%)
│  └─ poor: 8 (6%)
│
├─ source_breakdown
│  ├─ Indeed: 28 (24%)
│  ├─ Naukri: 12 (10%)
│  ├─ Glassdoor: 22 (19%)
│  ├─ GitHub: 31 (26%)
│  ├─ Stack Overflow: 18 (15%)
│  └─ Dice: 6 (5%)
│
├─ success_metrics
│  ├─ total_jobs_found: 117
│  ├─ jobs_applied: 42
│  ├─ success_rate: 36%
│  ├─ avg_quality_applied: 78%
│  └─ avg_quality_skipped: 38%
│
└─ failure_analysis
   ├─ quality_skips: 45 (38%)
   ├─ skill_match_skips: 22 (19%)
   ├─ captcha_timeouts: 2
   ├─ form_not_found: 1
   └─ network_errors: 3
```

## Performance Impact

### Time Estimates (for 50 jobs)

| Phase | Time | Notes |
|-------|------|-------|
| Job Scraping (6 sources) | 20s | Parallel execution |
| Quality Scoring | 10s | 50 jobs × 200ms each |
| Skill Matching | 8s | Keyword extraction |
| Resume Customization | 5s | Per-job tailoring |
| Cover Letter Generation | 45s | 12 jobs × 3.5s (Groq API) |
| Form Submissions | 150s | 12 jobs × 12s each (sequential) |
| **Total** | **238s** | ~4 minutes |

### Resource Usage

- **CPU**: Moderate (form submission is CPU-light with Playwright)
- **Memory**: 500-800 MB per run (Playwright browsers)
- **Network**: 10-50 MB per run
- **API Usage**: 
  - Groq: 12 requests per full run
  - GitHub API: 1 request (optional)

## References

- [Stack Overflow Jobs](https://stackoverflow.com/jobs)
- [Dice.com Jobs](https://www.dice.com/jobs)
- [Indeed Jobs](https://indeed.com/jobs)
- [Naukri Jobs](https://www.naukri.com/)

## Future Enhancements

1. **LinkedIn Integration**: When API becomes affordable
2. **Angel List**: For startup opportunities
3. **Craigslist**: For local jobs
4. **Custom Job Boards**: Enterprise client job sites
5. **Email Parsing**: Extract job postings from forwarded emails
6. **Job Alerts**: Real-time notifications for high-quality matches
7. **ML Quality Scorer**: Train model on user-rated jobs
8. **Cover Letter A/B Testing**: Test variants to maximize response
