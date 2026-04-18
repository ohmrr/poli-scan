import { Layout } from "./layout"
import { ConflictTable } from "./components/ConflictTable"
import { useState } from "react"

export function App() {
  const [jurisdiction, setJurisdiction] = useState("Sonoma County")
  const [year, setYear] = useState(2019)

  return (
    <Layout>
      <div className="flex w-full max-w-5xl flex-col items-center gap-y-10 py-5">
        <h1 className="text-5xl font-bold">PoliScan</h1>

        <ConflictTable jurisdiction={jurisdiction} year={year} />
      </div>
    </Layout>
  )
}

export default App
