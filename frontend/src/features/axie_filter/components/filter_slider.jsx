import "react"
import { NumberInput } from "./number_input"
import * as Slider from "@radix-ui/react-slider"


export function FilterSlider({title, min, max, numberInput=true, range, setRange}) {
    return (
        <div className="mx-2">
            <h3 className="text-lg font-medium">{title}</h3>

            <Slider.Root
                className="relative flex items-center select-none touch-none w-full h-6"
                min={min}
                max={max}
                step={1}
                minStepsBetweenThumbs={0}
                value={range}
                onValueChange={(newRange) => {
                    const [newMin, newMax] = newRange;
                    
                    if (newMin !== range[0] && newMin <= range[1]) {
                        setRange([newMin, range[1]])
                    }

                    if (newMax !== range[1] && newMax >= range[0]) {
                        setRange([range[0], newMax])
                    }
                }}
            >
                <Slider.Track className="bg-gray-300 relative grow rounded-full h-1">
                    <Slider.Range className="absolute bg-black rounded-full h-full" />
                </Slider.Track>
                <Slider.Thumb
                    className="block w-4 h-4 bg-white border-2 border-black rounded-full shadow hover:bg-blue-100 focus:outline-none"
                    aria-label="Minimum"
                />
                <Slider.Thumb
                    className="block w-4 h-4 bg-white border-2 border-black rounded-full shadow hover:bg-blue-100 focus:outline-none"
                    aria-label="Maximum"
                />
            </Slider.Root>
            {numberInput && (
                <div className="flex items-center columns-3 justify-between text-sm text-gray-600">
                <NumberInput
                    value={range[0]}
                    onChange={(newMin) => setRange([newMin, range[1]])}
                    min={min}
                    max={range[1]}
                />
                <p className="text-2xl mx-4">-</p>
                <NumberInput
                    value={range[1]}
                    onChange={(newMax) => setRange([range[0], newMax])}
                    min={range[0]}
                    max={max}
                />
            </div>
            )}
        </div>
    )
}