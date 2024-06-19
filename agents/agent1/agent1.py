import os
os.environ["OPENAI_API_KEY"] = "none"

from .tools import *
from .task import first_prompt
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain_community.chat_models import ChatOllama
from langchain.agents import create_structured_chat_agent, AgentExecutor

prompt = hub.pull("hwchase17/structured-chat-agent")
prompt.messages[-1].prompt.template = first_prompt + prompt.messages[-1].prompt.template

tools_list = [save_basic_info, is_basic_info_enough]
# model = ChatOpenAI(model_name="qwen-max",openai_api_base="http://127.0.0.1:8006/v1/")
model = ChatOllama(model="qwen:32b-chat",num_ctx=64536)

agent_1 = create_structured_chat_agent(llm=model, tools=tools_list, prompt=prompt)
agent1_executor = AgentExecutor(agent=agent_1, tools=tools_list, stop=["Observation:","<|eot_id|>"])