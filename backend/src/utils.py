import time


def binary_search(data: list[dict], field: str, target: int) -> int:
    left = 0
    right = len(data)

    while left < right:
        mid = (left + right) // 2
        if data[mid][field] >= target:
            left = mid + 1
        else:
            right = mid
    return left - 1 if left > 0 else left

def format_data_line_graph(raw_data: list[dict], time_unit: str, time_num:int):
    data = {
        "total_sales": 0,
        "total_volume_eth": 0,
        "avg_price_eth": 0,
        "chart": []
    }

    current_time = time.time()
    if time_unit == "hours":
            timeframe_seconds = 3600 * time_num
    elif time_unit == "days":
        timeframe_seconds = 86400 * time_num

    start_time = current_time - timeframe_seconds
    num_buckets = 30
    bucket_size = (current_time - start_time) // 30
    bucket_idx = 0

    # Pre-allocate chart buckets
    for _ in range(num_buckets):
        data["chart"].append({"sales": 0, "volume_eth": 0, "avg_price_eth": 0})

    # Binary search to find the first relevant index
    idx = binary_search(raw_data, "sale_date", start_time)
    if idx <= 0:
        return data

    # Assign each sale to the correct bucket.
    for i in range(idx, -1, -1):
        sale = raw_data[i]
        if sale["sale_date"] < start_time:
            break
        bucket_idx = int((sale["sale_date"] - start_time) // bucket_size)
        if bucket_idx >= num_buckets:
            bucket_idx = num_buckets - 1
        data["chart"][bucket_idx]["sales"] += 1
        data["chart"][bucket_idx]["volume_eth"] += sale["price_eth"]

    # Calculate average and totals
    for bucket in data["chart"]:
        if bucket["sales"] > 0:
            bucket["avg_price_eth"] = round(bucket["volume_eth"] / bucket["sales"], 5)
            data["total_sales"] += bucket["sales"]
            data["total_volume_eth"] += bucket["volume_eth"]

    if data["total_sales"] > 0:
        data["avg_price_eth"] = round(data["total_volume_eth"] / data["total_sales"], 5)
    data["total_volume_eth"] = round(data["total_volume_eth"], 5)
    return data

def format_data_line_graph_by_collection(raw_data: list[dict], time_unit: str, time_num: int):
    collections = [
        "Normal",
        "Mystic",
        "Origin",
        "MEO",
        "Xmas",
        "Shiny",
        "Japan",
        "Nightmare",
        "Summer",
        "AgamoGenesis",
    ]

    collection_fields = [
        "eyes_special_genes",
        "ears_special_genes",
        "mouth_special_genes",
        "horn_special_genes",
        "back_special_genes",
        "tail_special_genes",
        "collection_title"
    ]

    data = {}

    current_time = time.time()
    if time_unit == "hours":
            timeframe_seconds = 3600 * time_num
    elif time_unit == "days":
        timeframe_seconds = 86400 * time_num

    start_time = current_time - timeframe_seconds
    num_buckets = 30
    bucket_size = (current_time - start_time) // 30
    bucket_idx = 0

    # Pre-allocate collections and chart buckets
    for col in collections:
        data[col] = {
            "total_sales": 0,
            "total_volume_eth": 0,
            "avg_price_eth": 0,
            "chart": []
        }
        for _ in range(num_buckets):
            data[col]["chart"].append({"sales": 0, "volume_eth": 0, "avg_price_eth": 0})

    # Binary search to find the first relevant index
    idx = binary_search(raw_data, "sale_date", start_time)
    if idx <= 0:
        return data
    
    # Assign each sale to the correct collection and bucket.
    for i in range(idx, -1, -1):
        sale = raw_data[i]
        if sale["sale_date"] < start_time:
            break

        bucket_idx = int((sale["sale_date"] - start_time) // bucket_size)
        if bucket_idx >= num_buckets:
            bucket_idx = num_buckets - 1
        
        sale_collections = {}

        for field in collection_fields:
            if sale[field] != "" and sale[field] not in sale_collections:
                if "_" in sale[field]:
                    # Handle special cases where a part has multiple collections
                    part_collections = sale[field].split("_")
                    for col in part_collections:
                        if col not in sale_collections:
                            sale_collections[col] = True
                else:
                    sale_collections[sale[field]] = True

        if not sale_collections:
            data["Normal"]["chart"][bucket_idx]["sales"] += 1
            data["Normal"]["chart"][bucket_idx]["volume_eth"] += sale["price_eth"]
        else:
            for collection in collections:
                for key in sale_collections:
                    if collection.lower() in key.lower():
                        data[collection]["chart"][bucket_idx]["sales"] += 1
                        data[collection]["chart"][bucket_idx]["volume_eth"] += sale["price_eth"]
                        sale_collections.pop(key)
                        break

    # Calculate average and totals for each collection and buckets.
    for key in data:
        for bucket in data[key]["chart"]:
            if bucket["sales"] > 0:
                bucket["avg_price_eth"] = round(bucket["volume_eth"] / bucket["sales"], 5)
                data[key]["total_sales"] += bucket["sales"]
                data[key]["total_volume_eth"] += bucket["volume_eth"]

        if data[key]["total_sales"] > 0:
            data[key]["avg_price_eth"] = round(data[key]["total_volume_eth"] / data[key]["total_sales"], 5)
        data[key]["total_volume_eth"] = round(data[key]["total_volume_eth"], 5)

    return data

def format_data_bar_graph(raw_data: list[dict], field: str, field_range: list, time_unit: str, time_num: int):
    current_time = time.time()
    if time_unit == "hours":
            timeframe_seconds = 3600 * time_num
    elif time_unit == "days":
        timeframe_seconds = 86400 * time_num

    data = []

    start_time = current_time - timeframe_seconds
    num_buckets = len(field_range)

    # Binary search to find the first relevant index
    idx = binary_search(raw_data, "sale_date", start_time)
    if idx <= 0:
        return data
    
    # Pre-allocate chart buckets
    for _ in range(num_buckets):
        data.append({field: field_range[_], "sales": 0, "volume_eth": 0, "avg_price_eth": 0})

    hashmap = {}

    # Populate the hashmap
    for i in range(0, idx + 1):
        sale = raw_data[i]
        if sale["sale_date"] < start_time:
            break

        if sale[field] in hashmap:
            hashmap[sale[field]]["sales"] += 1
            hashmap[sale[field]]["volume_eth"] += sale["price_eth"]
        else:
            hashmap[sale[field]] = {"sales": 0, "volume_eth": 0}

    for bucket in data:
        if isinstance(bucket[field], list):
            for f in range(bucket[field][0], bucket[field][1] + 1):
                bucket["sales"] += hashmap[f]["sales"]
                bucket["volume_eth"] += hashmap[f]["volume_eth"]
        else:
            bucket["sales"] += hashmap[bucket[field]]["sales"]
            bucket["volume_eth"] += hashmap[bucket[field]]["volume_eth"]
        bucket["avg_price_eth"] = round(bucket["volume_eth"] / bucket["sales"], 5)
        bucket["volume_eth"] = round(bucket["volume_eth"], 5)

    return data