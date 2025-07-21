import "react";
import { useState, useEffect } from "react";

import { CartesianGrid, Line, LineChart, YAxis } from "recharts"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"


export function OverviewLineChart({data, label, labelData, keyName="", keyValue=""}) {
  const chartConfig = {
      overview: {
          label: keyName,
          color: "var(--chart-1)",
      },
  };

  return (
    <Card>
      <>
      {label && (
        <CardHeader>
          <div className="">
            <CardTitle>{label}</CardTitle>
            <p className="ml-auto">{labelData}</p>
          </div>
        </CardHeader>
      )}
      </>

      <CardContent>
        <ChartContainer config={chartConfig} className="h-24 md:h-32 w-full">
          <LineChart
            accessibilityLayer
            data={data["chart"]}
            margin={{
              left: 12,
              right: 12,
            }}
          >
            <CartesianGrid vertical={false} />
            
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent nameKey="overview" hideIndicator/>}
            />
            <Line
              dataKey={keyValue}
              type="monotone"
              stroke="var(--color-overview)"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}