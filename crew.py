from crewai import Crew, Task, Process
from agents import AutopatchAgents

class AutopatchCrew():
    def __init__(self, url):
        self.url = url

    # Replace the kickoff method in crew.py with this updated version

    def kickoff(self):
        agents = AutopatchAgents()
        # --- MODIFICATION START: Add the new crawler agent ---
        crawler = agents.crawler_agent()
        scout = agents.scout_agent()
        tester = agents.tester_agent()
        fixer = agents.fixer_agent()

        # --- MODIFICATION START: Add a new task for the crawler ---
        crawl_task = Task(
            description=f"Use the Crawl Website Tool to find all internal URLs starting from {self.url}.",
            expected_output="A Python list of all unique, internal URLs found on the website.",
            agent=crawler,
        )

        # --- MODIFICATION START: Update recon and test tasks to use the crawler's output ---
        recon_task = Task(
            description=f"For EACH URL in the provided list, use the Find Forms Tool to identify all forms on the page.",
            expected_output="A detailed report listing all URLs that contain forms, along with the HTML for each form.",
            agent=scout,
            context=[crawl_task] # This task now depends on the crawl_task
        )

        test_task = Task(
            description=(
                f"For EACH form identified in the previous task, perform comprehensive security tests. "
                f"1. Test for SQL injection using the Submit Form Tool with a payload like `{{\"username\": \"' OR 1=1 --\"}}`. "
                f"2. Test for XSS in text fields using the Test for XSS Tool. "
                f"3. If login forms are found, test for IDOR vulnerabilities using the IDOR Test Tool with different user accounts. "
                f"4. Check for security misconfigurations using the Security Configuration Checker on all discovered URLs. "
                f"Compile a single report detailing the results of ALL tests including any IDOR or configuration issues found."
            ),
            expected_output="A comprehensive report listing every form tested, the payloads used for SQLi and XSS, IDOR test results, security configuration findings, and a conclusion on all vulnerabilities found.",
            agent=tester,
            context=[recon_task]
        )

        

        fix_task = Task(
            description=(
                "Based on the vulnerability report from the previous task, provide a concise list of code fixes. "
                "For each confirmed vulnerability, provide an actionable code snippet showing the fix. "
                "Do NOT repeat the analysis or description of the vulnerability itself. Focus only on the solution."
            ),
            expected_output="A list of suggested code fixes with Python code snippets for each vulnerability.",
            agent=fixer,
            context=[test_task]
        )

        crew = Crew(
            # --- MODIFICATION START: Add the crawler to the crew ---
            agents=[crawler, scout, tester, fixer],
            tasks=[crawl_task, recon_task, test_task, fix_task],
            process=Process.sequential,
            verbose=2
        )

        result = crew.kickoff()
        return result