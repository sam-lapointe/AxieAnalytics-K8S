import "react"
import axios from "axios"
import { useRef, useState, useEffect } from "react"
import { Overview } from "../components/overview.jsx"
import { FilterSection } from "../features/axie_filter/components/filter_section.jsx"
import { ResultSection } from "../features/axie_sales/components/result_section.jsx"
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"


export function Axies() {
    const [timeframe, setTimeframe] = useState([1, "days"])
    const [parts, setParts] = useState({})
    const [selectedParts, setSelectedParts] = useState({})
    const [selectedClasses, setSelectedClasses] = useState([])
    const [levelRange, setLevelRange] = useState([1, 60])
    const [breedCountRange, setBreedCountRange] = useState([0, 7])
    const [evolvedPartsRange, setEvolvedPartsRange] = useState([0, 6])
    const [selectedCollections, setSelectedCollections] = useState({})
    const [sortBy, setSortBy] = useState("latest")
    const [overviewData, setOverviewData] = useState({
        "total_sales": 0,
        "total_volume_eth": 0,
        "avg_price_eth": 0,
        "chart": [{"sales": 0, "volume": 0, "avg_price_eth": 0}]
    })
    const [listData, setListData] = useState([])
    const [page, setPage] = useState(1)
    const [isLoading, setIsLoading] = useState({})
    const [error, setError] = useState(null)

    const debounceTimeout = useRef(null)
    const firstLoad = useRef(true) // To prevent initial fetch on mount
    const axiePartsOriginal = useRef({}) // Original parts data fetched from the backend and deep copied by parts

    const axiesPerPage = 60 // Number of axies per page


    useEffect(() => {
        if (firstLoad.current) {
            return
        }

        // Clear previous timeout if it exists
        if (debounceTimeout.current) {
            clearTimeout(debounceTimeout.current)
        }

        // Set a new timeout
        debounceTimeout.current = setTimeout(() => {
            if (page !== 1 && !firstLoad.current) {
                setPage(1)  // Reset to first page on filter change
            } else {
                fetchListOnly()
            }
            fetchOverviewOnly()
        }, 500)  // 500ms debounce time

        // Cleanup on unmount
        return () => clearTimeout(debounceTimeout.current)
    }, [
        timeframe,
        selectedParts,
        selectedClasses,
        levelRange,
        breedCountRange,
        evolvedPartsRange,
        selectedCollections,
    ])

    useEffect(() => {
        if (firstLoad.current) {
            fetchOverviewOnly()
            fetchListOnly()
            fetchParts()
            firstLoad.current = false
            return
        }
        fetchListOnly(page)
    }, [page, sortBy])

    async function fetchOverviewOnly() {
        try {
            const { includeParts, excludeParts } = formatSelectedParts(selectedParts)
            const body_data = {
                "time_unit": timeframe[1],
                "time_num": timeframe[0],
                "include_parts": includeParts,
                "exclude_parts": excludeParts,
                "axie_class": selectedClasses,
                "level": levelRange,
                "breed_count": breedCountRange,
                "evolved_parts_count": evolvedPartsRange,
                "collections": formatSelectedCollections(selectedCollections)
            }
            const headers = { "Content-Type": "application/json" }

            const responseOverview = await axios.post(
                    "https://dev.api.axieanalytics.com/axies/graph/overview",
                    body_data,
                    headers
                )

            setOverviewData(responseOverview.data)
            setIsLoading(false)
        } catch (err) {
            setError(err.message || "An error occured while fetching overview data.")
        }
    }

    async function fetchListOnly() {
        try {
            const { includeParts, excludeParts } = formatSelectedParts(selectedParts)
            const body_data = {
                "time_unit": timeframe[1],
                "time_num": timeframe[0],
                "limit": axiesPerPage,
                "offset": (page - 1) * axiesPerPage,
                "include_parts": includeParts,
                "exclude_parts": excludeParts,
                "axie_class": selectedClasses,
                "level": levelRange,
                "breed_count": breedCountRange,
                "evolved_parts_count": evolvedPartsRange,
                "collections": formatSelectedCollections(selectedCollections),
                "sort_by": sortBy
            }
            const headers = { "Content-Type": "application/json" }

            const responseList = await axios.post(
                "https://dev.api.axieanalytics.com/axies/list",
                body_data,
                headers
            )

            setListData(responseList.data)
            setIsLoading(false)
        } catch (err) {
            setError(err.message || "An error occured while fetching the list of axies.")
        }
    }

    async function fetchParts() {
        try {
            const responseParts = await axios.get(
                "https://dev.api.axieanalytics.com/axies/parts",
                { headers: { "Content-Type": "application/json" } }
            )

            axiePartsOriginal.current = responseParts.data
            setParts(structuredClone(axiePartsOriginal.current)) // Deep copy to avoid mutation.
        } catch (err) {
            setError(err.message || "An error occurred while fetching parts.")
        }
    }

    function formatSelectedParts(selectedParts) {
        const includeParts = {
            "eyes": [],
            "ears": [],
            "mouth": [],
            "horn": [],
            "back": [],
            "tail": []
        }
        const excludeParts = {
            "eyes": [],
            "ears": [],
            "mouth": [],
            "horn": [],
            "back": [],
            "tail": []
        }

        for (const part in selectedParts) {
            if (selectedParts[part]["action"] === "include") {
                includeParts[selectedParts[part]["type"]].push(selectedParts[part]["id"])
            } else if (selectedParts[part]["action"] === "exclude") {
                excludeParts[selectedParts[part]["type"]].push(selectedParts[part]["id"])
            }
        }
        return { includeParts, excludeParts }
    }

    function formatSelectedCollections(selectedCollections) {
        const formattedCollections = []
        for (const collection in selectedCollections) {
            if (collection === "Any Collection") {
                formattedCollections.push({"special": "Any Collection"})
                return formattedCollections
            } else if (collection === "No Collection") {
                formattedCollections.push({"special": "No Collection"})
                return formattedCollections
            } else if (selectedCollections[collection]["numParts"]) {
                formattedCollections.push({
                    "partCollection": collection,
                    "numParts": selectedCollections[collection]["numParts"]
                })
            } else if (!selectedCollections[collection]["numParts"]) {
                formattedCollections.push({
                    "title": collection
                })
            }
        }
        return formattedCollections
    }

    function handlePageChange(newPage) {
        if (newPage < 1 || newPage > Math.ceil(overviewData["total_sales"] / axiesPerPage)) {
            return; // Prevent invalid page change
        }
        setListData([]); // Clear previous data
        setPage(newPage);
    }

    function clearParts() {
        setSelectedParts({})
        setParts(structuredClone(axiePartsOriginal.current)) // Reset to original parts data
    }

    function clearAll() {
        setTimeframe([1, "days"])
        clearParts()
        setSelectedClasses([])
        setLevelRange([1, 60])
        setBreedCountRange([0, 7])
        setEvolvedPartsRange([0, 6])
        setSelectedCollections({})
    }


    return (
        <>
            <Overview
                title="Search Overview"
                data={overviewData}
                timeframe={timeframe}
                setTimeframe={setTimeframe}
                customTimeframe={true}
            />

            <div className="grid grid-rows-2 gap-6 m-5 p-6 border-2 rounded-lg">
                <div className="row-span-2">
                    <FilterSection 
                        timeframe={timeframe}
                        setTimeframe={setTimeframe}
                        parts={parts}
                        setParts={setParts}
                        selectedParts={selectedParts}
                        setSelectedParts={setSelectedParts}
                        selectedClasses={selectedClasses}
                        setSelectedClasses={setSelectedClasses}
                        levelRange={levelRange}
                        setLevelRange={setLevelRange}
                        breedCountRange={breedCountRange}
                        setBreedCountRange={setBreedCountRange}
                        evolvedPartsRange={evolvedPartsRange}
                        setEvolvedPartsRange={setEvolvedPartsRange}
                        selectedCollections={selectedCollections}
                        setSelectedCollections={setSelectedCollections}
                        sortBy={sortBy}
                        setSortBy={setSortBy}
                        clearParts={clearParts}
                        clearAll={clearAll}
                    />
                </div>

                <div className="">
                    <ResultSection 
                        data={listData}
                    />
                </div>
                <div>
                    <Pagination>
                        <PaginationContent>
                            {page > 1 && (
                                <PaginationItem>
                                <PaginationPrevious href="#" onClick={() => handlePageChange(page - 1)}/>
                            </PaginationItem>
                            )}
                            {page > 2 && (
                                <>
                                <PaginationItem>
                                    <PaginationLink href="#" onClick={() => handlePageChange(1)}>
                                        1
                                    </PaginationLink>
                                </PaginationItem>
                                <PaginationItem>
                                    <PaginationEllipsis />
                                </PaginationItem>
                                </>
                            )}
                            <PaginationItem>
                                <PaginationLink
                                    className="rounded-full border-1 pointer-events-none"
                                >
                                    {page}
                                </PaginationLink>
                            </PaginationItem>
                            {page + 1 <= Math.ceil(overviewData["total_sales"] / axiesPerPage) && (
                                <PaginationItem>
                                    <PaginationLink href="#" onClick={() => handlePageChange(page + 1)}>{page + 1}</PaginationLink>
                                </PaginationItem>
                            )}
                            {page + 2 <= Math.ceil(overviewData["total_sales"] / axiesPerPage) && (
                                <PaginationItem>
                                    <PaginationLink href="#" onClick={() => handlePageChange(page + 2)}>{page + 2}</PaginationLink>
                                </PaginationItem>
                            )}
                            {page + 2 < Math.ceil(overviewData["total_sales"] / axiesPerPage) && (
                                <>
                                <PaginationItem>
                                    <PaginationEllipsis />
                                </PaginationItem>
                                <PaginationItem>
                                    <PaginationLink href="#" onClick={() => handlePageChange(Math.ceil(overviewData["total_sales"] / axiesPerPage))}>
                                        {Math.ceil(overviewData["total_sales"] / axiesPerPage)}
                                    </PaginationLink>
                                </PaginationItem>
                                </>
                            )}
                            {page < Math.ceil(overviewData["total_sales"] / axiesPerPage) && (
                                <PaginationItem>
                                    <PaginationNext href="#" onClick={() => handlePageChange(page + 1)}/>
                                </PaginationItem>
                            )}
                        </PaginationContent>
                    </Pagination>
                </div>
            </div>
        </>
    )
}