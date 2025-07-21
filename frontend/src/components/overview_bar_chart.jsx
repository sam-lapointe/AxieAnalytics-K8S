import "react"
import { Bar, BarChart, CartesianGrid, XAxis } from "recharts"
import eth_logo from "../assets/eth_logo.svg"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"


const chartData = [
  { level: "1-9", sales: 186, averagePrice: 18 },
  { level: "10-19", sales: 305, averagePrice: 0.002 },
  { level: "20-29", sales: 237, averagePrice: 0.0022},
  { level: "30-39", sales: 73, averagePrice: 0.0025 },
  { level: "40-49", sales: 209, averagePrice: 0.003 },
  { level: "50-59", sales: 214, averagePrice: 0.0035 },
  { level: "60", sales: 17, averagePrice: 0.004 },
]


export function OverviewBarChart({data, keyName="", keyValue="", label="", additionalValue="", additionalLabel=""}) {
  const chartConfig = {
    [keyValue]: {
      label: label,
      color: "#00B4D8",
    },
    [additionalValue]: {
      label: additionalLabel
    }
  }

    return (
        <Card>
            <CardContent>
                <ChartContainer config={chartConfig}>
                <BarChart accessibilityLayer data={data}>
                    <CartesianGrid vertical={false} />
                    <XAxis
                      dataKey={keyName}
                      tickLine={false}
                      tickMargin={10}
                      axisLine={false}
                      tickFormatter={(value) => value.slice(0, 5)}
                    />
                    <ChartTooltip
                      cursor={false}
                      content={<ChartTooltipContent hideIndicator additionalPayload={additionalValue}/>}
                      // ChartTooltipContent has been customized to allow additionalPayload without having to display a second bar.
                    />
                    <Bar dataKey={keyValue} fill={chartConfig[`${keyValue}`]["color"]} radius={8} />
                </BarChart>
                </ChartContainer>
            </CardContent>
        </Card>
    )
}