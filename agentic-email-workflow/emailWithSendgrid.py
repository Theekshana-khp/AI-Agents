from dotenv import load_dotenv
from agents import Agent,Runner,trace,function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
import asyncio

load_dotenv(override=True)
message = "Write a cold sales email"

@function_tool
def send_test_email(message: str):
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
    from_email = Email("pasindutheekshana903@gmail.com")
    to_email = To("theekshanakhp@gmail.com")
    subject = "Hello from my AI Agent project"
    content = Content("text/html", message)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())

   
    return response.status_code

instructions1 = "You are a sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write professional, serious cold emails."

instructions2 = "You are a humorous, engaging sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write witty, engaging cold emails that are likely to get a response."

instructions3 = "You are a busy sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write concise, to the point cold emails."

sales_agent1 = Agent(
        name="Professional Sales Agent",
        instructions=instructions1,
        model="gpt-4o-mini"
)

sales_agent2 = Agent(
        name="Engaging Sales Agent",
        instructions=instructions2,
        model="gpt-4o-mini"
)

sales_agent3 = Agent(
        name="Busy Sales Agent",
        instructions=instructions3,
        model="gpt-4o-mini"
)

tool1 = sales_agent1.as_tool(tool_name="send_test_email1", tool_description=message)
tool2 = sales_agent2.as_tool(tool_name="send_test_email2", tool_description=message)
tool3 = sales_agent3.as_tool(tool_name="send_test_email3", tool_description=message)

subject_instructions = "You can write a subject for a cold sales email. \
You are given a message and you need to write a subject for an email that is likely to get a response."

html_instructions = "You can convert a text email body to an HTML email body. \
You are given a text email body which might have some markdown \
and you need to convert it to an HTML email body with simple, clear, compelling layout and design."

subject_writer = Agent(name="Email subject writer", instructions=subject_instructions, model="gpt-4o-mini")
subject_tool = subject_writer.as_tool(tool_name="subject_writer", tool_description="Write a subject for a cold sales email")

html_converter = Agent(name="HTML email body converter", instructions=html_instructions, model="gpt-4o-mini")
html_tool = html_converter.as_tool(tool_name="html_converter",tool_description="Convert a text email body to an HTML email body")


tools_for_email_drafting = [tool1, tool2, tool3]
tools_for_email_sending = [subject_tool, html_tool, send_test_email]

async def main():
    instructions_for_email_drafting = """
        You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
 
        Follow these steps carefully:
        1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
        
        2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
        You can use the tools multiple times if you're not satisfied with the results from the first try.
        
        3. Handoff for Sending: Pass ONLY the winning email draft to the 'Email_Manager' agent. The Email Manager will take care of formatting and sending.
        
        Crucial Rules:
        - You must use the sales agent tools to generate the drafts — do not write them yourself.
        - You must hand off exactly ONE email to the Email Manager — never more than one.
    """

    instructions_for_email_sending = """
        You are an email formatter and sender. You receive the body of an email to be sent. \
        You first use the subject_writer tool to write a subject for the email, then use the html_converter tool to convert the body to HTML. \
        Finally, you use the send_test_email tool to send the email with the subject and HTML body.
        Steps:
        1. Use subject_writer tool to generate subject from the email body.
        2. Use html_converter tool to convert email body into HTML.
        3. Use send_test_email tool to send the final email.

        Email_ManagerYou MUST call send_test_email tool. Do not stop until email is sent.
    """


    emailer_agent = Agent(
        name="Email_Manager",
        instructions=instructions_for_email_sending,
        tools=tools_for_email_sending,
        model="gpt-4o-mini",
        handoff_description="Convert an email to HTML and send it")

    handoffs = [emailer_agent]


    sales_picker = Agent(
        name="sales_picker",
        instructions=instructions_for_email_drafting,
        tools=tools_for_email_drafting,
        handoffs= handoffs,
        model="gpt-4o-mini"
    )

    message = "Send a cold sales email addressed to 'Dear CEO of [company name]' with the following message: [message]"

    with trace("sales_picker"):
        result = await Runner.run(sales_picker, message)
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())