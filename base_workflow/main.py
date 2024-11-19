from typing import Any, Union
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from base_workflow.workflow import workflow_graph

user_input = 'Order a pizza.'

config: RunnableConfig = {'configurable': {'thread_id': '1'}, 'recursion_limit': 150}


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
