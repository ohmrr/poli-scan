import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import type { Match } from "@/types/match"
import type { Official } from "@/types/official"
import type { Jurisdiction } from "@/types/jurisdiction"
import { useMemo } from "react"
import { Tooltip, TooltipContent, TooltipTrigger } from "./ui/tooltip"
import { ConfidenceBadge } from "./ConfidenceBadge"
import { DeleteMatchDialog } from "./DeleteMatchDialog"
import { jurisdictionPrettyName } from "@/lib/utils"

interface ConflictTableProps {
  matches: Match[]
  officials: Record<number, Official>
  jurisdictions: Jurisdiction[]
  jurisdiction: string
  officialId?: number
  startYear?: number
  endYear?: number
  loading: boolean
  minConfidence: number
  onDeleteMatch: (matchId: number) => void
}

export function ConflictTable({
  matches,
  officials,
  jurisdictions,
  jurisdiction,
  officialId,
  loading,
  onDeleteMatch,
}: ConflictTableProps) {
  const jurisdictionMap = useMemo(
    () =>
      Object.fromEntries(
        jurisdictions.map((j) => [j.id, jurisdictionPrettyName(j.slug)])
      ),
    [jurisdictions]
  )

  const isEmpty = matches.length === 0

  return (
    <div className="rounded-md border border-border bg-card">
      <Table>
        <TableHeader>
          <TableRow className="bg-muted/50 hover:bg-muted/50">
            <TableHead className="w-40 font-bold text-foreground">
              Jurisdiction
            </TableHead>
            <TableHead className="w-40 font-bold text-foreground">
              Name
            </TableHead>
            <TableHead className="w-15 font-bold text-foreground">
              Year
            </TableHead>
            <TableHead className="w-195 font-bold text-foreground">
              Matched Holding
            </TableHead>
            <TableHead className="font-bold text-foreground">PDF</TableHead>
            <TableHead className="w-40 text-center font-bold text-foreground">
              Confidence
            </TableHead>
            <TableHead className="w-10" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {loading || isEmpty ? (
            <TableRow>
              <TableCell
                colSpan={7}
                className="py-12 text-center text-muted-foreground"
              >
                {loading ? (
                  <>Loading records...</>
                ) : (
                  <>
                    No conflicts of interest found
                    {officialId && officials[officialId] && (
                      <>
                        {" "}
                        for{" "}
                        <span className="font-medium text-foreground">
                          {officials[officialId].full_name}
                        </span>
                      </>
                    )}
                    {jurisdiction && !officialId && (
                      <>
                        {" "}
                        in{" "}
                        <span className="font-medium text-foreground">
                          {jurisdiction}
                        </span>
                      </>
                    )}
                  </>
                )}
              </TableCell>
            </TableRow>
          ) : (
            matches.map((row) => (
              <TableRow
                key={row.id}
                className="transition-colors hover:bg-muted/40"
              >
                <TableCell>{jurisdictionMap[row.jurisdiction_id]}</TableCell>
                <TableCell>{officials[row.official_id]?.full_name}</TableCell>
                <TableCell className="text-muted-foreground">
                  {row.year}
                </TableCell>
                <TableCell className="truncate">
                  {row.matched_interest}
                </TableCell>
                <TableCell>
                  {row.pdf_url ? (
                    <a
                      href={row.pdf_url}
                      className="truncate text-primary underline-offset-4 hover:underline"
                    >
                      {row.pdf_url}
                    </a>
                  ) : (
                    <span className="text-muted-foreground">—</span>
                  )}
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
                    onConfirm={onDeleteMatch}
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
