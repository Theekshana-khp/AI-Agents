from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field
from typing import List
from .tools.custom_tool import PushNotificationTool


class TrendingCompany(BaseModel):
    name: str = Field(description="Company name")
    ticker: str = Field(description="Stock ticker symbol")
    reason: str = Field(description="Reason this company is trending in the news")


class TrendingCompanyList(BaseModel):
    companies: List[TrendingCompany]


class TrendingCompanyResearch(BaseModel):
    name: str
    market_position: str
    future_outlook: str
    investment_potential: str


class TrendingCompanyResearchList(BaseModel):
    research_list: List[TrendingCompanyResearch]


@CrewBase
class StockPicker:

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(
            config=self.agents_config["trending_company_finder"],
            tools=[SerperDevTool()],
            memory=True
        )

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["financial_researcher"],
            tools=[SerperDevTool()],
            memory=True
        )

    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config["stock_picker"],
            tools=[PushNotificationTool()],
            memory=True
        )

    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config["find_trending_companies"],
            output_pydantic=TrendingCompanyList,
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config["research_trending_companies"],
            output_pydantic=TrendingCompanyResearchList,
        )

    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config["pick_best_company"],
        )

    @crew
    def crew(self) -> Crew:

        manager = Agent(
            config=self.agents_config["manager"],
            allow_delegation=True
        )

        return Crew(
            agents=[
                self.trending_company_finder(),
                self.financial_researcher(),
                self.stock_picker(),
            ],
            tasks=[
                self.find_trending_companies(),
                self.research_trending_companies(),
                self.pick_best_company(),
            ],
            process=Process.hierarchical,
            manager_agent=manager,
            memory=True,
            verbose=True,
        )