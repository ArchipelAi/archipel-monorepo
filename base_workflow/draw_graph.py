from base_workflow.workflow import workflow_graph
from langchain_core.runnables.graph import MermaidDrawMethod


def main():
	with open('graph.png', 'wb') as fp:
		fp.write(
			workflow_graph.get_graph().draw_mermaid_png(
				draw_method=MermaidDrawMethod.API,
			)
		)


if __name__ == '__main__':
	main()
