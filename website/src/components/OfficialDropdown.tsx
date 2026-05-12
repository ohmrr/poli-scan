import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { Official } from "@/types/official"

interface OfficialDropdownProps {
  officials: Record<number, Official>
  selectedId: number | null
  onSelect: (id: number | null) => void
}

export function OfficialDropdown({
  officials,
  selectedId,
  onSelect,
}: OfficialDropdownProps) {
  const entries = Object.values(officials).sort((a, b) =>
    a.full_name.localeCompare(b.full_name)
  )

  const handleChange = (val: string) => {
    onSelect(val === "ALL" ? null : Number(val))
  }

  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium">Official</label>
      <Select
        value={selectedId !== null ? String(selectedId) : "ALL"}
        onValueChange={handleChange}
      >
        <SelectTrigger className="w-full cursor-pointer">
          <SelectValue placeholder="All officials" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem
            value="ALL"
            className="cursor-pointer text-muted-foreground"
          >
            All officials
          </SelectItem>
          {entries.map((official) => (
            <SelectItem
              key={official.id}
              value={String(official.id)}
              className="cursor-pointer"
            >
              {official.full_name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
