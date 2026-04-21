import { useState } from "react"
import { ConflictTable } from "./components/ConflictTable"
import { JurisdictionDropdown } from "./components/JurisdictionDropdown"
import { YearDropdown } from "./components/YearDropdown"
import { Layout } from "./layout"

export function App() {
  const [jurisdiction, setJurisdiction] = useState("sonoma-county")
  const [year] = useState(2019)

  const [startYear, setStartYear] = useState("2019")
  const [endYear, setEndYear] = useState("2023")

  return (
    <Layout>
      <div className="flex min-h-screen w-full">
        <div className="border-foreground-muted flex w-64 flex-col gap-6 border-r p-6">
          <h2 className="text-2xl font-bold">PoliScan</h2>

          <JurisdictionDropdown
            value={jurisdiction}
            onChange={setJurisdiction}
          />

          <div className="mt-20 flex flex-col gap-6">
            <div className="mt-4">
              <h3 className="border-b border-muted-foreground pb-1 text-lg font-semibold">
                Filters
              </h3>
            </div>

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

        <div className="flex flex-1 flex-col items-center gap-y-10 py-5">
          <h1 className="text-5xl font-bold">PoliScan</h1>
          <ConflictTable jurisdiction={jurisdiction} year={year} />
        </div>
      </div>
    </Layout>
  )
}

export default App
