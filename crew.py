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
                f"For EACH form identified in the previous task, perform a security test for SQL injection. "
                f"First, use the Get Form Fields Tool to understand the inputs. "
                f"Then, use the Submit Form Tool with a malicious payload like `{{\"username\": \"' OR 1=1 --\", \"password\": \"test\"}}`. "
                f"Analyze the results from all tests."
            ),
            expected_output="A comprehensive report listing every form tested across the site, the payloads used, and a conclusion on whether vulnerabilities were found.",
            agent=tester,
            context=[recon_task]
        )
        # --- MODIFICATION END ---

        fix_task = Task(
            description=f"Analyze the final vulnerability report. For each confirmed vulnerability, provide a code fix.",
            expected_output="A list of suggested code fixes or best practices based on the testing results.",
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