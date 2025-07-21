import "react"
import { Button } from "@/components/ui/button"
import { classColorMap } from "../../../data/color_variants"


const axieClasses = [
    "Aquatic",
    "Beast",
    "Bird",
    "Bug",
    "Plant",
    "Reptile",
    "Mech",
    "Dawn",
    "Dusk"
]


export function SelectClass({selectedClasses, setSelectedClasses}) {
    const toggleSelected = (selectedClass) => {
        setSelectedClasses((prev) => 
            prev.includes(selectedClass)
                ? prev.filter((c) => c !== selectedClass)
                : [...prev, selectedClass]
        );
    };

    return (
        <div className="mx-2">
            <h3 className="text-lg font-medium">Class</h3>
            
            <div className="flex flex-wrap gap-2">
                {axieClasses.map((axieClass) => {
                    const isActive = selectedClasses.includes(axieClass)
                    return (
                        <Button
                            key={axieClass}
                            onClick={() => toggleSelected(axieClass)}
                            className={`
                                ${classColorMap[axieClass.toLowerCase()].bg}
                                ${classColorMap[axieClass.toLowerCase()].bgHover}
                                ${isActive ? 'ring-2  ring-black' : ''}
                            `}
                        >
                            {axieClass}
                        </Button>
                    )
                })}
            </div>
        </div>
    )
}