import "react"
import { Button } from "@/components/ui/button"


export function SelectedFilter({text, action="", removeFilter}) {
    return (
        <div className="flex items-center align-center border-2 border-gray rounded-lg p-1">
            <p
                className={`
                    text-xs
                    ${action === "exclude" ? "line-through" : ""}    
                `}
            >
                {text}
            </p>
            <Button
                size="icon"
                className="text-xs text-black bg-white shadow-none hover:bg-gray-200 w-4 h-4"
                onClick={removeFilter}
            >
                X
            </Button>
        </div>
    )
}