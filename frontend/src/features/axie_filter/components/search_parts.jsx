import "react"
import { useState, useRef } from "react"
import { SelectedFilter } from "./selected_filter"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Popover,
  PopoverContent,
  PopoverAnchor,
} from "@/components/ui/popover"


const partNameButton = "w-14 h-6 text-xs bg-white text-black border-1 border-grey hover:bg-white hover:border-black"
const partStageButton = "w-10 h-4 border-1 bg-white text-black border-grey hover:bg-white hover:border-black"


export function SearchParts({selectedParts, onSelectPart, onUnselectPart, onClearParts, parts}) {
    const [inputValue, setInputValue] = useState("")
    const [isInputFocus, setIsInputFocus] = useState(false)

    const inputRef = useRef(null)

    const filteredParts = Object.keys(parts).sort().filter(
        (part) =>
            part.toLowerCase().startsWith(inputValue.toLowerCase()) &&
            parts[part]["partsIds"].length > 0
    )

    const handleSelectPart = (partName, partType, axieParts, action) => {
        if (inputRef.current) {
            inputRef.current.focus()
        }

        onSelectPart(partName, partType, axieParts, action)
    }

    return (
        <div className="mx-2">
            <div className="flex pb-1">
                <h3 className="text-lg font-medium">Parts</h3>
                <Button
                    size="sm"
                    variant="outline"
                    className="ml-auto w-20 h-7 hover:border-black"
                    onClick={onClearParts}
                >
                    Clear Parts
                </Button>
            </div>

            <div className="">
                <Popover open={isInputFocus}>
                    <PopoverAnchor asChild>
                        <Input
                            ref={inputRef}
                            placeholder="Search parts..."
                            onFocus={() => setIsInputFocus(true)}
                            // onBlur={() => setIsInputFocus(false)}
                            onChange={(e) => {setInputValue(e.target.value)}}
                            className = "focus-visible:ring-0 focus-visible:ring-offset-0 focus:outline-none"
                        />
                    </PopoverAnchor>
                    <PopoverContent
                        tabIndex={0}
                        onOpenAutoFocus={(e) => e.preventDefault()}
                        onPointerDownOutside={(e) => {
                            const target = e.target
                            if (inputRef.current && inputRef.current.contains(target)) {
                                e.preventDefault
                            } else {
                                setIsInputFocus(false)
                            }
                        }}
                        onWheel={(e) => e.stopPropagation()}
                        onTouchMove={(e) => e.stopPropagation()}
                        className="w-full min-w-[var(--radix-popover-trigger-width)] max-h-90 overflow-y-auto"
                    >
                        <div>
                            {
                                filteredParts.length === 0 ? (
                                    <div className="bg-gray-100 p-2 rounded-xl flex">
                                        <p className="mx-auto">Parts not found.</p>
                                    </div>
                                ) : (
                                    filteredParts.map((part) => (
                                        <div className="m-2 bg-gray-100 p-2 rounded-xl mb-4" key={part}>
                                            <div className="flex">
                                                <p className="font-bold">{part}</p>
                                                <div className="ml-auto gap-2 flex">
                                                    <Button
                                                        className={partNameButton}
                                                        size="icon"
                                                        onClick={() => handleSelectPart(part, parts[part]["type"], parts[part]["partsIds"], "include")}
                                                    >
                                                        Include
                                                    </Button>
                                                    <Button
                                                        className={partNameButton}
                                                        size="icon"
                                                        onClick={() => handleSelectPart(part, parts[part]["type"], parts[part]["partsIds"], "exclude")}
                                                    >
                                                        Exclude
                                                    </Button>
                                                </div>
                                            </div>
                                            {
                                                parts[part]["partsIds"].map((item) => {
                                                    return (
                                                        <div className="flex items-center" key={item.id}>
                                                            <p className="text-sm">Stage {item.stage}</p>
                                                                <div className="ml-auto gap-2 flex">
                                                                <Button
                                                                    className={partStageButton}
                                                                    size="icon"
                                                                    onClick={() => handleSelectPart(part, parts[part]["type"], [item], "include")}
                                                                >
                                                                    +
                                                                </Button>
                                                                <Button
                                                                    className={partStageButton}
                                                                    size="icon"
                                                                    onClick={() => handleSelectPart(part, parts[part]["type"], [item], "exclude")}
                                                                >
                                                                    -
                                                                </Button>
                                                            </div>
                                                        </div>
                                                    )
                                                })
                                            }
                                        </div>
                                    ))
                                )
                            }
                        </div>
                    </PopoverContent>
                </Popover>
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
                {
                    Object.keys(selectedParts).map((selectedPart) => {
                        return (
                            <SelectedFilter
                                key={selectedPart}
                                text={selectedPart}
                                action={selectedParts[selectedPart]["action"]}
                                removeFilter={() => onUnselectPart(selectedPart, selectedParts[selectedPart])}
                            />
                        )
                    })
                }
            </div>
        </div>
    )
}