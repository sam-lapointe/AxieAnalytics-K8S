import logging
import asyncpg
import aiohttp
import json
import time
import asyncio
from asyncpg.exceptions import UniqueViolationError
from datetime import datetime, timezone
from parts import Part


axies_token = "0x32950db2a7164ae833121501c797d79e7b79d74c"
axie_levels = {
    "1": {"total_xp": 0, "level_up_xp": 100},
    "2": {"total_xp": 100, "level_up_xp": 210},
    "3": {"total_xp": 310, "level_up_xp": 430},
    "4": {"total_xp": 740, "level_up_xp": 740},
    "5": {"total_xp": 1480, "level_up_xp": 1140},
    "6": {"total_xp": 2620, "level_up_xp": 1640},
    "7": {"total_xp": 4260, "level_up_xp": 2260},
    "8": {"total_xp": 6520, "level_up_xp": 2980},
    "9": {"total_xp": 9500, "level_up_xp": 3810},
    "10": {"total_xp": 13310, "level_up_xp": 4760},
    "11": {"total_xp": 18070, "level_up_xp": 5830},
    "12": {"total_xp": 23900, "level_up_xp": 7010},
    "13": {"total_xp": 30910, "level_up_xp": 8320},
    "14": {"total_xp": 39230, "level_up_xp": 9760},
    "15": {"total_xp": 48990, "level_up_xp": 11310},
    "16": {"total_xp": 60300, "level_up_xp": 13010},
    "17": {"total_xp": 73310, "level_up_xp": 14830},
    "18": {"total_xp": 88140, "level_up_xp": 16780},
    "19": {"total_xp": 104920, "level_up_xp": 18870},
    "20": {"total_xp": 123790, "level_up_xp": 21090},
    "21": {"total_xp": 144880, "level_up_xp": 23460},
    "22": {"total_xp": 168340, "level_up_xp": 25950},
    "23": {"total_xp": 194290, "level_up_xp": 28600},
    "24": {"total_xp": 222890, "level_up_xp": 31380},
    "25": {"total_xp": 254270, "level_up_xp": 34300},
    "26": {"total_xp": 288570, "level_up_xp": 37380},
    "27": {"total_xp": 325950, "level_up_xp": 40590},
    "28": {"total_xp": 366540, "level_up_xp": 43950},
    "29": {"total_xp": 410490, "level_up_xp": 47470},
    "30": {"total_xp": 457960, "level_up_xp": 51130},
    "31": {"total_xp": 509090, "level_up_xp": 54940},
    "32": {"total_xp": 564030, "level_up_xp": 58910},
    "33": {"total_xp": 622940, "level_up_xp": 63020},
    "34": {"total_xp": 685960, "level_up_xp": 67300},
    "35": {"total_xp": 753260, "level_up_xp": 71720},
    "36": {"total_xp": 824980, "level_up_xp": 76300},
    "37": {"total_xp": 901280, "level_up_xp": 81040},
    "38": {"total_xp": 982320, "level_up_xp": 85940},
    "39": {"total_xp": 1068260, "level_up_xp": 91000},
    "40": {"total_xp": 1159260, "level_up_xp": 96210},
    "41": {"total_xp": 1255470, "level_up_xp": 101590},
    "42": {"total_xp": 1357060, "level_up_xp": 107130},
    "43": {"total_xp": 1464190, "level_up_xp": 112820},
    "44": {"total_xp": 1577010, "level_up_xp": 118700},
    "45": {"total_xp": 1695710, "level_up_xp": 124720},
    "46": {"total_xp": 1820430, "level_up_xp": 130920},
    "47": {"total_xp": 1951350, "level_up_xp": 137280},
    "48": {"total_xp": 2088630, "level_up_xp": 143800},
    "49": {"total_xp": 2232430, "level_up_xp": 150500},
    "50": {"total_xp": 2382930, "level_up_xp": 157370},
    "51": {"total_xp": 2540300, "level_up_xp": 164390},
    "52": {"total_xp": 2704690, "level_up_xp": 171600},
    "53": {"total_xp": 2876290, "level_up_xp": 178970},
    "54": {"total_xp": 3055260, "level_up_xp": 186520},
    "55": {"total_xp": 3241780, "level_up_xp": 194240},
    "56": {"total_xp": 3436020, "level_up_xp": 202120},
    "57": {"total_xp": 3638140, "level_up_xp": 210190},
    "58": {"total_xp": 3848330, "level_up_xp": 218430},
    "59": {"total_xp": 4066760, "level_up_xp": 226840},
    "60": {"total_xp": 4293600, "level_up_xp": 235430},
}


class Axie:
    """
    Represent an axie and provide methods to gather and store informationa about it.
    """

    def __init__(
        self,
        connection: asyncpg.Connection,
        api_key: str,
        transaction_hash: str,
        axie_id: int,
        sale_date: int,
    ):
        self.__connection = connection
        self.__api_key = api_key
        self.__transaction_hash = transaction_hash
        self.__axie_id = axie_id
        self.__sale_date = sale_date

    async def __get_axie_data(self) -> dict:
        logging.info(f"[__get_axie_data] Fetching axie {self.__axie_id} data...")
        api_url = "https://api-gateway.skymavis.com/graphql/axie-marketplace"
        headers = {
            "accept": "application/json, multipart/mixed",
            "content-type": "application/json",
            "x-api-key": self.__api_key,
        }
        query = f"""
        query GetAxieData($lastNDays: Int = 30) {{
            axie(axieId: {self.__axie_id}) {{
                earnedAxpStat(lastNDays: $lastNDays)
                bodyShape
                breedCount
                class
                title
                parts {{
                    id
                    stage
                    type
                }}
                image
                axpInfo {{
                    level
                    xp
                }}
                stage
            }}
        }}
        """

        body = {"query": query, "operationName": "GetAxieData", "variables": {}}

        retries = 3
        delay = 5  # Initial delay of 5 seconds before retrying.
        for attempt in range(1, retries + 1):
            try:
                async with aiohttp.ClientSession() as http_client:
                    async with http_client.post(
                        api_url, headers=headers, data=json.dumps(body)
                    ) as axie_data_response:
                        axie_data = await axie_data_response.json()
                return axie_data["data"]
            except Exception as e:
                logging.error(
                    f"[__get_axie_data] Attempt {attempt} failed fetching axie {self.__axie_id} data: {e}"
                )
                if attempt == retries:
                    logging.error(
                        f"[__get_axie_data] All {retries} attempts failed for fetching axie {self.__axie_id} data."
                    )
                    raise e
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff

    async def __get_axie_activities(self) -> list:
        logging.info(
            f"[__get_axie_activities] Fetching axie {self.__axie_id} activities..."
        )
        api_url = "https://api-gateway.skymavis.com/graphql/axie-marketplace"
        headers = {
            "accept": "application/json, multipart/mixed",
            "content-type": "application/json",
            "x-api-key": self.__api_key,
        }
        query = """
        query GetAxieActivities($tokenAddress: String!, $tokenId: BigDecimal, $size: Int!) {
            axieActivities: tokenActivities(
                tokenAddress: $tokenAddress
                tokenId: $tokenId
                size: $size
                activityTypes: [EvolveAxie, AscendAxie, BreedAxie, DevolveAxie]
            ) {
                ...ActivityCommonFields
                activityDetails {
                    ... on AxiePartUpdateActivity {
                        ...AxiePartUpdateActivityFields
                    }
                    ... on AscendAxieActivity {
                        ...AscendAxieActivityFields
                    }
                }
            }
        }

        fragment AxiePartUpdateActivityFields on AxiePartUpdateActivity {
            partType
            partStage
        }

        fragment AscendAxieActivityFields on AscendAxieActivity {
            level
        }

        fragment ActivityCommonFields on Activity {
            activityType
            createdAt
        }
        """

        body = {
            "query": query,
            "operationName": "GetAxieActivities",
            "variables": {
                "tokenId": self.__axie_id,
                "tokenAddress": axies_token,
                "size": 50,
            },
        }

        retries = 3
        delay = 5  # Initial delay of 5 seconds before retrying
        for attempt in range(1, retries + 1):
            try:
                async with aiohttp.ClientSession() as http_client:
                    async with http_client.post(
                        api_url, headers=headers, data=json.dumps(body)
                    ) as axie_activities_response:
                        axie_activities = await axie_activities_response.json()

                return axie_activities["data"]
            except Exception as e:
                logging.error(
                    f"[__get_axie_activities] Attempt {attempt} failed fetching axie {self.__axie_id} activities: {e}"
                )
                if attempt == retries:
                    logging.error(
                        f"[__get_axie_activities] All {retries} attempts failed for fetching axie {self.__axie_id} activities."
                    )
                    raise e
                asyncio.sleep(delay)
                delay *= 2  # Exponential backoff

    async def __estimate_axie_level(
        self, axie_axp_info: dict, earned_axp_stat: dict, axie_activities: list
    ) -> dict:
        """
        Estimate the axie level at the time of sale.

        Return the updated axie axp_info.
        """
        logging.info(
            f"[__estimate_axie_level] Estimating axie {self.__axie_id} level at time of sale..."
        )

        sale_date = datetime.fromtimestamp(self.__sale_date).date()
        today_date = datetime.now().date()

        new_axp_info = axie_axp_info.copy()

        if sale_date != today_date:
            # Sort the dictionary from most recent dates to older dates
            sorted_earnings = dict(
                sorted(earned_axp_stat.items(), key=lambda item: item[0], reverse=True)
            )

            # Sum all the sources of xp per date
            sorted_summed_earnings = {
                date: sum(item["xp"] for item in items)
                for date, items in sorted_earnings.items()
            }

            # Current axie xp
            axie_xp = (
                axie_levels[str(axie_axp_info["level"])]["total_xp"]
                + axie_axp_info["xp"]
            )

            # Substract xp from now up to (not included) the sale date.
            for date, xp in sorted_summed_earnings.items():
                # The earned xp date is after the sale date
                if datetime.strptime(date, "%Y-%m-%d").date() > sale_date:
                    axie_xp -= xp
                else:
                    break

            # Calculate the axie axp info at time of sell
            for level in range(axie_axp_info["level"], 0, -1):
                if axie_xp < axie_levels[str(level)]["total_xp"]:
                    continue
                else:
                    remaining_xp = axie_xp - axie_levels[str(level)]["total_xp"]
                    new_axp_info["level"] = level
                    new_axp_info["xp"] = remaining_xp
                    break

        for activity in axie_activities:
            # Ascension was made after sale
            if (
                activity["createdAt"] > self.__sale_date
                and activity["activityType"] == "AscendAxie"
            ):
                # Axie level is lower than previously calculated
                if activity["activityDetails"]["level"] - 1 < new_axp_info["level"]:
                    new_level = activity["activityDetails"]["level"] - 1
                    new_axp_info["level"] = new_level
                    new_axp_info["xp"] = axie_levels[str(new_level)]["level_up_xp"]
            elif activity["createdAt"] < self.__sale_date:
                break

        return new_axp_info

    async def __verify_breed_count(
        self, axie_breed_count: int, axie_activities: list
    ) -> int:
        """
        Verify the breed count at the time of sale.

        Return the updated breed count.
        """
        logging.info(
            f"[__verify_breed_count] Verifying axie {self.__axie_id} breed count at time of sale..."
        )

        new_breed_count = axie_breed_count

        for activity in axie_activities:
            # Breeding was made after sale
            if (
                activity["createdAt"] > self.__sale_date
                and activity["activityType"] == "BreedAxie"
            ):
                new_breed_count -= 1
                print("Decreased breed count by 1")
            elif activity["createdAt"] < self.__sale_date:
                break

        return new_breed_count

    async def __verify_parts_stage(
        self, axie_parts: dict, axie_activities: list
    ) -> dict:
        """
        Verify the parts stages at the time of sale.

        Return a list of the updated axie parts.
        """
        logging.info(
            f"[__verify_parts_stage] Verifying {self.__axie_id} parts stages at time of sale..."
        )

        new_axie_parts = axie_parts.copy()
        modified_parts = set()
        evolved_after_sale = False

        for activity in axie_activities:
            if (
                activity["activityType"] == "EvolveAxie"
                or activity["activityType"] == "DevolveAxie"
            ):
                activity_type = activity["activityType"]
                part_type = activity["activityDetails"]["partType"]
                part_stage = activity["activityDetails"]["partStage"]
                # Verify if the axie was evolved or devolved between now and time of sale.
                if activity["createdAt"] > self.__sale_date:
                    if activity_type == "EvolveAxie":
                        new_axie_parts[part_type]["stage"] = part_stage - 1
                        modified_parts.add(part_type)
                        evolved_after_sale = True
                    elif activity_type == "DevolveAxie":
                        new_axie_parts[part_type]["stage"] = part_stage + 1
                        modified_parts.add(part_type)
                # Verify if the axie was evolved within 4 days before the sale.
                elif activity["createdAt"] < self.__sale_date and activity[
                    "createdAt"
                ] >= (self.__sale_date - 345600):  # 345600 seconds = 4 days
                    if (
                        activity_type == "EvolveAxie"
                        and not evolved_after_sale
                        and part_type not in modified_parts
                    ):
                        """
                        This means the part was evolving at the time of sale.
                        Because no part was evolved after the sale and the part was not devolved either.
                        Set the part stage to the evolved stage.
                        """
                        new_axie_parts[part_type]["stage"] = part_stage
                        modified_parts.add(part_type)

                        #  We can break here since only one part can be evolved at a time.
                        break
                    elif activity_type == "DevolveAxie" and not evolved_after_sale:
                        """
                        This mean the part was devolved before the time of sale.
                        """
                        modified_parts.add(part_type)

        # Get the ID for the modified parts
        for modified_part in sorted(modified_parts):
            try:
                # Get the current part
                part = await Part.get_part(
                    self.__connection, new_axie_parts[modified_part]["id"]
                )
                if not part:
                    """
                    This means the part was not found in the database.
                    Will try to get the latest version of the parts and update the database.
                    """
                    logging.warning(
                        f"[__verify_parts_stage] Part {new_axie_parts[modified_part]['id']} not found in the database, trying to get the latest version..."
                    )
                    await Part.search_and_update_parts_latest_version(self.__connection)
                    part = await Part.get_part(
                        self.__connection, new_axie_parts[modified_part]["id"]
                    )
                    if not part:
                        logging.error(
                            f"[__verify_parts_stage] Part {new_axie_parts[modified_part]['id']} not found in the database after updating the parts."
                        )
                        raise ValueError(
                            f"Part {new_axie_parts[modified_part]['id']} not found in the database after updating the parts."
                        )

                # Update the part ID based on the stage at the time of sale.
                if part["stage"] < new_axie_parts[modified_part]["stage"]:
                    """
                    This means the part stage is currently 1, but was 2 at time of sell.
                    Either the part was devolved since the sale or was evolving at time of sell.
                    Set the part id to the normal stage 2.
                    """
                    new_axie_parts[modified_part]["id"] = f"{part['id']}-2"
                elif part["stage"] > new_axie_parts[modified_part]["stage"]:
                    """
                    This means the part stage is currently 2, but was 1 at time of sell.
                    The part was evolved since the sale.
                    Set the part id to stage 1.
                    """
                    new_axie_parts[modified_part]["id"] = part["previous_stage_part_id"]
            except Exception as e:
                logging.error(
                    f"[__verify_parts_stage] An error occured while retrieving {new_axie_parts[modified_part]['id']} from database: {e}"
                )
                raise e

        return new_axie_parts

    async def __store_axie_data(self, axie_data: dict) -> None:
        logging.info(f"[__store_axie_data] Storing axie {self.__axie_id} data...")

        current_time_utc = datetime.now(timezone.utc)

        try:
            async with self.__connection.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO axies (
                        transaction_hash,
                        axie_id,
                        sale_date,
                        level,
                        xp,
                        breed_count,
                        image_url,
                        class,
                        eyes_id,
                        ears_id,
                        mouth_id,
                        horn_id,
                        back_id,
                        tail_id,
                        body_shape_id,
                        collection_title,
                        created_at,
                        modified_at
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
                    """,
                    self.__transaction_hash,
                    self.__axie_id,
                    self.__sale_date,
                    axie_data["axie"]["axpInfo"]["level"],
                    axie_data["axie"]["axpInfo"]["xp"],
                    axie_data["axie"]["breedCount"],
                    f"https://axiecdn.axieinfinity.com/axies/{self.__axie_id}/axie/axie-full-transparent.png",
                    axie_data["axie"]["class"],
                    axie_data["axie"]["parts"]["Eyes"]["id"],
                    axie_data["axie"]["parts"]["Ears"]["id"],
                    axie_data["axie"]["parts"]["Mouth"]["id"],
                    axie_data["axie"]["parts"]["Horn"]["id"],
                    axie_data["axie"]["parts"]["Back"]["id"],
                    axie_data["axie"]["parts"]["Tail"]["id"],
                    axie_data["axie"]["bodyShape"],
                    axie_data["axie"]["title"],
                    current_time_utc,
                    current_time_utc,
                )
        except UniqueViolationError:
            logging.info(
                f"[__store_axie_data] Axie {self.__axie_id} already exists in the database. Skipping insertion."
            )
        except Exception as e:
            logging.error(
                f"[__store_axie_data] An error occurred while storing axie {self.__axie_id}:{axie_data} data: {e}"
            )
            raise e

        logging.info(
            f"[__store_axie_data] Axie {self.__axie_id} data stored successfully."
        )
        return None

    async def process_axie_data(self) -> None:
        logging.info(f"[process_axie_data] Processing axie {self.__axie_id}...")
        axie_data = await self.__get_axie_data()
        axie_activities = await self.__get_axie_activities()

        # Verify if the axie is an egg. Stage 1 means it is an egg.
        if axie_data["axie"]["stage"] == 1:
            logging.info(
                f"[process_axie_data] Axie {self.__axie_id} is an egg. Skipping processing."
            )
            return None

        # Change the parts data structure from list of dict to dict.
        parts = {
            part["type"]: {"id": part["id"], "stage": part["stage"]}
            for part in axie_data["axie"]["parts"]
        }
        axie_data["axie"]["parts"] = parts

        """ 
        The parts stages must be validated even if the sale was processed immediately.
        Since Axie parts take multiple days to evolve and only update the stage once completed.
        So even if the part is "evolving", we count it as evolved because the cost was paid by the seller.
        The part ID will be set to its normal part. It does not take into account parts evolution such as nightmare.
        """
        axie_parts = await self.__verify_parts_stage(
            axie_data["axie"]["parts"], axie_activities["axieActivities"]
        )
        axie_data["axie"]["parts"] = axie_parts

        # Verify if the sale was not made within the last 1 minute
        current_epoch = int(time.time())
        if current_epoch >= self.__sale_date + 60:
            logging.info(
                "[process_axie_data] The sale was not made within the last 60 seconds."
            )

            axie_axp_info = await self.__estimate_axie_level(
                axie_data["axie"]["axpInfo"],
                axie_data["axie"]["earnedAxpStat"],
                axie_activities["axieActivities"],
            )
            axie_breed_count = await self.__verify_breed_count(
                axie_data["axie"]["breedCount"], axie_activities["axieActivities"]
            )

            # Update the axie_data
            axie_data["axie"]["axpInfo"] = axie_axp_info
            axie_data["axie"]["breedCount"] = axie_breed_count

        await self.__store_axie_data(axie_data)

        logging.info(
            f"[process_axie_data] Axie {self.__axie_id} processed successfully."
        )
        return None
