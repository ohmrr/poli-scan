import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"

interface ConflictTableProps {
  jurisdiction: string
  startYear: number
  endYear: number
}

// Placeholder rows — replace with real data fetch
const MOCK_DATA = [
  {
    id: 1,
    name: "Lynda Hopkins",
    year: 2019,
    matchedHolding: "LandPass Inc.",
    pdf: "form700_2019_hopkins.pdf",
    confidence: 98,
  },
  {
    id: 2,
    name: "James Carter",
    year: 2020,
    matchedHolding: "Redwood Ventures",
    pdf: "form700_2020_carter.pdf",
    confidence: 84,
  },
  {
    id: 3,
    name: "Maria Gonzalez",
    year: 2021,
    matchedHolding: "Pacific Development LLC",
    pdf: "form700_2021_gonzalez.pdf",
    confidence: 61,
  },
]

function ConfidenceBadge({ value }: { value: number }) {
  const variant =
    value >= 90 ? "destructive" : value >= 70 ? "secondary" : "outline"
  return <Badge variant={variant} className="w-12">{value}%</Badge>
}

export function ConflictTable({
  jurisdiction,
  startYear,
  endYear,
}: ConflictTableProps) {
  const filtered = MOCK_DATA.filter(
    (row) => row.year >= startYear && row.year <= endYear
  )

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
                  {row.name}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {row.year}
                </TableCell>
                <TableCell className="text-foreground">
                  {row.matchedHolding}
                </TableCell>
                <TableCell>
                  <a
                    href={`/pdfs/${row.pdf}`}
                    className="text-sm text-primary underline-offset-4 hover:underline"
                  >
                    {row.pdf}
                  </a>
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
