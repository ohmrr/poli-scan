import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { getMatches, deleteMatch } from "@/services/match"
import { getOfficialById } from "@/services/official"
import type { Match } from "@/types/match"
import type { Official } from "@/types/official"
import { useEffect, useMemo, useState } from "react"
import { Tooltip, TooltipContent, TooltipTrigger } from "./ui/tooltip"
import type { Jurisdiction } from "@/types/jurisdiction"
import { ConfidenceBadge } from "./ConfidenceBadge"
import { DeleteMatchDialog } from "./DeleteMatchDialog"
import { jurisdictionPrettyName } from "@/lib/utils"

interface ConflictTableProps {
  jurisdictions: Jurisdiction[]
  jurisdiction: string
  startYear?: number
  endYear?: number
}

export function ConflictTable({
  jurisdictions,
  jurisdiction,
  startYear,
  endYear,
}: ConflictTableProps) {
  const [matches, setMatches] = useState<Match[]>([])
  const [officials, setOfficials] = useState<Record<number, Official>>({})
  const [loading, setLoading] = useState<boolean>(true)

  const handleDelete = async (matchId: number) => {
    await deleteMatch(matchId)
    setMatches((prev) => prev.filter((m) => m.id !== matchId))
  }

  const jurisdictionMap = useMemo(
    () => Object.fromEntries(jurisdictions.map(j => [j.id, jurisdictionPrettyName(j.slug)])),
    [jurisdictions]
  )

  useEffect(() => {
    getMatches()
      .then(setMatches)
      .catch((err) => console.error(err))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!matches.length) return

    const uniqueIds = [...new Set(matches.map((m) => m.official_id))]

    Promise.all(uniqueIds.map((id) => getOfficialById(id)))
      .then((data) => {
        const map: Record<number, Official> = {}
        data.forEach((official) => {
          map[official.id] = official
        })
        setOfficials(map)
      })
      .catch((err) => console.error(err))
  }, [matches])

  const filtered = matches.filter((row) => {
    const afterStart = startYear ? row.year >= startYear : true
    const beforeEnd = endYear ? row.year <= endYear : true
    return afterStart && beforeEnd
  })

  return (
    <div className="rounded-md border border-border bg-card">
      <Table>
        <TableHeader>
          <TableRow className="bg-muted/50 hover:bg-muted/50">
            <TableHead className="w-40 font-semibold text-foreground">Jurisdiction</TableHead>
            <TableHead className="w-40 font-semibold text-foreground">
              Name
            </TableHead>
            <TableHead className="w-15 font-semibold text-foreground">
              Year
            </TableHead>
            <TableHead className="w-195 font-semibold text-foreground">
              Matched Holding
            </TableHead>
            <TableHead className="font-semibold text-foreground">
              PDF
            </TableHead>
            <TableHead className="w-40 text-center font-semibold text-foreground">
              Confidence
            </TableHead>
            <TableHead className="w-10" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {(filtered.length === 0 && jurisdiction) || loading ? (
            <TableRow>
              <TableCell
                colSpan={6}
                className="py-12 text-center text-muted-foreground"
              >
                {loading ? (
                  <>Loading records...</>
                ) : (
                  <>
                    No conflicts of interest found for{" "}
                    <span className="font-medium text-foreground">
                      {jurisdiction}
                    </span>
                  </>
                )}
              </TableCell>
            </TableRow>
          ) : (
            filtered.map((row) => (
              <TableRow
                key={row.id}
                className="transition-colors hover:bg-muted/40"
              >
                <TableCell>{jurisdictionMap[row.jurisdiction_id]}</TableCell>
                <TableCell>
                  {officials[row.official_id]?.full_name}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {row.year}
                </TableCell>
                <TableCell className="truncate">
                  {row.matched_interest}
                </TableCell>
                <TableCell>
                  {row.pdf_url ? (<a href={row.pdf_url} className="text-primary truncate underline-offset-4 hover:underline">
                    {row.pdf_url}
                  </a>) : (<span className="text-muted-foreground">—</span>)}
                </TableCell>
                <TableCell className="text-center">
                  <Tooltip>
                    <TooltipTrigger className="inline-flex justify-center">
                      <ConfidenceBadge value={row.confidence} />
                    </TooltipTrigger>
                    <TooltipContent>{row.reason}</TooltipContent>
                  </Tooltip>
                </TableCell>
                <TableCell>
                  <DeleteMatchDialog
                    matchId={row.id}
                    officialName={officials[row.official_id]?.full_name}
                    onConfirm={handleDelete}
                  />
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}
