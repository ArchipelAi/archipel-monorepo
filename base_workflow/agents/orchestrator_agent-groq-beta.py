# from typing import Dict, Any, Optional
# import json
# import os
# from groq import Groq


# class OrchestratorAgent:
# 	def __init__(self, model_name='llama3-70b-8192', temperature=0.5, max_tokens=1024):
# 		self.client = Groq(
# 			api_key=os.environ.get('GROQ_API_KEY'),
# 		)
# 		self.model_name = model_name
# 		self.temperature = temperature
# 		self.max_tokens = max_tokens
# 		self.top_p = 0.1
# 		self.user_task: Optional[str] = None

# 	def store_user_task(self, task: str):
# 		self.original_task = task

# 	def evaluate_completion(self, completion: str) -> Dict[str, Any]:
# 		"""Evaluate if the task has been completed and return next steps if needed."""
# 		system_message = f"""
#         Original Task: {self.original_task}
#         Latest Completion: {completion}
#         """

# 		response = self.client.chat.completions.create(
# 			messages=[
# 				{
# 					'role': 'system',
# 					'content': 'You orchestrate multi-agent interactions. Be precise in your output and clearly follow the instructions provided.',
# 				},
# 				{
# 					'role': 'user',
# 					'content': self._create_evaluation_prompt(system_message),
# 				},
# 			],
# 			model=self.model_name,
# 			temperature=self.temperature,
# 			max_tokens=self.max_tokens,
# 			top_p=self.top_p,
# 			stop=None,
# 			stream=False,
# 		)

# 		try:
# 			content = response.choices[0].message.content
# 			if '```json' in content:
# 				json_str = content.split('```json')[1].split('```')[0].strip()
# 				return json.loads(json_str)
# 			return json.loads(content)
# 		except json.JSONDecodeError:
# 			return {
# 				'complete': False,
# 				'analysis': 'Failed to parse orchestrator response',
# 				'new_steps': ['Retry evaluation with proper JSON formatting'],
# 			}

# 	def _create_evaluation_prompt(self, system_message: str) -> str:
# 		return """You are an orchestrator that coordinates multi-agent interactions.
#                 Review the current state and determine if the original user task has been completed.
#                 If tasks are incomplete, provide next steps in a structured format.
                
#                 Format your response as:
#                 {
#                     "complete": boolean,
#                     "analysis": "Your detailed analysis",
#                     "missing_aspects": ["list", "of", "missing", "items"],
#                     "new_steps": ["step1", "step2"] # Only if incomplete
#                 }"""

# 	def is_complete(self, state: Dict[str, Any]) -> bool:
# 		"""Determine if the workflow should continue based on the current state."""
# 		if not state.get('messages'):
# 			return True
# 		last_message = state['messages'][-1]
# 		if not hasattr(last_message, 'content'):
# 			return True
# 		evaluation = self.evaluate_completion(last_message.content)
# 		return not evaluation.get('complete', False)
