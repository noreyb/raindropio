class ItemCreate:
    def __init__(
        self,
        link: str,  # required
        tags: list[str]=[]
        collection: int=None
        title: str=None,
    ):
        self.link = link
        self.tags = tags
        self.collection = collection
        self.title = title

    def to_dict(self):
        return {
            "link": self.link,
            "tags": self.tags,
            "collection": {"$id": f"{self.collection}"},
            "title": self.title,
        }


class ItemUpdate:
    def __init__(
        self,
        _id: str,  # required
        link: str,
        tags: list[str],
        src_collection: int
        dst_collection: int,
        title: str=None,
    ):
        self.id = _id
        self.link = link
        self.tags = tags
        self.src_collection = src_collection
        self.dst_collection = dst_collection
        self.title = title

    def to_dict(self):
        return {
            "link": self.link,
            "tags": self.tags,
            "collection": {"$id": f"{self.dst_collection}"},
            "title": self.title,
        }

    def get_src_collection(self):
        return self.src_collection

class ItemBulkUpdate:
    def __init__(
        self,
        ids: list[str],  # required
        tags: list[str],
        collection: int,
    ):
        self.ids = ids
        self.tags = tags
        self.collection = collection

    def to_dict(self):
        return {
            "ids": self.ids,
            "tags": self.tags,
            "collection": {"$id": f"{self.collection}"},
        }

    def get_ids(self):
        return self.ids


class RaindropIO:
    def __init__(self, token: str):
        self.token = token
        self.base = "https://api.raindrop.io/rest/v1"
        self.endpoint = "raindrops"
        self.url = f"{self.base}/{self.endpoint}"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def _get_tolal_pages(self, collection_id: int):
        n_page = 0
        while True:
            query = {
                "perpage": 50,
                "page": n_page,
            }

            r = requests.get(
                f"{self.url}/{collection_id}",
                heders=self.headers,
                param=query,
            )

            if r.status_code != requests.codes.ok:
                print(r.text)
                raise Exception

            time.sleep(1)
            count = len(r.json()["items"])
            if count == 0:
                break
            n_page += 1
        return n_page
        

    def bulk_fetch_random(self, collection_id):
        total_page = self._get_tolal_pages(collection_id)
        n_page = random.randint(0, total_page - 1)

        return self.fetch(collection_id=collection_id, page=n_page)


    def bulk_fetch(self, collection_id: int, page: int=0):
        # collection_id: raindropio collection id
        # page: page number, default 0 is latest

        query = {
            "perpage": 50,
            "page": page,
        }

        r = requests.get(
            f"{self.url}/{collection_id}",
            heders=self.headers,
            param=query,
        )

        if r.status_code != requests.codes.ok:
            print(r.text)
            raise Exception

        return r.json()["items"]

    def fetch_all(self, collection_id: int):
        total_pages = self._get_tolal_pages(collection_id)

        result = []
        for n in range(total_pages):
            items = self.fetch(collection_id=collection_id, page=n)
            result.append(items)
        return items

    def create(self, item: ItemCreate):
        _item = item.to_dict()

        body = {
            "item": _item,
        }

        r = requests.post(
            f"{self.url}",
            heders=self.headers,
            json=body
        )

        if r.status_code != requests.codes.ok:
            print(r.text)
            raise Exception
        
        return r.json()["item"], r.json()["result"]

    def _split_list(items: list, max_items=100):
        return [items[i:i+n] for i in range(0, len(items), n)

    def bulk_create(self, items: list[ItemCreate]):
        items2d = self._split_list(items)

        result = []
        for items1d in items2d:
            tmp = [i.to_dict() for i in items1d]
        
            body = {
                "items": tmp,
            }

            r = requests.post(
                f"{self.url}",
                heders=self.headers,
                json=body
            )

            if r.status_code != requests.codes.ok:
                print(r.text)
                raise Exception
            time.sleep(1)

            result.append(r.json()["items"])
        
        result = sum(result, [])
        return result

    def update(self, item: ItemUpdate):
        _id = item.get_id
        _item = item.to_dict()

        body = {
            "item": _item,
        }

        r = requests.put(
            f"{self.url}/{_id}",
            heders=self.headers,
            json=body
        )

        if r.status_code != requests.codes.ok:
            print(r.text)
            raise Exception
        
        return r.json()["item"]

    def bulk_update(self, items: ItemBulkUpdate, collection_id: int):
        # fixfix
        items2d = self._split_list(items)

        result = []
        for items1d in items2d:
            tmp = [i.to_dict() for i in items1d]
        
            body = {
                "items": tmp,
            }

            r = requests.put(
                f"{self.url}/{collection_id}",
                heders=self.headers,
                json=body
            )

            if r.status_code != requests.codes.ok:
                print(r.text)
                raise Exception
            time.sleep(1)

            result.append(r.json()["items"])
        
        result = sum(result, [])
        return result


if __name__ == "__main__":
    pass
