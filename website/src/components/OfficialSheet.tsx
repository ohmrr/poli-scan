import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet"
import { Separator } from "@/components/ui/separator"
import type { Official } from "@/types/official"

interface OfficialSheetProps {
  official: Official | null
  open: boolean
  onClose: () => void
}

export function OfficialSheet({ official, open, onClose }: OfficialSheetProps) {
  if (!official) return null

  const holdingsByYear = official.holdings.reduce<Record<string, string[]>>(
    (acc, h) => {
      const key = h.year !== null ? String(h.year) : "Unknown Year"
      if (!acc[key]) acc[key] = []
      acc[key].push(h.entity_name)
      return acc
    },
    {}
  )

  const sortedYears = Object.keys(holdingsByYear).sort((a, b) => {
    if (a === "Unknown Year") return 1
    if (b === "Unknown Year") return -1
    return Number(b) - Number(a)
  })

  return (
    <Sheet open={open} onOpenChange={(val) => !val && onClose()}>
      <SheetContent className="w-110 overflow-y-auto p-0 sm:max-w-110">
        <div className="px-8 pt-8 pb-6">
          <SheetHeader className="space-y-3">
            <SheetTitle className="text-xl font-bold">
              {official.full_name}
            </SheetTitle>
            <SheetDescription asChild>
              <div className="flex flex-col gap-1.5">
                {official.position && (
                  <span className="text-sm font-medium text-foreground">
                    {official.position}
                  </span>
                )}
                {official.agency && (
                  <span className="text-sm text-muted-foreground">
                    {official.agency}
                  </span>
                )}
                {official.email && (
                  <a
                    href={`mailto:${official.email}`}
                    className="w-fit text-sm text-primary underline-offset-4 hover:underline"
                  >
                    {official.email}
                  </a>
                )}
              </div>
            </SheetDescription>
          </SheetHeader>
        </div>

        <Separator />

        <div className="flex flex-col gap-6 px-8 py-6">
          <p className="text-xs font-semibold tracking-widest text-muted-foreground uppercase">
            Disclosed Holdings
          </p>

          {official.holdings.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No holdings on record.
            </p>
          ) : (
            sortedYears.map((year) => (
              <div key={year} className="flex flex-col gap-2">
                <p className="text-sm font-semibold text-foreground">{year}</p>
                <ul className="flex flex-col gap-1.5">
                  {holdingsByYear[year].map((name, i) => (
                    <li
                      key={i}
                      className="rounded-md border border-border bg-muted/30 px-4 py-2.5 text-sm text-foreground"
                    >
                      {name}
                    </li>
                  ))}
                </ul>
              </div>
            ))
          )}
        </div>
      </SheetContent>
    </Sheet>
  )
}
