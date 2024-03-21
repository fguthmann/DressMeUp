import pytest
from unittest.mock import patch, MagicMock
from app.clothes_recommendations import get_random_item, pick_outfit


# Mock database responses for get_random_item
@pytest.mark.parametrize("clothing_type, mock_return, expected", [
    ("shirt", [("image_data_shirt",)], "image_data_shirt"),
    ("pants", [], None),  # Test case where no items are returned
])
def test_get_random_item(mocker, clothing_type, mock_return, expected):
    # Mock the psycopg2 connect method and cursor
    mock_conn = mocker.patch("psycopg2.connect", autospec=True)
    mock_cursor = MagicMock()
    mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = mock_return

    result = get_random_item(clothing_type, db_params={})
    assert result == expected


# Mock database responses for pick_outfit based on temperature
@pytest.mark.parametrize("temp_celsius, expected_item_types", [
    (25, ["dress", "shoe", "bag"]),
    (10, ["shirt", "jacket", "pants", "shoe", "bag"]),
    (15, ["shirt", "pants", "shoe", "bag"]),
])
def test_pick_outfit(mocker, temp_celsius, expected_item_types):
    # Mock get_random_item to return image data containing the item type
    mocker.patch("app.clothes_recommendations.get_random_item", side_effect=lambda item_type, _: f"image_data_{item_type}")

    outfit = pick_outfit(temp_celsius, db_params={})
    for item_type in expected_item_types:
        assert outfit[item_type] == f"image_data_{item_type}"
