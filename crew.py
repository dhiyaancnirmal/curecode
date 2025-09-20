# File: crew.py
from crewai import Crew, Task, Process
from agents import AutopatchAgents

class AutopatchCrew():
    def __init__(self, url):
        self.url = url

    def kickoff(self):
        agents = AutopatchAgents()
        scout = agents.scout_agent()

        # Define the task for the scout agent
        recon_task = Task(
            description=f"Access the website at {self.url} and identify all the forms available on that single page. Your final answer must be a list of all the forms you found.",
            expected_output="A comprehensive list detailing the HTML of each form found on the page.",
            agent=scout,
            # The 'tools' parameter is removed from here because the agent already has its tools defined.
        )

        crew = Crew(
            agents=[scout],
            tasks=[recon_task],
            process=Process.sequential,
            verbose=2
        )

        result = crew.kickoff()
        return result