import pytest
from unittest.mock import MagicMock
from app.image_processing import process_image, insert_image


def test_process_image(mocker):
    # Configure mocks
    mock_exists = mocker.patch('app.image_processing.os.path.exists', side_effect=lambda path: True)
    # Adjusted mock_listdir to return specific files for each clothing type directory

    def listdir_side_effect(path):
        crops = {
            'runs/detect/predict/dress': ['test_dress.jpg'],
            'runs/detect/predict/jacket': ['test_jacket.jpg'],
            'runs/detect/predict/shoe': ['test_shoe.jpg'],
        }
        for dir_path, files in crops.items():
            if path.startswith(dir_path):
                return files
        return []

    mock_listdir = mocker.patch('app.image_processing.os.listdir', side_effect=listdir_side_effect)
    mocker.patch('app.image_processing.open', mocker.mock_open(read_data="binary data"))
    mock_rmtree = mocker.patch('app.image_processing.shutil.rmtree')
    mock_insert_image = mocker.patch('app.image_processing.insert_image')

    mock_detection_model = MagicMock()
    mock_detection_model.predict.return_value = None

    # Dummy database connection and cursor
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    # Call the function under test
    process_image('test_image.jpg', mock_detection_model, mock_conn, mock_cur)

    # Assertions to verify behavior
    assert mock_insert_image.call_count == 3
    # Verify the removal of the directory
    mock_rmtree.assert_called_once_with('runs/detect/predict')


# Function to read binary data from a file
def read_test_file(filename):
    with open(filename, 'rb') as file:
        return file.read()


@pytest.fixture
def binary_data():
    # Path to the test image file
    return read_test_file('/app/tests/test_dress.jpg')


def test_insert_image_success(mocker, binary_data):
    # Mock the database cursor and connection
    mock_cur = mocker.MagicMock()
    mock_conn = mocker.MagicMock()

    # Call the function under test
    insert_image('dress', binary_data, mock_conn, mock_cur)

    # Assertions to verify behavior
    mock_cur.execute.assert_called_once_with(
        "INSERT INTO table_dress (image) VALUES (%s)", (binary_data,)
    )
    mock_conn.commit.assert_called_once()


def test_insert_image_failure(mocker, binary_data):
    # Mock the database cursor and connection
    mock_cur = mocker.MagicMock()
    mock_conn = mocker.MagicMock()
    # Configure the cursor to raise an exception when execute is called
    mock_cur.execute.side_effect = Exception("Insertion failed")

    # Call the function under test and expect it to handle the exception
    insert_image('dress', binary_data, mock_conn, mock_cur)

    # Assertions to verify behavior
    mock_conn.rollback.assert_called_once()
    mock_cur.execute.assert_called()  # We check that execute was called, but it raised an error
