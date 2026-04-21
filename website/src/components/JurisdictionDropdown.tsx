import { useEffect, useState } from "react"

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export interface Jurisdiction {
  id: number
  slug: string
  display_name: string
}

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

  useEffect(() => {
    fetch("/api/jurisdictions/")
      .then((res) => res.json())
      .then((data) => {
        setJurisdictions(data)
      })
      .catch((err) => {
        console.error("Fetch error:", err)
      })
  }, [])

  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium">Select County</label>

      <Select value={value} onValueChange={onChange}>
        <SelectTrigger className="w-55">
          <SelectValue placeholder="Select County" />
        </SelectTrigger>

        <SelectContent>
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
