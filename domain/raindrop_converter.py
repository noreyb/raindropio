from domain.raindrop import Raindrop
from typing import List, Dict, Any


class RaindropConverter:
    @staticmethod
    def json_to_raindrop(json_data: Dict[str, Any]) -> Raindrop:
        return Raindrop(
            _id=json_data.get('_id'),
            collection_id=json_data.get('collectionId'),
            link=json_data.get('link'),
            title=json_data.get('title'),
            tags=json_data.get('tags', [])
        )

    @staticmethod
    def json_list_to_raindrops(json_list: List[Dict[str, Any]]) -> List[Raindrop]:
        return [RaindropConverter.json_to_raindrop(item) for item in json_list]

    @staticmethod
    def api_response_to_raindrops(api_response: Dict[str, Any]) -> List[Raindrop]:
        if 'items' in api_response:
            return RaindropConverter.json_list_to_raindrops(api_response['items'])
        else:
            raise ValueError("Invalid API response format")
