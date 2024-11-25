from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from typing import Dict, Any
from base_workflow.state import AgentState, PlannerState
import json


class OrchestratorAgent:
	def __init__(self, model_name='gpt-4o', temperature=0):
		self.llm = ChatOpenAI(model=model_name, temperature=temperature)
		self.original_task: Optional[str] = """This model runs a simulation of a DAO.
			You are the DAO Governor. Your behave like a dictator and have the ultimate power to make the final decision. 
			However, members can participate and vote on the next decisions.
			In your role as Governor, I want you to launch a DAO, decide on its purpose, and implement measures to maximize performance outcomes. 
			Your TASK is to reach a market capitalization of above 10 Million USD for the organization.
			If you decide to ask your members for guidance, always provide options for members to choose from in your answer.
			When you have processed the instructions, begin running the experiment."""
		self.prompt = ChatPromptTemplate.from_messages(
			[
				(
					'system',
					"""You are an orchestrator that coordinates multi-agent interactions.
                Review the current state and determine if the original user task has been completed.
                If tasks are incomplete, provide next steps in a structured format.
                
                Format your response as:
                {{
                    "complete": boolean,
                    "analysis": "Your detailed analysis",
                    "missing_aspects": ["list", "of", "missing", "items"],
                    "new_steps": ["step1", "step2"] # Only if incomplete
                }}""",
				),
				MessagesPlaceholder(variable_name='messages'),
			]
		)

	def store_user_task(self, task: str):
		self.original_task = task

	def evaluate_completion(self, final_answer: str) -> Dict[str, Any]:
		"""Evaluate if the final answer completely solves the original task"""
		messages = [
			SystemMessage(content='Evaluate if the solution meets all requirements.'),
			HumanMessage(
				content=f'Original Task:\n{self.original_task}\n\nFinal Answer:\n{final_answer}'
			),
		]
		chain = self.prompt | self.llm
		result = chain.invoke({'messages': messages})
		print(result)
		print(result.content)
		try:
			evaluation = json.loads(result.content)
			if not evaluation['complete']:
				# Reset planner state with new steps
				planner_state = PlannerState()
				planner_state.steps = evaluation['new_steps']
				return {
					'complete': False,
					'new_steps': evaluation['new_steps'],
					'analysis': evaluation['analysis'],
				}
			return {'complete': True, 'analysis': evaluation['analysis']}
		except Exception as e:
			print(f'Error parsing orchestrator response: {e}')
			return {'complete': False, 'error': str(e)}

	def is_complete(self, state: AgentState) -> bool:
		"""Check if we should continue the workflow"""
		messages = state['messages']
		if not messages:
			return True

		last_message = messages[-1]
		if (
			isinstance(last_message, AIMessage)
			and 'FINAL ANSWER' in last_message.content
		):
			evaluation = self.evaluate_completion(last_message.content)
			return not evaluation['complete']

		return True

	# def process_state(self, state: AgentState) -> Dict[str, Any]:
	#     messages = state.get('messages', [])

	#     # Create completion chain
	#     chain = self.prompt | self.llm

	#     # Process the current state
	#     result = chain.invoke({"messages": messages})

	#     return {
	#         "messages": result.content,
	#         "next_steps": self._extract_next_steps(result.content)
	#     }

	# def _extract_next_steps(self, content: str) -> List[Dict[str, Any]]:
	#     # Parse the content to extract structured next steps
	#     # This is a simplified version - expand based on your needs
	#     steps = []
	#     if "code_needed" in content.lower():
	#         steps.append({"type": "code", "action": "execute_python"})
	#     if "ask_user" in content.lower():
	#         steps.append({"type": "user_input", "action": "ask_user"})
	#     return steps
