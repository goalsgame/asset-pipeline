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


# Recursive helper for serialization:
def _convert_for_serialization(value: t.Any) -> t.Any:
    if isinstance(value, Path):
        return str(value)
    elif isinstance(value, list):
        return [_convert_for_serialization(item) for item in value]
    elif isinstance(value, dict):
        return {k: _convert_for_serialization(v) for k, v in value.items()}
    else:
        return value


def serialize_dataclass(instance: t.Any) -> dict:
    """
    Convert a dataclass instance to a dictionary.
    Handles conversion of non-JSON-friendly types like Path and nested dataclasses.
    """
    data = dc.asdict(instance)
    return _convert_for_serialization(data)


# Helper for deserialization: recursively convert values based on the field type.
def _convert_to_field(field_type: t.Any, value: t.Any) -> t.Any:
    if value is None:
        return value

    # Direct conversion for Path
    if field_type is Path:
        return Path(value)

    # If the field is a dataclass, recursively deserialize it.
    if dc.is_dataclass(field_type):
        return deserialize_dataclass(field_type, value)

    # If the field is a list, check its inner type.
    origin = t.get_origin(field_type)
    if origin is list:
        (inner_type,) = t.get_args(field_type)
        if inner_type is Path:
            return [Path(item) for item in value]
        elif dc.is_dataclass(inner_type):
            return [deserialize_dataclass(inner_type, item) for item in value]
        else:
            return value

    # For any other type, assume it is JSON–friendly.
    return value

def deserialize_dataclass(cls: t.Type, data: dict) -> t.Any:
    """
    Convert a dictionary into a dataclass instance.
    Handles conversion of fields like lists of Paths or nested dataclasses.
    """
    field_values = {}
    for field in dc.fields(cls):
        raw_value = data.get(field.name)
        field_values[field.name] = _convert_to_field(field.type, raw_value)
    return cls(**field_values)