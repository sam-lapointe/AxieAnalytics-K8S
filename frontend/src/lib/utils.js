import { clsx } from "clsx";
import { twMerge } from "tailwind-merge"
import { axieCollectionParts, axieCollectionTitles } from "../data/collections";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function formatSaleDate(epoch) {
  const d = new Date(epoch * 1000)
  const pad = n => n.toString().padStart(2, "0")
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${d.getHours()}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

export function getAxieCollections(parts, collectionTitle) {
  const collections = {}

  Object.keys(parts).map((part) => {
    if (parts[part].special_genes) {
      const partCollections = parts[part].special_genes.split("_")
      for (let partCollection of partCollections) {
        for (let axieCollectionPart of axieCollectionParts) {
          if (partCollection.toLowerCase().includes(axieCollectionPart.toLowerCase())) {
            if (collections[axieCollectionPart]) {
              collections[axieCollectionPart] += 1
            } else {
              collections[axieCollectionPart] = 1
            }
            break
          }
        }
      }
    }
  })

  if (collectionTitle && axieCollectionTitles.includes(collectionTitle)) {
    collections[collectionTitle] = 1
  }

  return collections
}