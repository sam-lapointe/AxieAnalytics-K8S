import "react"
import { Button } from "@/components/ui/button"
import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectLabel,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";


export function TitleAndDefaultTimerange({title, timeframe = [1, "days"], setTimeframe = "", customTimeframe = false}) {
    return (
        <div className="flex items-baseline">
                <h1 className="font-bold text-2xl">{title}</h1>

                {
                    !customTimeframe ?
                    (
                        <>
                            {/* Buttons for medium and up */}
                            <div className="md:flex gap-3 ml-auto hidden">
                                <Button
                                    className={timeframe[0] === 1 ? "bg-blue-600" : ""}
                                    onClick={() => setTimeframe([1, "days"])}
                                >24H</Button>
                                <Button
                                    className={timeframe[0] === 7 ? "bg-blue-600" : ""}
                                    onClick={() => setTimeframe([7, "days"])}
                                >7D</Button>
                                <Button
                                    className={timeframe[0] === 30 ? "bg-blue-600" : ""}
                                    onClick={() => setTimeframe([30, "days"])}
                                >30D</Button>
                            </div>

                            {/* Dropdown for small screens */}
                            <div className="md:hidden ml-auto">
                                <Select
                                    value={timeframe[0]}
                                    onValueChange={(e) => setTimeframe([e, "days"])}
                                >
                                    <SelectTrigger>
                                        <SelectValue/>
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectGroup>
                                        <SelectItem value={1}>24H</SelectItem>
                                        <SelectItem value={7}>7D</SelectItem>
                                        <SelectItem value={30}>30D</SelectItem>
                                        </SelectGroup>
                                    </SelectContent>
                                </Select>
                            </div>
                        </>
                    ) : (
                        <div className="ml-auto">
                            <p className="font-semibold">Last {timeframe[0] > 1 ? `${timeframe[0]} ${timeframe[1]}` : timeframe[1].slice(0, -1)}</p>
                        </div>
                    )
                }
        </div>
    )
}