from typing import Sequence
from langchain.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(model='gpt-4o-mini')


def create_agent(
	model: BaseChatModel,
	tools: Sequence[BaseTool],
	system_message: str,
):
	"""Create an agent."""
	prompt = ChatPromptTemplate.from_messages(
		[
			(
				'system',
				'You are a helpful AI assistant, collaborating with other assistants.'
				' Use the provided tools to progress towards answering the question.'
				" If you are unable to fully answer, that's OK, another assistant with different tools "
				' will help where you left off. Execute what you can to make progress.'
				' If you or any of the other assistants have the final answer or deliverable,'
				' Once finished send only FINAL ANSWER so the team knows to stop.'
				' You have access to the following tools: {tool_names}.\\\\n{system_message}',
			),
			MessagesPlaceholder(variable_name='messages'),
		]
	)
	prompt = prompt.partial(system_message=system_message)
	prompt = prompt.partial(tool_names=', '.join([tool.name for tool in tools]))
	return prompt | model.bind_tools(tools)
