import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { useEffect, useState } from "react"
import type { Match } from "@/types/match"
import { getMatches } from "@/services/match"
import type { Official } from "@/types/official"
import { getOfficialById } from "@/services/official"

interface ConflictTableProps {
  jurisdiction: string
  startYear?: number
  endYear?: number
}

function ConfidenceBadge({ value }: { value: number }) {
  const variant =
    value >= 90 ? "destructive" : value >= 70 ? "secondary" : "outline"
  return (
    <Badge variant={variant} className="w-12">
      {value}%
    </Badge>
  )
}

export function ConflictTable({
  jurisdiction,
  startYear,
  endYear,
}: ConflictTableProps) {
  const [matches, setMatches] = useState<Match[]>([])
  const [officials, setOfficials] = useState<Record<number, Official>>({})

  useEffect(() => {
    getMatches()
      .then(setMatches)
      .catch((err) => console.error(err))
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
            <TableHead className="w-40 font-semibold text-foreground">
              Name
            </TableHead>
            <TableHead className="w-20 font-semibold text-foreground">
              Year
            </TableHead>
            <TableHead className="font-semibold text-foreground">
              Matched Holding
            </TableHead>
            <TableHead className="font-semibold text-foreground">PDF</TableHead>
            <TableHead className="w-32 font-semibold text-foreground">
              Confidence
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filtered.length === 0 ? (
            <TableRow>
              <TableCell
                colSpan={5}
                className="py-12 text-center text-muted-foreground"
              >
                No conflicts of interest found for{" "}
                <span className="font-medium text-foreground">
                  {jurisdiction}
                </span>{" "}
                between {startYear}-{endYear}.
              </TableCell>
            </TableRow>
          ) : (
            filtered.map((row) => (
              <TableRow
                key={row.id}
                className="transition-colors hover:bg-muted/40"
              >
                <TableCell className="font-medium text-foreground">
                  {officials[row.official_id]?.full_name}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {row.year}
                </TableCell>
                <TableCell className="text-foreground">
                  {row.matched_interest}
                </TableCell>
                <TableCell>
                  {row.pdf_url ? (
                    <a
                      href={row.pdf_url}
                      className="text-sm text-primary underline-offset-4 hover:underline"
                    >
                      {row.pdf_url}
                    </a>
                  ) : (
                    <p className="text-sm text-primary underline-offset-4 hover:underline"></p>
                  )}
                </TableCell>
                <TableCell>
                  <ConfidenceBadge value={row.confidence} />
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}
