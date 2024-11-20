from langchain.schema import AIMessage
from base_workflow.state import AgentState
from base_workflow.agents.orchestrator_agent import OrchestratorAgent

orchestrator = OrchestratorAgent()


def router(state: AgentState):
	messages = state['messages']
	last_message = messages[-1]

	if isinstance(last_message, AIMessage):
		if last_message.tool_calls:
			return 'call_tool'
		if 'FINAL ANSWER' in last_message.content:
			if not orchestrator.is_complete(state):
				return 'continue'  # Continue workflow with new steps
			else:
				print('Workflow completed successfully')
				return 'end'
	return 'continue'
