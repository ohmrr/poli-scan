import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface Props {
  label: string;
  value: string;
  onChange: (value: string) => void;
}
//hardcoded years
const years = ["2018", "2019", "2020", "2021", "2022", "2023"];

export function YearDropdown({ label, value, onChange }: Props) {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium">{label}</label>

      <Select value={value} onValueChange={onChange}>
        <SelectTrigger className="w-[220px] bg-white text-black">
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
  );
}