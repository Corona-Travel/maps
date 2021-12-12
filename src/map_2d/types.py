from typing import List, NamedTuple

from pydantic import BaseModel


class Position(NamedTuple):
    lat: float
    lng: float


class Marker2D(BaseModel):
    name: str
    place_id: str
    pos: Position


Markers2D = List[Marker2D]
