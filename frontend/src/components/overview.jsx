import "react";
import { useState, useEffect } from "react";
import { OverviewLineChart } from "./overview_line_chart";
import { TitleAndDefaultTimerange } from "./title_and_default_timerange";
import eth_logo from "../assets/eth_logo.svg"


export function Overview({data, title="Overall Sales", timeframe, setTimeframe, customTimeframe}) {
    const tempData = {
        "total_sales": 0,
        "total_volume_eth": 0,
        "avg_price_eth": 0,
        "chart": [{"sales": 0, "volume": 0, "avg_price_eth": 0}]
    }

    const insert_eth_logo = (text) => {
        return (
            <div className="flex">
                <p>{text}</p>
                <img src={eth_logo} className="w-4 h-4 ml-2 my-auto"/>
            </div>
        )
    }

    return (
        <div className="grid grid-rows-2 gap-6 m-5 p-6 border-2 rounded-lg">
            <div className="row-span-2">
                <TitleAndDefaultTimerange title={title} timeframe={timeframe} setTimeframe={setTimeframe} customTimeframe={customTimeframe}/>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 col-span-full">
                <OverviewLineChart
                    data={data}
                    keyValue="sales"
                    label="Total Sales"
                    labelData={data["total_sales"]}
                    keyName="Axies Sold"
                />
                <OverviewLineChart
                    data={data}
                    keyValue="volume_eth"
                    label={insert_eth_logo("Total Volume")}
                    labelData={data["total_volume_eth"]}
                    keyName={<img src={eth_logo}className="w-3 h-3 my-auto"/>}
                />
                <OverviewLineChart
                    data={data}
                    keyValue="avg_price_eth"
                    label={insert_eth_logo("Average Price")}
                    labelData={data["avg_price_eth"]}
                    keyName={<img src={eth_logo} className="w-3 h-3 my-auto"/>}
                />
            </div>
        </div>
    )
}