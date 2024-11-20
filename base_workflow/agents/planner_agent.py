from langchain_openai import ChatOpenAI
from base_workflow.utils import create_agent
from base_workflow.state import PlannerState
from base_workflow.tools.create_steps import create_steps


def create_planner_agent(model: str = 'gpt-4o-mini'):
	llm = ChatOpenAI(model=model)

	system_prompt = """You are a planning agent that breaks down complex tasks into sequential steps.
	Analyze the input and create a detailed list of steps needed to accomplish the goal.
	Your ONLY task is to break down the input into sequential steps.
	Each step should be clear and actionable.
    You must respond in this exact JSON format:
    {
        "steps": [
            "Step 1: [action]",
            "Step 2: [action]",
            ...
        ]
    }
    """

	return create_agent(llm, [create_steps], system_prompt)


# Global state instance
planner_state = PlannerState()
