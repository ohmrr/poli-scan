import { Button } from "@/components/ui/button"
import { Download } from "lucide-react"
import type { Match } from "@/types/match"
import type { Official } from "@/types/official"
import type { Jurisdiction } from "@/types/jurisdiction"
import { jurisdictionPrettyName } from "@/lib/utils"

interface ExportButtonProps {
  matches: Match[]
  officials: Record<number, Official>
  jurisdictions: Jurisdiction[]
}

export function ExportButton({
  matches,
  officials,
  jurisdictions,
}: ExportButtonProps) {
  const jurisdictionMap = Object.fromEntries(
    jurisdictions.map((j) => [j.id, jurisdictionPrettyName(j.slug)])
  )

  const handleExport = () => {
    const headers = [
      "Jurisdiction",
      "Name",
      "Year",
      "Matched Holding",
      "PDF URL",
      "Confidence",
      "Reason",
    ]

    const rows = matches.map((row) => [
      jurisdictionMap[row.jurisdiction_id] ?? "",
      officials[row.official_id]?.full_name ?? "",
      row.year,
      row.matched_interest,
      row.pdf_url ?? "",
      row.confidence,
      row.reason ?? "",
    ])

    const csv = [headers, ...rows]
      .map((row) =>
        row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(",")
      )
      .join("\n")

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = `poliscan-export-${new Date().toISOString().slice(0, 10)}.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <Button
      variant="outline"
      className="w-full cursor-pointer"
      onClick={handleExport}
      disabled={matches.length === 0}
    >
      <Download className="mr-2 h-4 w-4" />
      Export as CSV
    </Button>
  )
}
