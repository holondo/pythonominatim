import asyncio
from typing import Union, List, Dict, Optional
from pydantic import BaseModel, field_validator, AnyHttpUrl
from loguru import logger
import aiohttp
from pythonominatim.model.location import Location


class SearchParams(BaseModel):
    """Search parameters for the Nominatim API."""

    # Query parameters
    q: Optional[str] = None
    amenity: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postalcode: Optional[str] = None

    # Output format
    format: str = "jsonv2"
    json_callback: Optional[str] = None

    # Output details
    addressdetails: int = 0
    extratags: int = 0
    namedetails: int = 0

    # Result restrictions
    limit: int = 10
    countrycodes: Optional[str] = None
    layer: Optional[str] = None
    featureType: Optional[str] = None
    exclude_place_ids: Optional[str] = None
    viewbox: Optional[str] = None
    bounded: int = 0

    # Polygon output
    polygon_geojson: int = 0
    polygon_kml: int = 0
    polygon_svg: int = 0
    polygon_text: int = 0
    polygon_threshold: float = 0.0

    # Other
    dedupe: int = 1
    debug: int = 0

    @field_validator("format")
    def validate_format(cls, value: str) -> str:
        """Validate the output format."""
        allowed_formats = ["xml", "json", "jsonv2", "geojson", "geocodejson"]
        if value not in allowed_formats:
            raise ValueError(f"Invalid format. Choose from: {allowed_formats}")
        return value

    @field_validator("limit")
    def validate_limit(cls, value: int) -> int:
        """Validate the result limit."""
        if not (1 <= value <= 40):
            raise ValueError("Limit must be between 1 and 40.")
        return value

    @field_validator(
        "addressdetails", "extratags", "namedetails", "bounded", "dedupe", "debug"
    )
    def validate_zero_one(cls, value: int) -> int:
        """Validate if the value is 0 or 1."""
        if value not in (0, 1):
            raise ValueError("Value must be 0 or 1.")
        return value

    @field_validator("viewbox")
    def validate_viewbox(cls, value: Optional[str]) -> Optional[str]:
        """Validate the viewbox format."""
        if value:
            coords = value.split(",")
            if len(coords) != 4:
                raise ValueError("Viewbox must have four comma-separated values.")
            try:
                coords = [float(coord) for coord in coords]
            except ValueError:
                raise ValueError("Viewbox coordinates must be floating-point numbers.")
        return value


class NominatimSearch:
    """Asynchronous helper for the Nominatim search API."""

    def __init__(
        self,
        base_url: AnyHttpUrl = "https://nominatim.openstreetmap.org/search",
        user_agent: Optional[str] = None,
        email: Optional[str] = None,
    ):
        self.base_url = base_url
        self.user_agent = user_agent
        self.email = email

    async def search(self, params: Union[str, Dict, SearchParams]) -> List[Location]:
        """Perform an asynchronous search on the Nominatim API."""

        if isinstance(params, str):
            params = SearchParams(q=params)

        elif isinstance(params, dict):
            params = SearchParams(**params)
        elif not isinstance(params, SearchParams):
            raise TypeError("Invalid parameters. Must be str, dict, or SearchParams.")

        headers = {}
        if self.user_agent:
            headers["User-Agent"] = self.user_agent

        params_dict = params.model_dump(exclude_none=True, exclude_unset=True)
        params_dict.update({"format": "jsonv2"})

        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.base_url,
                params=params_dict,
                headers=headers,
            ) as response:
                logger.info(f"Request made to {response.url}")
                if response.status == 200:
                    data = await response.json()
                    return [Location(**item) for item in data]
                else:
                    logger.error(
                        f"Request error: {response.status} - {response.reason}"
                    )
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message=response.reason,
                        headers=response.headers,
                    )

    async def search_multiple(
        self, queries: List[Union[str, Dict, SearchParams]]
    ) -> List[List[Location]]:
        """Perform multiple asynchronous searches on the Nominatim API."""
        tasks = [self.search(query) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    def reduce_locations(
        self, locations: List[Location], min_distance: float
    ) -> List[Location]:
        """Reduce the number of locations by merging those within a minimum distance."""
        if not locations:
            return []

        reduced_locations = [locations[0]]
        for loc in locations[1:]:
            if all(loc.distance_to(r) >= min_distance for r in reduced_locations):
                reduced_locations.append(loc)
        return reduced_locations

    async def sort_by_importance(self, locations: List[Location]) -> List[Location]:
        """sorts the locations by importance."""
        return sorted(locations, key=lambda x: x.importance, reverse=True)

    async def sort_by_distance(
        self, locations: List[Location], origin: Location
    ) -> List[Location]:
        """sorts the locations by distance to an origin location."""
        return sorted(locations, key=lambda x: x.distance_to(origin))
