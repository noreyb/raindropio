from domain.raindrop import Raindrop
from domain.raindrop_id import RaindropId


def response_to_raindrop(item: dict) -> Raindrop:
    return Raindrop(
        link=item["link"],
        _id=RaindropId(item["_id"]),
        collection_id=item["collection"]["$id"],
        title=item["title"],
        tags=item["tags"],
    )
