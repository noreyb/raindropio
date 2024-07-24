import pytest
from unittest.mock import patch, MagicMock
from repository.raindropio import RaindropIO
from domain.raindrop import Raindrop
from domain.raindrop_id import RaindropId


@pytest.fixture
def raindropio():
    return RaindropIO("test_token")


@pytest.mark.parametrize("raindrop_data, expected_result", [
    (
        {"collection_id": 1, "link": "https://example.com",
            "title": "Test Raindrop", "tags": ["test"],
         },
        {"_id": 1, "title": "Test Raindrop", "link": "https://example.com",
         "tags": ["test"], "collection": {"$id": 1}}
    ),
])
def test_create(raindropio, raindrop_data, expected_result):
    with patch('repository.raindropio.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"item": expected_result}
        mock_post.return_value = mock_response

        raindrop = Raindrop(
            link=raindrop_data["link"],
            collection_id=raindrop_data["collection_id"],
            title=raindrop_data["title"],
            tags=raindrop_data["tags"],
        )
        result = raindropio.create(raindrop)

        assert result._id == expected_result["_id"]
        assert result.title == expected_result["title"]
        assert result.link == expected_result["link"]
        assert result.tags == expected_result["tags"]
        mock_post.assert_called_once()


def test_update_tags(raindropio):
    with patch('repository.raindropio.requests.put') as mock_put:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "item": {"_id": 1, "tags": ["updated"], "link": "https://example.com", "collection": {"$id": 1}, "title": ""}
        }
        mock_put.return_value = mock_response

        raindrop_id = RaindropId(1)
        tags = ["updated"]
        result = raindropio.update_tags(raindrop_id, tags)

        assert result._id == 1
        assert result.tags == ["updated"]
        mock_put.assert_called_once()


def test_delete(raindropio):
    with patch('repository.raindropio.requests.delete') as mock_delete:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": True}
        mock_delete.return_value = mock_response

        raindrop_id = RaindropId(1)
        result = raindropio.delete(raindrop_id)

        assert result is True
        mock_delete.assert_called_once()


def test_get(raindropio):
    raindrop_id = 12345
    expected_raindrop = {
        "_id": raindrop_id,
        "title": "Test Raindrop",
        "link": "https://example.com",
        "tags": ["test", "example"],
        "collection": {"$id": 1},
    }

    with patch('repository.raindropio.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"item": expected_raindrop}
        mock_get.return_value = mock_response

        raindrop_id = RaindropId(12345)
        result = raindropio.get(raindrop_id)

        assert result._id == expected_raindrop["_id"]
        mock_get.assert_called_once_with(
            f"{raindropio.url.get_single()}/{raindrop_id}",
            headers=raindropio.headers
        )


def test_get_error(raindropio):
    raindrop_id = 12345

    with patch('repository.raindropio.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        with pytest.raises(Exception) as excinfo:
            raindrop_id = RaindropId(12345)
            raindropio.get(raindrop_id)

        assert "API request failed with status code: 404" in str(excinfo.value)
        mock_get.assert_called_once_with(
            f"{raindropio.url.get_single()}/{raindrop_id}",
            headers=raindropio.headers
        )


def test_bulk_get_mock(raindropio):
    with patch('repository.raindropio.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
                "items": [{
                    "_id": 1,
                    "title": "Test Item",
                    "link": "https://example.com",
                    "tags": ["test"],
                    "collection": {"$id": 1},
                    }]}
        mock_get.return_value = mock_response

        result = raindropio.bulk_get(collection_id=1, page=0)

        assert len(result) == 1
        assert result[0]._id == 1
        assert result[0].title == "Test Item"
        mock_get.assert_called_once_with(
            f"{raindropio.url.get_bulk()}/1",
            headers=raindropio.headers,
            params={"perpage": 50, "page": 0}
        )


def test_bulk_get_all_mock(raindropio):
    with patch.object(raindropio, '_get_total_pages', return_value=2):
        with patch.object(raindropio, 'bulk_get') as mock_bulk_get:
            mock_bulk_get.side_effect = [
                [{"id": 1, "title": "Item 1"}],
                [{"id": 2, "title": "Item 2"}]
            ]

            result = raindropio.bulk_get_all(collection_id=1)

            assert len(result) == 2
            assert result[0]["id"] == 1
            assert result[1]["id"] == 2
            assert mock_bulk_get.call_count == 2


def test_get_total_pages_mock(raindropio):
    with patch.object(raindropio, 'bulk_get') as mock_bulk_get:
        mock_bulk_get.side_effect = [
            [{"id": 1}],
            [{"id": 2}],
            []
        ]

        result = raindropio._get_total_pages(collection_id=1)

        assert result == 2
        assert mock_bulk_get.call_count == 3


def test_bulk_get_random_mock(raindropio):
    with patch.object(raindropio, '_get_total_pages', return_value=3):
        with patch.object(raindropio, 'bulk_get') as mock_bulk_get:
            with patch('repository.raindropio.random.randint', return_value=1):
                mock_bulk_get.return_value = [
                    {"id": 2, "title": "Random Item"}]

                result = raindropio.bulk_get_random(collection_id=1)

                assert len(result) == 1
                assert result[0]["id"] == 2
                assert result[0]["title"] == "Random Item"
                raindropio._get_total_pages.assert_called_once_with(1)
                mock_bulk_get.assert_called_once_with(collection_id=1, page=1)


def test_bulk_get_random_empty_collection_mock(raindropio):
    with patch.object(raindropio, '_get_total_pages', return_value=0):
        result = raindropio.bulk_get_random(collection_id=1)
        assert result == []
        raindropio._get_total_pages.assert_called_once_with(1)


def test__bulk_create_mock(raindropio):
    raindrops = [
        Raindrop(
            link="https://example1.com",
        ),
        Raindrop(
            link="https://example2.com",
        )
    ]

    with patch('repository.raindropio.requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "_id": 1,
                    "link": "https://example1.com",
                    "collection": {"$id": 1},
                    "tags": [],
                    "title": ""
                    },
                {
                    "_id": 2,
                    "link": "https://example2.com",
                    "collection": {"$id": 1},
                    "tags": [],
                    "title": ""
                }
            ]
        }
        mock_post.return_value = mock_response

        result = raindropio.bulk_create(raindrops)

        assert len(result) == 2
        assert result[0]._id == 1
        assert result[1]._id == 2
        mock_post.assert_called_once()


def test_bulk_create_mock(raindropio):
    raindrops = [
        Raindrop(
            link=f"https://example{i}.com",
            _id=RaindropId(i),
        )
        for i in range(150)
    ]

    with patch.object(raindropio, '_bulk_create') as mock_bulk_create:
        mock_bulk_create.side_effect = [
            [{"_id": i} for i in range(100)],
            [{"_id": i} for i in range(100, 150)]
        ]

        result = raindropio.bulk_create(raindrops)

        assert len(result) == 150
        assert mock_bulk_create.call_count == 2

    # 追加のアサーション
    assert result[0]["_id"] == 0
    assert result[-1]["_id"] == 149


def test_bulk_update_mock(raindropio):
    src_collection_id = 1
    raindrops = [
            Raindrop(
                link=f"https://example{i}.com",
                _id=RaindropId(i)
            )
            for i in range(1, 6)
    ]
    new_tags = ["updated"]
    dst_collection_id = 2

    with patch('repository.raindropio.requests.put') as mock_put:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": True, "modified": 5}
        mock_put.return_value = mock_response

        result = raindropio.bulk_update(
            src_collection_id, raindrops, tags=new_tags, dst_collection_id=dst_collection_id
        )

        assert result is None
        mock_put.assert_called_once()
        called_url, called_kwargs = mock_put.call_args
        assert called_url[0] == f"{raindropio.url.get_bulk()}/{src_collection_id}"
        assert called_kwargs['headers'] == raindropio.headers
        assert 'json' in called_kwargs
        assert 'ids' in called_kwargs['json']
        assert 'tags' in called_kwargs['json']
        assert 'collection' in called_kwargs['json']
        assert called_kwargs['json']['collection']['$id'] == dst_collection_id


def test_bulk_update_large_list_mock(raindropio):
    src_collection_id = 1
    raindrops = [
        Raindrop(link=f"https://example{i}.com", _id=RaindropId(i)) for i in range(1, 202)
    ]  # 201 raindrops
    new_tags = ["updated"]

    with patch('repository.raindropio.requests.put') as mock_put:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": True, "modified": 100}
        mock_put.return_value = mock_response

        result = raindropio.bulk_update(
            src_collection_id, raindrops, tags=new_tags
        )

        assert result is None
        assert mock_put.call_count == 3  # Should be called 3 times due to chunking
