import { z } from 'zod';

const basePlanEntrySchema = z.object({
  step: z.string(),
});

type PlanEntry = z.infer<typeof basePlanEntrySchema> & {
  subSteps?: PlanEntry[];
};

const planEntrySchema: z.ZodType<PlanEntry> = basePlanEntrySchema.extend({
  subSteps: z.lazy(() => planEntrySchema.array()),
});

export type PlanEntryExtended = z.infer<typeof planEntrySchema>;

export type PlanExecuteState = {
  input: string;
  plan: PlanEntry[];
  pastSteps: [string, string][];
  response?: string;
};
