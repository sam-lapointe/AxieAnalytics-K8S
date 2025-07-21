import "react"
import { TitleAndDefaultTimerange } from "./title_and_default_timerange"
import { OverviewBarChart } from "./overview_bar_chart"
import eth_logo from "../assets/eth_logo.svg"


export function OverviewByBreedCount({data, timeframe, setTimeframe}) {
    return (
        <div className="grid grid-rows-2 gap-6 m-5 p-6 border-2 rounded-lg">
            <div className="row-span-2">
                <TitleAndDefaultTimerange
                    title="Normal Axies Sales By Breed Count"
                    timeframe={timeframe}
                    setTimeframe={setTimeframe}
                />
            </div>
            
            <div>
                <OverviewBarChart 
                    data={data}
                    keyName="breed_count_range"
                    keyValue="sales"
                    label="Axies Sold"
                    additionalValue="avg_price_eth"
                    additionalLabel={(
                        <div className="flex">
                            <p>Avg</p>
                            <img src={eth_logo} className="w-3 h-3 ml-2 my-auto"/>
                        </div>
                    )}
                />
            </div>
        </div>
    )
}