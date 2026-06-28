from agents import Agent, WebSearchTool, trace, Runner, function_tool
from agents.model_settings import ModelSettings
import asyncio
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

load_dotenv(override=True)

INSTRUCTIONS_FOR_SEARCH = "You are a research assistant. Given a search term, you search the web for that term and \
produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 \
words. Capture the main points. Write succintly, no need to have complete sentences or good \
grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the \
essence and ignore any fluff. Do not include any additional commentary other than the summary itself."

search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS_FOR_SEARCH,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required")
)

HOW_MANY_SEARCHES = 3
INSTRUCTIONS_FOR_PLAN = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."

class WebSearchItem(BaseModel):
    query: str = Field(description="The search term to use for the web search.")
    reason: str = Field(description="Your reasoning for why this search is important to the query.")

class ResearchPlan(BaseModel):
    searches : list[WebSearchItem] =Field(description="A list of web searches to perform to best answer the query.")

planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS_FOR_PLAN,
    output_type=ResearchPlan,
    model="gpt-4o-mini"
)

INSTRUCTIONS_FOR_REPORT = (
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, and some initial research done by a research assistant.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output2.\n"
    "The final output2 should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 5-10 pages of content, at least 1000 words."
)

class ReportData(BaseModel):
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")

    markdown_report: str = Field(description="The final report")

    follow_up_questions: list[str] = Field(description="Suggested topics to research further")

report_agent = Agent(
    name="ReportAgent",
    instructions=INSTRUCTIONS_FOR_REPORT,
    output_type=ReportData,
    model="gpt-4o-mini"
)

@function_tool
def send_email(subject: str, html_body: str) :
    """ Send out an email with the given subject and HTML body """
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("pasindutheekshana903@gmail.com")
    to_email = To("theekshanakhp@gmail.com")
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    response = sg.client.mail.send.post(request_body=mail)
    return response.status_code

INSTRUCTIONS_FOR_EMAILS = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed report. You should use your tool to send one email, providing the 
report converted into clean, well presented HTML with an appropriate subject line."""

email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS_FOR_EMAILS,
    tools=[send_email],
    model="gpt-4o-mini",
)

async def plan_search(query: str):
    """Searching for research on a topic: {query}"""
    print("Searching for research plan ...")
    results =await Runner.run(planner_agent, query)
    return results.final_output

async def search_handler(items:ResearchPlan):
    """Search the web for the given search term"""
    tasks = [asyncio.create_task(search(item)) for item in items.searches]
    results = await asyncio.gather(*tasks)
    print("Finished searching")
    return results

async def search(item:WebSearchItem):
    """ Use the search agent to run a web search for each item in the search plan """
    inputs = f"Search term: {item.query}\nReason for searching: {item.reason}"
    result = await Runner.run(search_agent, inputs)
    return result.final_output

async def generate_report(query: str, search_results: list[str]):
    """ Use the writer agent to write a report based on the search results"""
    results = await Runner.run(report_agent, f"Query: {query}\nSearch results: {search_results}")
    return results.final_output

async def send_emails(report: ReportData):
    """ Use the email agent to send an email with the report """
    print("Writing email...")
    result = await Runner.run(email_agent, report.markdown_report)
    print("Email sent")
    return report

async def main():
    query = input("Enter your research topic: ")

    with trace("agent_work_flow"):
        search_plan = await plan_search(query)
        print(search_plan)
        print("\n\n")
        search_results = await search_handler(search_plan)
        print(search_results)
        print("\n\n")
        report = await generate_report(query, search_results)
        print(search_plan)
        print("\n\n")
        await send_emails(report)
        print("Research completed")

if __name__ == "__main__":
    asyncio.run(main())