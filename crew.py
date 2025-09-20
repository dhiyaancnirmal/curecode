from crewai import Crew, Task, Process
from agents import AutopatchAgents

class AutopatchCrew():
    def __init__(self, url):
        self.url = url

    def kickoff(self):
        agents = AutopatchAgents()
        scout = agents.scout_agent()
        tester = agents.tester_agent()
        fixer = agents.fixer_agent()

        # --- MODIFICATION START: Updated task descriptions for new tools ---
        recon_task = Task(
            description=f"Use the Find Forms Tool to scan the website at {self.url} and identify all forms on the page.",
            expected_output="A list of strings, each containing the HTML of a form found on the page.",
            agent=scout,
        )

        test_task = Task(
            description=(
                f"For the website at {self.url}, use the forms found in the previous task to test for SQL injection. "
                f"First, use the Get Form Fields Tool to understand the inputs. "
                f"Then, use the Submit Form Tool with a malicious payload like `{{\"username\": \"' OR 1=1 --\", \"password\": \"test\"}}`. "
                f"Analyze the result from the tool. If the login succeeds or the page changes significantly, it's a vulnerability."
            ),
            expected_output="A report listing the form tested, the payload used, and a conclusion on whether a vulnerability was found, with evidence.",
            agent=tester,
            context=[recon_task]
        )

        fix_task = Task(
            description=f"Analyze the vulnerability report from the previous task. For each confirmed vulnerability, provide a code fix. "
                        f"For SQL injection, suggest using parameterized queries and provide a Python `sqlite3` example.",
            expected_output="A list of suggested code fixes or best practices based on the testing results.",
            agent=fixer,
            context=[test_task]
        )
        # --- MODIFICATION END ---

        # --- MODIFICATION START: Correctly define the crew once with all agents and tasks ---
        crew = Crew(
            agents=[scout, tester, fixer],
            tasks=[recon_task, test_task, fix_task],
            process=Process.sequential,
            verbose=2
        )
        # --- MODIFICATION END ---

        result = crew.kickoff()
        return result