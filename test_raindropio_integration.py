import pytest
from repository.raindropio import RaindropIO
from domain.raindrop import Raindrop
# from domain.raindrop_converter import RaindropConverter
from dotenv import load_dotenv
import os
import time

load_dotenv()


@pytest.fixture(scope="module")
def raindropio():
    API_TOKEN = os.getenv("RAINDROPIO_API_TOKEN")
    return RaindropIO(API_TOKEN)


def test_create_get_update_delete_flow(raindropio):
    TEST_COLLECTION_ID_SINGLE = os.getenv(
        "TEST_COLLECTION_ID_SINGLE"
    )

    # Create
    new_raindrop = Raindrop(
        collection_id=TEST_COLLECTION_ID_SINGLE,
        link="https://example.com",
        # title="Integration Test Raindrop",
        tags=["test", "integration"]
    )
    created = raindropio.create(new_raindrop)
    # assert created["title"] == "Integration Test Raindrop"
    assert created["link"] == "https://example.com"
    assert set(created["tags"]) == set(["test", "integration"])

    # Get
    get_raindrop = Raindrop(_id=created["_id"])
    retrieved = raindropio.get(get_raindrop)
    assert retrieved["_id"] == created["_id"]
    assert retrieved["title"] == created["title"]

    # Update
    update_raindrop = Raindrop(
        _id=created["_id"],
        tags=["test", "integration", "updated"]
    )
    updated = raindropio.update_tags(update_raindrop)
    assert set(updated["tags"]) == set(["test", "integration", "updated"])

    # Delete
    delete_raindrop = Raindrop(_id=created["_id"])
    deleted = raindropio.delete(delete_raindrop)
    assert deleted["_id"] == created["_id"]

    # Verify deletion
    with pytest.raises(Exception):
        raindropio.get(created["_id"])


def test_bulk_get(raindropio):
    TEST_COLLECTION_ID_BULK = os.getenv(
        "TEST_COLLECTION_ID_BULK"
    )

    # test collection has 3 raindrops
    # http://example.com/
    # https://forest.watch.impress.co.jp
    # https://jprs.co.jp

    # Get
    retrieved = raindropio.bulk_get(TEST_COLLECTION_ID_BULK)
    assert len(retrieved) == 50


def test_bulk_get_integration(raindropio):
    TEST_COLLECTION_ID_BULK = os.getenv(
        "TEST_COLLECTION_ID_BULK"
    )
    result = raindropio.bulk_get(collection_id=TEST_COLLECTION_ID_BULK, page=0)
    assert isinstance(result, list)
    if result:
        assert "_id" in result[0]
        assert "title" in result[0]


def test_bulk_get_all(raindropio):
    test_collection_id = os.getenv("TEST_COLLECTION_ID_BULK")
    result = raindropio.bulk_get_all(collection_id=test_collection_id)
    assert isinstance(result, list)
    if result:
        assert len(result) == 55
        assert "_id" in result[0]
        assert "title" in result[0]
        assert result[-1]["link"] == "https://forest.watch.impress.co.jp/"


def test_get_total_pages_integration(raindropio):
    test_collection_id = os.getenv("TEST_COLLECTION_ID_BULK")
    total_pages = raindropio._get_total_pages(collection_id=test_collection_id)
    assert isinstance(total_pages, int)
    assert total_pages == 2


def test_bulk_get_random_integration(raindropio):
    test_collection_id = os.getenv("TEST_COLLECTION_ID_BULK")
    result = raindropio.bulk_get_random(collection_id=test_collection_id)
    assert isinstance(result, list)
    if result:
        assert "_id" in result[0]
        assert "title" in result[0]


def test_bulk_get_random_consistency_integration(raindropio):
    test_collection_id = os.getenv("TEST_COLLECTION_ID_BULK")
    results = set()
    for _ in range(5):  # 複数回実行して結果が異なることを確認
        result = raindropio.bulk_get_random(collection_id=test_collection_id)
        if result:
            results.add(result[0]["_id"])

    # 少なくとも2つ以上の異なる結果が得られることを期待
    # (注: 小さなコレクションや運が悪い場合、このテストは失敗する可能性があります)
    assert len(
        results) > 1, "Random selection doesn't seem to be working correctly"


def test_bulk_get_random_empty_collection_integration(raindropio):
    # 空のコレクションIDを使用 (存在しないIDを使用)
    empty_collection_id = 46288157  # 非常に大きな数字を使用
    result = raindropio.bulk_get_random(collection_id=empty_collection_id)
    assert result == []


@pytest.mark.skipif(True, reason="This test is too slow to run in CI environment")
def test_bulk__create_integration(raindropio):
    test_collection_id = os.getenv("TEST_COLLECTION_ID_BULK")
    raindrops = [
        Raindrop(collection_id=test_collection_id, link="https://example1.com",
                 title="Integration Test 1", tags=["test", "integration"]),
        Raindrop(collection_id=test_collection_id, link="https://example2.com",
                 title="Integration Test 2", tags=["test", "integration"])
    ]

    result = raindropio._bulk_create(raindrops)

    assert len(result) == 2
    assert result[0]["title"] == "Integration Test 1"
    assert result[1]["title"] == "Integration Test 2"

    # Clean up: Delete created raindrops
    for item in result:
        raindrop = Raindrop(_id=item["_id"])
        raindropio.delete(raindrop)
        time.sleep(1)


@pytest.mark.skipif(True, reason="This test is too slow to run in CI environment")
def test_bulk_create_integration(raindropio):
    test_collection_id = os.getenv("TEST_COLLECTION_ID_BULK")
    raindrops = [
        Raindrop(
            collection_id=test_collection_id,
            link=f"https://example{i}.com",
            title=f"Large Integration Test {i}",
            tags=["test", "integration", "large"])
        for i in range(150)
    ]

    result = raindropio.bulk_create(raindrops)

    assert len(result) == 150
    assert all("_id" in item for item in result)

    # Clean up: Delete created raindrops
    for item in result:
        raindrop = Raindrop(_id=item["_id"])
        raindropio.delete(raindrop)
        time.sleep(1)


def test_bulk_update_tags_integration(raindropio):
    test_collection_id = os.getenv("TEST_COLLECTION_ID_BULK")

    # Create test raindrops
    raindrops = [
        Raindrop(
            collection_id=test_collection_id,
            link=f"https://example{i}.com",
            title=f"Bulk Update Test {i}",
            tags=["test", "integration"],
        )

        for i in range(5)
    ]
    created_raindrops = raindropio.bulk_create(raindrops)
    created_raindrops = [
        Raindrop(
            _id=r["_id"],
            collection_id=r["collectionId"],
            title=r["title"],
            link=r["link"],
            tags=r["tags"],
        ) for r in created_raindrops
    ]

    # Update tags
    new_tags = ["updated", "bulk"]
    raindropio.bulk_update_tags(
        test_collection_id, new_tags, created_raindrops, overwrite=True)
    time.sleep(5)

    # Verify updates
    updated_raindrops = raindropio.bulk_get_all(test_collection_id)
    for raindrop in updated_raindrops:
        if raindrop["title"].startswith("Bulk Update Test"):
            assert set(raindrop["tags"]) == set(
                new_tags), f"Tags not updated for {raindrop['title']}"

    # Clean up
    for raindrop in created_raindrops:
        delete_raindrop = Raindrop(_id=raindrop._id)
        raindropio.delete(delete_raindrop)
        time.sleep(1)


# def test_bulk_update_collection_integration(raindropio):
#     src_collection_id = os.getenv("TEST_COLLECTION_ID_BULK")
#     dst_collection_id = os.getenv("TEST_COLLECTION_ID_SINGLE")
#
#     # Create test raindrops
#     raindrops = [
#         Raindrop(collection_id=src_collection_id, link=f"https://example{i}.com", title=f"Bulk Update Collection Test {i}", tags=["test", "integration"])
#         for i in range(3)
#     ]
#     created_raindrops = raindropio.bulk_create(raindrops)
#
#     # Update collection
#     raindropio.bulk_update(src_collection_id, created_raindrops, dst_collection_id=dst_collection_id)
#
#     # Verify updates
#     updated_raindrops = raindropio.bulk_get_all(dst_collection_id)
#     updated_titles = [r["title"] for r in updated_raindrops if r["title"].startswith("Bulk Update Collection Test")]
#     assert len(updated_titles) == 3
#
#     # Clean up
#     for raindrop in created_raindrops:
#         delete_raindrop = Raindrop(_id=raindrop["_id"])
#         raindropio.delete(delete_raindrop)
#         time.sleep(1)
