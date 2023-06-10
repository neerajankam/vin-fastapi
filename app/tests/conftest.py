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
