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

export function YearDropdown({
  years,
  label,
  value,
  onChange,
}: YearDropdownProps) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium">{label}</label>

      <Select key={value ?? "empty"} value={value} onValueChange={onChange}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Select year" />
        </SelectTrigger>

        <SelectContent>
          <SelectItem value="CLEAR">&nbsp;</SelectItem>

          {years.map((year) => (
            <SelectItem key={year} value={year.toString()}>
              {year}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
