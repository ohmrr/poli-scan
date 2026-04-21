import { Layout } from "./layout";
import { ConflictTable } from "./components/ConflictTable";
import { useState } from "react";
import { JurisdictionDropdown } from "./components/JurisdictionDropdown";
import { YearDropdown } from "./components/YearDropdown";

export function App() {
  //selected county
  const [jurisdiction, setJurisdiction] = useState("sonoma-county");

  //current year
  const [year] = useState(2019);

  //start year
  const [startYear, setStartYear] = useState("2019");

  //end year
  const [endYear, setEndYear] = useState("2023");

  return (
    <Layout>
      <div className="flex min-h-screen w-full">
        
        {/* left side bar */}
        <div className="w-64 border-r border-gray-300 p-6 flex flex-col gap-6">
          <h2 className="text-2xl font-bold">PoliScan</h2>

          {/* county dropdown */}
          <JurisdictionDropdown
            value={jurisdiction}
            onChange={setJurisdiction}
          />

          {/* move down */}
          <div className="flex flex-col gap-6 mt-20">

          {/* headerfilter}*/}
          <div className="mt-4">
            <h3 className="text-lg font-semibold border-b border-gray-400 pb-1">
              Filters
              </h3>
          </div>

          {/* start year dropdown */}
          <YearDropdown
            label="Start Year"
            value={startYear}
            onChange={setStartYear}
          />

          {/* end year dropdown */}
          <YearDropdown
            label="End Year"
            value={endYear}
            onChange={setEndYear}
          />
        </div>
        </div>

        <div className="flex-1 flex flex-col items-center gap-y-10 py-5">
          <h1 className="text-5xl font-bold">PoliScan</h1>

          {/* conflict table */}
          <ConflictTable jurisdiction={jurisdiction} year={year} />
        </div>

      </div>
    </Layout>
  );
}

export default App;
