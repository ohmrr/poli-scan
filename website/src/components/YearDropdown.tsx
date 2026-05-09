import { useState } from "react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface YearDropdownProps {
  years: number[]
  label: string
  value?: string
  onChange: (value: string) => void
}

export function YearDropdown({ years, label, value, onChange }: YearDropdownProps) {
  const [resetKey, setResetKey] = useState(0)

  const handleChange = (val: string) => {
    if (val === "CLEAR") {
      setResetKey((k) => k + 1)
    }
    onChange(val)
  }

  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium">{label}</label>
      <Select
        key={value === undefined ? `reset-${resetKey}` : value}
        value={value}
        onValueChange={handleChange}
      >
        <SelectTrigger className="w-full cursor-pointer">
          <SelectValue placeholder="Select year" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="CLEAR" className="cursor-pointer text-muted-foreground">
            Reset
          </SelectItem>
          {years.map((year) => (
            <SelectItem key={year} value={year.toString()} className="cursor-pointer">
              {year}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}