# File: agents.py
import os
from crewai import Agent
from langchain_openai import ChatOpenAI
from tools.browser_tools import BrowserInteractionTool

# --- MODIFICATION START ---
# We are moving the tool and llm initialization inside the class
# to make them proper attributes.

class AutopatchAgents():
    def __init__(self):
        self.browser_tool = BrowserInteractionTool()
        self.llm = ChatOpenAI(
            model="x-ai/grok-4-fast:free",
            api_key=os.environ.get("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "Autopatch"
            }
        )

    def scout_agent(self):
        return Agent(
            role='Website Reconnaissance Specialist',
            goal='Scan the provided URL to identify all web forms present on the page.',
            backstory=(
                'As a seasoned web crawler expert, your primary objective is to meticulously map out '
                'the structure of a target website. You specialize in identifying interactive elements, '
                'especially forms, which are critical entry points for security testing.'
            ),
            tools=[self.browser_tool],  # Use self.browser_tool
            llm=self.llm,              # Use self.llm
            verbose=True,
            allow_delegation=False
        )
# --- MODIFICATION END ---