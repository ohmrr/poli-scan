import { Slider } from "@/components/ui/slider"

interface ConfidenceSliderProps {
    value: number
    onChange: (value: number) => void
}

export function ConfidenceSlider({ value, onChange }: ConfidenceSliderProps) {
    return (
        <div className="flex flex-col gap-3">
            <div className="flex items-center justify-between">
                <label className="text-sm font-medium">Min. Confidence</label>
                <span className="text-sm text-muted-foreground">{value}%</span>
            </div>
            <Slider
                min={0}
                max={100}
                step={5}
                value={[value]}
                onValueChange={([val]) => onChange(val)}
                className="cursor-pointer"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
                <span>0%</span>
                <span>100%</span>
            </div>
        </div>
    )
}