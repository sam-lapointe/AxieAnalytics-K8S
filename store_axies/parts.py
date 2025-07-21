import logging
import asyncpg
import aiohttp
from datetime import datetime, timedelta, timezone


class Part:
    @staticmethod
    async def get_part(connection: asyncpg.Connection, part_id: str) -> dict:
        logging.info(f"[get_part] Fetching data for part {part_id} from database...")
        try:
            async with connection.acquire() as conn:
                part = await conn.fetchrow(
                    "SELECT * FROM axie_parts WHERE id = $1", part_id
                )
            return part
        except Exception as e:
            logging.error(
                f"[get_part] An error occured while fetching part {part_id}: {e}"
            )
            raise e

    @staticmethod
    async def get_current_version(connection: asyncpg.Connection) -> str | None:
        async with connection.acquire() as conn:
            logging.info(
                "[get_current_version] Fetching the current version of parts from database..."
            )
            try:
                result = await conn.fetchrow("SELECT version FROM versions LIMIT 1")
                if result:
                    return result["version"]
                else:
                    logging.info(
                        "[get_current_version] No version found in the database."
                    )
                    return None
            except Exception as e:
                logging.error(
                    f"[get_current_version] An error occurred while fetching the current version: {e}"
                )
                raise e

    @staticmethod
    async def search_parts_update(
        connection: asyncpg.Connection, days: int = 90, current_version: str = None
    ) -> tuple[str | None, str | None, dict]:
        """
        This method should be used on demand to verify if there was an update to the parts from Axie Infinity today.
        """
        logging.info(
            f"[search_parts_update] Verifying if there was an update to Axies parts in the last {days} days..."
        )
        today_date = datetime.now().date()
        current_version_date = (
            datetime.strptime(current_version, "%Y%m%d").date()
            if current_version
            else datetime.min.date()
        )

        try:
            for i in range(0, days + 1):
                date = today_date - timedelta(days=i)
                date_str = date.strftime("%Y%m%d")

                if current_version_date > date:
                    logging.info(
                        "[search_parts_update] Stopping the search, current version is up to date."
                    )
                    return None, None, {}

                parts_url = f"https://cdn.axieinfinity.com/game/origin-cards/base/origin-cards-data-{date_str}/part_data.json"
                async with aiohttp.ClientSession() as http_client:
                    async with http_client.get(parts_url) as axie_parts_response:
                        if axie_parts_response.status != 404:
                            logging.info(
                                "[search_parts_update] There is a new update to parts, returning it..."
                            )
                            axie_parts = await axie_parts_response.json()
                            return parts_url, date_str, axie_parts

            logging.info(
                f"[search_parts_update] No new parts update was found in the last {days} days."
            )
            return None, None, {}
        except Exception as e:
            logging.error(
                f"[search_parts_update] An error occured while fetching the list of parts: {e}"
            )
            raise e

    @staticmethod
    async def update_parts(
        connection: asyncpg.Connection, date: str, parts: dict
    ) -> None:
        logging.info("[update_parts] Updating the axie_parts table...")

        # Update the current version of parts
        for key, value in parts.items():
            try:
                part_id = value["part_id"]
                part_class = value["class"]
                part_name = value["name"]
                part_stage = value["part_stage"]
                previous_stage_part_id = (
                    None
                    if value["stage_part_ids"][0] == part_id
                    else value["stage_part_ids"][0]
                )
                part_type = value["type"]
                special_genes = value["special_genes"]
                current_time_utc = datetime.now(timezone.utc)

                # In the list of parts from Axie Infinity, the Shiny parts are set in the name instead of special_genes.
                if "shiny" in part_name.lower():
                    special_genes = special_genes + "_shiny"

                async with connection.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO axie_parts (
                            id, class, name, stage, previous_stage_part_id, type, special_genes, created_at, modified_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                        ON CONFLICT (id) DO UPDATE SET
                            class = EXCLUDED.class,
                            name = EXCLUDED.name,
                            stage = EXCLUDED.stage,
                            previous_stage_part_id = EXCLUDED.previous_stage_part_id,
                            type = EXCLUDED.type,
                            special_genes = EXCLUDED.special_genes,
                            modified_at = EXCLUDED.modified_at
                        """,
                        part_id,
                        part_class,
                        part_name,
                        part_stage,
                        previous_stage_part_id,
                        part_type,
                        special_genes,
                        current_time_utc,
                        current_time_utc,
                    )
                logging.info(
                    f"[update_parts] Updated or inserted part {part_id} successfully."
                )
            except Exception as e:
                logging.error(
                    f"[update_parts] An error occurred while updating/inserting part {part_id}: {e}"
                )
                raise e

        # Update the version of parts
        try:
            current_time_utc = datetime.now(timezone.utc)
            logging.info(f"[update_parts] Updating the version of parts to {date}...")

            # Insert or update the version in the versions table
            async with connection.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO versions (id, version, created_at, modified_at)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (id) DO UPDATE SET
                        version = EXCLUDED.version,
                        modified_at = EXCLUDED.modified_at
                    """,
                    "axie_parts_version",
                    date,
                    current_time_utc,
                    current_time_utc,
                )
            logging.info(f"[update_parts] Updated the version of parts to {date}.")
        except Exception as e:
            logging.error(
                f"[update_parts] An error occurred while updating the version of parts: {e}"
            )
            raise e

        logging.info("[update_parts] All parts updated successfully.")
        return None

    @staticmethod
    async def search_and_update_parts_latest_version(
        connection: asyncpg.Connection,
    ) -> None:
        """
        This method should be used to get the latest version of parts from Axie Infinity and update the database.
        """
        logging.info(
            "[get_and_update_parts_latest_version] Fetching the latest version of parts..."
        )
        current_version = await Part.get_current_version(connection)

        if not current_version:
            logging.info(
                "[get_and_update_parts_latest_version] No current version of parts found in the database, fetching the latest version..."
            )
            (
                latest_parts_url,
                latest_version_date,
                axie_parts,
            ) = await Part.search_parts_update(connection, days=90)
            if latest_parts_url:
                logging.info(
                    f"[get_and_update_parts_latest_version] Latest parts URL: {latest_parts_url}, Date: {latest_version_date}"
                )
                await Part.update_parts(connection, latest_version_date, axie_parts)
            else:
                logging.info(
                    "[get_and_update_parts_latest_version] No new parts update found."
                )
                raise ValueError(
                    "No current version of parts found in the database and no new parts update found."
                )
        else:
            logging.info(
                f"[get_and_update_parts_latest_version] Current version of parts is {current_version}. Looking for updates..."
            )
            (
                latest_parts_url,
                latest_version_date,
                axie_parts,
            ) = await Part.search_parts_update(
                connection, days=90, current_version=current_version
            )
            if latest_parts_url:
                logging.info(
                    f"[get_and_update_parts_latest_version] Latest parts URL: {latest_parts_url}, Date: {latest_version_date}"
                )
                await Part.update_parts(connection, latest_version_date, axie_parts)
            else:
                logging.info(
                    "[get_and_update_parts_latest_version] No new parts update found."
                )

        logging.info(
            "[get_and_update_parts_latest_version] Parts update process completed."
        )
        return None
