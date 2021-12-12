import asyncio
from json import loads
from logging import getLogger
from typing import Any, Awaitable, Callable

import httpx
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .settings import Settings, get_settings
from .types import Marker3D, Markers3D, Position

app = FastAPI(openapi_tags=[{"name": "service:map3D"}])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger = getLogger("service:map3D")


def type_obj2id(obj_type: str, obj: Any) -> str:
    if obj_type == "fact":
        return obj["fact_id"]
    elif obj_type == "quiz":
        return obj["quiz_id"]
    elif obj_type == "media":
        return obj["media_id"]


async def get_url(url_type_and_string: tuple[str, str]) -> Markers3D:
    url_type, url = url_type_and_string

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        # if response.status_code != 200:
        #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        objects = [obj for obj in loads(response.text)]

        res = [
            Marker3D(
                type=url_type,
                name=obj["name"],
                pos=obj["pos"],
                marker_id=type_obj2id(url_type, obj),
            )
            for obj in objects
        ]
    return res


@app.get("/map/3D/{lng}/{lat}", response_model=Markers3D, tags=["service:map3D"])
async def map3D(
    lng: float,
    lat: float,
    max_distance: float = 10000,
    settings: Settings = Depends(get_settings),
):
    type2url: dict[str, str] = {
        "fact": f"{settings.facts_url}facts/near/{lng}/{lat}?max_dist={max_distance}",
        "quiz": f"{settings.quizzes_url}quizzes/near/{lng}/{lat}?max_dist={max_distance}",
    }

    markers: Markers3D = [
        marker
        for markers in await asyncio.gather(*map(get_url, type2url.items()))
        for marker in markers
    ]
    return markers
