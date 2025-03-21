import pytest
from pathlib import Path

import asset_pipeline.core.datafiles.metadata as md

@pytest.fixture
def mock_asset_path():
    """Fixture to mock a file path for testing."""
    asset_path = Path(f"mock_asset.svg")
    # Create a mock file for testing
    with open(asset_path, "w") as f:
        f.write("This is a mock asset file.")
    yield asset_path
    # Cleanup after test
    asset_path.unlink()


def test_create_metadata(mock_asset_path):
    """Test creating metadata from a file."""
    metadata = md.create_metadata(mock_asset_path)
    assert metadata is not None
    assert metadata.uuid is not None
    assert metadata.checksum == md.calculate_checksum(mock_asset_path)


def test_save_and_load_metadata(mock_asset_path):
    """Test saving and loading metadata."""
    metadata = md.create_metadata(mock_asset_path)
    metadata_path = md.get_metadata_path(mock_asset_path)

    # Save metadata to file
    md.save_metadata(metadata, metadata_path)

    # Load metadata back from file
    loaded_metadata = md.load_metadata(metadata_path)

    assert loaded_metadata.uuid == metadata.uuid
    assert loaded_metadata.checksum == metadata.checksum

    metadata_path.unlink()