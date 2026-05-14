import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { FileInput, Loader2 } from "lucide-react"
import { apiFetch } from "@/services/api"

interface IngestResponse {
  jurisdiction: string
  year: number
  officials_processed: number
  holdings_processed: number
}

interface IngestForm700ButtonProps {
  jurisdiction: string
  startYear: number | null
}

export function IngestForm700Button({
  jurisdiction,
  startYear,
}: IngestForm700ButtonProps) {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)

  const isDisabled = !jurisdiction || startYear === null

  const handleIngest = async () => {
    if (isDisabled) return
    setLoading(true)
    setResult(null)
    try {
      const data = await apiFetch<IngestResponse>(
        `/ingest/form700/${encodeURIComponent(jurisdiction)}/${startYear}`,
        { method: "POST" }
      )
      const o = data.officials_processed
      const h = data.holdings_processed
      setResult(
        `Done — ${o} official${o !== 1 ? "s" : ""}, ${h} holding${h !== 1 ? "s" : ""} processed.`
      )
    } catch (err: unknown) {
      setResult(err instanceof Error ? err.message : "Ingest failed.")
    } finally {
      setLoading(false)
    }
  }

  const tooltipText =
    !jurisdiction && startYear === null
      ? "Select a jurisdiction and start year first"
      : !jurisdiction
        ? "Select a jurisdiction first"
        : "Select a start year first"

  return (
    <TooltipProvider delayDuration={200}>
      <Tooltip>
        <TooltipTrigger asChild>
          <span className="w-full">
            <Button
              variant="outline"
              className="w-full cursor-pointer"
              onClick={handleIngest}
              disabled={isDisabled || loading}
            >
              {loading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <FileInput className="mr-2 h-4 w-4" />
              )}
              {loading ? "Ingesting…" : "Ingest Form 700"}
            </Button>
          </span>
        </TooltipTrigger>
        {isDisabled && (
          <TooltipContent side="right">
            <p>{tooltipText}</p>
          </TooltipContent>
        )}
      </Tooltip>
      {result && <p className="mt-1 text-xs text-muted-foreground">{result}</p>}
    </TooltipProvider>
  )
}
