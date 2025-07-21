import "react";
import { useState, useEffect } from "react";
import { CardCollection } from "./card_collection";
import { TitleAndDefaultTimerange } from "./title_and_default_timerange";
import {
    Carousel,
    CarouselContent,
    CarouselItem,
    CarouselNext,
    CarouselPrevious,
  } from "@/components/ui/carousel";

export function OverviewByCollection({data, timeframe, setTimeframe}) {
    return (
        <div className="grid grid-rows-2 gap-6 m-5 p-6 border-2 rounded-lg">
            <div className="row-span-2">
                <TitleAndDefaultTimerange title="Sales By Collection" timeframe={timeframe} setTimeframe={setTimeframe}/>
            </div>

            <div className="flex justify-center w-full max-w-full relative overflow-hidden">
                <Carousel
                    opts={{
                        align: "start",
                    }}
                    className="w-full"
                    >
                    <CarouselContent>
                        {Object.entries(data).map(([key, value]) => (
                        <CarouselItem key={key} className="md:basis-1/2 lg:basis-1/3">
                            <CardCollection
                                data={value}
                                collection={key}
                            />
                        </CarouselItem>
                        ))}
                    </CarouselContent>
                    <CarouselPrevious className="absolute left-0 top-1/2 -translate-y-1/2 z-10"/>
                    <CarouselNext className="absolute right-0 top-1/2 -translate-y-1/2 z-10"/>
                </Carousel>
            </div>
        </div>
    )
}