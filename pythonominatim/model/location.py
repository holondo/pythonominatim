from typing import Optional, Dict, List
from geopy.distance import geodesic
from pydantic import BaseModel


class Location(BaseModel):
    """Represents a location obtained from Nominatim."""

    place_id: int
    osm_type: str
    osm_id: int
    lat: float
    lon: float
    display_name: str
    address: Optional[Dict] = None
    boundingbox: Optional[List[float]] = None
    class_: Optional[str] = None
    type_: Optional[str] = None
    importance: Optional[float] = None
    icon: Optional[str] = None

    # class Config:
    #     fields = {"class_": "class", "type_": "type"}
    def area(self) -> float:
        """Calculate the area of the location in km²."""
        if self.boundingbox:
            return (self.boundingbox[1] - self.boundingbox[0]) * (
                self.boundingbox[2] - self.boundingbox[3]
            )
        else:
            raise ValueError("Boundingbox not found")

    def distance_to(self, other: "Location") -> float:
        """Calculate the distance to another Location object in meters."""
        return geodesic((self.lat, self.lon), (other.lat, other.lon)).meters

    def to_dict(self) -> Dict:
        """Return the Location object as a dictionary."""
        return self.model_dump()

    def __str__(self) -> str:
        """Return a JSON string representation of the Location object."""
        return self.model_dump_json()
