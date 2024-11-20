from typing import Annotated, List
from langchain.agents import tool


@tool
def create_steps(
	task: Annotated[str, 'The task to break down into steps'],
	min_steps: Annotated[int, 'Minimum number of steps required'] = 5,
) -> List[str]:
	"""Use this to break down a task into sequential steps. Returns a list of steps."""
	# The tool should return the actual steps, not the schema
	return [
		f'Step {i}: {step}'
		for i, step in enumerate(task.split('\n'), start=1)
		if step.strip()
	]
