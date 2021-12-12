from enum import Enum
from typing import List, NamedTuple, Tuple

from pydantic import BaseModel


class Position(NamedTuple):
    lng: float
    lat: float


class Marker3DType(str, Enum):
    fact = "fact"
    media = "media"
    quiz = "quiz"


class Marker3D(BaseModel):
    name: str
    marker_id: str
    type: Marker3DType
    pos: Position


Markers3D = List[Marker3D]
