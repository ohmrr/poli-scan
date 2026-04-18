import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface ConflictTableProps {
  jurisdiction: string
  year: number
}

export function ConflictTable({ jurisdiction, year }: ConflictTableProps) {
  return (
    <Table>
      <TableCaption>
        A list of all conflict of interests found in {year} for {jurisdiction}.
      </TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead className="w-25">Name</TableHead>
          <TableHead>Year</TableHead>
          <TableHead>Matched Holding</TableHead>
          <TableHead>PDF</TableHead>
          <TableHead>Confidence (%)</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow>
          <TableCell className="font-medium">Lynda Hopkins</TableCell>
          <TableCell>2019</TableCell>
          <TableCell>LandPass</TableCell>
          <TableCell>Placeholder</TableCell>
          <TableCell>98%</TableCell>
        </TableRow>
      </TableBody>
    </Table>
  )
}
