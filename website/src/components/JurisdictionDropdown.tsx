import { useState } from "react"
import type { Jurisdiction } from "@/types/jurisdiction"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { jurisdictionPrettyName } from "@/lib/utils"

interface JurisdictionDropdownProps {
  jurisdictions: Jurisdiction[]
  selectedSlug: string
  onSelect: (slug: string) => void
  loading: boolean
}

export function JurisdictionDropdown({ jurisdictions, selectedSlug, onSelect, loading }: JurisdictionDropdownProps) {
  const [resetKey, setResetKey] = useState(0)

  const handleChange = (val: string) => {
    if (val === "CLEAR") {
      setResetKey((k) => k + 1)
    }
    onSelect(val === "CLEAR" ? "" : val)
  }

  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium">Jurisdiction</label>
      <Select
        key={selectedSlug === "" ? `reset-${resetKey}` : selectedSlug}
        value={selectedSlug || undefined}
        onValueChange={handleChange}
      >
        <SelectTrigger className="w-full cursor-pointer">
          <SelectValue placeholder={loading ? "Loading..." : "Select Jurisdiction"} />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="CLEAR" className="cursor-pointer text-muted-foreground">
            Reset
          </SelectItem>
          {jurisdictions.map((j) => (
            <SelectItem key={j.id} value={j.slug} className="cursor-pointer">
              {jurisdictionPrettyName(j.display_name || j.slug)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}