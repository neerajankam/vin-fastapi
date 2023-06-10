import pytest
from unittest.mock import patch

module_path = "app.main.{}"


@pytest.fixture
def mock_cache():
    with patch(module_path.format("cache")) as dummy_cache:
        yield dummy_cache


@pytest.fixture
def mock_request():
    with patch(module_path.format("Request")) as mock_request:
        yield mock_request


@pytest.fixture
def mock_requests():
    with patch(module_path.format("requests")) as mock_requests:
        yield mock_requests


@pytest.fixture
def mock_structure():
    with patch(module_path.format("structure_response")) as mock_structure:
        yield mock_structure


@pytest.fixture
def mock_logger():
    with patch(module_path.format("logger")) as mock_logger:
        yield mock_logger


@pytest.fixture
def mock_make_request():
    with patch(module_path.format("make_request")) as mock_make_request:
        yield mock_make_request


@pytest.fixture
def mock_parse_response():
    with patch(module_path.format("parse_response")) as mock_parse_response:
        yield mock_parse_response


@pytest.fixture
def mock_convert_database():
    with patch(
        module_path.format("convert_database_to_parquet")
    ) as mock_convert_database:
        yield mock_convert_database


@pytest.fixture
def mock_response():
    with patch(module_path.format("Response")) as mock_response:
        yield mock_response


@pytest.fixture
def mock_os():
    with patch(module_path.format("os")) as mock_os:
        yield mock_os


@pytest.fixture
def mock_database_connection():
    with patch(module_path.format("DatabaseConnection")) as mock_database_connection:
        yield mock_database_connection


@pytest.fixture
def mock_pandas():
    with patch(module_path.format("pd")) as mock_pandas:
        yield mock_pandas


@pytest.fixture
def mock_arrow():
    with patch(module_path.format("pa")) as mock_arrow:
        yield mock_arrow


@pytest.fixture
def mock_parquet():
    with patch(module_path.format("pq")) as mock_parquet:
        yield mock_parquet
