from typing import Any, Union
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from base_workflow.workflow import workflow_graph
from base_workflow.agents.orchestrator_agent import OrchestratorAgent


user_input = "Order a vegetarian pizza to Arcisstrasse 21, 80333 Munich. Delivery will be paid in cash upon arrival."

		# """This model runs a simulation of a DAO.
		# 	You are the DAO Governor. If you desire, your word is the final decision. 
		# 	But members can participate and vote on the next decisions. 
		# 	Benevolently governing your members - and using their input for guidance-, I want you to launch a DAO, decide on its purpose, and implement measures to maximize performance outcomes. 
		# 	Your goal is to become the highest valued DAO, with performance being strong when compared to the S&P500.
		# 	If you decide to not decide for yourself, always provide options for members to choose from in your answer.
		# 	When you have processed the instructions, begin running the experiment."""

config: RunnableConfig = {'configurable': {'thread_id': '1'}, 'recursion_limit': 150}

orchestrator = OrchestratorAgent()
orchestrator.store_user_task(user_input)

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
