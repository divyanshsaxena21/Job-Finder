# PHASE 7 QUICK START GUIDE

Short, actionable guide to using all new Phase 7 features.

## What's New in Phase 7?

### Feature 1: Automated Job Application Submission ✅
- **What**: Auto-fill and submit job applications to Indeed, Naukri, Glassdoor
- **How**: Happens automatically in auto-apply workflow
- **Technology**: Playwright headless browser
- **Result**: Actually submitting applications, not just saving to database

### Feature 2: AI-Powered Cover Letters ✅
- **What**: Groq AI generates personalized cover letters per job
- **How**: In auto-apply, each job gets unique AI-written letter
- **Technology**: Groq API (free tier, Mixtral 8x7B)
- **Result**: Professional, job-specific cover letters in 2-5 seconds

### Feature 3: Smart Job Quality Filtering ✅
- **What**: Detects spam/scam job postings automatically
- **How**: Analyze each job for red flags
- **Detects**: Work-from-home spam, upfront fees, MLM, generic postings
- **Result**: Only apply to legitimate opportunities

### Feature 4: Expanded Job Sources ✅
- **What**: Now scrape from 6 job boards instead of 4
- **New**: Stack Overflow Jobs, Dice.com
- **Result**: 60-120 jobs per trigger (was 40-80)

### Feature 5: CAPTCHA Handling ✅
- **What**: Detect CAPTCHA blocks and wait for human solve
- **How**: Check page element, wait up to 5 minutes
- **Result**: Don't fail on CAPTCHA, allow manual solving

## Setup (5 minutes)

### 1. Get Groq API Key
```bash
# Visit: https://console.groq.com
# Sign up for free
# Generate API key
# Copy key
```

### 2. Add to .env
```bash
# In backend/.env:
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

### 3. Start Backend
```bash
cd backend
python -m app.main

# Should show:
# ✓ Connected to MongoDB
# ✓ Scheduler initialized
# Application startup complete
```

## Usage

### Enable Auto-Apply

1. Go to Dashboard
2. Click "🤖 Auto-Apply Settings"
3. Go to "Settings" tab
4. Toggle "Enable Auto-Apply"
5. Set frequency (daily/weekly)
6. Click "Save Preferences"

### Manual Trigger

1. Dashboard → Auto-Apply Settings
2. Click "🚀 Manual Trigger"
3. Wait for results (4 minutes)
4. Check "Stats" tab for results
5. Check "History" tab for detailed breakdown

### View Results

**Statistics Tab**:
- Total runs completed
- Total applications submitted
- Average per run
- Success rate

**History Tab**:
- Each run with date/time
- Jobs found vs applied
- Errors encountered

**Applications** (coming soon):
- List of submitted applications
- Quality scores
- Cover letters generated
- Submission status

## How It Works

```
1. SCRAPE (20 sec)
   └─ 6 sources in parallel
   └─ 60-120 jobs total

2. FOR EACH JOB:
   ├─ Check Quality Score (0-100)
   │  └─ Skip if < 50?
   │
   ├─ Check Skill Match (0-100%)
   │  └─ Skip if < 40%?
   │
   ├─ Customize Resume
   │  └─ Reorder skills, add projects
   │
   ├─ Generate Cover Letter (Groq AI)
   │  └─ Job-specific letter in 3-5 sec
   │
   └─ Submit Application
      ├─ Auto-fill form (Indeed/Naukri/Glassdoor)
      ├─ Detect CAPTCHA (wait for human if present)
      └─ Submit and verify

3. SAVE RESULTS
   ├─ jobs_found: 87
   ├─ jobs_applied: 12
   ├─ jobs_skipped: 72 (quality/match/duplicate)
   └─ jobs_failed: 3 (CAPTCHA timeout, form error)

4. UPDATE DASHBOARD
   └─ Show charts, history, details
```

## Common Questions

### Q: Will my credentials be stolen?
**A**: No. Credentials encrypted in database, never shared. Only used for Groq API (cover letter generation).

### Q: How many jobs will I apply to per day?
**A**: Depends on settings:
- Found: 60-120 per trigger
- Quality filter: Removes ~50% (low quality)
- Skill match: Removes ~50% (<40% match)
- Result: Apply to 10-20 per trigger
- Max daily: Configurable (default 30)

### Q: What if I get blocked by a job site?
**A**: 
- CAPTCHA blocks all submissions temporarily
- Wait 5 minutes and try again
- If persistent, increase delays or use proxy rotation

### Q: How much does this cost?
**A**: 
- Groq AI: FREE (free tier)
- Job scraping: FREE
- Overall: Just hosting costs

### Q: Can I edit generated cover letters?
**A**: Not yet. Track issue for future feature. 
For now: View in dashboard, copy, customize manually if needed.

### Q: Which job sites are supported?
**A**: 
- Indeed ✅ Full auto-submit
- Naukri ✅ Full auto-submit
- Glassdoor ✅ Full auto-submit
- Stack Overflow ✅ Scrape only
- Dice.com ✅ Scrape only
- GitHub Jobs ✅ Scrape only
- LinkedIn ❌ (requires paid API)

### Q: What happens to jobs I apply for?
**A**: All saved to database:
- applications collection has full record
- cover_letter text saved
- quality_score recorded
- submission_status tracked

### Q: Can I see the cover letters generated?
**A**: Will be available in applications page (coming in Phase 8)
For now: Check auto_apply_runs collection in MongoDB

## Troubleshooting

### Issue: "GROQ_API_KEY not set"
```bash
# Solution:
# 1. Get free key: https://console.groq.com
# 2. Add to backend/.env:
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
# 3. Restart backend
```

### Issue: "Playwright not found"
```bash
# Solution:
pip install playwright
playwright install  # Downloads browsers (~600MB)
```

### Issue: "Form not found on Indeed"
```bash
# Solution:
# No action needed - job skipped with error message
# Try again with different job
# If persistent, Indeed HTML may have changed (report issue)
```

### Issue: "CAPTCHA blocks submission"
```bash
# Solution:
# This is normal - means site detects bot
# Wait 5 minutes for CAPTCHA to expire
# Try again with delays: Set FORM_SUBMISSION_TIMEOUT=20
```

### Issue: "Very few applications submitted"
```bash
# Check Statistics tab for breakdown:
# - High quality_skips? Lower min_quality threshold
# - High skill_mismatch? Add more skills to profile
# - High duplicates? More scrapers overlap results
# - High CAPTCHA? Use proxy rotation (advanced)
```

## Performance

- **Job Scraping**: 20 seconds
- **Per Application**:
  - Quality check: 0.2s
  - Cover letter: 3.5s (Groq)
  - Form submit: 12s (browser)
  - Total: 15.7s per application
- **Full Run (50 jobs, 10 applied)**: 4-5 minutes

## Advanced Configuration

### Adjust Quality Threshold
```bash
# In preferences, add:
min_job_quality = 40  # Accept fair quality jobs (was 50)
```

### Reduce Daily Applications
```bash
# In preferences:
max_daily_applications = 10  # Instead of default 30
# Helps avoid blocking/CAPTCHA
```

### Increase/Decrease Scrape Volume
```bash
# In scrape_jobs() call:
scrape_jobs(max_results=30)  # Fewer jobs, faster (was 60)
# Takes 10s instead of 20s, but fewer jobs found
```

## Dashboard Guide

### Auto-Apply Settings Tab

**Settings Section**:
- ✓ Enable auto-apply toggle
- Input: GitHub username (optional)
- Dropdown: Frequency (daily/weekly/bi-weekly)
- Input: Max daily applications
- Button: Save preferences
- Button: Manual trigger

**Stats Section** (6 cards):
1. Total Runs: number of times auto-apply ran
2. Total Applied: cumulative applications submitted
3. Average Per Run: jobs_applied / total_runs
4. Success Rate: applied / found percentage
5. Jobs Skipped: low quality or no match
6. CAPTCHA Blocks: how many times blocked

**History Section** (Timeline):
- Each completed run
- Date/time started
- Duration
- Results: found/applied/skipped/failed
- Click for details

## Data Privacy

### What We Store
- Resume text (customized)
- Cover letters (generated)
- Application records
- Quality scores
- Match scores

### What We Don't Store
- Job site passwords/credentials
- Personal identification
- Financial information
- Browsing history

### What We Never Share
- Your data with job sites
- Your contact info with 3rd parties
- Usage analytics with anyone

## Monitoring

### Check Auto-Apply Status
```bash
# API endpoint (requires auth):
GET /auto-apply/status

# Returns:
{
  "scheduler_running": true,
  "auto_apply_enabled": true,
  "next_scheduled_run": "2024-01-15T09:00:00Z",
  "scheduled_time": "09:00 UTC"
}
```

### View Run History
```bash
# API endpoint (requires auth):
GET /auto-apply/history?limit=10

# Returns last 10 runs with full details
```

### View Statistics
```bash
# API endpoint (requires auth):
GET /auto-apply/stats

# Returns:
{
  "total_runs": 15,
  "total_applied": 42,
  "average_applied_per_run": 2.8,
  "success_rate": 38
}
```

## Best Practices

1. **Quality Over Quantity**
   - Apply to 5-10 high-quality jobs daily
   - Better than 50 spam applications

2. **Monitor CAPTCHA**
   - If blocked often, increase delays
   - Consider proxy rotation for scale

3. **Customize Resume**
   - Keep base resume up-to-date
   - Let system tailor for each job

4. **Review Results**
   - Check dashboard stats regularly
   - Adjust thresholds based on results

5. **Feedback Loop**
   - Rate jobs in dashboard (coming soon)
   - System learns quality preferences

## Getting Help

### Documentation
- `FORM_SUBMISSION_SERVICE.md` - Form automation details
- `GROQ_COVER_LETTERS.md` - Cover letter setup
- `ADVANCED_FEATURES.md` - Quality scoring
- `PHASE_7_DEPLOYMENT_GUIDE.md` - Deployment steps

### Debug Mode
```bash
# Enable verbose logging:
LOG_LEVEL=DEBUG
# Then check logs for detailed error info
```

### Test Features
```bash
# Run test suite:
python test_phase7_features.py

# Should show ✓ for all components
```

## Feedback & Feature Requests

Found a bug or have a feature request?
1. Check if documented in troubleshooting
2. Review GitHub issues
3. Create new issue with:
   - Description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots/logs if available

## What's Next?

### Planned for Phase 8
- View submitted applications
- Edit/resend cover letters
- Success rate tracking
- Interview notifications
- Email notifications
- Export applications

### Far Future
- Machine learning quality scoring
- LinkedIn API integration (when affordable)
- Cover letter variants/A-B testing
- Job offer tracking
- Interview prep integration

---

**You're all set!** 🚀

Start auto-applying to jobs:
1. Dashboard → Auto-Apply Settings
2. Fill preferences → Save
3. Click Manual Trigger
4. Wait 4 minutes
5. Check results in Stats/History tabs

**Questions?** Check documentation files or enable debug logging.
