# Nominatim Helper

This Python package provides an asynchronous helper for interacting with the Nominatim geocoding API. It allows you to search for locations, retrieve location details, and perform distance calculations.

## Usage
'''python
import asyncio
from pythonominatim.nominatim_helper import NominatimSearch, Location
async def main():
nominatim = NominatimSearch()
# Search for a location

```python
locations = await nominatim.search("New York City")
print(locations)
```
# Search for multiple locations

```python
results = await nominatim.search_multiple(["Paris", "Tokyo", "Sydney"])
print(results)
```
# Reduce locations by minimum distance

```python
reduced_locations = nominatim.reduce_locations(locations, min_distance=1000)
print(reduced_locations)
```
# Sort locations by importance

```python
sorted_by_importance = await nominatim.sort_by_importance(locations)
print(sorted_by_importance)
```
# Sort locations by distance to an origin
```python
origin = Location(lat=40.7128, lon=-74.0060) # New York City
sorted_by_distance = await nominatim.sort_by_distance(locations, origin)
print(sorted_by_distance)
if name == "main":
asyncio.run(main())
```


## API Reference

### `NominatimSearch` Class

#### `__init__(base_url, user_agent, email)`

- `base_url`: The base URL for the Nominatim API (default: `https://nominatim.openstreetmap.org/search`).
- `user_agent`: The user agent string to use for requests.
- `email`: Your email address (optional, recommended for rate limiting).

#### `search(params)`

Performs an asynchronous search on the Nominatim API.

- `params`: The search parameters. Can be a string (for simple queries), a dictionary, or a `SearchParams` object.
- Returns: A list of `Location` objects.

#### `search_multiple(queries)`

Performs multiple asynchronous searches on the Nominatim API.

- `queries`: A list of search queries (strings, dictionaries, or `SearchParams` objects).
- Returns: A list of lists of `Location` objects.

#### `reduce_locations(locations, min_distance)`

Reduces the number of locations by merging those within a minimum distance.

- `locations`: A list of `Location` objects.
- `min_distance`: The minimum distance between locations in meters.
- Returns: A list of `Location` objects.

#### `sort_by_importance(locations)`

Sorts the locations by importance.

- `locations`: A list of `Location` objects.
- Returns: A list of `Location` objects.

#### `sort_by_distance(locations, origin)`

Sorts the locations by distance to an origin location.

- `locations`: A list of `Location` objects.
- `origin`: The origin `Location` object.
- Returns: A list of `Location` objects.

### `Location` Class

Represents a location obtained from Nominatim.

#### Attributes

- `place_id`: The Nominatim place ID.
- `osm_type`: The OpenStreetMap object type (e.g., "node", "way", "relation").
- `osm_id`: The OpenStreetMap object ID.
- `lat`: The latitude.
- `lon`: The longitude.
- `display_name`: The display name of the location.
- `address`: A dictionary containing address details.
- `boundingbox`: A list of bounding box coordinates.
- `class_`: The class of the location (e.g., "highway", "amenity").
- `type_`: The type of the location (e.g., "residential", "restaurant").
- `importance`: The importance of the location (0-1).
- `icon`: The URL of an icon representing the location.

#### Methods

- `distance_to(other)`: Calculates the distance to another `Location` object in meters.
- `to_dict()`: Returns the `Location` object as a dictionary.
- `__str__()`: Returns a JSON string representation of the `Location` object.

### `SearchParams` Class

Represents search parameters for the Nominatim API.
