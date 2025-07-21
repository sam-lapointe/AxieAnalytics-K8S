from pydantic import BaseModel, RootModel, Field, field_validator, model_validator
from typing import Literal, List, Dict, Annotated, Optional

Axie_Classes = Literal[
    "Beast",
    "Aquatic",
    "Plant",
    "Bug",
    "Bird",
    "Reptile",
    "Mech",
    "Dawn",
    "Dusk"
]

Axie_Collection_Parts = Literal[
    "Mystic",
    "Summer",
    "Japan",
    "Shiny",
    "Xmas",
    "Nightmare",
]

Axie_Collection_Titles = Literal[
    "MEO Corp",
    "MEO Corp II",
    "Origin",
    "AgamoGenesis",
]

Axie_Parts = Literal[
    "eyes",
    "ears",
    "mouth",
    "horn",
    "back",
    "tail",
    "body",
]

Sort_By = Literal[
    "latest",
    "lowest_price",
    "highest_price",
    "lowest_level",
    "highest_level",
]


def validate_two_number_range(
    v: List[int], 
    min_allowed: int, 
    max_allowed: int, 
    field_name: str = "value"
) -> List[int]:
    if len(v) != 2:
        raise ValueError(f"{field_name} must contain exactly two integers.")
    low, high = v
    if not (min_allowed <= low <= max_allowed and min_allowed <= high <= max_allowed):
        raise ValueError(f"Each element in {field_name} must be between {min_allowed} and {max_allowed}.")
    if low > high:
        raise ValueError(f"The first element in {field_name} must be less than or equal to the second element.")
    return v


class CollectionFilter(BaseModel):
    partCollection: Optional[Axie_Collection_Parts] = None
    numParts: Optional[List[int]] = None
    title: Optional[Axie_Collection_Titles] = None
    special: Optional[Literal["Any Collection", "No Collection"]] = None

    @field_validator("numParts", mode="before")
    @classmethod
    def validate_num_parts(cls, v, values):
        if values.data.get("partCollection") and v is not None:
            return validate_two_number_range(v, 1, 6, "numParts")
        return v
    
    @model_validator(mode="after")
    def only_one_field(self):
        fields = [self.partCollection, self.title, self.special]
        if sum(field is not None for field in fields) != 1:
            raise ValueError("Exactly one of partCollection, title, or special must be set.")
        return self
    
    @model_validator(mode="after")
    def set_default_num_parts(self):
        if self.partCollection and self.numParts is None:
            self.numParts = [1, 6]
        return self


class CollectionDetail(BaseModel):
    numParts: Annotated[List[int], Field(default_factory=lambda: [1, 6])]

    @field_validator("numParts")
    @classmethod
    def validate_num_parts(cls, v):
        return validate_two_number_range(v, 1, 6, "numParts")


class CollectionWrapper(RootModel[Dict[Axie_Collection_Parts, CollectionDetail]]):
    @field_validator("root")
    @classmethod
    def one_key_only(cls, v):
        if len(v) != 1:
            raise ValueError("Each collection item must have exactly one key.")
        return v


class AxieSalesSearch(BaseModel):
    time_unit: Literal["days", "hours"] = "days"
    time_num: Annotated[int, Field(default=30, gt=0, lt=366)]
    limit: Annotated[Optional[int], Field(default=None, ge=1, le=250)]
    offset: Annotated[Optional[int], Field(default=0, ge=0)]
    include_parts: Annotated[Dict[Axie_Parts, List[str]], Field(default_factory=list)]
    exclude_parts: Annotated[Dict[Axie_Parts, List[str]], Field(default_factory=list)]
    axie_class: Annotated[List[Axie_Classes], Field(default_factory=list)]
    level: Annotated[List[int], Field(default_factory=lambda: [1, 60])]
    breed_count: Annotated[List[int], Field(default_factory=lambda: [0, 7])]
    evolved_parts_count: Annotated[List[int], Field(default_factory=lambda: [0, 6])]
    collections: Annotated[List[CollectionFilter], Field(default_factory=list)]
    sort_by: Annotated[Sort_By, Field(default="latest")]

    @field_validator("level")
    @classmethod
    def validate_level(cls, v):
        return validate_two_number_range(v, 1, 60, "level")
    
    @field_validator("breed_count")
    @classmethod
    def validate_breed_count(cls, v):
        return validate_two_number_range(v, 0, 7, "breed_count")
    
    @field_validator("evolved_parts_count")
    @classmethod
    def validate_evolved_parts_count(cls, v):
        return validate_two_number_range(v, 0, 6, "evolved_parts_count")
    
    @model_validator(mode="after")
    def special_collection_exclusive(self):
        specials = [c for c in self.collections if c.special is not None]
        if specials and len(self.collections) > 1:
            raise ValueError("If a special collection is set, no other collections can be set.")
        return self

    @model_validator(mode="after")
    def clean_empty_parts(self):
        # Remove keys with empty lists
        if self.include_parts:
            self.include_parts = {k: v for k, v in self.include_parts.items() if v}
        if self.exclude_parts:
            self.exclude_parts = {k: v for k, v in self.exclude_parts.items() if v}
        return self