# This is the class for raindropio objects


class Raindrop:
    def __init__(
        self,
        _id: int = None,
        collection_id: int = None,
        link: str = None,
        title: str = None,
        tags: list = None,
    ):
        self._id = _id
        self.collection_id = collection_id
        self.link = link
        self.title = title
        self.tags = tags

    # def __str__(self):
    #     return f"Raindrop: {self.title} ({self.link})"

    # def __repr__(self):
    #     return f"Raindrop: {self.title} ({self.link})"

    def __eq__(self, other):
        return self.link == other.link

    def __hash__(self):
        return hash(self.link)

    def get_id(self) -> int:
        if self._id is None:
            raise ValueError("ID cannot be None")

        return self._id

    def create(self) -> dict:
        if self.link is None:
            raise ValueError("Link cannot be None")

        request_body = {
            "pleaseParse": {},
            "collection": {"$id": self.collection_id},
            "link": self.link,
        }

        if self.title is not None:
            request_body["title"] = self.title

        if self.tags is not None:
            request_body["tags"] = self.tags

        return request_body

    def update(self, which=None) -> (int, dict):
        if self._id is None:
            raise ValueError("ID cannot be None")

        path_param = self._id

        if which == "tags":
            request_body = {
                "tags": self.tags,
            }
        elif which == "collection":
            request_body = {
                "collection": {"$id": self.collection_id},
            }
        else:
            request_body = {
                "title": self.title,
                "tags": self.tags,
            }

        return path_param, request_body

    def delete(self) -> int:
        if self._id is None:
            raise ValueError("ID cannot be None")

        return self._id
