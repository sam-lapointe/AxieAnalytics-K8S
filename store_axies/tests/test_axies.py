import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from axies import Axie


# Mock the database connection.
@pytest.fixture
def mock_connection(mocker):
    """Create a mock database connection."""
    return mocker.AsyncMock()


@pytest.fixture
def axie_instance(mock_connection):
    """Create an Axie instance with a mock connection."""
    return Axie(
        connection=mock_connection,
        api_key="test_api_key",
        transaction_hash="test_hash",
        axie_id=12345,
        sale_date=1740000000,
    )


@pytest.fixture
def axie_parts():
    """Fixture to provide axie parts for testing."""
    return {
        "Eyes": {
            "id": "eyes-telescope",
            "stage": 1,
        },
        "Ears": {
            "id": "ears-nimo",
            "stage": 1,
        },
        "Mouth": {
            "id": "mouth-little-owl",
            "stage": 1,
        },
        "Horn": {
            "id": "horn-eggshell-2",
            "stage": 2,
        },
        "Back": {
            "id": "back-pigeon-post",
            "stage": 1,
        },
        "Tail": {
            "id": "tail-hare-2",
            "stage": 2,
        },
    }


@pytest.fixture
def ears_obj():
    """Fixture to provide ears object for testing."""
    return {
        "id": "ears-nimo",
        "class": "aquatic",
        "name": "Nimo",
        "stage": 1,
        "previous_stage_part_id": None,
        "type": "ears",
        "special_genes": "",
        "created_at": datetime.now(timezone.utc),
        "modified_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def tail_obj():
    """Fixture to provide tail object for testing."""
    return {
        "id": "tail-hare-2",
        "class": "beast",
        "name": "Hare",
        "stage": 2,
        "previous_stage_part_id": "tail-hare",
        "type": "tail",
        "special_genes": "",
        "created_at": datetime.now(timezone.utc),
        "modified_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def eyes_obj():
    """Fixture to provide eyes object for testing."""
    return {
        "id": "eyes-telescope",
        "class": "aquatic",
        "name": "Telescope",
        "stage": 1,
        "previous_stage_part_id": None,
        "type": "eyes",
        "special_genes": "",
        "created_at": datetime.now(timezone.utc),
        "modified_at": datetime.now(timezone.utc),
    }


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (
            # Axie Sold Level 19Max -> Ascended -> Earned AXP (Different date than sale date) -> Processed Delayed
            {
                "sale_date": "",
                "axie_axp_info": {"level": 20, "xp": 12000},
                "earned_axp_stat": {
                    "2025-06-03": [
                        {"source_id": "7", "xp": 10000},
                    ],
                    "2025-06-02": [
                        {"source_id": "7", "xp": 2000},
                    ],
                },
                "axie_activities": [
                    {
                        # Ascended after sale date
                        "activityType": "AscendAxie",
                        "createdAt": 1741000000,
                        "activityDetails": {"level": 20},
                    },
                ],
            },
            {"level": 19, "xp": 18870},
        ),
        (
            # Axie Sold Level 19Max -> Ascended -> Processed Delayed
            {
                "sale_date": "",
                "axie_axp_info": {"level": 20, "xp": 0},
                "earned_axp_stat": {},
                "axie_activities": [
                    {
                        # Ascended after sale date
                        "activityType": "AscendAxie",
                        "createdAt": 1741000000,
                        "activityDetails": {"level": 20},
                    },
                ],
            },
            {"level": 19, "xp": 18870},
        ),
        (
            # Axie Sold Level 17 -> Earn AXP (Different date than sale date) up to Level 19Max -> Processed Delayed
            {
                "sale_date": "",
                "axie_axp_info": {"level": 19, "xp": 18870},
                "earned_axp_stat": {
                    "2025-06-03": [
                        {"source_id": "7", "xp": 10000},
                        {"source_id": "2", "xp": 480},
                    ],
                    "2025-06-02": [
                        {"source_id": "7", "xp": 2000},
                        {"source_id": "3", "xp": 5000},
                    ],
                    "2025-06-01": [
                        {"source_id": "7", "xp": 10000},
                        {"source_id": "4", "xp": 3000},
                    ],
                    "2025-05-31": [
                        {"source_id": "7", "xp": 10000},
                        {"source_id": "5", "xp": 2000},
                    ],
                },
                "axie_activities": [
                    {
                        # Ascended before sale date
                        "activityType": "AscendAxie",
                        "createdAt": 1739000000,
                        "activityDetails": {"level": 10},
                    },
                ],
            },
            {"level": 17, "xp": 8000},
        ),
        (
            # Axie Sold Level 19 -> Earn AXP (Same date as sale date) up to Level 19Max -> Ascended -> Earn AXP -> Processed Delayed
            {
                "sale_date": "",
                "axie_axp_info": {"level": 20, "xp": 12000},
                "earned_axp_stat": {
                    "2025-06-03": [
                        {"source_id": "7", "xp": 10000},
                        {"source_id": "2", "xp": 2000},
                    ],
                    # This is the date of the sale
                    "2025-02-19": [
                        {"source_id": "7", "xp": 8870},
                    ],
                },
                "axie_activities": [
                    {
                        # Ascended after sale date
                        "activityType": "AscendAxie",
                        "createdAt": 1741000000,
                        "activityDetails": {"level": 20},
                    },
                ],
            },
            # The AXP earned on the sale date is not counted towards the level estimation.
            {"level": 19, "xp": 18870},
        ),
        (
            # Axie Sold Level 29 -> Earn AXP (Same date as sale date) up to Level 29Max -> Ascended -> Processed Same Day
            {
                "sale_date": "today",
                "axie_axp_info": {"level": 30, "xp": 2000},
                "earned_axp_stat": {
                    "2025-02-19": [
                        {"source_id": "7", "xp": 10000},
                        {"source_id": "2", "xp": 2000},
                    ],
                },
                "axie_activities": [
                    {
                        # Ascended after sale
                        "activityType": "AscendAxie",
                        "createdAt": 1740000500,
                        "activityDetails": {"level": 30},
                    },
                ],
            },
            {"level": 29, "xp": 47470},
        ),
        (
            # Axie Sold Level 20 -> Processed Same Day
            {
                "sale_date": "today",
                "axie_axp_info": {"level": 20, "xp": 0},
                "earned_axp_stat": {},
                "axie_activities": [],
            },
            {"level": 20, "xp": 0},
        ),
    ],
)
@pytest.mark.asyncio
async def test_estimate_axie_level(monkeypatch, axie_instance, input, expected_result):
    """Test the estimate_axie_level method."""

    if input["sale_date"] == "today":
        # Mock today's date.
        mock_today_date = datetime(2025, 2, 19, 12, 0, 0, tzinfo=timezone.utc)
        monkeypatch.setattr("axies.datetime", mock_today_date)

    axp_info = await axie_instance._Axie__estimate_axie_level(
        axie_axp_info=input["axie_axp_info"],
        earned_axp_stat=input["earned_axp_stat"],
        axie_activities=input["axie_activities"],
    )

    assert axp_info == expected_result


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (
            # Breed -> Sale -> Breed -> Breed -> Process
            {
                "breed_count": 3,
                "axie_activities": [
                    {
                        # After sale
                        "activityType": "BreedAxie",
                        "createdAt": 1742000000,
                        "activityDetails": {},
                    },
                    {
                        # After sale
                        "activityType": "BreedAxie",
                        "createdAt": 1741000000,
                        "activityDetails": {},
                    },
                    {
                        # Before Sale
                        "activityType": "BreedAxie",
                        "createdAt": 1739000000,
                        "activityDetails": {},
                    },
                ],
            },
            1,
        ),
        (
            # Breed -> Sale -> Process
            {
                "breed_count": 1,
                "axie_activities": [
                    {
                        # Before sale
                        "activityType": "BreedAxie",
                        "createdAt": 1739000000,
                        "activityDetails": {},
                    },
                ],
            },
            1,
        ),
        (
            # Sale -> Process
            {
                "breed_count": 5,
                "axie_activities": [],
            },
            5,
        ),
    ],
)
@pytest.mark.asyncio
async def test_verify_breed_count(axie_instance, input, expected_result):
    """Test the verify_breed_count method."""

    breed_count = await axie_instance._Axie__verify_breed_count(
        input["breed_count"], input["axie_activities"]
    )

    assert breed_count == expected_result


@pytest.mark.parametrize(
    "axie_activities, expected_result",
    [
        (
            [],
            {
                "Eyes": {
                    "id": "eyes-telescope",
                    "stage": 1,
                },
                "Ears": {
                    "id": "ears-nimo",
                    "stage": 1,
                },
                "Mouth": {
                    "id": "mouth-little-owl",
                    "stage": 1,
                },
                "Horn": {
                    "id": "horn-eggshell-2",
                    "stage": 2,
                },
                "Back": {
                    "id": "back-pigeon-post",
                    "stage": 1,
                },
                "Tail": {
                    "id": "tail-hare-2",
                    "stage": 2,
                },
            },
        )
    ],
)
@pytest.mark.asyncio
async def test_verify_parts_stage_0_modified_part(
    monkeypatch, axie_instance, axie_parts, axie_activities, expected_result
):
    new_axie_parts = await axie_instance._Axie__verify_parts_stage(
        axie_parts, axie_activities
    )

    assert new_axie_parts == expected_result


@pytest.mark.parametrize(
    "axie_activities, expected_result",
    [
        (
            # Evolve Ears -> Devolve Ears -> Sale -> Process
            [
                {
                    "activityType": "DevolveAxie",
                    "createdAt": 1739900000,
                    "activityDetails": {"partType": "Ears", "partStage": 1},
                },
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1739800000,
                    "activityDetails": {"partType": "Ears", "partStage": 2},
                },
            ],
            {
                "Eyes": {
                    "id": "eyes-telescope",
                    "stage": 1,
                },
                "Ears": {
                    "id": "ears-nimo",
                    "stage": 1,
                },
                "Mouth": {
                    "id": "mouth-little-owl",
                    "stage": 1,
                },
                "Horn": {
                    "id": "horn-eggshell-2",
                    "stage": 2,
                },
                "Back": {
                    "id": "back-pigeon-post",
                    "stage": 1,
                },
                "Tail": {
                    "id": "tail-hare-2",
                    "stage": 2,
                },
            },
        ),
        (
            # Evolve Ears (Evolving) -> Sale -> Process
            [
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1739800000,
                    "activityDetails": {"partType": "Ears", "partStage": 2},
                },
            ],
            {
                "Eyes": {
                    "id": "eyes-telescope",
                    "stage": 1,
                },
                "Ears": {
                    "id": "ears-nimo-2",
                    "stage": 2,
                },
                "Mouth": {
                    "id": "mouth-little-owl",
                    "stage": 1,
                },
                "Horn": {
                    "id": "horn-eggshell-2",
                    "stage": 2,
                },
                "Back": {
                    "id": "back-pigeon-post",
                    "stage": 1,
                },
                "Tail": {
                    "id": "tail-hare-2",
                    "stage": 2,
                },
            },
        ),
        (
            # Sale -> Evolve Ears -> Devolve Ears -> Process
            [
                {
                    "activityType": "DevolveAxie",
                    "createdAt": 1742000000,
                    "activityDetails": {"partType": "Ears", "partStage": 1},
                },
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1741000000,
                    "activityDetails": {"partType": "Ears", "partStage": 2},
                },
            ],
            {
                "Eyes": {
                    "id": "eyes-telescope",
                    "stage": 1,
                },
                "Ears": {
                    "id": "ears-nimo",
                    "stage": 1,
                },
                "Mouth": {
                    "id": "mouth-little-owl",
                    "stage": 1,
                },
                "Horn": {
                    "id": "horn-eggshell-2",
                    "stage": 2,
                },
                "Back": {
                    "id": "back-pigeon-post",
                    "stage": 1,
                },
                "Tail": {
                    "id": "tail-hare-2",
                    "stage": 2,
                },
            },
        ),
        (
            # Evolve Ears (Evolving) -> Sale -> Devolve Ears -> Process
            [
                {
                    "activityType": "DevolveAxie",
                    "createdAt": 1741000000,
                    "activityDetails": {"partType": "Ears", "partStage": 1},
                },
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1739900000,
                    "activityDetails": {"partType": "Ears", "partStage": 2},
                },
            ],
            {
                "Eyes": {
                    "id": "eyes-telescope",
                    "stage": 1,
                },
                "Ears": {
                    "id": "ears-nimo-2",
                    "stage": 2,
                },
                "Mouth": {
                    "id": "mouth-little-owl",
                    "stage": 1,
                },
                "Horn": {
                    "id": "horn-eggshell-2",
                    "stage": 2,
                },
                "Back": {
                    "id": "back-pigeon-post",
                    "stage": 1,
                },
                "Tail": {
                    "id": "tail-hare-2",
                    "stage": 2,
                },
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_verify_parts_stage_1_modified_part_stage_1(
    monkeypatch,
    mocker,
    axie_instance,
    ears_obj,
    axie_parts,
    axie_activities,
    expected_result,
):
    """Test the verify_parts_stage method with 1 modified part that is currently at stage 1."""

    get_part_mock = mocker.AsyncMock(side_effect=[ears_obj])
    monkeypatch.setattr("axies.Part.get_part", get_part_mock)

    new_axie_parts = await axie_instance._Axie__verify_parts_stage(
        axie_parts, axie_activities
    )

    assert new_axie_parts == expected_result


@pytest.mark.parametrize(
    "axie_activities, expected_result",
    [
        (
            # Evolve Ears -> Sale -> Evolve Tail -> Devolve Ears-> Process
            [
                {
                    "activityType": "DevolveAxie",
                    "createdAt": 1742000000,
                    "activityDetails": {"partType": "Ears", "partStage": 1},
                },
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1741000000,
                    "activityDetails": {"partType": "Tail", "partStage": 2},
                },
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1739900000,
                    "activityDetails": {"partType": "Ears", "partStage": 2},
                },
            ],
            {
                "Eyes": {
                    "id": "eyes-telescope",
                    "stage": 1,
                },
                "Ears": {
                    "id": "ears-nimo-2",
                    "stage": 2,
                },
                "Mouth": {
                    "id": "mouth-little-owl",
                    "stage": 1,
                },
                "Horn": {
                    "id": "horn-eggshell-2",
                    "stage": 2,
                },
                "Back": {
                    "id": "back-pigeon-post",
                    "stage": 1,
                },
                "Tail": {
                    "id": "tail-hare",
                    "stage": 1,
                },
            },
        ),
        (
            # Evolve Tail -> Evolve Ears (Evolving) -> Sale -> Process
            [
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1739900000,
                    "activityDetails": {"partType": "Ears", "partStage": 2},
                },
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1739800000,
                    "activityDetails": {"partType": "Tail", "partStage": 2},
                },
            ],
            {
                "Eyes": {
                    "id": "eyes-telescope",
                    "stage": 1,
                },
                "Ears": {
                    "id": "ears-nimo-2",
                    "stage": 2,
                },
                "Mouth": {
                    "id": "mouth-little-owl",
                    "stage": 1,
                },
                "Horn": {
                    "id": "horn-eggshell-2",
                    "stage": 2,
                },
                "Back": {
                    "id": "back-pigeon-post",
                    "stage": 1,
                },
                "Tail": {
                    "id": "tail-hare-2",
                    "stage": 2,
                },
            },
        ),
        (
            # Sale -> Evolve Tail -> Evolve Ears (Evolving) -> Process
            [
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1742000000,
                    "activityDetails": {"partType": "Ears", "partStage": 2},
                },
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1741000000,
                    "activityDetails": {"partType": "Tail", "partStage": 2},
                },
            ],
            {
                "Eyes": {
                    "id": "eyes-telescope",
                    "stage": 1,
                },
                "Ears": {
                    "id": "ears-nimo",
                    "stage": 1,
                },
                "Mouth": {
                    "id": "mouth-little-owl",
                    "stage": 1,
                },
                "Horn": {
                    "id": "horn-eggshell-2",
                    "stage": 2,
                },
                "Back": {
                    "id": "back-pigeon-post",
                    "stage": 1,
                },
                "Tail": {
                    "id": "tail-hare",
                    "stage": 1,
                },
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_verify_parts_stage_2_modified_parts_both_stages(
    monkeypatch,
    mocker,
    axie_instance,
    ears_obj,
    tail_obj,
    axie_parts,
    axie_activities,
    expected_result,
):
    """Test the verify_parts_stage method with 2 modified parts, one at stage 1 and the other at stage 2."""

    # Must be careful with the order of the mock calls, as the first call will be for ears_obj and the second for tail_obj.
    get_part_mock = mocker.AsyncMock(side_effect=[ears_obj, tail_obj])
    monkeypatch.setattr("axies.Part.get_part", get_part_mock)

    new_axie_parts = await axie_instance._Axie__verify_parts_stage(
        axie_parts, axie_activities
    )

    assert new_axie_parts == expected_result


@pytest.mark.parametrize(
    "axie_activities, expected_result",
    [
        (
            # Sale -> Evolve Ears -> Evolve Eyes (Evolving) -> Devolve Ears -> Process
            [
                {
                    "activityType": "DevolveAxie",
                    "createdAt": 1743000000,
                    "activityDetails": {"partType": "Ears", "partStage": 1},
                },
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1742000000,
                    "activityDetails": {"partType": "Eyes", "partStage": 2},
                },
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1741000000,
                    "activityDetails": {"partType": "Ears", "partStage": 2},
                },
            ],
            {
                "Eyes": {
                    "id": "eyes-telescope",
                    "stage": 1,
                },
                "Ears": {
                    "id": "ears-nimo",
                    "stage": 1,
                },
                "Mouth": {
                    "id": "mouth-little-owl",
                    "stage": 1,
                },
                "Horn": {
                    "id": "horn-eggshell-2",
                    "stage": 2,
                },
                "Back": {
                    "id": "back-pigeon-post",
                    "stage": 1,
                },
                "Tail": {
                    "id": "tail-hare-2",
                    "stage": 2,
                },
            },
        ),
        (
            # Evolve Ears -> Evolve Eyes (Evolving) -> Devolve Ears -> Sale -> Process
            [
                {
                    "activityType": "DevolveAxie",
                    "createdAt": 1739900000,
                    "activityDetails": {"partType": "Ears", "partStage": 1},
                },
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1739800000,
                    "activityDetails": {"partType": "Eyes", "partStage": 2},
                },
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1739700000,
                    "activityDetails": {"partType": "Ears", "partStage": 2},
                },
            ],
            {
                "Eyes": {
                    "id": "eyes-telescope-2",
                    "stage": 2,
                },
                "Ears": {
                    "id": "ears-nimo",
                    "stage": 1,
                },
                "Mouth": {
                    "id": "mouth-little-owl",
                    "stage": 1,
                },
                "Horn": {
                    "id": "horn-eggshell-2",
                    "stage": 2,
                },
                "Back": {
                    "id": "back-pigeon-post",
                    "stage": 1,
                },
                "Tail": {
                    "id": "tail-hare-2",
                    "stage": 2,
                },
            },
        ),
        (
            # Evolve Ears -> Evolve Eyes (Evolving) -> Sale -> Devolve Ears -> Process
            [
                {
                    "activityType": "DevolveAxie",
                    "createdAt": 1741000000,
                    "activityDetails": {"partType": "Ears", "partStage": 1},
                },
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1739900000,
                    "activityDetails": {"partType": "Eyes", "partStage": 2},
                },
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1739800000,
                    "activityDetails": {"partType": "Ears", "partStage": 2},
                },
            ],
            {
                "Eyes": {
                    "id": "eyes-telescope-2",
                    "stage": 2,
                },
                "Ears": {
                    "id": "ears-nimo-2",
                    "stage": 2,
                },
                "Mouth": {
                    "id": "mouth-little-owl",
                    "stage": 1,
                },
                "Horn": {
                    "id": "horn-eggshell-2",
                    "stage": 2,
                },
                "Back": {
                    "id": "back-pigeon-post",
                    "stage": 1,
                },
                "Tail": {
                    "id": "tail-hare-2",
                    "stage": 2,
                },
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_verify_parts_stage_2_modified_parts_stage_1(
    monkeypatch,
    mocker,
    axie_instance,
    ears_obj,
    eyes_obj,
    axie_parts,
    axie_activities,
    expected_result,
):
    """Test the verify_parts_stage method with 2 modified parts, both at stage 1."""

    # Must be careful with the order of the mock calls, as the first call will be for ears_obj and the second for eyes_obj.
    get_part_mock = mocker.AsyncMock(side_effect=[ears_obj, eyes_obj])
    monkeypatch.setattr("axies.Part.get_part", get_part_mock)

    new_axie_parts = await axie_instance._Axie__verify_parts_stage(
        axie_parts, axie_activities
    )

    assert new_axie_parts == expected_result


@pytest.mark.parametrize(
    "axie_activities, expected_result",
    [
        (
            # Sale -> Evolve Ears (Evolving) -> Process
            [
                {
                    "activityType": "EvolveAxie",
                    "createdAt": 1741000000,
                    "activityDetails": {"partType": "Ears", "partStage": 2},
                },
            ],
            {
                "Eyes": {
                    "id": "eyes-telescope",
                    "stage": 1,
                },
                "Ears": {
                    "id": "ears-nimo",
                    "stage": 1,
                },
                "Mouth": {
                    "id": "mouth-little-owl",
                    "stage": 1,
                },
                "Horn": {
                    "id": "horn-eggshell-2",
                    "stage": 2,
                },
                "Back": {
                    "id": "back-pigeon-post",
                    "stage": 1,
                },
                "Tail": {
                    "id": "tail-hare-2",
                    "stage": 2,
                },
            },
        )
    ],
)
@pytest.mark.asyncio
async def test_verify_parts_stage_part_not_found(
    monkeypatch,
    mocker,
    axie_instance,
    ears_obj,
    axie_parts,
    axie_activities,
    expected_result,
):
    """Test the verify_parts_stage method when a part is not found and then found after update."""

    # Mock the Part.get_part method to return None the first time and the ears_obj the second time.
    get_part_mock = mocker.AsyncMock(side_effect=[None, ears_obj])
    monkeypatch.setattr("axies.Part.get_part", get_part_mock)
    monkeypatch.setattr(
        "axies.Part.search_and_update_parts_latest_version", mocker.AsyncMock()
    )

    new_axie_parts = await axie_instance._Axie__verify_parts_stage(
        axie_parts, axie_activities
    )

    assert new_axie_parts == expected_result


@pytest.mark.asyncio
async def test_verify_parts_stage_part_not_found_after_update(
    monkeypatch, mocker, axie_instance, axie_parts
):
    axie_activities = [
        {
            "activityType": "EvolveAxie",
            "createdAt": 1741000000,
            "activityDetails": {"partType": "Ears", "partStage": 2},
        },
    ]

    # Mock the Part.get_part method to return None after update.
    get_part_mock = mocker.AsyncMock(side_effect=[None, None])
    monkeypatch.setattr("axies.Part.get_part", get_part_mock)
    monkeypatch.setattr(
        "axies.Part.search_and_update_parts_latest_version", mocker.AsyncMock()
    )

    with pytest.raises(ValueError):
        await axie_instance._Axie__verify_parts_stage(axie_parts, axie_activities)
