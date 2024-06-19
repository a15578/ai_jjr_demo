import os

#配置langsmith参数
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "业务agent"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__e6fb551d27e6470ead241ba5b06b4ae8"

from talk import *
from agents import *
import functools
from typing import TypedDict
from langgraph.graph import END, StateGraph


class AgentState(TypedDict):
    input: str


def agent_node(state,agent_exc):
    result = agent_exc.invoke(state)
    return {"input":result["output"]}


agent1_node = functools.partial(agent_node, agent_exc=agent1_executor)
agent2_node = functools.partial(agent_node, agent_exc=agent2_executor)
agent3_node = functools.partial(agent_node, agent_exc=agent3_executor)


def should_continue(state):
    if "信息不够" in state["input"]:
        return "agent2"
    else:
        return "agent3"


#使用langgraph构建工作流
workflow = StateGraph(AgentState)

workflow.add_node("agent1",agent1_node)
workflow.add_node("agent2",agent2_node)
workflow.add_node("agent3",agent3_node)
workflow.set_entry_point("agent1")

workflow.add_conditional_edges(
    "agent1",
    should_continue,
    {
        "agent2": "agent2",
        "agent3": "agent3",
    },
)
workflow.add_edge("agent2",END)
workflow.add_edge("agent3",END)

app = workflow.compile()


if __name__=="__main__":
    input = FIRST_TALK
    result = app.invoke({"input":input})
    print(result['input'])
