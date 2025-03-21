"""
GOALS Source Asset Metadata (.gsam) Handler

Minimal module for handling GOALS source asset metadata files (.gsam).
Provides functionality to track source assets and their exported derivatives.
"""
from enum import Enum
from pathlib import Path
import dataclasses as dc
import typing as t
import hashlib
import uuid

import asset_pipeline.core.logging as logging
import asset_pipeline.core.datafiles.serialization as ser

logger = logging.get_logger(__name__)

METADATA_EXTENSION = ".gsam"


@dc.dataclass(frozen=True)
class AssetMetadata:
    """Immutable metadata for a source asset."""
    uuid: str
    checksum: str
    exported_files: t.List[Path] = dc.field(default_factory=list)
    version: int = 1

# Type definition for update operations
class AssetMetadataUpdate(t.TypedDict, total=False):
    """TypedDict for metadata update operations with optional fields."""
    exported_files: t.NotRequired[t.List[Path]]



class AssetStatus(Enum):
    """
    Enum representing the status of an asset during processing.
    """
    NEW = "new"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


def get_metadata_path(asset_path: t.Union[str, Path]) -> Path:
    """
    Calculate the metadata file path from an asset path.

    :param asset_path: Path to the source asset
    :returns: Path to the metadata file
    """
    asset_path = Path(asset_path)
    # Append metadata extension to preserve the original extension
    return Path(f"{asset_path}{METADATA_EXTENSION}")


def calculate_checksum(file_path: t.Union[str, Path]) -> str:
    """
    Calculate SHA-256 checksum of a file.

    :param file_path: Path to the file
    :returns: Hexadecimal string representation of the file's SHA-256 hash
    """
    file_path = Path(file_path)
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def create_metadata(
        asset_path: t.Union[str, Path]
) -> AssetMetadata:
    """
    Create metadata for a source asset.

    :param asset_path: Path to the source asset
    :returns: Asset metadata object
    """

    return AssetMetadata(
        uuid=str(uuid.uuid4()),
        checksum=calculate_checksum(asset_path)
    )


def save_metadata(metadata: AssetMetadata, metadata_path: t.Union[str, Path]) -> Path:
    """
    Save metadata to a file.

    :param metadata: Asset metadata to save
    :param metadata_path: Path to the metadata file
    :returns: Path to the saved metadata file
    """

    metadata_dict = ser.serialize_dataclass(metadata)
    ser.save_json(metadata_dict, metadata_path)
    logger.debug(f"Saved metadata file: {metadata_path}")
    return metadata_path


def load_metadata(metadata_path: t.Union[str, Path]) -> AssetMetadata:
    """
    Load metadata from a file.

    :param metadata_path: Path to the metadata file
    :returns: Asset metadata object
    """

    metadata_dict = ser.load_json(metadata_path)
    return ser.deserialize_dataclass(AssetMetadata, metadata_dict)


def retrieve_metadata(asset_path: t.Union[str, Path]) -> AssetMetadata:
    """
    Retrieve metadata for an asset, creating it if it doesn't exist.

    :param asset_path: Path to the source asset
    :returns: Asset metadata, either existing or newly created
    """

    if not asset_path.exists():
        raise FileNotFoundError(f"Asset file not found: {asset_path}")

    metadata_path = get_metadata_path(asset_path)
    logger.debug(f"Checking for metadata at: {metadata_path}")

    if metadata_path.exists():
        # Metadata already exists, load it
        logger.debug(f"Found existing metadata for {asset_path}")
        return load_metadata(metadata_path)

    # Metadata doesn't exist, create it
    asset_path = Path(asset_path)
    metadata = create_metadata(asset_path)
    save_metadata(metadata, metadata_path)
    logger.info(f"Created new metadata for {asset_path}")

    return metadata


def refresh_metadata(asset_path: t.Union[str, Path], **changes: t.Unpack[AssetMetadataUpdate]) -> AssetMetadata:
    """
    Update metadata and save it to disk.

    :param asset_path: Path to the source asset
    :param changes: Keyword arguments with field values to update
    :returns: Updated asset metadata
    """
    # Get the metadata file path
    metadata_path = get_metadata_path(asset_path)
    metadata = retrieve_metadata(asset_path)

    # Update the metadata
    updated_metadata = dc.replace(metadata, **changes, checksum=calculate_checksum(asset_path))

    # Save the updated metadata
    save_metadata(updated_metadata, metadata_path)
    logger.debug(f"Updated and saved metadata for {asset_path}")

    return updated_metadata


def get_asset_status(asset_path: t.Union[str, Path]) -> AssetStatus:
    """
    Determines the status of an asset.

    :param asset_path: Path to the asset file to check
    :returns:
        AssetStatus.NEW        - if the asset has no metadata (never processed before)
        AssetStatus.MODIFIED   - if the asset has metadata but was changed
        AssetStatus.UNCHANGED  - if the asset is unchanged
    """
    asset_path = Path(asset_path)
    metadata_path  = get_metadata_path(asset_path)

    if not Path(metadata_path).exists():
        return AssetStatus.NEW

    metadata = load_metadata(metadata_path)
    current_checksum = calculate_checksum(asset_path)
    if current_checksum != metadata.checksum:
        return AssetStatus.MODIFIED

    return AssetStatus.UNCHANGED
