from langchain.schema import AIMessage
from base_workflow.state import AgentState
from base_workflow.agents.orchestrator_agent import OrchestratorAgent
from base_workflow.agents.planner_agent import planner_state


orchestrator = OrchestratorAgent()

def _normalize_boolean(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return False


def router(state: AgentState):
	messages = state['messages']
	last_message = messages[-1]

	if isinstance(last_message, AIMessage):
		if last_message.tool_calls:
			return 'call_tool'
		if 'FINAL ANSWER' in last_message.content:
			evaluation = orchestrator.evaluate_completion(last_message.content)
			is_complete = _normalize_boolean(evaluation.get('complete', False))
			if not is_complete:
				# Update planner state with new steps
				new_steps = evaluation.get('new_steps', [])
				if new_steps:
					print("\nNew Steps:")
					for step in new_steps:
						print(f"- {step}")
					planner_state.steps = new_steps
					planner_state.current_step = 0

				return 'continue'  # Continue workflow with new steps

			else:
				print('Workflow completed successfully')
			return 'end'

	return 'continue'
