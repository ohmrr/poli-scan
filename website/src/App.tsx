import { useState } from "react"
import { ConflictTable } from "./components/ConflictTable"
import { JurisdictionDropdown } from "./components/JurisdictionDropdown"
import { YearDropdown } from "./components/YearDropdown"
import { Separator } from "@/components/ui/separator"
import { ModeToggle } from "./components/mode-toggle"

const currentYear = new Date().getFullYear()
const years = [...Array(10)].map((_, i) => currentYear - i)

export function App() {
  const [jurisdiction, setJurisdiction] = useState("")
  const [startYear, setStartYear] = useState<number | null>(null)
  const [endYear, setEndYear] = useState<number | null>(null)

  const startYearOptions =
    endYear === null ? years : years.filter((year) => year <= endYear)

  const endYearOptions =
    startYear === null ? years : years.filter((year) => year >= startYear)

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
          <JurisdictionDropdown
            value={jurisdiction}
            onChange={setJurisdiction}
          />

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
              <span className="font-medium text-foreground">
                {jurisdiction || "all jurisdictions"}
              </span>{" "}
              {startYear || endYear ? (
                <>
                  from{" "}
                  <span className="font-medium text-foreground">
                    {startYear ?? "the beginning"}
                  </span>{" "}
                  to{" "}
                  <span className="font-medium text-foreground">
                    {endYear ?? "present"}
                  </span>
                </>
              ) : (
                "across all years"
              )}
            </p>
          </div>
        </header>

        <main className="flex-1 overflow-auto px-8 py-6">
          <ConflictTable
            jurisdiction={jurisdiction}
            startYear={startYear ?? undefined}
            endYear={endYear ?? undefined}
          />
        </main>
      </div>
    </div>
  )
}

export default App
