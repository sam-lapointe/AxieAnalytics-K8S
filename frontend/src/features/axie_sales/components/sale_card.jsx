import "react"
import eth_logo from "../../../assets/eth_logo.svg"
import { formatSaleDate } from "../../../lib/utils"
import { getAxieCollections } from "../../../lib/utils"
import { classColorMap } from "../../../data/color_variants"
import { Store } from "lucide-react"
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card"


const partsOrder = [
    "eyes",
    "ears",
    "mouth",
    "horn",
    "back",
    "tail"
]


export function AxieSaleCard({data}) {
    const collections = getAxieCollections(data.parts, data.collection_title)

    return (
        <Card className="p-2 gap-0">
            <CardHeader className="p-0">
                <div className="flex w-full">
                    <img
                        src={data.image_url}
                        className="w-40"    
                    />
                    <div className="rounded-xl ml-auto">
                        <p className="border-2 rounded-lg px-1 text-sm font-bold text-center">#{data.axie_id}</p>
                        {Object.keys(collections).sort().map((collection) => (
                            <p className="border-2 rounded-lg my-1 px-2 text-xs text-center" key={collection}>{collection}{collections[collection] > 1 ? ` (${collections[collection]})` : ""}</p>
                        ))}
                    </div>
                </div>
            </CardHeader>
            <CardContent className="p-0">
                <div className="flex items-center">
                    <div className="flex">
                        <p>{data.price_eth.toFixed(6)}</p>
                        <img src={eth_logo} className="w-4 h-4 ml-2 my-auto"/>
                    </div>
                    <p className={`rounded-lg my-1 py-1 px-3 text-xs text-white text-center ml-auto ${classColorMap[data.class.toLowerCase()].bg}`}>{data.class}</p>
                </div>
                <div className="grid grid-cols-2 gap-1 text-xs">
                    <p className="rounded bg-gray-200 pl-1">Level: <strong>{data.level}</strong></p>
                    <p className="rounded bg-gray-200 pl-1">Breed Count: {data.breed_count}/7</p>
                </div>
                <div className="my-2">
                    <p className="font-semibold">Parts</p>
                    <div className="max-h-50 overflow-y-auto">
                        {partsOrder.map((part) => {
                            return (
                                <div className="flex gap-2 items-center" key={part}>
                                    <p className={`text-xs font-semibold ${classColorMap[data.parts[part].class].text}`}>{part.charAt(0).toUpperCase() + part.slice(1)}: {data.parts[part].name}</p>
                                    <p className="text-xs font-semibold">S{data.parts[part].stage}</p>
                                    {data.parts[part].special_genes && (
                                        data.parts[part].special_genes.split("_").map(collection => (
                                            <p className="border-1 rounded-lg px-1 text-xs" key={collection}>{collection.charAt(0).toUpperCase() + collection.slice(1)}</p>
                                        ))
                                    )}
                                </div>
                            )
                        })}
                        <div className="flex gap-2 items-center mt-1">
                            <p className="text-xs font-semibold">Body: {data.body_shape}</p>
                        </div>
                    </div>
                </div>
            </CardContent>
            <CardFooter className="p-0 border-t-2">
                <div className="flex items-center w-full mt-1">
                    <div>
                        <p className="text-xs">
                            Tx Hash: <a 
                                href={`https://app.roninchain.com/tx/${data.transaction_hash}`}
                                target="_blank"
                                rel="noreferrer"
                            >{data.transaction_hash.slice(0, 8)}...{data.transaction_hash.slice(-8)}</a>
                        </p>
                        <p className="text-xs italic mt-1">Sold: {formatSaleDate(data.sale_date)}</p>
                    </div>
                    <a
                        className="ml-auto mr-4 text-xs"
                        href={`https://app.axieinfinity.com/marketplace/axies/${data.axie_id}/`}
                        target="_blank"
                        rel="noreferrer"
                    >
                        <Store/>
                    </a>
                </div>
            </CardFooter>
        </Card>
    )
}