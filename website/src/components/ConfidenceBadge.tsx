import { Badge } from "./ui/badge"

export function ConfidenceBadge({ value }: { value: number }) {
  const variant =
    value >= 90 ? "destructive" : value >= 70 ? "secondary" : "outline"
  return (
    <Badge variant={variant} className="w-12 justify-center">
      {value}%
    </Badge>
  )
}
