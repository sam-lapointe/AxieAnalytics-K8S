import "react"
import { AxieSaleCard } from "./sale_card"


export function ResultSection({data}) {
    return(
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 3xl:grid-cols-7 4xl:grid-cols-8 gap-4">
            {data.map((sale, index) => (
                <AxieSaleCard
                    key={index}
                    data={sale}
                />
            ))}
        </div>
    )
}