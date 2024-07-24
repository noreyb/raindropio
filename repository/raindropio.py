import random
import time

import requests

from domain.raindrop import Raindrop
from domain.raindrop_id import RaindropId
from domain.raindropio_url import RaindropIOUrl
from domain.response_to_raindrop import response_to_raindrop


class RaindropIO:
    def __init__(self, token: str):
        self.token = token
        self.url = RaindropIOUrl()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        self.MAX_ITEMS_PER_REQUEST = 100

    def _make_request(self, method: str, url: str, body=None, query=None):
        if method == "GET":
            if query:
                r = requests.get(url, headers=self.headers, params=query)
            else:
                r = requests.get(url, headers=self.headers)
        elif method == "POST":
            r = requests.post(url, headers=self.headers, json=body)
        elif method == "PUT":
            r = requests.put(url, headers=self.headers, json=body)
        elif method == "DELETE":
            r = requests.delete(url, headers=self.headers)
        else:
            raise Exception("Invalid method")

        if r.status_code != requests.codes.ok:
            print(r.text)
            raise Exception(f"API request failed with status code: {r.status_code}")

        return r

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
        return [items[i : i + max_items] for i in range(0, len(items), max_items)]

    def get(self, _id: RaindropId) -> Raindrop:
        r = self._make_request(
            method="GET",
            url=f"{self.url.get_single()}/{_id.value}",
        )
        return response_to_raindrop(r.json()["item"])

    @staticmethod
    def _make_request_body_create(raindrop: Raindrop):
        if raindrop.link is None:
            raise Exception("Raindrop.link is required.")
        body = {
            "pleaseParse": {},
            "link": raindrop.link,
        }
        if raindrop.title:
            body["title"] = raindrop.title
        if raindrop.collection_id:
            body["collection"] = {"$id": raindrop.collection_id}
        if raindrop.tags:
            body["tags"] = raindrop.tags

        return body

    def create(self, raindrop: Raindrop) -> Raindrop:
        body = self._make_request_body_create(raindrop)
        r = self._make_request(
            method="POST",
            url=self.url.get_single(),
            body=body,
        )
        return response_to_raindrop(r.json()["item"])

    def update_tags(self, _id: RaindropId, tags: list[str]) -> Raindrop:
        body = {
            "tags": tags,
        }
        r = self._make_request(
            method="PUT",
            url=f"{self.url.get_single()}/{_id.value}",
            body=body,
        )
        return response_to_raindrop(r.json()["item"])

    def delete(self, _id: RaindropId) -> bool:
        r = self._make_request(
            method="DELETE",
            url=f"{self.url.get_single()}/{_id.value}",
        )
        return r.json()["result"]

    def bulk_get(self, collection_id: int, page: int = 0) -> list[Raindrop]:
        # collection_id: raindropio collection id
        # page: page number, default 0 is latest

        query = {
            "perpage": 50,
            "page": page,
        }
        r = self._make_request(
            method="GET",
            url=f"{self.url.get_bulk()}/{collection_id}",
            query=query,
        )
        return [response_to_raindrop(item) for item in r.json()["items"]]

    def bulk_get_all(self, collection_id: int) -> list[Raindrop]:
        total_pages = self._get_total_pages(collection_id)

        result = []
        for n in range(total_pages):
            items = self.bulk_get(collection_id=collection_id, page=n)
            result.extend(items)
        return result

    def bulk_get_random(self, collection_id) -> list[Raindrop]:
        total_pages = self._get_total_pages(collection_id)
        if total_pages == 0:
            return []
        random_page = random.randint(0, total_pages - 1)
        return self.bulk_get(collection_id=collection_id, page=random_page)

    def bulk_create(self, raindrops: list[Raindrop]) -> list[Raindrop]:
        # APIの制限に合わせて、リストを分割する（例：最大100項目ずつ）
        raindrop_chunks = self._split_list(
            raindrops, max_items=self.MAX_ITEMS_PER_REQUEST
        )

        results = []
        for chunk in raindrop_chunks:
            result = self._bulk_create(chunk)
            time.sleep(1)
            results.extend(result)

        return results

    def _bulk_create(self, raindrops: list[Raindrop]) -> list[Raindrop]:
        # リクエストボディの作成
        items = [self._make_request_body_create(raindrop) for raindrop in raindrops]
        body = {"items": items}

        r = self._make_request(
            method="POST",
            url=self.url.get_bulk(),
            body=body,
        )
        return [response_to_raindrop(item) for item in r.json()["items"]]

    def bulk_update_tags(
        self,
        src_collection_id: int,
        tags: list[str],
        raindrops: list[Raindrop],
        overwrite=False,  # Add tags to existing tags if false, otherwise overwrite
    ) -> None:
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
    ) -> None:
        raindrop_chunks = self._split_list(
            raindrops, max_items=self.MAX_ITEMS_PER_REQUEST
        )

        for chunk in raindrop_chunks:
            self._bulk_update(src_collection_id, chunk, tags, dst_collection_id)

        return None

    @staticmethod
    def _make_request_body_bulk_update(
        raindrops: list[Raindrop],
        tags: list[str] = None,
        dst_collection_id: int = None,
    ) -> dict:
        ids = [raindrop._id for raindrop in raindrops]
        body = {
            "ids": ids,
        }
        if tags is not None:
            body["tags"] = tags
        if dst_collection_id:
            body["collection"] = {"$id": dst_collection_id}
        return body

    def _bulk_update(
        self,
        src_collection_id: int,
        raindrops: list[Raindrop],
        tags: list[str] = None,
        dst_collection_id: int = None,
    ) -> None:
        body = self._make_request_body_bulk_update(
            raindrops,
            tags,
            dst_collection_id,
        )

        _ = self._make_request(
            method="PUT", url=f"{self.url.get_bulk()}/{src_collection_id}", body=body
        )
        return None


if __name__ == "__main__":
    pass
