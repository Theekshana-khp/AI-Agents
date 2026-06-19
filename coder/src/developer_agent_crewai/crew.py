from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent


@CrewBase
class DeveloperAgentCrewai():
    """Coder crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def coder(self) -> Agent:
        return Agent(
            config=self.agents_config['coder'],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode='safe',
            max_execution_time=30,
            max_retry_limit=5
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['coding_task'],
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the DeveloperAgentCrewai crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
