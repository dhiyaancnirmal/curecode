from crewai import Crew, Task, Process
from agents import CureCodeAgents

class CureCodeCrew():
    def __init__(self, url):
        self.url = url

    # Replace the kickoff method in crew.py with this updated version

    def kickoff(self):
        agents = CureCodeAgents()
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
                f"For EACH form identified in the previous task, perform security tests. "
                f"1. Test for SQL injection using the Submit Form Tool with a payload like `{{\"username\": \"' OR 1=1 --\"}}`. "
                f"2. Test for XSS in text fields using the Test for XSS Tool. "
                f"3. Check for security misconfigurations on all discovered URLs. "
                f"CRITICAL: YOU MUST ONLY REPORT ON VULNERABILITIES THAT YOU HAVE PERSONALLY CONFIRMED WITH A TOOL. "
                f"Do not guess or infer other vulnerabilities. For each confirmed finding, report the type, location, payload, and evidence. "
                f"DO NOT provide any solutions, fixes, or code examples. DO NOT provide a 'Final Answer' section. "
                f"When you finish testing, simply stop without providing any final summary."
            ),
            expected_output="A concise report listing ONLY the vulnerabilities that were successfully confirmed with a tool, including evidence for each. NO solutions or code examples.",
            agent=tester,
            context=[recon_task, crawl_task]
        )

        

        fix_task = Task(
            description=(
                "Based only on the confirmed vulnerabilities reported by the previous task, provide a concise list of code fixes. For each fix, you must first state the vulnerability type and location exactly as it was reported, and then provide an actionable code snippet for the fix. Do NOT provide fixes for any vulnerabilities that were not explicitly confirmed in the previous report. "
                "For each confirmed vulnerability, provide an actionable code snippet showing the fix. "
                "Do NOT repeat the analysis or description of the vulnerability itself. Focus only on the solution."
            ),
            expected_output="A list of suggested code fixes with code snippets in the appropriate language for each vulnerability.",
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