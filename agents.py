import os
from crewai import Agent
from langchain_openai import ChatOpenAI
from tools.browser_tools import FindFormsTool, GetFormFieldsTool, SubmitFormTool, CrawlWebsiteTool

class AutopatchAgents():
    def __init__(self):
        # --- MODIFICATION START: Instantiate all the new tools ---
        self.find_forms_tool = FindFormsTool()
        self.get_form_fields_tool = GetFormFieldsTool()
        self.submit_form_tool = SubmitFormTool()
        # --- MODIFICATION END ---
        self.llm = ChatOpenAI(
            model="x-ai/grok-4-fast:free",
            api_key=os.environ.get("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "Autopatch"
            }
        )

    def crawler_agent(self):
        return Agent(
            role='Website Crawler',
            goal=f'Crawl the provided website to discover all accessible internal URLs.',
            backstory=(
                'You are a meticulous web spider. Your mission is to navigate a website and compile a '
                'comprehensive list of every unique internal page, creating a site map for the security team.'
            ),
            tools=[CrawlWebsiteTool()], # Give it the new tool
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def scout_agent(self):
        return Agent(
            role='Website Reconnaissance Specialist',
            goal='Scan the provided URL to identify all web forms present on the page.',
            backstory='You are an expert web crawler. Your job is to find all the forms on a page so the tester can analyze them.',
            # --- MODIFICATION START: Give the scout only the tool it needs ---
            tools=[self.find_forms_tool],
            # --- MODIFICATION END ---
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def tester_agent(self):
        return Agent(
            role='Vulnerability Tester',
            goal='Test identified forms for SQL injection vulnerabilities.',
            backstory=(
                'You are a penetration tester. Use the Get Form Fields Tool to see what inputs a form has. '
                'Then, use the Submit Form Tool to send SQL injection payloads (e.g., {"username": "\' OR 1=1 --", "password": "password"}) '
                'and analyze the result. If the submission is successful or the page changes unexpectedly, it could be vulnerable.'
            ),
            # --- MODIFICATION START: Give the tester only the tools it needs ---
            tools=[self.get_form_fields_tool, self.submit_form_tool],
            # --- MODIFICATION END ---
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def fixer_agent(self):
        return Agent(
            role='Vulnerability Fixer',
            goal='Analyze vulnerabilities and suggest code fixes.',
            backstory='You are a security engineer. Suggest patches for vulns found by the tester (e.g., parameterized queries for SQLi). Provide code snippets in Python.',
            tools=[], # The fixer doesn't need browser tools
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )