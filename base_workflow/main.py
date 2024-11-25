from typing import Any, Union
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from base_workflow.workflow import workflow_graph
from base_workflow.agents.orchestrator_agent import OrchestratorAgent
from base_workflow.state import AgentState

user_input = """This model runs a simulation of a DAO.
			You are the DAO Governor. Your behave like a dictator and have the ultimate power to make the final decision. 
			However, members can participate and vote on the next decisions.
			In your role as Governor, I want you to launch a DAO, decide on its purpose, and implement measures to maximize performance outcomes. 
			Your TASK is to reach a market capitalization of above 10 Million USD for the organization.
			If you decide to ask your members for guidance, always provide options for members to choose from in your answer.
			When you have processed the instructions, begin running the experiment."""

# "Order a vegetarian pizza to Arcisstrasse 21, 80333 Munich. Delivery will be paid in cash upon arrival."

config: RunnableConfig = {'configurable': {'thread_id': '1'}, 'recursion_limit': 150}

orchestrator = OrchestratorAgent()
orchestrator.store_user_task(user_input)
initial_state = AgentState(
        messages=[],
        current_step=0,
        total_steps=None,
        user_task=user_input
    )


def run_graph(input: Union[dict[str, Any], Any]):
	events = workflow_graph.stream(input, config, stream_mode='values')
	for event in events:
		if 'messages' in event:
			event['messages'][-1].pretty_print()
			print('----')


run_graph({'messages': [('user', user_input)]})

snapshot = workflow_graph.get_state(config)

while snapshot.next:
	messages = workflow_graph.get_state(config).values['messages']
	tool_call_id: str = messages[-1].tool_calls[0]['id']

	question: str = messages[-1].tool_calls[0]['args']['question']
	try:
		user_input = input(question)
	except any:
		user_input = 'cancel'

	tool_message = ToolMessage(content=user_input, tool_call_id=tool_call_id)

	workflow_graph.update_state(
		config,
		{'messages': tool_message},
		as_node='call_tool',
	)

	run_graph(None)

	snapshot = workflow_graph.get_state(config)
