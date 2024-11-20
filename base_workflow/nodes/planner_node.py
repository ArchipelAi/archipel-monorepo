from langchain.schema import SystemMessage
from base_workflow.agents.planner_agent import create_planner_agent, planner_state
from base_workflow.state import AgentState
import json


def planner_node(state: AgentState) -> AgentState:
	if not planner_state.steps:
		if planner_state.can_add_steps():
			agent = create_planner_agent()
			result = agent.invoke({'messages': state['messages']})
			#print('Messages received by planner_node:', state['messages'])

			try:
				content = result.content.strip()
				parsed = json.loads(content)
				planner_state.steps = parsed['steps']
			except:
				planner_state.steps = ['No steps needed at the current state.']

	current_time = planner_state.get_elapsed_time()
	print(current_time)
	if planner_state.current_step < len(planner_state.steps):
		current_step = planner_state.steps[planner_state.current_step]
		return {
            'messages': [
                SystemMessage(
                    content=f'Time elapsed: {current_time:.2f}s\nCurrent step: {current_step}'
                )
            ],
            'current_step': planner_state.current_step,
            'total_steps': len(planner_state.steps),
        }
	
	return state