import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface Props {
  label: string
  value: string
  onChange: (value: string) => void
}

// Grab current year, and push 10 previous years into array
const currentYear = new Date().getFullYear()
const years = [...Array(10)].map((_, i) => (currentYear - i).toString())

export function YearDropdown({ label, value, onChange }: Props) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium">{label}</label>

      <Select value={value} onValueChange={onChange}>
        <SelectTrigger className="w-55">
          <SelectValue placeholder="Select year" />
        </SelectTrigger>

        <SelectContent>
          {years.map((year) => (
            <SelectItem key={year} value={year}>
              {year}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
