import "react"
import { useState } from "react"
import { Timeframe } from "./timeframe"
import { SearchParts } from "./search_parts"
import { SelectClass } from "./select_class"
import { FilterSlider } from "./filter_slider"
import { SelectCollection } from "./select_collection"
import { SelectedFilter } from "./selected_filter"
import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
  } from "@/components/ui/dialog"
  import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"


export function FilterSection({
    timeframe, setTimeframe,
    parts, setParts,
    selectedParts, setSelectedParts,
    selectedClasses, setSelectedClasses,
    levelRange, setLevelRange,
    breedCountRange, setBreedCountRange,
    evolvedPartsRange, setEvolvedPartsRange,
    selectedCollections, setSelectedCollections,
    sortBy, setSortBy,
    clearParts, clearAll,
}) {
    const onSelectPart = (partName, partType, axieParts, action) => {
        if (partName && partType && axieParts && action) {
            for (let p = 0; p < axieParts.length; p++) {
                const displayName = `${partName}-${axieParts[p]["stage"]}`

                setSelectedParts((prev) => {
                    if (!prev.hasOwnProperty(displayName)) {
                        return (
                            {
                                ...prev,
                                [displayName]: {
                                    "type": partType,
                                    ...axieParts[p],
                                    "action": action
                                }
                            }
                        )
                    }
                    return prev
                })

                // Remove the part from the parts[partName][partsIds] list
                setParts((prev) => {
                    return (
                        {
                            ...prev,
                            [partName]: {
                                ...prev[partName],
                                "partsIds": prev[partName]["partsIds"].filter((item) => item.id !== axieParts[p]["id"])
                            }
                        }
                    )
                })
            }
        }
    }

    const onUnselectPart = (displayName, partInfo) => {
        if (displayName && partInfo) {
            const partName = displayName.split("-")[0]
            const {partAction, ...partWithoutAction} = partInfo

            // Remove the part from the selectedParts
            setSelectedParts((prev) => {
                if (prev.hasOwnProperty(displayName)) {
                    return Object.fromEntries(
                        Object.entries(prev).filter(([p]) => p !== displayName)
                    )
                }
            })

            // Add the part to the parts[partName][partsIds] list
            setParts((prev) => {
                return (
                    {
                        ...prev,
                        [partName]: {
                            ...prev[partName],
                            "partsIds": [...prev[partName]["partsIds"], partWithoutAction].sort((a, b) => a.stage - b.stage)
                        }
                    }
                )
            })
        }
    }

    return (
        <div className="flex flex-wrap items-center gap-2">
            <Dialog>
                <form>
                    <DialogTrigger asChild>
                    <Button variant="outline">Filter</Button>
                    </DialogTrigger>
                    <DialogContent
                        className="sm:max-w-[425px] max-h-[90vh] flex flex-col"
                    >
                        <DialogHeader className="text-left">
                            <DialogTitle className="text-xl ml-2" autoFocus tabIndex={0}>Filter</DialogTitle>
                        </DialogHeader>
                        <DialogDescription className="hidden"/>
                        <div className="grid gap-4 flex-1 overflow-y-auto">
                            <Timeframe value={timeframe} onChange={setTimeframe}/>
                            <SearchParts
                                selectedParts={selectedParts}
                                setSelectedParts={setSelectedParts}
                                onSelectPart={(partName, partType, axieParts, action) => onSelectPart(partName, partType, axieParts, action)}
                                onUnselectPart={(displayName, partInfo) => onUnselectPart(displayName, partInfo)}
                                onClearParts={clearParts}
                                parts={parts}
                                setParts={setParts}
                            />
                            <SelectClass selectedClasses={selectedClasses} setSelectedClasses={setSelectedClasses}/>
                            <FilterSlider
                                title="Level"
                                min={1}
                                max={60}
                                range={levelRange}
                                setRange={setLevelRange}
                            />
                            <FilterSlider
                                title="Breed Count"
                                min={0}
                                max={7}
                                range={breedCountRange}
                                setRange={setBreedCountRange}
                            />
                            <FilterSlider
                                title="Evolved Parts Count"
                                min={0}
                                max={6}
                                range={evolvedPartsRange}
                                setRange={setEvolvedPartsRange}
                            />
                            <SelectCollection collections={selectedCollections} setCollections={setSelectedCollections}/>
                        </div>
                        <DialogFooter>
                            <Button
                                variant="outline"
                                className="hover:border-black"
                                onClick={clearAll}
                            >
                                Clear all
                            </Button>
                            <DialogClose asChild>
                                <Button variant="outline" className="hover:border-black">Apply</Button>
                            </DialogClose>
                        </DialogFooter>
                    </DialogContent>
                </form>
            </Dialog>

            {/* Selected Parts */}
            {Object.keys(selectedParts).map((selectedPart) => {
                return (
                    <SelectedFilter
                        key={selectedPart}
                        text={selectedPart}
                        action={selectedParts[selectedPart]["action"]}
                        removeFilter={() => onUnselectPart(selectedPart, selectedParts[selectedPart])}
                    />
                )
            })}

            {/* Selected Classes */}
            {selectedClasses.map((axieClass) => {
                return (
                    <SelectedFilter
                        key={axieClass}
                        text={axieClass}
                        removeFilter={() => setSelectedClasses(selectedClasses.filter((c) => c !== axieClass))}
                    />
                )
            })}
            
            {/* Selected Level Range */}
            {
                // Does not display if the level range is [1,60].
                (levelRange[0] !== 1 || levelRange[1] !== 60) && (
                <SelectedFilter
                    // If the range is [50,50] the text will be Level 50, else Level 50-55 if the range is [50,55].
                    text={`Level ${levelRange[0]}${levelRange[0] !== levelRange[1] ? `-${levelRange[1]}`: ""}`}
                    removeFilter={() => setLevelRange([1, 60])}
                />
                )
            }

            {/* Selected Breed Count Range */}
            {
                // Does not display if the breed count range is [0,7].
                (breedCountRange[0] !== 0 || breedCountRange[1] !== 7) && (
                <SelectedFilter
                    // If the range is [2,2] the text will be Breed 2, else Breed 2-5 if the range is [2,5].
                    text={`Breed ${breedCountRange[0]}${breedCountRange[0] !== breedCountRange[1] ? `-${breedCountRange[1]}`: ""}`}
                    removeFilter={() => setBreedCountRange([0, 7])}
                />
                )
            }

            {/* Selected Evolved Parts Range */}
            {
                // Does not display if the evolved parts range is [0,6].
                (evolvedPartsRange[0] !== 0 || evolvedPartsRange[1] !== 6) && (
                <SelectedFilter
                    // If the range is [2,2] the text will be Evolved 2, else Evolved 2-5 if the range is [2,5].
                    text={`Evolved ${evolvedPartsRange[0]}${evolvedPartsRange[0] !== evolvedPartsRange[1] ? `-${evolvedPartsRange[1]}`: ""}`}
                    removeFilter={() => setEvolvedPartsRange([0, 6])}
                />
                )
            }

            {/* Selected Collections */}
            {Object.keys(selectedCollections).map((collection) => {
                return (
                    <SelectedFilter
                        key={collection}
                        text={
                            selectedCollections[collection]["numParts"]
                                ? `${collection} ${selectedCollections[collection]["numParts"][0]}-${selectedCollections[collection]["numParts"][1]}`
                                : `${collection}`
                        }
                        removeFilter={() => {
                            setSelectedCollections((prev) => {
                                if (prev.hasOwnProperty(collection)) {
                                    return Object.fromEntries(
                                        Object.entries(prev).filter(([p]) => p !== collection)
                                    )
                                }
                            })
                        }
                        }
                    />
                )
            })}

            <Button
                variant="outline"
                onClick={clearAll}
            >
                Clear All
            </Button>
            <Select
                value={sortBy}
                onValueChange={(e) => setSortBy(e)}
            >
                <SelectTrigger className="font-medium">
                    <SelectValue/>
                </SelectTrigger>
                <SelectContent className="font-medium">
                    <SelectGroup>
                    <SelectItem value={"latest"}>Latest</SelectItem>
                    <SelectItem value={"lowest_price"}>Lowest Price</SelectItem>
                    <SelectItem value={"highest_price"}>Highest Price</SelectItem>
                    <SelectItem value={"lowest_level"}>Lowest Level</SelectItem>
                    <SelectItem value={"highest_level"}>Highest Level</SelectItem>
                    </SelectGroup>
                </SelectContent>
            </Select>
        </div>
    )
}