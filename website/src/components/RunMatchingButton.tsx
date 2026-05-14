import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { ScanSearch, Loader2 } from "lucide-react"
import { apiFetch } from "@/services/api"

interface MatchingResponse {
  official_id: number
  official_name: string
  jurisdiction_slug: string
  holdings_count: number
  matches_found: number
  matches: unknown[]
}

interface RunMatchingButtonProps {
  officialId: number | null
  jurisdictionSlug: string
  year: number | null
}

export function RunMatchingButton({
  officialId,
  jurisdictionSlug,
  year,
}: RunMatchingButtonProps) {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)

  const isDisabled = officialId === null || !jurisdictionSlug || year === null

  const handleMatch = async () => {
    if (isDisabled) return
    setLoading(true)
    setResult(null)
    try {
      const params = new URLSearchParams({
        jurisdiction_slug: jurisdictionSlug,
      })
      params.set("year", String(year))

      const data = await apiFetch<MatchingResponse>(
        `/matching/official/${officialId}?${params.toString()}`,
        { method: "POST" }
      )
      const m = data.matches_found ?? 0
      const h = data.holdings_count ?? 0
      if (h === 0) {
        setResult("No holdings found for this official — nothing to match.")
      } else {
        setResult(
          `Done — ${m} match${m !== 1 ? "es" : ""} found across ${h} holding${h !== 1 ? "s" : ""}.`
        )
      }
    } catch (err: unknown) {
      setResult(err instanceof Error ? err.message : "Matching failed.")
    } finally {
      setLoading(false)
    }
  }

  const tooltipText =
    officialId === null && !jurisdictionSlug
      ? "Select a jurisdiction and an official first"
      : officialId === null
        ? "Select an official first"
        : "Select a jurisdiction first"

  return (
    <TooltipProvider delayDuration={200}>
      <Tooltip>
        <TooltipTrigger asChild>
          <span className="w-full">
            <Button
              variant="outline"
              className="w-full cursor-pointer"
              onClick={handleMatch}
              disabled={isDisabled || loading}
            >
              {loading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <ScanSearch className="mr-2 h-4 w-4" />
              )}
              {loading ? "Running…" : "Run Matching"}
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
