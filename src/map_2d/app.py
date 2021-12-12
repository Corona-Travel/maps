from fastapi import FastAPI, Depends
from json import loads
from logging import getLogger

import httpx

from .types import Marker2D, Markers2D
from .settings import Settings, get_settings

app = FastAPI(openapi_tags=[{"name": "service:map2D"}])

logger = getLogger("service:map2D")


@app.get("/map/2D", response_model=Markers2D, tags=["service:map2D"])
async def map2D(settings: Settings = Depends(get_settings)):
    logger.debug("searching for 2D markers")
    async with httpx.AsyncClient() as client:
        markers = loads((await client.get(f"{settings.places_url}places")).text)
        res = []
        for marker in markers:
            res.append(
                Marker2D(
                        name=marker["name"],
                        place_id=marker["place_id"],
                        pos=marker["pos"],
                )
            )
        return res
