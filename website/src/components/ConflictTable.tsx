import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { getMatches, deleteMatch } from "@/services/match"
import { getOfficialById } from "@/services/official"
import type { Match } from "@/types/match"
import type { Official } from "@/types/official"
import { useEffect, useState } from "react"
import { Tooltip, TooltipContent, TooltipTrigger } from "./ui/tooltip"
import { Trash2 } from "lucide-react"

interface ConflictTableProps {
  jurisdiction: string
  startYear?: number
  endYear?: number
}

function ConfidenceBadge({ value }: { value: number }) {
  const variant =
    value >= 90 ? "destructive" : value >= 70 ? "secondary" : "outline"
  return (
    <Badge variant={variant} className="w-12 justify-center">
      {value}%
    </Badge>
  )
}

interface DeleteMatchDialogProps {
  matchId: number
  officialName?: string
  onConfirm: (matchId: number) => Promise<void>
}

function DeleteMatchDialog({
  matchId,
  officialName,
  onConfirm,
}: DeleteMatchDialogProps) {
  const [loading, setLoading] = useState(false)

  const handleConfirm = async () => {
    setLoading(true)
    try {
      await onConfirm(matchId)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <button className="cursor-pointer text-muted-foreground transition-colors hover:text-destructive">
          <Trash2 className="h-4 w-4" />
        </button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete this record?</AlertDialogTitle>
          <AlertDialogDescription>
            {officialName ? (
              <>
                This will permanently delete the conflict record for{" "}
                <span className="font-medium text-foreground">
                  {officialName}
                </span>
                . This action cannot be undone.
              </>
            ) : (
              <>
                This will permanently delete the record. This action cannot be
                undone.
              </>
            )}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={loading} className="cursor-pointer">
            Cancel
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={handleConfirm}
            disabled={loading}
            className="text-destructive-foreground cursor-pointer bg-destructive hover:bg-destructive/90"
          >
            {loading ? "Deleting..." : "Delete"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}

export function ConflictTable({
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
            <TableHead className="w-40 font-semibold text-foreground">
              Name
            </TableHead>
            <TableHead className="w-20 font-semibold text-foreground">
              Year
            </TableHead>
            <TableHead className="font-semibold text-foreground">
              Matched Holding
            </TableHead>
            <TableHead className="w-45 font-semibold text-foreground">
              PDF
            </TableHead>
            <TableHead className="w-32 text-center font-semibold text-foreground">
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
                <TableCell className="font-medium text-foreground">
                  {officials[row.official_id]?.full_name}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {row.year}
                </TableCell>
                <TableCell className="max-w-xs truncate">
                  <Tooltip>
                    <TooltipTrigger className="block truncate">
                      {row.matched_interest}
                    </TooltipTrigger>
                    <TooltipContent align="start">
                      {row.matched_interest}
                    </TooltipContent>
                  </Tooltip>
                </TableCell>
                <TableCell className="max-w-45">
                  {row.pdf_url ? (
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <a
                          href={row.pdf_url}
                          className="block truncate text-sm text-primary underline-offset-4 hover:underline"
                        >
                          {row.pdf_url}
                        </a>
                      </TooltipTrigger>
                      <TooltipContent align="start">
                        {row.pdf_url}
                      </TooltipContent>
                    </Tooltip>
                  ) : (
                    <span className="text-sm text-muted-foreground">—</span>
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
