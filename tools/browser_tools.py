from crewai_tools import BaseTool
from playwright.sync_api import sync_playwright
from typing import Type, List, Dict
from pydantic.v1 import BaseModel, Field
from urllib.parse import urlparse, urljoin
import re
from collections import defaultdict

# Global headless mode control
HEADLESS_MODE = True

def toggle_headless_mode():
    """Toggle the global headless mode setting"""
    global HEADLESS_MODE
    HEADLESS_MODE = not HEADLESS_MODE
    return HEADLESS_MODE

def get_headless_mode():
    """Get the current headless mode setting"""
    return HEADLESS_MODE

# --- A shared Playwright setup function to avoid repetitive code ---
def run_playwright(url: str, task_function):
    try:
        with sync_playwright() as p:
            # Use global headless mode setting
            browser = p.chromium.launch(headless=HEADLESS_MODE, slow_mo=100)
            page = browser.new_page()
            # Pass the page object to the task function
            result = task_function(page, url)
            browser.close()
            return result
    except Exception as e:
        return f"An error occurred during browser interaction: {e}"

# --- Tool 1: Smart Crawl Website Tool ---
class CrawlWebsiteTool(BaseTool):
    name: str = "Crawl Website Tool"
    description: str = "Intelligently crawls a given URL to find all internal links, avoiding repetitive database-generated content."

    def _run(self, url: str, max_pages: int = 100) -> List[str]:
        def task(page, start_url):
            print(f"[Crawler] Starting smart crawl of: {start_url}")
            queue = [start_url]
            visited = set([start_url])
            base_domain = urlparse(start_url).netloc
            
            # Pattern tracking for smart crawling
            url_patterns = defaultdict(int)  # Track how many URLs match each pattern
            pattern_limits = defaultdict(int)  # Track how many we've crawled per pattern
            max_per_pattern = 5  # Maximum URLs to crawl per detected pattern
            
            # Common database-generated URL patterns to limit
            db_patterns = [
                r'/tag/[^/]+/?$',           # /tag/tagname
                r'/category/[^/]+/?$',      # /category/categoryname
                r'/post/[^/]+/?$',          # /post/postname
                r'/article/[^/]+/?$',       # /article/articlename
                r'/page/\d+/?$',            # /page/123
                r'/\d{4}/\d{2}/[^/]+/?$',  # /2024/01/postname (date-based)
                r'/user/[^/]+/?$',          # /user/username
                r'/author/[^/]+/?$',        # /author/authorname
                r'/\?page=\d+',             # ?page=123
                r'/\?tag=[^&]+',            # ?tag=tagname
                r'/\?category=[^&]+',       # ?category=categoryname
                r'/quote/[^/]+/?$',         # /quote/quotename (for quote sites)
                r'/quotes/[^/]+/?$',        # /quotes/quotename
                r'/topic/[^/]+/?$',         # /topic/topicname
                r'/archive/[^/]+/?$',       # /archive/archivename
                r'/search\?[^&]*q=[^&]+',   # /search?q=query
            ]
            
            # Dynamic pattern detection - learn from the site structure
            dynamic_patterns = defaultdict(int)
            max_dynamic_patterns = 3  # Max URLs per dynamically detected pattern
            
            def is_database_generated_url(url_path):
                """Check if URL matches database-generated patterns"""
                for pattern in db_patterns:
                    if re.search(pattern, url_path):
                        return pattern
                return None
            
            def detect_dynamic_pattern(url_path):
                """Detect dynamic patterns by analyzing URL structure"""
                # Look for patterns like /something/123, /something/name, etc.
                # where the last segment varies but the structure is consistent
                parts = url_path.strip('/').split('/')
                if len(parts) >= 2:
                    # Create a pattern by replacing the last part with a placeholder
                    pattern_parts = parts[:-1] + ['[DYNAMIC]']
                    dynamic_pattern = '/' + '/'.join(pattern_parts) + '/?$'
                    return dynamic_pattern
                return None
            
            def should_skip_url(url_path, pattern):
                """Determine if we should skip this URL based on pattern frequency"""
                if pattern:
                    pattern_limits[pattern] += 1
                    if pattern_limits[pattern] > max_per_pattern:
                        return True
                
                # Check dynamic patterns
                dynamic_pattern = detect_dynamic_pattern(url_path)
                if dynamic_pattern:
                    dynamic_patterns[dynamic_pattern] += 1
                    if dynamic_patterns[dynamic_pattern] > max_dynamic_patterns:
                        return True
                
                return False
            
            while queue and len(visited) < max_pages:
                current_url = queue.pop(0)
                print(f"[Crawler] Visiting: {current_url}")
                
                try:
                    page.goto(current_url, wait_until="domcontentloaded", timeout=10000)
                    page.set_default_timeout(10000)
                    
                    a_tags = page.query_selector_all("a")
                    new_links_found = 0
                    
                    for tag in a_tags:
                        href = tag.get_attribute("href")
                        if href:
                            absolute_url = urljoin(current_url, href)
                            parsed_url = urlparse(absolute_url)
                            
                            # Only process internal links we haven't visited
                            if parsed_url.netloc == base_domain and absolute_url not in visited:
                                url_path = parsed_url.path
                                
                                # Check if this is a database-generated URL
                                db_pattern = is_database_generated_url(url_path)
                                
                                # Skip if we've already crawled too many of this pattern
                                if should_skip_url(url_path, db_pattern):
                                    if db_pattern:
                                        print(f"[Crawler] Skipping {absolute_url} (pattern limit reached: {db_pattern})")
                                    continue
                                
                                # Track the pattern
                                if db_pattern:
                                    url_patterns[db_pattern] += 1
                                    print(f"[Crawler] Found database URL pattern: {db_pattern} (count: {url_patterns[db_pattern]})")
                                
                                visited.add(absolute_url)
                                queue.append(absolute_url)
                                new_links_found += 1
                    
                    if new_links_found > 0:
                        print(f"[Crawler] Found {new_links_found} new links on {current_url}")
                    
                except Exception as e:
                    print(f"[Crawler] Error visiting {current_url}: {e}")
            
            # Print pattern summary
            if url_patterns:
                print(f"[Crawler] Database URL patterns detected:")
                for pattern, count in url_patterns.items():
                    print(f"[Crawler] - {pattern}: {count} URLs")
            
            if dynamic_patterns:
                print(f"[Crawler] Dynamic URL patterns detected:")
                for pattern, count in dynamic_patterns.items():
                    print(f"[Crawler] - {pattern}: {count} URLs")
            
            print(f"[Crawler] Crawl completed. Found {len(visited)} total URLs")
            print(f"[Crawler] URLs discovered:")
            for i, url in enumerate(list(visited), 1):
                print(f"[Crawler] {i}. {url}")
            return list(visited)
            
        return run_playwright(url, task)

# --- Tool 2: Find Forms ---
class FindFormsTool(BaseTool):
    name: str = "Find Forms Tool"
    description: str = "Scans a given URL and returns the HTML of all forms found on the page."

    def _run(self, url: str) -> str:
        def task(page, target_url):
            page.goto(target_url, wait_until="networkidle")
            forms = page.query_selector_all("form")
            if not forms:
                return f"No forms found on {target_url}."
            form_details = [f"Form #{i+1}:\n{form.inner_html() or ''}\n" for i, form in enumerate(forms)]
            return f"Found {len(forms)} forms on {target_url}:\n{''.join(form_details)}"
        
        return run_playwright(url, task)

# --- Tool 3: Get Form Fields ---
class GetFormFieldsTool(BaseTool):
    name: str = "Get Form Fields Tool"
    description: str = "Inspects the first form on a URL and returns its input fields."

    def _run(self, url: str) -> str:
        def task(page, target_url):
            page.goto(target_url, wait_until="networkidle")
            form = page.query_selector("form")
            if not form:
                return f"No form found on {target_url}."
            inputs = form.query_selector_all("input, textarea, select")
            fields = [f"{inp.get_attribute('name') or 'unnamed'} (type: {inp.get_attribute('type') or 'text'})" for inp in inputs]
            return f"Form fields: {', '.join(fields)}"
        
        return run_playwright(url, task)

# --- Tool 4: Submit Form ---
class SubmitFormInput(BaseModel):
    url: str = Field(description="The URL with the form to submit.")
    payload: Dict[str, str] = Field(description="Dictionary of field 'name' and value to fill.")

class SubmitFormTool(BaseTool):
    name: str = "Submit Form Tool"
    description: str = "Fills out and submits the first form on a URL with the provided data."
    args_schema: Type[BaseModel] = SubmitFormInput

    def _run(self, url: str, payload: Dict[str, str]) -> str:
        def task(page, target_url):
            page.goto(target_url, wait_until="networkidle")
            form = page.query_selector("form")
            if not form:
                return f"No form found on {target_url}."
            
            # --- FIX: Only fill visible fields. Do not try to fill hidden fields. ---
            for field, value in payload.items():
                try:
                    # Check if the element is visible before trying to fill it
                    element = page.locator(f'[name="{field}"]')
                    if element.is_visible():
                        element.fill(value)
                    else:
                        print(f"Skipping hidden field: {field}")
                except Exception as e:
                    print(f"Could not fill field {field}: {e}")
            
            page.click('form [type="submit"]')
            page.wait_for_timeout(2000)
            
            new_url = page.url
            snippet = page.content()[:500]
            return f"Submitted form. New URL: {new_url}\nPage snippet: {snippet}"

        return run_playwright(url, task)

# --- Tool 5: Test for XSS ---
class TestXSS_Tool(BaseTool):
    name: str = "Test for XSS Tool"
    description: str = "Injects an XSS payload into a specific form field and checks if an alert dialog appears."

    def _run(self, url: str, payload_field: str) -> str:
        def task(page, target_url):
            alert_fired = False
            def handle_dialog(dialog):
                nonlocal alert_fired
                alert_fired = True
                print(f"[XSS Tool] Alert dialog detected with message: {dialog.message}")
                dialog.dismiss()

            page.on('dialog', handle_dialog)
            
            page.goto(target_url, wait_until="networkidle")
            form = page.query_selector("form")
            if not form:
                page.remove_listener('dialog', handle_dialog)
                return "No form found to test for XSS."

            xss_payload = "<script>alert('autopatch-xss-test')</script>"
            try:
                # --- FIX: Use page.fill which is more reliable than form.fill ---
                page.fill(f'[name="{payload_field}"]', xss_payload)
                page.click('form [type="submit"]')
                page.wait_for_timeout(2000)
            except Exception as e:
                page.remove_listener('dialog', handle_dialog)
                return f"Error submitting form for XSS test: {e}"
            
            page.remove_listener('dialog', handle_dialog)
            if alert_fired:
                return f"XSS Vulnerability Confirmed! An alert was triggered on {url} in the '{payload_field}' field."
            else:
                return f"No XSS vulnerability detected on {url} in the '{payload_field}' field."
        
        return run_playwright(url, task)

# --- Tool 6: IDOR Testing Tool ---
class IDORTestInput(BaseModel):
    login_url: str = Field(description="The URL where users can log in")
    user_a_credentials: Dict[str, str] = Field(description="Dictionary with username/password for User A")
    user_b_credentials: Dict[str, str] = Field(description="Dictionary with username/password for User B")
    private_url: str = Field(description="The private URL to test (e.g., /orders/123)")
    logout_url: str = Field(description="The URL to log out from")

class IDORTestTool(BaseTool):
    name: str = "IDOR Test Tool"
    description: str = "Tests for Insecure Direct Object References by attempting to access private resources with different user accounts"
    args_schema: Type[BaseModel] = IDORTestInput

    def _run(self, login_url: str, user_a_credentials: Dict[str, str], user_b_credentials: Dict[str, str], private_url: str, logout_url: str) -> str:
        def task(page, base_url):
            results = []
            
            try:
                # Step 1: Login as User A
                print(f"[IDOR Test] Step 1: Logging in as User A ({user_a_credentials.get('username', 'user_a')})")
                page.goto(login_url, wait_until="domcontentloaded", timeout=10000)
                
                # Fill login form
                username_field = page.locator('input[name="username"], input[name="email"], input[type="email"]').first
                password_field = page.locator('input[name="password"], input[type="password"]').first
                
                if username_field.is_visible() and password_field.is_visible():
                    username_field.fill(user_a_credentials.get('username', ''))
                    password_field.fill(user_a_credentials.get('password', ''))
                    page.click('button[type="submit"], input[type="submit"], button:has-text("Login"), button:has-text("Sign In")')
                    page.wait_for_timeout(2000)
                    results.append("✓ Successfully logged in as User A")
                else:
                    return "❌ Could not find login form fields"
                
                # Step 2: Visit private page as User A
                print(f"[IDOR Test] Step 2: Visiting private URL as User A: {private_url}")
                page.goto(private_url, wait_until="domcontentloaded", timeout=10000)
                user_a_content = page.content()[:1000]  # Get first 1000 chars
                results.append(f"✓ User A can access {private_url}")
                
                # Step 3: Logout
                print(f"[IDOR Test] Step 3: Logging out")
                page.goto(logout_url, wait_until="domcontentloaded", timeout=10000)
                page.wait_for_timeout(1000)
                results.append("✓ Successfully logged out")
                
                # Step 4: Login as User B
                print(f"[IDOR Test] Step 4: Logging in as User B ({user_b_credentials.get('username', 'user_b')})")
                page.goto(login_url, wait_until="domcontentloaded", timeout=10000)
                
                username_field = page.locator('input[name="username"], input[name="email"], input[type="email"]').first
                password_field = page.locator('input[name="password"], input[type="password"]').first
                
                if username_field.is_visible() and password_field.is_visible():
                    username_field.fill(user_b_credentials.get('username', ''))
                    password_field.fill(user_b_credentials.get('password', ''))
                    page.click('button[type="submit"], input[type="submit"], button:has-text("Login"), button:has-text("Sign In")')
                    page.wait_for_timeout(2000)
                    results.append("✓ Successfully logged in as User B")
                else:
                    return "❌ Could not find login form fields for User B"
                
                # Step 5: Attempt to access private page as User B
                print(f"[IDOR Test] Step 5: Attempting to access {private_url} as User B")
                page.goto(private_url, wait_until="domcontentloaded", timeout=10000)
                user_b_content = page.content()[:1000]  # Get first 1000 chars
                
                # Check if User B can see the same content as User A
                if user_a_content == user_b_content:
                    results.append("🚨 CRITICAL IDOR VULNERABILITY FOUND!")
                    results.append("User B can access User A's private data")
                    return "\n".join(results)
                else:
                    results.append("✓ No IDOR vulnerability detected")
                    results.append("User B cannot access User A's private data")
                    return "\n".join(results)
                    
            except Exception as e:
                return f"❌ IDOR test failed: {str(e)}"
        
        return run_playwright(login_url, task)

# --- Tool 7: Security Configuration Checker ---
class SecurityConfigTool(BaseTool):
    name: str = "Security Configuration Checker"
    description: str = "Checks HTTP headers for security misconfigurations and revealing information"

    def _run(self, url: str) -> str:
        import requests
        
        try:
            print(f"[Security Config] Checking security headers for: {url}")
            response = requests.get(url, timeout=10, allow_redirects=True)
            headers = response.headers
            
            issues = []
            recommendations = []
            
            # Check for revealing server information
            server_header = headers.get('Server', '').lower()
            if server_header:
                issues.append(f"⚠️ Server header reveals: {headers.get('Server')}")
                recommendations.append("Remove or obfuscate Server header")
            
            # Check for missing security headers
            security_headers = {
                'Content-Security-Policy': 'Prevents XSS attacks',
                'X-Frame-Options': 'Prevents clickjacking',
                'X-Content-Type-Options': 'Prevents MIME sniffing',
                'Strict-Transport-Security': 'Enforces HTTPS',
                'X-XSS-Protection': 'XSS protection (legacy)',
                'Referrer-Policy': 'Controls referrer information'
            }
            
            for header, purpose in security_headers.items():
                if header not in headers:
                    issues.append(f"❌ Missing {header}: {purpose}")
                    recommendations.append(f"Add {header} header")
                else:
                    print(f"[Security Config] ✓ {header} present")
            
            # Check for dangerous headers
            if 'X-Powered-By' in headers:
                issues.append(f"⚠️ X-Powered-By reveals: {headers.get('X-Powered-By')}")
                recommendations.append("Remove X-Powered-By header")
            
            # Check HTTPS enforcement
            if not url.startswith('https://') and 'Strict-Transport-Security' in headers:
                issues.append("⚠️ HSTS header present but site not using HTTPS")
            
            result = f"Security Configuration Analysis for {url}:\n\n"
            
            if issues:
                result += "ISSUES FOUND:\n"
                for issue in issues:
                    result += f"{issue}\n"
            else:
                result += "✓ No major security misconfigurations detected"
            
            return result
            
        except Exception as e:
            return f"❌ Security configuration check failed: {str(e)}"