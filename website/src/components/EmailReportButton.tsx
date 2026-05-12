import { Button } from "@/components/ui/button"
import { Mail } from "lucide-react"
import type { Match } from "@/types/match"
import type { Official } from "@/types/official"
import type { Jurisdiction } from "@/types/jurisdiction"
import { jurisdictionPrettyName } from "@/lib/utils"

interface EmailReportButtonProps {
  matches: Match[]
  officials: Record<number, Official>
  jurisdictions: Jurisdiction[]
}

export function EmailReportButton({
  matches,
  officials,
  jurisdictions,
}: EmailReportButtonProps) {
  const jurisdictionMap = Object.fromEntries(
    jurisdictions.map((j) => [j.id, jurisdictionPrettyName(j.slug)])
  )

  const handleOpen = () => {
    const html = `
  <html>
  <head>
    <style>
      body { font-family: sans-serif; padding: 2rem; color: #111; }
      h1 { font-size: 1.25rem; margin-bottom: 0.25rem; }
      p { color: #666; font-size: 0.875rem; margin-bottom: 1.5rem; }
      table { border-collapse: collapse; width: 100%; font-size: 0.8rem; }
      th { background: #f4f4f5; text-align: left; padding: 0.4rem 0.5rem; border: 1px solid #e4e4e7; font-weight: 600; white-space: nowrap; }
      td { padding: 0.4rem 0.5rem; border: 1px solid #e4e4e7; vertical-align: top; }
      td.wrap { word-break: break-word; min-width: 0; }
      td.nowrap { white-space: nowrap; }
      tr:nth-child(even) td { background: #fafafa; }
      .confidence { text-align: center; }
      .muted { color: #888; }
      footer { margin-top: 2rem; font-size: 0.75rem; color: #999; }
      .banner { background: #f4f4f5; border: 1px solid #e4e4e7; border-radius: 0.5rem; padding: 0.75rem 1rem; margin-bottom: 1.5rem; font-size: 0.875rem; color: #555; }
      .banner kbd { background: #fff; border: 1px solid #ccc; border-radius: 0.25rem; padding: 0.1rem 0.4rem; font-family: monospace; font-size: 0.8rem; }
    </style>
  </head>
  <body>
    <div class="banner">
      Press <kbd>Ctrl+A</kbd> then <kbd>Ctrl+C</kbd> to copy, then paste into your email.
    </div>
    <h1>PoliScan — Conflict of Interest Report</h1>
    <p>Generated: ${new Date().toLocaleString()} &nbsp;·&nbsp; ${matches.length} record${matches.length === 1 ? "" : "s"}</p>
    <table>
      <thead>
        <tr>
          <th>Jurisdiction</th>
          <th>Name</th>
          <th>Year</th>
          <th>Matched Holding</th>
          <th>Confidence</th>
        </tr>
      </thead>
      <tbody>
        ${matches
          .map(
            (row) => `
          <tr>
            <td class="nowrap">${jurisdictionMap[row.jurisdiction_id] ?? ""}</td>
            <td class="nowrap">${officials[row.official_id]?.full_name ?? ""}</td>
            <td class="muted nowrap">${row.year}</td>
            <td class="wrap">${row.matched_interest}</td>
            <td class="confidence nowrap">${row.confidence}%</td>
          </tr>
        `
          )
          .join("")}
      </tbody>
    </table>
    <footer>Data sourced from public disclosures &nbsp;·&nbsp; <a href="https://www.fppc.ca.gov/">FPPC</a></footer>
  </body>
  </html>
`
    const win = window.open("", "_blank")
    win?.document.write(html)
    win?.document.close()
  }

  return (
    <div className="flex flex-col gap-2">
      <Button
        variant="outline"
        className="w-full cursor-pointer"
        onClick={handleOpen}
        disabled={matches.length === 0}
      >
        <Mail className="mr-2 h-4 w-4" />
        Email Report
      </Button>
    </div>
  )
}
