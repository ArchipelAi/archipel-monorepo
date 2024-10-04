import { ChatPromptTemplate } from '@langchain/core/prompts';
import zodToJsonSchema from 'zod-to-json-schema';
import type { PlanEntryExtended, PlanExecuteState } from '../../types';
import { PlanSchema } from './types';
import { plannerModel } from '../../models';

const plan = zodToJsonSchema(PlanSchema);

const planFunction = {
  name: 'plan',
  description: 'This tool is used to plan the steps to follow',
  parameters: plan,
};

const plannerPrompt = ChatPromptTemplate.fromTemplate(
  `For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

{objective}`,
);

const model = plannerModel.withStructuredOutput(planFunction);

const planner = plannerPrompt.pipe(model);

async function planStep(
  state: PlanExecuteState,
): Promise<Partial<PlanExecuteState>> {
  const plan = PlanSchema.parse(
    await planner.invoke({ objective: state.input }),
  );

  const mappedPlan: PlanEntryExtended[] = plan.steps.map((step) => ({
    step: step,
  }));

  return { plan: mappedPlan };
}

export { planStep };
