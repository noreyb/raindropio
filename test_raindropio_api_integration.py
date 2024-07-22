import os
import pytest
from dotenv import load_dotenv
from raindropio import RaindropIO

load_dotenv()
collection_id = 46274319  # test collection 1

@pytest.fixture(scope="module")
def raindrop_io():
    api_token = os.getenv("RAINDROPIO_API_TOKEN")
    if not api_token:
        pytest.skip("API token not set in .env file")
    return RaindropIO(api_token)

def test_bulk_fetch(raindrop_io):

    result = raindrop_io.bulk_fetch(collection_id=collection_id, page=0)
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert "_id" in result[0]
    assert "title" in result[0]

def test_create_and_delete_item(raindrop_io):
    from raindropio import ItemCreate

    test_item = ItemCreate(
        link="https://example.com",
        tags=["hoge", "fuga"],
        collection=collection_id,
    )

    created_item = raindrop_io.create(test_item)
    assert "_id" in created_item
