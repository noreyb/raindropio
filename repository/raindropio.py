import requests
import time
import random

from domain.raindrop import Raindrop
from domain.raindropio_url import RaindropIOUrl


class RaindropIO:
    def __init__(self, token: str):
        self.token = token
        self.url = RaindropIOUrl()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        self.MAX_ITEMS_PER_REQUEST = 100

    def _get_total_pages(self, collection_id: int):
        page = 0
        while True:
            items = self.bulk_get(collection_id=collection_id, page=page)
            time.sleep(1)
            if not items:
                break
            page += 1
        return page

    @staticmethod
    def _split_list(items: list, max_items=100):
        return [
            items[i:i + max_items] for i in range(0, len(items), max_items)
        ]

    def get(self, raindrop: Raindrop):
        _id = raindrop.get_id()

        r = requests.get(
            f"{self.url.get_single()}/{_id}",
            headers=self.headers,
        )

        if r.status_code != requests.codes.ok:
            print(r.text)
            raise Exception(
                f"API request failed with status code: {r.status_code}"
            )

        return r.json()["item"]

    def create(self, raindrop: Raindrop):
        body = raindrop.create()
        r = requests.post(
            f"{self.url.get_single()}",
            headers=self.headers,
            json=body,
        )

        if r.status_code != requests.codes.ok:
            print(r.text)
            raise Exception(
                f"API request failed with status code: {r.status_code}")

        return r.json()["item"]

    def update_tags(self, raindrop: Raindrop):
        _id, body = raindrop.update(which="tags")
        r = requests.put(
            f"{self.url.get_single()}/{_id}",
            headers=self.headers,
            json=body,
        )
        if r.status_code != requests.codes.ok:
            print(r.text)
            raise Exception

        return r.json()["item"]

    def delete(self, raindrop: Raindrop):
        _id = raindrop.delete()
        r = requests.delete(
            f"{self.url.get_single()}/{_id}",
            headers=self.headers,
        )
        if r.status_code != requests.codes.ok:
            print(r.text)
            raise Exception

        return r.json()["item"]

    def bulk_get(self, collection_id: int, page: int = 0):
        # collection_id: raindropio collection id
        # page: page number, default 0 is latest

        query = {
            "perpage": 50,
            "page": page,
        }

        r = requests.get(
            f"{self.url.get_bulk()}/{collection_id}",
            headers=self.headers,
            params=query,
        )

        if r.status_code != requests.codes.ok:
            print(r.text)
            raise Exception(
                f"API request failed with status code: {r.status_code}")

        return r.json()["items"]

    def bulk_get_all(self, collection_id: int):
        total_pages = self._get_total_pages(collection_id)

        result = []
        for n in range(total_pages):
            items = self.bulk_get(collection_id=collection_id, page=n)
            result.extend(items)
        return result

    def bulk_get_random(self, collection_id):
        total_pages = self._get_total_pages(collection_id)
        if total_pages == 0:
            return []
        random_page = random.randint(0, total_pages - 1)
        return self.bulk_get(collection_id=collection_id, page=random_page)

    def bulk_create(self, raindrops: list[Raindrop]):
        # APIの制限に合わせて、リストを分割する（例：最大100項目ずつ）
        raindrop_chunks = self._split_list(
            raindrops, max_items=self.MAX_ITEMS_PER_REQUEST
        )

        results = []
        for chunk in raindrop_chunks:
            result = self._bulk_create(chunk)
            results.extend(result)

        return results

    def _bulk_create(self, raindrops: list[Raindrop]):
        # リクエストボディの作成
        items = [raindrop.create() for raindrop in raindrops]
        body = {
            "items": items
        }

        # APIリクエストの送信
        r = requests.post(
            f"{self.url.get_bulk()}",
            headers=self.headers,
            json=body
        )

        if r.status_code != requests.codes.ok:
            print(r.text)
            raise Exception(
                f"API request failed with status code: {r.status_code}")

        # 作成されたRaindropオブジェクトのリストを返す
        return r.json()["items"]

    def bulk_update_tags(
            self,
            src_collection_id: int,
            tags: list[str],
            raindrops: list[Raindrop],
            overwrite=False,
    ):
        if overwrite:
            self.bulk_update(
                src_collection_id,
                raindrops,
                tags=[],
            )
            time.sleep(5)

        return self.bulk_update(
            src_collection_id,
            raindrops,
            tags=tags,
        )

    # bulk_get_allなどで取得したRaindropオブジェクトのリストを更新する
    def bulk_update(
            self,
            src_collection_id: int,
            raindrops: list[Raindrop],
            tags=None,
            dst_collection_id=None,
    ):
        raindrop_chunks = self._split_list(
            raindrops, max_items=self.MAX_ITEMS_PER_REQUEST
        )

        n_modified = 0
        for chunk in raindrop_chunks:
            n_modified += self._bulk_update(
                src_collection_id, chunk, tags, dst_collection_id
            )
            # results.extend(result)

        return n_modified

    def _bulk_update(
            self,
            src_collection_id: int,
            raindrops: list[Raindrop],
            tags: list[str] = None,
            dst_collection_id: int = None,
    ):
        body = {}
        ids = [raindrop.get_id() for raindrop in raindrops]
        body["ids"] = ids
        if tags is not None:
            body["tags"] = tags
        if dst_collection_id:
            body["collection"] = {"$id": dst_collection_id}

        r = requests.put(
            f"{self.url.get_bulk()}/{src_collection_id}",
            headers=self.headers,
            json=body
        )

        if r.status_code != requests.codes.ok:
            print(r.text)
            raise Exception(
                f"API request failed with status code: {r.status_code}"
            )

        return r.json()["modified"]


if __name__ == "__main__":
    pass
