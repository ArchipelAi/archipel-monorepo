import { UseChatHelpers } from 'ai/react'

import { Button } from '@/components/ui/button'
import { ExternalLink } from '@/components/external-link'
import { IconArrowRight } from '@/components/ui/icons'

export function EmptyScreen() {
  return (
    <div className="mx-auto max-w-2xl px-4">
      <div className="flex flex-col gap-2 rounded-lg border bg-background p-8">
        <h1 className="text-lg font-semibold">Archipel AI Chat</h1>
        <p className="leading-normal text-muted-foreground">
          In this AI project, we utilize multiple AI language models like
          ChatGPT, Mistral, and LLaMA to enhance performance through
          collaboration and validation. Each model processes the same input, and
          their outputs are synthesized to extract a consensus, ensuring higher
          accuracy.
        </p>
        <p className="leading-normal text-muted-foreground">
          This consensus is validated against technical and scientific
          benchmarks by an AI & Validator Network and then stored on a
          blockchain, serving as a transparent and secure long-term memory. The
          blockchain ensures the traceability of data, which can be referenced
          for future validations.
        </p>
      </div>
    </div>
  )
}
