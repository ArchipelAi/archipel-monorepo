import {
  END,
  START,
  StateGraph,
  type StateGraphArgs,
} from '@langchain/langgraph';
import type { PlanEntryExtended, PlanExecuteState } from './types';
import { planStep } from './agents/planner/planner';

const planExecuteState: StateGraphArgs<PlanExecuteState>['channels'] = {
  input: {
    reducer: (left?: string, right?: string) => right ?? left ?? '',
  },
  plan: {
    reducer: (x?: PlanEntryExtended[], y?: PlanEntryExtended[]) => y ?? x ?? [],
    default: () => [],
  },
  pastSteps: {
    reducer: (x: [string, string][], y: [string, string][]) => x.concat(y),
    default: () => [],
  },
  response: {
    reducer: (x?: string, y?: string) => y ?? x,
    default: () => undefined,
  },
};

const workflow = new StateGraph<PlanExecuteState>({
  channels: planExecuteState,
})
  .addNode('planner', planStep)
  .addEdge(START, 'planner')
  .addEdge('planner', END);

// Finally, we compile it!
// This compiles it into a LangChain Runnable,
// meaning you can use it as you would any other runnable
const app = workflow.compile();

const config = { recursionLimit: 50 };

export const main = async (message: string) => {
  for await (const event of await app.stream(
    {
      input: message,
    },
    config,
  )) {
    console.log(JSON.stringify(event));
  }
  return 'ok';
};

const input = 'what is the hometown of the 2024 Australian open winner?';

main(input);
