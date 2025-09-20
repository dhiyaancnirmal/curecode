# File: tools/browser_tools.py
from crewai_tools import BaseTool
from playwright.sync_api import sync_playwright  # <-- This line is corrected
from typing import Optional

class BrowserInteractionTool(BaseTool):
    name: str = "Browser Interaction Tool"
    description: str = (
        "Provides capabilities to interact with a web browser to perform actions like finding all forms on a page. "
        "Requires a URL and an action to be performed."
    )

    def _run(self, url: str, action: str, payload: Optional[dict] = None) -> str:
        if not url or not action:
            return "Error: 'url' and 'action' must be provided."

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=500)
            page = browser.new_page()
            
            try:
                page.goto(url, wait_until='networkidle')

                if action == 'find_forms':
                    forms = page.query_selector_all('form')
                    if not forms:
                        browser.close()
                        return f"No forms were found on {url}."
                    
                    form_details = []
                    for i, form in enumerate(forms):
                        form_html = form.inner_html()
                        form_details.append(f"Form #{i+1}:\n{form_html}\n")
                    browser.close()
                    return f"Found {len(forms)} forms on {url}:\n{''.join(form_details)}"
                
                else:
                    browser.close()
                    return f"Action '{action}' is not supported."
            except Exception as e:
                browser.close()
                return f"An error occurred: {e}"