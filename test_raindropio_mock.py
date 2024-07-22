import pytest
from unittest.mock import patch, MagicMock
from raindropio import RaindropIO, ItemCreate, ItemUpdate, ItemBulkUpdate


@pytest.fixture
def raindrop_io():
    return RaindropIO("fake_token")


@pytest.fixture
def mock_requests():
    with patch("raindropio.requests") as mock:
        mock.codes = MagicMock()
        mock.codes.ok = 200
        yield mock

def test_init(raindrop_io):
    assert raindrop_io.token == "fake_token"
    assert raindrop_io.base == "https://api.raindrop.io/rest/v1"
    assert raindrop_io.endpoint == "raindrop"
    assert raindrop_io.url == "https://api.raindrop.io/rest/v1/raindrop"
    assert raindrop_io.headers == {
        "Content-Type": "application/json",
        "Authorization": "Bearer fake_token",
    }

def test_bulk_fetch(raindrop_io, mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": [{"id": 1}, {"id": 2}]}
    mock_requests.get.return_value = mock_response

    result = raindrop_io.bulk_fetch(collection_id=123, page=0)

    assert mock_requests.get.called
    assert result == [{"id": 1}, {"id": 2}]

    mock_requests.get.assert_called_once_with(
        "https://api.raindrop.io/rest/v1/raindrops/123",
        headers=raindrop_io.headers,
        params={"perpage": 50, "page": 0}
    )

def test_create(raindrop_io, mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"item": {"id": 1}, "result": True}
    mock_requests.post.return_value = mock_response

    item = ItemCreate(link="https://example.com", tags=["hogehoge", "fuga"])
    result = raindrop_io.create(item)


    assert result == {"id": 1}
    mock_requests.post.assert_called_once_with(
        "https://api.raindrop.io/rest/v1/raindrop",
        headers=raindrop_io.headers,
        json=item.to_dict()
    )

def test_update(raindrop_io, mock_requests):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"item": {"id": 1, "link": "https://updated.com"}}
    mock_requests.put.return_value = mock_response

    item = ItemUpdate("1", "https://updated.com", ["hoge", "fuga"], 123, 456)
    result = raindrop_io.update(item)

    assert result == {"id": 1, "link": "https://updated.com"}
    mock_requests.put.assert_called_once_with(
        "https://api.raindrop.io/rest/v1/raindrop/1",
        headers=raindrop_io.headers,
        json={"item": item.to_dict()}
    )
