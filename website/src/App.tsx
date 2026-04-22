import { useState } from "react"
import { ConflictTable } from "./components/ConflictTable"
import { JurisdictionDropdown } from "./components/JurisdictionDropdown"
import { YearDropdown } from "./components/YearDropdown"
import { Separator } from "@/components/ui/separator"

export function App() {
  const [jurisdiction, setJurisdiction] = useState("sonoma-county")
  const [startYear, setStartYear] = useState("2019")
  const [endYear, setEndYear] = useState("2023")

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
              label="Start Year"
              value={startYear}
              onChange={setStartYear}
            />
            <YearDropdown
              label="End Year"
              value={endYear}
              onChange={setEndYear}
            />
          </div>
        </div>

        <div className="flex flex-col gap-2 border-t border-border px-6 py-4">
          <p className="text-xs text-muted-foreground">
            Data sourced from public disclosures.
          </p>
          <a
            href="https://www.fppc.ca.gov/"
            className="text-xs font-medium text-primary underline-offset-4 hover:underline"
          >
            &copy; {new Date().getFullYear()} PoliScan | FPPC
          </a>
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
                {jurisdiction}
              </span>{" "}
              from{" "}
              <span className="font-medium text-foreground">{startYear}</span>{" "}
              to <span className="font-medium text-foreground">{endYear}</span>
            </p>
          </div>
        </header>

        <main className="flex-1 overflow-auto px-8 py-6">
          <ConflictTable
            jurisdiction={jurisdiction}
            startYear={Number(startYear)}
            endYear={Number(endYear)}
          />
        </main>
      </div>
    </div>
  )
}

export default App
