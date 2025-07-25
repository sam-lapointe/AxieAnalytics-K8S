import json
import time
import logging
from src.models.axie_sales_search import AxieSalesSearch
from src.services.axie_sales import get_all_data, get_data_by_breed_count, get_axie_parts
from src.utils import format_data_line_graph, format_data_line_graph_by_collection
from src.database import db

async def refresh_graph_overview():
    """
    Refresh the graph overview data in Redis.
    """
    query_select = "SELECT price_eth, sale_date FROM axies_full_info"
    filter = AxieSalesSearch()
    raw_data = await get_all_data(query_select, filter)

    d1_data = format_data_line_graph(raw_data, "days", 1)
    d7_data = format_data_line_graph(raw_data, "days", 7)
    d30_data = format_data_line_graph(raw_data, "days", 30)

    data = {
        "1d": d1_data,
        "7d": d7_data,
        "30d": d30_data,
    }
    await db.redis_client.client.set("axie_graph_overview", json.dumps(data), ex=120)


async def refresh_graph_collection():
    """
    Refresh the graph collection data in Redis.
    """
    query_select = """
        SELECT
            price_eth,
            sale_date,
            eyes_special_genes,
            ears_special_genes,
            mouth_special_genes,
            horn_special_genes,
            back_special_genes,
            tail_special_genes,
            collection_title
        FROM axies_full_info
    """
    filter = AxieSalesSearch()
    raw_data = await get_all_data(query_select, filter)

    d1_data = format_data_line_graph_by_collection(raw_data, "days", 1)
    d7_data = format_data_line_graph_by_collection(raw_data, "days", 7)
    d30_data = format_data_line_graph_by_collection(raw_data, "days", 30)

    data = {
        "1d": d1_data,
        "7d": d7_data,
        "30d": d30_data,
    }
    await db.redis_client.client.set("axie_graph_collection", json.dumps(data), ex=120)

async def refresh_graph_breed_count():
    """
    Refresh the graph breed count data in Redis.
    """
    d1_data = await get_data_by_breed_count("days", 1)
    d7_data = await get_data_by_breed_count("days", 7)
    d30_data = await get_data_by_breed_count("days", 30)

    data = {
        "1d": d1_data,
        "7d": d7_data,
        "30d": d30_data,
    }

    # Convert to dict and round values
    for key in data:
        new_list = []
        for item in data[key]:
            d = dict(item)
            d["volume_eth"] = round(d["volume_eth"], 5)
            d["avg_price_eth"] = round(d["avg_price_eth"], 5)
            new_list.append(d)
        data[key] = new_list
    
    await db.redis_client.client.set("axie_graph_breed_count", json.dumps(data), ex=120)

async def refresh_axie_parts():
    """
    Refresh the axie parts data in Redis.
    """
    query_select = "SELECT id, class, name, stage, type, special_genes FROM axie_parts"
    raw_data = await get_axie_parts(query_select)
    
    parts = {}
    duplicate_part_names = set()
    for part in raw_data:
        if part["name"] not in parts:
            parts[part["name"]] = {
                "type": part["type"],
                "class": part["class"],
                "special_genes": part["special_genes"],
                "partsIds": [
                    {"id": part["id"], "stage": part["stage"]}
                ]
            }
        else:
            """
            There are some parts that have the same name but different types (e.g. "eyes" and "back").
            """
            if parts[part["name"]]["type"] == part["type"]:
                parts[part["name"]]["partsIds"].append({"id": part["id"], "stage": part["stage"]})
            else:
                if f"{part['name']} ({part['type'].capitalize()})" not in parts:
                    parts[f"{part['name']} ({part['type'].capitalize()})"] = {
                        "type": part["type"],
                        "class": part["class"],
                        "special_genes": part["special_genes"],
                        "partsIds": [{"id": part["id"], "stage": part["stage"]}]
                    }
                    duplicate_part_names.add(part["name"])
                else:
                    parts[f"{part['name']} ({part['type'].capitalize()})"]["partsIds"].append({"id": part["id"], "stage": part["stage"]})

    # Rename parts with duplicate names to include their type in the name
    for duplicate_name in duplicate_part_names:
        if duplicate_name in parts:
            part_type = parts[duplicate_name]["type"]
            parts[f"{duplicate_name} ({part_type.capitalize()})"] = parts.pop(duplicate_name)

    await db.redis_client.client.set("axie_parts", json.dumps(parts), ex=43200)