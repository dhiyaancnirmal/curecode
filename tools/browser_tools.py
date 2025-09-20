from crewai_tools import BaseTool
from playwright.sync_api import sync_playwright
from typing import Type, List, Dict
from pydantic.v1 import BaseModel, Field

# --- A shared Playwright setup function to avoid repetitive code ---
def run_playwright(url: str, task_function):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=500)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            result = task_function(page)
            browser.close()
            return result
    except Exception as e:
        return f"An error occurred during browser interaction: {e}"

# --- Tool 1: Find Forms ---
class FindFormsTool(BaseTool):
    name: str = "Find Forms Tool"
    description: str = "Scans a given URL and returns the HTML of all forms found on the page."

    def _run(self, url: str) -> str:
        def task(page):
            forms = page.query_selector_all("form")
            if not forms:
                return f"No forms found on {url}."
            
            form_details = []
            for i, form in enumerate(forms):
                form_html = form.inner_html() or ""
                form_details.append(f"Form #{i+1}:\n{form_html}\n")
            return f"Found {len(forms)} forms on {url}:\n{''.join(form_details)}"
        
        return run_playwright(url, task)

# --- Tool 2: Get Form Fields ---
class GetFormFieldsTool(BaseTool):
    name: str = "Get Form Fields Tool"
    description: str = "Inspects the first form on a page and returns a list of its input fields (names and types)."

    def _run(self, url: str) -> str:
        def task(page):
            form = page.query_selector("form")
            if not form:
                return f"No form found on {url}."
            
            inputs = form.query_selector_all("input, textarea, select")
            fields = []
            for input_el in inputs:
                name = input_el.get_attribute("name") or "unnamed"
                field_type = input_el.get_attribute("type") or "text"
                fields.append(f"{name} (type: {field_type})")
            return f"Form fields: {', '.join(fields)}"

        return run_playwright(url, task)

# --- Tool 3: Submit Form ---
class SubmitFormInput(BaseModel):
    url: str = Field(description="The URL of the page with the form to submit.")
    payload: Dict[str, str] = Field(description="A dictionary where keys are the input field 'name' attributes and values are the data to fill in.")

class SubmitFormTool(BaseTool):
    name: str = "Submit Form Tool"
    description: str = "Fills out and submits the first form on a given URL with the provided data."
    args_schema: Type[BaseModel] = SubmitFormInput

    def _run(self, url: str, payload: Dict[str, str]) -> str:
        def task(page):
            form = page.query_selector("form")
            if not form:
                return f"No form found on {url}."
            
            for field, value in payload.items():
                try:
                    page.fill(f'[name="{field}"]', value)
                except Exception as e:
                    print(f"Could not fill field {field}: {e}")
            
            page.click('form [type="submit"]')
            page.wait_for_timeout(2000) # Wait for page to potentially reload
            
            new_url = page.url
            snippet = page.content()[:500]
            return f"Submitted form. New URL: {new_url}\nPage snippet: {snippet}"

        return run_playwright(url, task)