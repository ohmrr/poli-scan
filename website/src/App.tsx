import { useState, useEffect, useMemo } from "react"
import { ConflictTable } from "./components/ConflictTable"
import { JurisdictionDropdown } from "./components/JurisdictionDropdown"
import { OfficialDropdown } from "./components/OfficialDropdown"
import { YearDropdown } from "./components/YearDropdown"
import { Separator } from "@/components/ui/separator"
import { ModeToggle } from "./components/mode-toggle"
import type { Jurisdiction } from "./types/jurisdiction"
import type { Official } from "./types/official"
import type { Match } from "./types/match"
import { getJurisdictions } from "@/services/jurisdiction"
import { getMatches, deleteMatch } from "@/services/match"
import { getOfficialById } from "@/services/official"
import { ConfidenceSlider } from "./components/ConfidenceSlider"
import { ExportButton } from "./components/ExportButton"
import { EmailReportButton } from "./components/EmailReportButton"

const currentYear = new Date().getFullYear()
const years = [...Array(10)].map((_, i) => currentYear - i)

export function App() {
  const [jurisdictions, setJurisdictions] = useState<Jurisdiction[]>([])
  const [matches, setMatches] = useState<Match[]>([])
  const [officials, setOfficials] = useState<Record<number, Official>>({})
  const [jurisdiction, setJurisdiction] = useState("")
  const [officialId, setOfficialId] = useState<number | null>(null)
  const [startYear, setStartYear] = useState<number | null>(null)
  const [endYear, setEndYear] = useState<number | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [minConfidence, setMinConfidence] = useState(0)

  const startYearOptions =
    endYear === null ? years : years.filter((year) => year <= endYear)

  const endYearOptions =
    startYear === null ? years : years.filter((year) => year >= startYear)

  const subject = officialId
    ? (officials[officialId]?.full_name ?? "selected official")
    : "all officials"

  const period =
    startYear || endYear
      ? `from ${startYear ?? "the beginning"} to ${endYear ?? "present"}`
      : "across all years"

  useEffect(() => {
    Promise.all([getJurisdictions(), getMatches()])
      .then(([j, m]) => {
        setJurisdictions(j)
        setMatches(m)
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!matches.length) return

    const missingIds = [...new Set(matches.map((m) => m.official_id))].filter(
      (id) => !officials[id]
    )
    if (!missingIds.length) return

    Promise.all(missingIds.map((id) => getOfficialById(id)))
      .then((data) => {
        setOfficials((prev) => {
          const next = { ...prev }
          data.forEach((o) => (next[o.id] = o))
          return next
        })
      })
      .catch((err) => console.error(err))
  }, [matches])

  const filteredMatches = useMemo(
    () =>
      matches.filter((row) => {
        if (officialId && row.official_id !== officialId) return false
        if (startYear && row.year < startYear) return false
        if (endYear && row.year > endYear) return false
        if (row.confidence < minConfidence) return false
        return true
      }),
    [matches, officialId, startYear, endYear, minConfidence]
  )

  const handleDeleteMatch = async (matchId: number) => {
    await deleteMatch(matchId)
    setMatches((prev) => prev.filter((m) => m.id !== matchId))
  }

  return (
    <div className="flex min-h-screen w-full bg-background text-foreground">
      <aside className="flex w-64 flex-col border-r border-border bg-card">
        <div className="flex flex-col gap-1 border-b border-border px-6 py-5">
          <span className="text-xs font-semibold tracking-widest text-muted-foreground uppercase">
            Dashboard
          </span>
          <h2 className="text-2xl font-bold tracking-tight text-card-foreground">
            PoliScan
          </h2>
        </div>

        <div className="flex flex-1 flex-col gap-6 overflow-y-auto px-6 py-6">
          <div className="flex flex-col gap-4">
            <p className="text-xs font-semibold tracking-widest text-muted-foreground uppercase">
              Search
            </p>

            <JurisdictionDropdown
              jurisdictions={jurisdictions}
              selectedSlug={jurisdiction}
              onSelect={(val) => {
                setJurisdiction(val)
                setOfficialId(null)
              }}
              loading={loading}
            />

            <OfficialDropdown
              officials={officials}
              selectedId={officialId}
              onSelect={(val) => setOfficialId(val)}
            />
          </div>

          <Separator />

          <div className="flex flex-col gap-4">
            <p className="text-xs font-semibold tracking-widest text-muted-foreground uppercase">
              Filters
            </p>

            <YearDropdown
              years={startYearOptions}
              label="Start Year"
              value={startYear !== null ? startYear.toString() : undefined}
              onChange={(val) =>
                setStartYear(val === "CLEAR" ? null : Number(val))
              }
            />

            <YearDropdown
              years={endYearOptions}
              label="End Year"
              value={endYear !== null ? endYear.toString() : undefined}
              onChange={(val) =>
                setEndYear(val === "CLEAR" ? null : Number(val))
              }
            />

            <ConfidenceSlider
              value={minConfidence}
              onChange={setMinConfidence}
            />
          </div>

          <Separator />

          <div className="flex flex-col gap-4">
            <p className="text-xs font-semibold tracking-widest text-muted-foreground uppercase">
              Export
            </p>

            <ExportButton
              matches={filteredMatches}
              officials={officials}
              jurisdictions={jurisdictions}
            />

            <EmailReportButton
              matches={filteredMatches}
              officials={officials}
              jurisdictions={jurisdictions}
            />
          </div>
        </div>

        <div className="flex flex-col gap-2 border-t border-border px-6 py-4 text-center">
          <p className="text-xs text-muted-foreground">
            Data sourced from public disclosures.
          </p>
          <a
            href="https://www.fppc.ca.gov/"
            className="text-xs font-medium text-primary underline-offset-4 hover:underline"
          >
            &copy; {new Date().getFullYear()} PoliScan | FPPC
          </a>

          <div className="justify-center">
            <ModeToggle />
          </div>
        </div>
      </aside>

      <div className="flex flex-1 flex-col bg-background">
        <header className="flex items-center border-b border-border bg-card px-8 py-5">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-card-foreground">
              Conflict of Interest Reports
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Reviewing disclosures for{" "}
              <span className="font-medium text-foreground">{subject}</span>
              {jurisdiction && (
                <>
                  {" "}
                  in{" "}
                  <span className="font-medium text-foreground">
                    {jurisdiction}
                  </span>
                </>
              )}{" "}
              {period}
            </p>
          </div>
        </header>

        <main className="flex-1 overflow-auto px-8 py-6">
          <ConflictTable
            matches={filteredMatches}
            officials={officials}
            jurisdictions={jurisdictions}
            jurisdiction={jurisdiction}
            officialId={officialId ?? undefined}
            startYear={startYear ?? undefined}
            endYear={endYear ?? undefined}
            loading={loading}
            onDeleteMatch={handleDeleteMatch}
            minConfidence={minConfidence}
          />
        </main>
      </div>
    </div>
  )
}

export default App
