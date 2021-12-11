from json import loads
import asyncio
from typing import Any, Awaitable, Callable
from logging import getLogger

from fastapi import FastAPI, Depends, HTTPException, status
import httpx

from .types import Marker3D, Markers3D, Position
from .settings import Settings, get_settings

app = FastAPI(openapi_tags=[{"name": "service:map3D"}])

logger = getLogger("service:map3D")

max_distance = 100


def type_obj2id(obj_type: str, obj: Any) -> str:
    if obj_type == "fact":
        return obj["fact_id"]
    if obj_type == "quiz":
        return obj["quiz_id"]
    if obj_type == "media":
        return obj["media_id"]


def get_url_factory(
    position: Position, distance: float
) -> Callable[[tuple[str, str]], Awaitable[Markers3D]]:
    async def get_url(url_type_and_string: tuple[str, str]) -> Markers3D:
        url_type, url = url_type_and_string

        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        # if response.status_code != 200:
        #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        objs = loads(response.text)

        objects = [
            o for o in objs
        ]

        res = [
            Marker3D(
                type=url_type,
                name=o["name"],
                marker_id=type_obj2id(url_type, o),
                pos=o["pos"],
            )
            for o in objects
        ]
        return res

    return get_url


@app.get("/map/3D/{lng}/{lat}", response_model=Markers3D, tags=["service:map3D"])
async def map3D(
    lng: float,
    lat: float,
    distance: float = 20,
    settings: Settings = Depends(get_settings)
):
    type2url: dict[str, str] = {
        "fact": f"{settings.facts_url}/facts/near/{lng}/{lat}?max_dist={max_distance}",
        "quiz": f"{settings.quizes_url}/quizzes/near/{lng}/{lat}?max_dist={max_distance}",
        "media_url": f"{settings.media_url}/media/near/{lng}/{lat}?max_dist={max_distance}"
    }
    cur_position = Position(lat=lat, lng=lng)

    markers: Markers3D = [
        marker
        for markers in await asyncio.gather(
            *map(get_url_factory(cur_position, distance), type2url.items())
        )
        for marker in markers
    ]
    return markers