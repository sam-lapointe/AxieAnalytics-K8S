import logging
from datetime import datetime
from src.models.axie_sales_search import AxieSalesSearch
from src.database import db


async def get_all_data(query: str, filter: AxieSalesSearch) -> list[dict]:
    logging.info(["[get_all_data] Retrieving data for graph..."])
    try:
        if db.database is None or not hasattr(db.database, "pool"):
            raise RuntimeError("Database is not initialized or not connected.")

        query_values = {}
        param_idx = 1

        # Time filter
        if filter.time_unit == "hours":
            timeframe_seconds = 3600 * filter.time_num
        elif filter.time_unit == "days":
            timeframe_seconds = 86400 * filter.time_num
        now = int(datetime.now().timestamp())  # Current epoch time
        start_time = now - timeframe_seconds
        query += f" WHERE sale_date >= ${param_idx}"
        query_values[param_idx] = start_time
        param_idx += 1

        # Include Parts
        if filter.include_parts:
            first_iteration = True
            query += " AND ("
            for key, value in filter.include_parts.items():
                if not value:
                    continue

                if first_iteration:
                    query += f"{key.lower()}_id = ANY(${param_idx})"
                    first_iteration = False
                else:
                    query += f" AND {key.lower()}_id = ANY(${param_idx})"
                query_values[param_idx] = value
                param_idx += 1
            query += ")"

        # Exclude Parts
        if filter.exclude_parts:
            first_iteration = True
            query += " AND ("
            for key, value in filter.exclude_parts.items():
                if not value:
                    continue

                if first_iteration:
                    query += f"{key.lower()}_id != ALL(${param_idx})"
                    first_iteration = False
                else:
                    query += f" AND {key.lower()}_id != ALL(${param_idx})"
                query_values[param_idx] = value
                param_idx += 1
            query += ")"

        # Axie Classes
        if filter.axie_class:
            first_iteration = True
            query += " AND ("
            for axie_class in filter.axie_class:
                if first_iteration:
                    query += f"LOWER(class) = ${param_idx}"
                    first_iteration = False
                else:
                    query += f" OR LOWER(class) = ${param_idx}"
                query_values[param_idx] = axie_class.lower()
                param_idx += 1
            query += ")"

        # Axie Level
        query += f" AND level BETWEEN ${param_idx} AND ${param_idx + 1}"
        query_values[param_idx] = filter.level[0]
        query_values[param_idx + 1] = filter.level[1]
        param_idx += 2

        # Breed Count
        query += f" AND breed_count BETWEEN ${param_idx} AND ${param_idx + 1}"
        query_values[param_idx] = filter.breed_count[0]
        query_values[param_idx + 1] = filter.breed_count[1]
        param_idx += 2

        # Evolved Parts
        query += f""" AND
            (CASE WHEN eyes_stage > 1 THEN 1 ELSE 0 END +
            CASE WHEN ears_stage > 1 THEN 1 ELSE 0 END +
            CASE WHEN mouth_stage > 1 THEN 1 ELSE 0 END +
            CASE WHEN horn_stage > 1 THEN 1 ELSE 0 END +
            CASE WHEN back_stage > 1 THEN 1 ELSE 0 END +
            CASE WHEN tail_stage > 1 THEN 1 ELSE 0 END)
            BETWEEN ${param_idx} AND ${param_idx + 1}
        """
        query_values[param_idx] = filter.evolved_parts_count[0]
        query_values[param_idx + 1] = filter.evolved_parts_count[1]
        param_idx += 2

        # Collection Parts
        if filter.collections:
            titles = [c.title for c in filter.collections if c.title is not None]
            if titles:
                first_iteration = True
                query += " AND ("
                for title in titles:
                    if first_iteration:
                        query += f"LOWER(collection_title) = ${param_idx}"
                        first_iteration = False
                    else:
                        query += f" OR LOWER(collection_title) = ${param_idx}"
                    query_values[param_idx] = title.lower()
                    param_idx += 1
                query += ")"

            for collection in filter.collections:
                if collection.special == "Any Collection":
                    query += """ AND
                        (CASE WHEN eyes_special_genes != '' THEN 1 ELSE 0 END +
                        CASE WHEN ears_special_genes != '' THEN 1 ELSE 0 END +
                        CASE WHEN mouth_special_genes != '' THEN 1 ELSE 0 END +
                        CASE WHEN horn_special_genes != '' THEN 1 ELSE 0 END +
                        CASE WHEN back_special_genes != '' THEN 1 ELSE 0 END +
                        CASE WHEN tail_special_genes != '' THEN 1 ELSE 0 END +
                        CASE WHEN collection_title != '' THEN 1 ELSE 0 END)
                        > 0
                    """
                    break
                elif collection.special == "No Collection":
                    query += """ AND
                        (eyes_special_genes = '' AND
                        ears_special_genes = '' AND
                        mouth_special_genes = '' AND
                        horn_special_genes = '' AND
                        back_special_genes = '' AND
                        tail_special_genes = '' AND
                        collection_title = '')
                    """
                    break
                if collection.partCollection:
                    numParts = collection.numParts
                    query += f""" AND
                        (CASE WHEN eyes_special_genes LIKE ('%' || ${param_idx} || '%') THEN 1 ELSE 0 END +
                        CASE WHEN ears_special_genes LIKE ('%' || ${param_idx} || '%') THEN 1 ELSE 0 END +
                        CASE WHEN mouth_special_genes LIKE ('%' || ${param_idx} || '%') THEN 1 ELSE 0 END +
                        CASE WHEN horn_special_genes LIKE ('%' || ${param_idx} || '%') THEN 1 ELSE 0 END +
                        CASE WHEN back_special_genes LIKE ('%' || ${param_idx} || '%') THEN 1 ELSE 0 END +
                        CASE WHEN tail_special_genes LIKE ('%' || ${param_idx} || '%') THEN 1 ELSE 0 END)
                        BETWEEN ${param_idx + 1} AND ${param_idx + 2}
                    """
                    query_values[param_idx] = collection.partCollection.lower()
                    query_values[param_idx + 1] = numParts[0]
                    query_values[param_idx + 2] = numParts[1]
                    param_idx += 3

        # Order By
        if filter.sort_by == "latest":
            query += " ORDER BY sale_date DESC"
        elif filter.sort_by == "lowest_price":
            query += " ORDER BY price_eth ASC"
        elif filter.sort_by == "highest_price":
            query += " ORDER BY price_eth DESC"
        elif filter.sort_by == "lowest_level":
            query += " ORDER BY level ASC, xp ASC"
        elif filter.sort_by == "highest_level":
            query += " ORDER BY level DESC, xp DESC"

        # Limit and Offset
        if filter.limit is not None:
            query += f" LIMIT ${param_idx} OFFSET ${param_idx + 1}"
            query_values[param_idx] = filter.limit
            query_values[param_idx + 1] = filter.offset
            param_idx += 2

        # Prepare parameters in order for asyncpg
        params = [query_values[i] for i in range(1, param_idx)]

        async with db.database.pool.acquire() as conn:
            data = await conn.fetch(query, *params)
        return data
    except Exception as e:
        logging.error(
            f"[get_all_data] An error occured while retrieving all data: {e}"
        )
        raise e

async def get_data_by_breed_count(time_unit: str, time_num: int) -> dict:
    logging.info(["[get_data_by_breed_count] Retrieving data by breed count for bar graph..."])
    try:
        if db.database is None or not hasattr(db.database, "pool"):
            raise RuntimeError("Database is not initialized or not connected.")

        query = """
            SELECT
                CASE
                    WHEN breed_count = 0 THEN '0'
                    WHEN breed_count = 1 THEN '1'
                    WHEN breed_count = 2 THEN '2'
                    WHEN breed_count = 3 THEN '3'
                    WHEN breed_count = 4 THEN '4'
                    WHEN breed_count = 5 THEN '5'
                    WHEN breed_count = 6 THEN '6'
                    WHEN breed_count = 7 THEN '7'
                END AS breed_count_range,
                COUNT(*) as sales,
                SUM(price_eth) as volume_eth,
                AVG(price_eth) as avg_price_eth
            FROM axies_full_info
        """
        query_values = {}
        param_idx = 1

        # Time filter
        if time_unit == "hours":
            timeframe_seconds = 3600 * time_num
        elif time_unit == "days":
            timeframe_seconds = 86400 * time_num
        now = int(datetime.now().timestamp())  # Current epoch time
        start_time = now - timeframe_seconds
        query += f" WHERE sale_date >= ${param_idx}"
        query_values[param_idx] = start_time
        param_idx += 1

        # Normal Axie (No Collection)
        query += """ AND
            (eyes_special_genes = '' AND
            ears_special_genes = '' AND
            mouth_special_genes = '' AND
            horn_special_genes = '' AND
            back_special_genes = '' AND
            tail_special_genes = '' AND
            collection_title = '')"""

        # Group By
        query += " GROUP BY breed_count_range"

        # Order By
        query += " ORDER BY MIN(breed_count)"

        # Prepare parameters in order for asyncpg
        params = [query_values[i] for i in range(1, param_idx)]

        async with db.database.pool.acquire() as conn:
            data = await conn.fetch(query, *params)
        return data
    except Exception as e:
        logging.error(
            f"[get_data_by_breed_count] An error occured while retrieving data by breed count for bar graph: {e}"
        )
        raise e

async def get_axie_parts(query: str) -> list:
    logging.info(["[get_axie_parts] Retrieving axie parts..."])
    try:
        async with db.database.pool.acquire() as conn:
            data = await conn.fetch(query)
        return data
    except Exception as e:
        logging.error(f"[get_axie_parts] An error occurred while retrieving axie parts: {e}")
        raise e