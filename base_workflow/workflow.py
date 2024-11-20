from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from base_workflow.router import router
from base_workflow.nodes import agent_node, planner_node, benchmark_node
from base_workflow.state import AgentState
from base_workflow.tools import (
	ask_user,
	execute_python,
	get_available_cities,
	get_restaurants_and_menu_in_city,
	order_pizza,
)


workflow = StateGraph(AgentState)

workflow.add_node('planner', planner_node)
workflow.add_node('agent', agent_node)
workflow.add_node('benchmark', benchmark_node)
workflow.add_node(
	'call_tool',
	ToolNode(
		[
			ask_user,
			execute_python,
			get_available_cities,
			get_restaurants_and_menu_in_city,
			order_pizza,
		]
	),
)
workflow.add_edge('planner', 'agent')
workflow.add_edge('call_tool', 'agent')
workflow.add_edge('agent', 'benchmark')
workflow.add_conditional_edges(
	'benchmark',
	router,
	{'continue': 'agent', 'call_tool': 'call_tool', 'end': END},
)
workflow.set_entry_point('planner')

memory = MemorySaver()

workflow_graph = workflow.compile(checkpointer=memory)
