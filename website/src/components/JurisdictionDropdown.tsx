import { useEffect, useState } from "react"
import type { Jurisdiction } from "@/types/jurisdiction"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { getJurisdictions } from "@/services/jurisdiction"

interface Props {
  value: string
  onChange: (slug: string) => void
}

function prettyName(name: string) {
  return name
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ")
}

export function JurisdictionDropdown({ value, onChange }: Props) {
  const [jurisdictions, setJurisdictions] = useState<Jurisdiction[]>([])
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    getJurisdictions()
      .then(setJurisdictions)
      .catch((err) => console.error(err))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium">Select County</label>

      <Select value={value} onValueChange={onChange}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder={loading ? "Loading..." : "Select County"} />
        </SelectTrigger>

        <SelectContent>
          {/* <SelectItem>&nbsp;</SelectItem> */}

          {jurisdictions.map((j) => (
            <SelectItem key={j.id} value={j.slug}>
              {prettyName(j.display_name || j.slug)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
