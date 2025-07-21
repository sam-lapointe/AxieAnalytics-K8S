import "react"
import eth_logo from "../assets/eth_logo.svg"
import { OverviewLineChart } from "./overview_line_chart"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"


export function CardCollection({data, collection="Collection"}) {
    return (
        <div className="">
            <Card className="pt-2 pb-0 gap-0">
                <CardHeader className="border-b-2 py-2">
                    <CardTitle>{collection}</CardTitle>
                </CardHeader>
                <CardContent className="px-0 py-0">
                    <div className="[&_.bg-card]:rounded-none [&_.bg-card]:border-0">
                        <OverviewLineChart
                        data={data}
                        keyName="Axies Sold"
                        keyValue="sales"
                        className="px-0"
                    />
                    </div>
                </CardContent>
                <CardFooter className="grid grid-cols-2 border-t-2 py-2">
                    <div className="grid grid-rows-2">
                        <p>Total Sales</p>
                        <p>{data["total_sales"]}</p>
                    </div>
                    <div className="grid grid-rows-2">
                        <p>Average Price</p>
                        <div className="flex">
                            <img src={eth_logo} className="w-4 h-4 my-auto mr-1"/>
                            <p>{data["avg_price_eth"]}</p>
                        </div>
                    </div>
                </CardFooter>
            </Card>
        </div>
    )
}