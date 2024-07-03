import { z } from 'zod';

export const PlanSchema = z.object({
  steps: z
    .array(z.string())
    .describe('different steps to follow, should be in sorted order'),
});
