[![YouTube](https://github.com/user-attachments/assets/5b3ad836-0c0c-4b09-9b43-8d9a41b0bcba)](https://vimeo.com/1120598811?share=copy&fl=sv&fe=ci)

Watch a demo here ^

# CudeCode is An autonomous AI agent security crew that scans and identifies web vulnerabilities and provides actionable code fixes. 


Inspiration

For this hackathon, I wanted to build something that truly demonstrated the power of AI agents. I kept thinking about how agents could excel at complex, repetitive tasks that require a high degree of autonomy and reasoning—things that are too tricky for simple scripts or traditional automation. This made me look at cybersecurity, specifically the tedious and time-consuming process of penetration testing. It clicked: this was the perfect use case.
What it does

CureCode is a multi-agent system I designed to automatically perform the initial phases of a security assessment. It intelligently navigates a web application, identifies potential attack points like web forms, and autonomously tests them for common security vulnerabilities. The final output is a detailed report of confirmed vulnerabilities along with suggested code fixes.
How I built it

I created a crew of specialized agents, each with a specific role:

    A Crawler Agent maps the entire application, intelligently handling dynamic content and avoiding redundant pages.
    A Reconnaissance Specialist pinpoints and analyzes all web forms, which are prime targets for attacks.
    A Vulnerability Tester uses custom tools to test for SQL Injection, XSS, and security misconfigurations, gathering concrete evidence of successful exploits.
    A Vulnerability Fixer provides actionable code snippets to remediate the reported issues.

The entire system is built on a Python-based Flask web server and powered by CrewAI.
Challenges I ran into

Building a robust agent-based system presented significant challenges, particularly with dependency management among the numerous packages. The biggest hurdle was preventing the final agent from hallucinating, which would cause it to generate irrelevant fixes—such as writing Python code for a PHP application. I've begun to address this by refining the agent's prompts and improving the handover of contextual information.
Accomplishments I'm proud of

I'm proud to have built a functional proof of concept that demonstrates the power of autonomous agents in a complex domain. The tool's ability to not only identify but also provide evidence for vulnerabilities autonomously is a major step toward making security analysis more accessible and efficient.
What I learned

I learned that while agents are incredibly powerful, they require careful prompting and a structured flow to prevent logical errors like hallucination. Ensuring that agents are given the correct context, such as the application's technology stack, is vital for generating accurate and useful outputs.
What's next for CureCode

I plan to refine the prompt engineering to ensure the fixer agent consistently provides correct, language-specific fixes. I also aim to expand the tool's capabilities to test for a wider range of vulnerabilities beyond injection and XSS, such as business logic flaws and SSRF.
