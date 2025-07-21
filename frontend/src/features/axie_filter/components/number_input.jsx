import "react"
import { useState, useEffect } from "react"
import { Input } from "@/components/ui/input"


export function NumberInput({ value, onChange, min, max, className}){
    const [inputValue, setInputValue] = useState(String(value))

    useEffect(() => {
        setInputValue(String(value))
    }, [value])

    const handleInputChange = (e) => {
        const val = e.target.value

        // Allow empty input temporarily while typing
        if (val === "" || /^[0-9]*$/.test(val)) {
            setInputValue(val)
        }
    }

    const commitValue = (val) => {
        const num = parseInt(val, 10)

        if (!isNaN(num)) {
            const newMin = Math.max(min, Math.min(max, num))
            onChange(newMin)
            setInputValue(String(newMin))
        } else {
            setInputValue(String(value))
        }
    }

    const handleKeyDown = (e) => {
        if (e.key === "Enter") {
            commitValue(e.target.value)
        }
    }

    const handleBlur = (e) => {
        commitValue(e.target.value)
    }

    return (
        <Input
            type="text"
            inputMode="numeric"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onBlur={handleBlur}
            className={`h-6 ${className ?? ""}`}
        />
    )
}