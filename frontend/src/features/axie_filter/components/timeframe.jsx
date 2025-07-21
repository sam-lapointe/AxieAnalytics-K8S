import "react"
import { NumberInput } from "./number_input";
import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";


export function Timeframe({value, onChange}) {
    return (
        <div className="mx-2">
            <h3 className="text-lg font-medium">Timeframe</h3>
            
            <div className="flex gap-3 items-center">
                <p>Last</p>
                <NumberInput
                    value={value[0]}
                    onChange={(newNumber) => onChange([newNumber, value[1]])}
                    min={1}
                    max={365}
                    className="!w-15"
                />
                <Select
                    defaultValue={value[1]}
                    onValueChange={(e) => onChange([value[0], e])}
                >
                    <SelectTrigger className="!h-6 py-1 text-sm">
                        <SelectValue placeholder={value[1].charAt(0).toUpperCase() + value[1].slice(1)} />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectGroup>
                        <SelectItem value="hours">Hours</SelectItem>
                        <SelectItem value="days">Days</SelectItem>
                        </SelectGroup>
                    </SelectContent>
                </Select>
            </div>
        </div>
    )
}