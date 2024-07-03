import { ChatOpenAI } from '@langchain/openai';

const OPENAI_MODEL = 'gpt-4o';

export const plannerModel = new ChatOpenAI({
  model: OPENAI_MODEL,
});
