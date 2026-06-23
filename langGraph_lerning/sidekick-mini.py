from typing import Annotated, TypedDict, List, Dict, Any, Optional
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
import gradio as gr
import nest_asyncio
import uuid
from dotenv import load_dotenv

load_dotenv(override=True)

class EvaluatorOutput(BaseModel):
    feedback: str = Field(description="Feedback on the assistant's response")
    success_criteria_met: bool = Field(description="Whether the success criteria have been met")
    user_input_needed: bool = Field(description="True if more input is needed from the user, or clarification is needed")

class State(TypedDict):
    messages: Annotated[list, add_messages]
    success_criteria: str
    feedback_on_work: Optional[str]
    success_criteria_met: bool
    user_input_needed: bool

nest_asyncio.apply()

async_browser = create_async_playwright_browser(headless=False)
toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
tools = toolkit.get_tools()

worker_llm = ChatOpenAI(model="gpt-4o-mini")
worker_llm_with_tools = worker_llm.bind_tools(tools)

evaluator_llm = ChatOpenAI(model="gpt-4o-mini")
evaluator_llm_with_output = evaluator_llm.with_structured_output(EvaluatorOutput)

def worker(state: State) -> Dict[str, Any]:
    system_message = f"""You are a helpful assistant.
Success criteria:
{state['success_criteria']}
You must either ask a question or provide final answer.
"""

    if state.get("feedback_on_work"):
        system_message += f"""
Previous feedback:
{state['feedback_on_work']}
"""

    found_system_message = False
    messages = state["messages"]

    for message in messages:
        if isinstance(message, SystemMessage):
            message.content = system_message
            found_system_message = True

    if not found_system_message:
        messages = [SystemMessage(content=system_message)] + messages

    response = worker_llm_with_tools.invoke(messages)

    return {"messages": [response]}

def worker_router(state: State) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "evaluator"

def format_conversation(messages: List[Any]) -> str:
    text = ""
    for m in messages:
        if isinstance(m, HumanMessage):
            text += f"User: {m.content}\n"
        elif isinstance(m, AIMessage):
            text += f"Assistant: {m.content}\n"
    return text

def evaluator(state: State) -> Dict[str, Any]:
    last_response = state["messages"][-1].content

    system_message = "You are an evaluator."

    user_message = f"""
Conversation:
{format_conversation(state['messages'])}

Success criteria:
{state['success_criteria']}

Last response:
{last_response}
"""

    eval_result = evaluator_llm_with_output.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content=user_message)
    ])

    return {
        "messages": [{"role": "assistant", "content": eval_result.feedback}],
        "feedback_on_work": eval_result.feedback,
        "success_criteria_met": eval_result.success_criteria_met,
        "user_input_needed": eval_result.user_input_needed
    }

def route_based_on_evaluation(state: State) -> str:
    if state["success_criteria_met"] or state["user_input_needed"]:
        return END
    return "worker"

graph_builder = StateGraph(State)

graph_builder.add_node("worker", worker)
graph_builder.add_node("tools", ToolNode(tools=tools))
graph_builder.add_node("evaluator", evaluator)

graph_builder.add_conditional_edges("worker", worker_router, {
    "tools": "tools",
    "evaluator": "evaluator"
})

graph_builder.add_edge("tools", "worker")

graph_builder.add_conditional_edges("evaluator", route_based_on_evaluation, {
    "worker": "worker",
    END: END
})

graph_builder.add_edge(START, "worker")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

def make_thread_id():
    return str(uuid.uuid4())

async def process_message(message, success_criteria, history, thread):
    config = {"configurable": {"thread_id": thread}}

    state = {
        "messages": [HumanMessage(content=message)],
        "success_criteria": success_criteria,
        "feedback_on_work": None,
        "success_criteria_met": False,
        "user_input_needed": False
    }

    result = await graph.ainvoke(state, config=config)

    user = {"role": "user", "content": message}
    reply = {"role": "assistant", "content": result["messages"][-2].content}
    feedback = {"role": "assistant", "content": result["messages"][-1].content}

    return history + [user, reply, feedback]

async def reset():
    return "", "", None, make_thread_id()

with gr.Blocks(theme=gr.themes.Default(primary_hue="emerald")) as demo:
    gr.Markdown("## Sidekick Personal Co-worker")
    thread = gr.State(make_thread_id())

    with gr.Row():
        chatbot = gr.Chatbot(label="Sidekick", height=300, type="messages")
    with gr.Group():
        with gr.Row():
            message = gr.Textbox(show_label=False, placeholder="Your request to your sidekick")
        with gr.Row():
            success_criteria = gr.Textbox(show_label=False, placeholder="What are your success critiera?")
    with gr.Row():
        reset_button = gr.Button("Reset", variant="stop")
        go_button = gr.Button("Go!", variant="primary")
    message.submit(process_message, [message, success_criteria, chatbot, thread], [chatbot])
    success_criteria.submit(process_message, [message, success_criteria, chatbot, thread], [chatbot])
    go_button.click(process_message, [message, success_criteria, chatbot, thread], [chatbot])
    reset_button.click(reset, [], [message, success_criteria, chatbot, thread])


demo.launch()