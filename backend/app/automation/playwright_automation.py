from playwright.async_api import async_playwright, Page, Browser
import asyncio
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class PlaywrightAutomation:
    """Handles automated form filling for job applications"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def launch_browser(self, headless: bool = True) -> Browser:
        """Launch browser instance"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=headless)
        return self.browser

    async def close_browser(self):
        """Close browser instance"""
        if self.browser:
            await self.browser.close()

    async def open_job_page(self, url: str) -> Page:
        """Open job application page"""
        if not self.browser:
            await self.launch_browser()
        
        self.page = await self.browser.new_page()
        
        # Add delay to avoid bot detection
        await self.page.goto(url, wait_until="networkidle")
        await asyncio.sleep(2)
        
        return self.page

    async def detect_form_fields(self) -> dict:
        """Detect input fields on the page"""
        if not self.page:
            raise Exception("No page opened")
        
        field_info = await self.page.evaluate("""
            () => {
                const fields = {};
                
                // Detect text inputs
                document.querySelectorAll('input[type="text"], textarea').forEach(el => {
                    const label = el.previousElementSibling?.textContent || 
                                 el.parentElement?.querySelector('label')?.textContent ||
                                 el.getAttribute('placeholder') ||
                                 el.getAttribute('name') || 
                                 el.id;
                    
                    if (label) {
                        fields[label] = {
                            type: 'text',
                            selector: '#' + el.id || '.' + el.className,
                            placeholder: el.getAttribute('placeholder')
                        };
                    }
                });
                
                // Detect file inputs
                document.querySelectorAll('input[type="file"]').forEach(el => {
                    fields['resume_upload'] = {
                        type: 'file',
                        selector: '#' + el.id || '.' + el.className
                    };
                });
                
                // Detect select dropdowns
                document.querySelectorAll('select').forEach(el => {
                    fields[el.name || el.id] = {
                        type: 'select',
                        selector: '#' + el.id || '.' + el.className
                    };
                });
                
                return fields;
            }
        """)
        
        return field_info

    async def fill_text_field(self, field_selector: str, text: str, typing_delay: int = 50):
        """Fill text field with typing simulation to avoid bot detection"""
        if not self.page:
            raise Exception("No page opened")
        
        # Focus on element
        await self.page.focus(field_selector)
        await asyncio.sleep(0.5)
        
        # Type with delay between characters
        for char in text:
            await self.page.keyboard.press(char)
            await asyncio.sleep(typing_delay / 1000)

    async def upload_resume(self, file_path: str, input_selector: str) -> bool:
        """Upload resume file"""
        if not self.page:
            raise Exception("No page opened")
        
        try:
            file_input = await self.page.query_selector(input_selector)
            if file_input:
                await file_input.set_input_files(file_path)
                await asyncio.sleep(1)
                return True
            return False
        except Exception as e:
            logger.error(f"Error uploading resume: {e}")
            return False

    async def click_element(self, selector: str):
        """Click an element"""
        if not self.page:
            raise Exception("No page opened")
        
        await self.page.click(selector)
        await asyncio.sleep(1)

    async def fill_form(self, form_data: dict) -> bool:
        """Fill entire form with provided data"""
        if not self.page:
            raise Exception("No page opened")
        
        try:
            # Detect form fields first
            form_fields = await self.detect_form_fields()
            
            # Fill text fields
            for field_name, field_value in form_data.items():
                if field_name == "resume_path":
                    # Handle resume upload
                    if "resume_upload" in form_fields:
                        await self.upload_resume(
                            field_value,
                            form_fields["resume_upload"]["selector"]
                        )
                elif field_name in form_fields:
                    field_info = form_fields[field_name]
                    if field_info["type"] == "text":
                        await self.fill_text_field(field_info["selector"], field_value)
                        await asyncio.sleep(1)
            
            return True
        except Exception as e:
            logger.error(f"Error filling form: {e}")
            return False

    async def get_page_content(self) -> str:
        """Get current page content"""
        if not self.page:
            raise Exception("No page opened")
        
        return await self.page.content()

    async def wait_for_element(self, selector: str, timeout: int = 5000) -> bool:
        """Wait for element to appear"""
        if not self.page:
            raise Exception("No page opened")
        
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False

    async def pause_for_review(self, timeout_minutes: int = 5):
        """Pause and wait for user approval before submission"""
        logger.info(f"Pausing for {timeout_minutes} minutes for user approval...")
        
        # Wait for user to approve via Telegram or API
        # In real implementation, this would check a messaging queue
        await asyncio.sleep(timeout_minutes * 60)

    async def submit_form(self, submit_button_selector: str) -> bool:
        """Submit the form"""
        if not self.page:
            raise Exception("No page opened")
        
        try:
            await self.click_element(submit_button_selector)
            await asyncio.sleep(2)
            
            # Wait for page to load after submission
            await self.page.wait_for_load_state("networkidle")
            
            return True
        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            return False

    async def save_session_state(self) -> dict:
        """Save current session state"""
        if not self.page:
            raise Exception("No page opened")
        
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "filled_at": str(asyncio.get_event_loop().time())
        }

    async def close_page(self):
        """Close current page"""
        if self.page:
            await self.page.close()


# Helper function for automation task
async def automate_job_application(
    job_url: str,
    resume_path: str,
    cover_letter: str,
    form_config: dict
) -> Tuple[bool, str]:
    """
    Automate job application with given data
    
    Args:
        job_url: URL of job application page
        resume_path: Path to resume file
        cover_letter: Cover letter text
        form_config: Configuration of form fields to fill
    
    Returns:
        (success, message)
    """
    automation = PlaywrightAutomation()
    
    try:
        # Launch browser
        await automation.launch_browser(headless=True)
        
        # Open job page
        await automation.open_job_page(job_url)
        
        # Detect and fill form
        form_data = {
            **form_config,
            "resume_path": resume_path,
            "cover_letter": cover_letter
        }
        
        success = await automation.fill_form(form_data)
        if not success:
            raise Exception("Failed to fill form")
        
        # Pause for user review
        # In production, this would be asynchronous
        logger.info("Application filled. Waiting for user approval...")
        
        return True, "Application successfully prepared"
    
    except Exception as e:
        logger.error(f"Automation error: {e}")
        return False, str(e)
    
    finally:
        await automation.close_page()
        await automation.close_browser()
