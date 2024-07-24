# This is the class for raindropio objects
from domain.raindrop_id import RaindropId


class Raindrop:
    def __init__(
        self,
        link: str,
        _id: RaindropId = None,
        collection_id: int = None,
        title: str = None,
        tags: list[str] = None,
    ):
        self._id = _id.get() if _id else None
        self.collection_id = collection_id
        self.link = link
        self.title = title
        self.tags = tags
