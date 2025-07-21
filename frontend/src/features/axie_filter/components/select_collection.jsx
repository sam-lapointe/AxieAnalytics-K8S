import "react"
import { useState } from "react"
import { Checkbox } from "@/components/ui/checkbox"
import { FilterSlider } from "./filter_slider"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"


const special_collections = {
    Mystic: {"isParts": true},
    Summer: {"isParts": true},
    Japan: {"isParts": true},
    Shiny: {"isParts": true},
    Xmas: {"isParts": true},
    Nightmare: {"isParts": true},
    "MEO Corp": {"isParts": false},
    "MEO Corp II": {"isParts": false},
    Origin: {"isParts": false},
    AgamoGenesis: {"isParts": false},
}

export function SelectCollection({collections, setCollections}) {
    const [isAnySelected, setIsAnySelected] = useState(collections.hasOwnProperty("Any Collection"))
    const [isNoneSelected, setIsNoneSelected] = useState(collections.hasOwnProperty("No Collection"))

    const handleCollectionSelection = (selectedCollection) => {
        setCollections((prev) => {
            if (prev.hasOwnProperty(selectedCollection)) {
                return Object.fromEntries(
                    Object.entries(prev).filter(([c]) => c !== selectedCollection)
                )
            } else {
                return special_collections[selectedCollection]["isParts"]
                    ? {...prev, [selectedCollection]: {"numParts": [1, 6]}}
                    : {...prev, [selectedCollection]: {}}
            }
        })
    }

    const handleCollectionParts = (selectedCollection, numParts) => {
        setCollections((prev) => {
            if (prev.hasOwnProperty(selectedCollection)) {
                return {
                    ...prev,
                    [selectedCollection]: {
                        ...prev[selectedCollection],
                        numParts
                    }
                }
            } else {
                return prev
            }
        })
    }

    return (
        <div className="mx-2">
            <h3 className="text-lg font-medium mb-2">Special Collection</h3>
            
            <div className="grid grid-cols-2 gap-3">
                <div className="flex items-center">
                    <Switch
                        checked={isAnySelected}
                        onCheckedChange={(checked) => {
                            setIsAnySelected(checked)
                            setIsNoneSelected(false)
                            if (checked) {
                                setCollections({"Any Collection": true})
                            } else {
                                setCollections({})
                            }
                        }}
                    />
                    <Label className="ml-2">Any Collection</Label>
                </div>
                <div className="flex">
                    <Switch
                        checked={isNoneSelected}
                        onCheckedChange={(checked) => {
                            setIsNoneSelected(checked)
                            setIsAnySelected(false)
                            if (checked) {
                                setCollections({"No Collection": true})
                            } else {
                                setCollections({})
                            }
                        }}
                    />
                    <Label className="ml-2">No Collection</Label>
                </div>
            </div>
            <h5 className="test-lg font-medium mt-2">Parts</h5>
            <div className="grid grid-cols-2 gap-3">
                {Object.keys(special_collections)
                    .filter((col) => special_collections[col]["isParts"])
                    .map((col) => {
                    const isSelected = collections.hasOwnProperty(col)

                    return (
                        <div className="flex flex-wrap items-center" key={col}>
                            <Checkbox
                                checked={isSelected}
                                onCheckedChange={() => handleCollectionSelection(col)}
                                disabled={isNoneSelected || isAnySelected}
                            />
                            <p className="ml-2">{col}</p>
                            {isSelected && special_collections[col]["isParts"] && (
                                <FilterSlider
                                    title=""
                                    min={1}
                                    max={6}
                                    range={collections[col]["numParts"]}
                                    setRange={(numParts) => handleCollectionParts(col, numParts)}
                                />
                            )}
                        </div>
                    )
                })}
            </div>
            <h5 className="test-lg font-medium mt-2">Titles</h5>
            <div className="grid grid-cols-2 gap-3">
                {Object.keys(special_collections)
                    .filter((col) => special_collections[col]["isParts"] === false)
                    .map((col) => {
                    const isSelected = collections.hasOwnProperty(col)

                    return (
                        <div className="flex flex-wrap items-center" key={col}>
                            <Checkbox
                                checked={isSelected}
                                onCheckedChange={() => handleCollectionSelection(col)}
                                disabled={isNoneSelected || isAnySelected}
                            />
                            <p className="ml-2">{col}</p>
                            {isSelected && special_collections[col]["isParts"] && (
                                <FilterSlider
                                    title=""
                                    min={1}
                                    max={6}
                                    range={collections[col]["numParts"]}
                                    setRange={(numParts) => handleCollectionParts(col, numParts)}
                                />
                            )}
                        </div>
                    )
                })}
            </div>
        </div>
    )
}