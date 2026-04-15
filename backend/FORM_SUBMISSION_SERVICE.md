# Form Submission Service Documentation

## Overview

The Form Submission Service (`app/services/form_submission.py`) handles automated job application form submission across multiple job platforms using Playwright browser automation.

## Features

- **Browser Automation**: Uses Playwright headless Chromium for form interaction
- **Multi-Platform Support**: Indeed, Naukri, Glassdoor, GitHub Jobs
- **Smart Field Detection**: Identifies and fills common form fields
- **File Upload**: Handles resume file uploads
- **CAPTCHA Detection**: Detects blocking CAPTCHAs and provides options
- **Error Handling**: Graceful error handling with detailed messages

## Architecture

### FormSubmissionService Class

Main service class with static methods for form submission:

```python
FormSubmissionService.submit_job_application(
    job_url: str,
    job_source: str,
    resume_text: str,
    cover_letter: str,
    user_email: str,
    user_name: str,
    phone_number: Optional[str] = None,
    github_url: Optional[str] = None,
    linkedin_url: Optional[str] = None
) -> Tuple[bool, str]
```

### Supported Job Sources

#### 1. Indeed
- **Method**: Playwright browser automation
- **Form Fields**:
  - Email (required)
  - Name (if available)
  - Phone (optional)
  - Resume (file upload)
  - Cover Letter (optional field)
- **Submit Button**: "Apply" or "Submit" button
- **Detection**: Uses `button[aria-label*='Apply']` selector

**Example Flow**:
```
1. Click "Apply Now" button
2. Popup appears with form fields
3. Fill email, name, phone
4. Upload resume file
5. Click "Submit Application"
6. Wait for confirmation message
```

#### 2. Naukri
- **Method**: Playwright browser automation
- **Form Fields**:
  - Resume (pre-selected from profile)
  - Cover Letter (textarea)
  - LinkedIn URL (if shown)
- **Submit Button**: "Apply" button
- **Detection**: `button:has-text('Apply')`

**Example Flow**:
```
1. Click "Apply" button
2. Naukri shows resume + cover letter form
3. Fill cover letter
4. Click "Apply" to submit
5. Job saved to Naukri profile
```

#### 3. Glassdoor
- **Method**: Playwright browser automation
- **Form Fields**:
  - Name (required)
  - Email (required)
  - Phone (optional)
  - Resume Upload
  - Cover Letter (optional)
- **Submit Button**: "Apply" button
- **Detection**: `button:has-text('Apply')`

**Example Flow**:
```
1. Click "Apply" button
2. Form popup appears
3. Fill name, email, phone
4. Upload resume file
5. Click "Apply" to submit
6. Redirected to company site or confirmation page
```

#### 4. GitHub Jobs
- **Method**: Email/redirect based
- **Behavior**: GitHub Jobs links to company career pages
- **Fallback**: Extract contact email and return for manual application
- **Selectors**: `a[href*='mailto:']`, `a[href*='apply']`

**Example Flow**:
```
1. Look for "Apply" button or "Email" link
2. If found, click to open email client or apply page
3. If not, search job posting for contact email
4. Return email for manual follow-up
```

## Implementation Details

### Field Filling Strategy

1. **Dynamic Field Detection**
   ```python
   # Find email input
   email_fields = await page.query_selector_all("input[type='email']")
   if email_fields:
       await email_fields[0].fill(email)
   
   # Find name input
   name_fields = await page.query_selector_all("input[type='text']")
   if name_fields:
       await name_fields[0].fill(name)
   ```

2. **File Upload Handling**
   ```python
   file_input = await page.query_selector("input[type='file']")
   if file_input:
       # Save resume to temp file
       import tempfile
       with tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as f:
           f.write(resume_text)
           await file_input.set_input_files(f.name)
   ```

3. **Button Clicking**
   ```python
   submit_btn = await page.query_selector(
       "button:has-text('Submit')"
   ) or await page.query_selector(
       "button:has-text('Apply')"
   )
   if submit_btn:
       await submit_btn.click()
       await page.wait_for_timeout(2000)
   ```

### Error Handling

**Common Issues & Solutions**:

| Issue | Detection | Handling |
|-------|-----------|----------|
| CAPTCHA Present | DOM contains reCAPTCHA/hCaptcha elements | Return error, flag for manual review |
| Form Not Found | No buttons/inputs found | Return "form not found" error |
| Timeout | Navigation takes > 15 seconds | Skip job with timeout error |
| File Not Uploaded | File input present but upload fails | Skip resume upload, try form submit anyway |
| Button Not Found | No submit button detected | Log error, return failure |

### CAPTCHA Detection & Handling

```python
@staticmethod
async def check_captcha_present(page: Page) -> bool:
    """Check if CAPTCHA is present on page"""
    # Check for reCAPTCHA
    recaptcha = await page.query_selector("div[class*='recaptcha']")
    if recaptcha:
        return True
    
    # Check for hCaptcha
    hcaptcha = await page.query_selector("div[class*='h-captcha']")
    if hcaptcha:
        return True
    
    return False

@staticmethod
async def wait_for_human_captcha(
    page: Page, 
    timeout_seconds: int = 300
) -> bool:
    """Wait for human to solve CAPTCHA (5 minutes max)"""
    start_time = datetime.now()
    
    while (datetime.now() - start_time).total_seconds() < timeout_seconds:
        captcha_present = await FormSubmissionService.check_captcha_present(page)
        if not captcha_present:
            return True
        await asyncio.sleep(2)
    
    return False
```

## Integration with Auto-Apply Orchestrator

The FormSubmissionService is called from `AutoApplyOrchestrator._submit_application()`:

```python
# In auto_apply.py orchestrator
success, submit_msg = await FormSubmissionService.submit_job_application(
    job_url=job.apply_link,
    job_source=job.source,
    resume_text=resume,
    cover_letter=cover_letter,
    user_email=preferences.email,
    user_name=preferences.name,
    phone_number=preferences.phone,
    github_url=preferences.github_username,
    linkedin_url=preferences.linkedin_url
)

# Save application with submission status
app_data = {
    "status": "applied" if success else "failed",
    "submission_status": submit_msg,
    "submitted_at": datetime.now()
}
```

## Data Flow

```
Auto-Apply Trigger
    ↓
Job Matching & Quality Scoring
    ↓
Resume Customization
    ↓
Cover Letter Generation (Groq AI)
    ↓
FormSubmissionService.submit_job_application()
    ├─ Launch Playwright browser
    ├─ Navigate to job_url
    ├─ Detect job_source platform
    ├─ Fill form fields:
    │  ├─ Email
    │  ├─ Name
    │  ├─ Phone
    │  ├─ Resume (file upload)
    │  └─ Cover Letter
    ├─ Click submit button
    ├─ Check for CAPTCHA
    ├─ Wait for confirmation
    └─ Return (success, message)
    ↓
Save to auto_apply_runs collection
    ├─ status: "applied" or "failed"
    ├─ submission_status: "Successfully submitted to Indeed", etc.
    ├─ submitted_at: timestamp
    └─ error_message: if failed
```

## Performance Metrics

| Source | Avg Time | Timeout | Notes |
|--------|----------|---------|-------|
| Indeed | 8-12s | 15s | Rapid JavaScript rendering |
| Naukri | 5-8s | 15s | Moderate JS rendering |
| Glassdoor | 10-15s | 15s | Slower page load |
| GitHub Jobs | 2-4s | 10s | Mostly static/redirect |

**Total per Application**: 8-15 seconds (sequential)
**With Parallel Processing**: Could theoretically parallelize but not recommended due to rate limiting

## Configuration

### Environment Variables

```bash
# Playwright settings
PLAYWRIGHT_HEADLESS=true  # Always headless for background jobs
PLAYWRIGHT_TIMEOUT=15000  # 15 second timeout per page load
PLAYWRIGHT_SLOWMO=0       # No slow-motion (would delay submissions)

# Form submission settings
FORM_SUBMISSION_MAX_RETRIES=2
FORM_SUBMISSION_TIMEOUT=15
FORM_SUBMISSION_CAPTCHA_TIMEOUT=300  # 5 minutes for CAPTCHA
```

### Database Schema

**applications** Collection:
```javascript
{
    user_id: ObjectId,
    job_id: String,          // Reference to job
    resume: String,          // Customized resume content
    cover_letter: String,    // Generated cover letter
    status: String,          // "applied", "failed", "manual_review"
    submission_status: String,  // "Successfully submitted to Indeed", error message
    submitted_at: Date,      // When application was submitted
    created_at: Date         // When record was created
}
```

## Best Practices

### 1. Rate Limiting
- **Respect Site Terms of Service**: Don't submit >5 applications per minute to same site
- **Add Delays**: Include 2-4 second delays between submissions to different sites
- **User-Agent Rotation**: Vary user-agent headers to avoid detection
- **IP Rotation**: Optional - Use proxies for high-volume submissions

### 2. Resume/Cover Letter Quality
- Always provide complete resume text
- Ensure cover letter is customized per job (not generic)
- Validate fields before submission
- Include GitHub profile URL if relevant

### 3. Error Handling
- Log all failures with job_id, source, error message
- Distinguish between temporary (network, timeout) and permanent (form structure changed) errors
- Retry temporary failures up to 2 times
- Flag permanent failures for manual review

### 4. User Communication
- Show submission success/failure in dashboard
- Provide detailed error messages for failed submissions
- Warn if CAPTCHA detected
- Track application history for user reference

## Testing

### Unit Tests
```python
# Test form detection for each platform
async def test_indeed_form_submission():
    success, msg = await FormSubmissionService.submit_job_application(
        job_url="https://indeed.com/viewjob?jk=test123",
        job_source="indeed",
        resume_text="...",
        cover_letter="...",
        user_email="test@example.com",
        user_name="John Doe"
    )
    assert success or "form not found" in msg.lower()

# Test CAPTCHA detection
async def test_captcha_detection():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com/captcha")
        result = await FormSubmissionService.check_captcha_present(page)
        assert result == True  # CAPTCHA present
```

### Integration Tests
```python
# Test full submission flow
async def test_auto_apply_form_submission():
    # Create user, preferences
    # Trigger auto-apply
    # Verify applications saved with correct status
    # Check database for submission_status field
```

### Manual Testing
1. Create test job listings with actual forms
2. Submit manually to verify form fields are filled correctly
3. Check Indeed, Naukri, Glassdoor with test account
4. Verify resume and cover letter appear in submission
5. Test CAPTCHA detection and timeout behavior

## Troubleshooting

### Issue: "Apply button not found"
**Cause**: HTML structure changed or button uses different selectors
**Solution**: 
1. Check job site's current HTML using Chrome DevTools
2. Add alternative selector to code
3. Submit PR with new selector logic

### Issue: CAPTCHA blocks submission
**Cause**: Playwright detected as bot
**Solution**:
1. Add stealth mode options
2. Increase delays between actions
3. Rotate user-agents
4. Consider proxy rotation

### Issue: Resume file not uploading
**Cause**: File input not found or permission issue
**Solution**:
1. Check file input selector
2. Ensure temp file has read permissions
3. Try uploading to different field
4. Log error and continue with form-only submission

### Issue: Form data not saved to job site
**Cause**: Hidden fields or AJAX validation
**Solution**:
1. Add more waits for AJAX to complete
2. Check for validation errors on page
3. Look for hidden/required fields not visible
4. Debug with page screenshots before/after submit

## Future Enhancements

1. **Intelligent Form Parsing**: Use ML to map resume fields to unknown form structures
2. **Proxy Rotation**: Implement rotating proxy service for high-volume submissions
3. **Browser Fingerprinting**: Randomize browser profile to avoid detection
4. **OCR for CAPTCHAs**: Add CAPTCHA solving (3rd party service)
5. **Session Management**: Maintain authenticated sessions across submissions
6. **Video Evidence**: Screenshot/record successful submissions for audit trail
7. **A/B Testing**: Test different resume/cover letter variants

## References

- [Playwright Documentation](https://playwright.dev/)
- [Indeed Application Form HTML](https://indeed.com/jobs)
- [Naukri Application Flow](https://www.naukri.com/jobs)
- [Glassdoor Careers](https://www.glassdoor.com/jobs)
