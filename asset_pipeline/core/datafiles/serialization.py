import json
import dataclasses as dc
from pathlib import Path
import typing as t


def save_json(data: t.Any, file_path: t.Union[str, Path], indent: int = 2) -> None:
    """
    Save data to a JSON file.

    :param data: Data to serialize
    :param file_path: Destination file path
    :param indent: Indentation for the JSON file
    """
    file_path = Path(file_path)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)


def load_json(file_path: t.Union[str, Path]) -> t.Any:
    """
    Load data from a JSON file.

    :param file_path: Source file path
    :returns: Deserialized data
    """
    file_path = Path(file_path)
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def serialize_dataclass(instance: t.Any) -> dict:
    """
    Convert a dataclass instance to a dictionary.
    Handles conversion of non-JSON-friendly types like Path.

    :param instance: Dataclass instance to serialize
    :returns: Dictionary representation suitable for JSON
    """
    data = dc.asdict(instance)
    for field_info in dc.fields(instance):
        if t.get_origin(field_info.type) is list:
            # Check if it's a list of Path objects
            list_args = t.get_args(field_info.type)
            if list_args and list_args[0] is Path:
                data[field_info.name] = [str(item) for item in data[field_info.name]]
    return data


def deserialize_dataclass(cls: t.Type, data: dict) -> t.Any:
    """
    Convert a dictionary into a dataclass instance.
    Handles conversion of fields like lists of Paths.

    :param cls: Dataclass type
    :param data: Dictionary with data
    :returns: Dataclass instance
    """
    field_types = {field.name: field.type for field in dc.fields(cls)}
    for field_name, field_type in field_types.items():
        if t.get_origin(field_type) is list:
            list_args = t.get_args(field_type)
            if list_args and list_args[0] is Path:
                data[field_name] = [Path(p) for p in data.get(field_name, [])]
    return cls(**data)
