# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# model/schema.py

TYPE_MAP = {
    "string": "string",
    "integer": "int",
    "number": "double",
    "boolean": "bool"
}


def _build_object_schema(items_schema: dict) -> dict:
    """Build a Pydantic-like schema dict from an items' schema."""

    return {
        "type": "object",
        "properties": items_schema.get("properties", {}),
        "required": items_schema.get("required", [])
    }


def _convert_array_field(field: dict) -> dict | None:
    """Convert array fields (list of str, int, float, or dict)."""
    items = field.get("items", {})
    items_type = items.get("type")

    # Only support list of str, int, float, dict
    if items_type == "string":
        return {"bsonType": "array", "items": {"bsonType": "string"}}

    if items_type == "integer":
        return {"bsonType": "array", "items": {"bsonType": "int"}}

    if items_type == "number":
        return {"bsonType": "array", "items": {"bsonType": "double"}}

    if items_type == "object":
        return {"bsonType": "array", "items": {"bsonType": "object"}}

    return None


def _convert_dict_field(field: dict) -> dict | None:
    """Convert dict[str, str], dict[str, int], dict[str, float], dict[str, dict] fields."""
    if field.get("type") == "object":
        ap = field.get("additionalProperties", {})

        # Only support dict[str, str], dict[str, int], dict[str, float], dict[str, dict]
        if not field.get("properties"):
            if isinstance(ap, dict):
                ap_type = ap.get("type")
                if ap_type == "string":
                    return {"bsonType": "object", "additionalProperties": {"bsonType": "string"}}

                if ap_type == "integer":
                    return {"bsonType": "object", "additionalProperties": {"bsonType": "int"}}

                if ap_type == "number":
                    return {"bsonType": "object", "additionalProperties": {"bsonType": "double"}}

                if ap_type == "object":
                    return {"bsonType": "object", "additionalProperties": {"bsonType": "object"}}

            elif isinstance(ap, bool):
                # True means allow any type, False means no additional properties
                if ap:
                    return {"bsonType": "object"}  # allow any

                else:
                    return {"bsonType": "object", "additionalProperties": False}

    return None


def _convert_anyof_field(field: dict) -> dict | None:
    """Convert Optional fields (anyOf with null)."""

    if "anyOf" not in field:
        return None

    bson_types = set()
    anyof_list = []

    for option in field["anyOf"]:
        opt_type = option.get("type")
        if opt_type == "null":
            bson_types.add("null")

        elif opt_type == "array":
            array_result = _convert_array_field(option)
            if array_result:
                anyof_list.append(array_result)

        elif opt_type == "object":
            dict_result = _convert_dict_field(option)
            if dict_result:
                anyof_list.append(dict_result)

        elif opt_type:
            bson_types.add(TYPE_MAP.get(opt_type, opt_type))

    anyof_list.extend({"bsonType": t} for t in bson_types)
    return anyof_list[0] if len(anyof_list) == 1 else {"anyOf": anyof_list}


def _convert_field(field: dict) -> dict:
    """Convert a single Pydantic field to MongoDB JSON schema format."""

    # Try each field type converter in order
    if result := _convert_dict_field(field):
        return result

    if field.get("type") == "array":
        if result := _convert_array_field(field):
            return result

    if result := _convert_anyof_field(field):
        return result

    # Handle nullable (Pydantic 2+)
    if field.get("nullable"):
        field_type = field.get("type")
        return {"bsonType": [TYPE_MAP.get(field_type, field_type), "null"]}

    # Handle simple types
    if field_type := field.get("type"):
        return {"bsonType": TYPE_MAP.get(field_type, field_type)}

    # Fallback
    return {"bsonType": "string"}


def _is_required(field: dict) -> bool:
    """Check if a field is required (non-optional)."""

    if "anyOf" in field:
        if any(opt.get("type") == "null" for opt in field["anyOf"]):
            return False

    return not field.get("nullable", False)


def _normalize_field_name(name: str) -> str:
    """Convert 'id' to '_id' for MongoDB compatibility."""

    return "_id" if name == "id" else name


def pydantic_to_mongo_jsonschema(pydantic_schema: dict) -> dict:
    """ Convert a Pydantic JSON schema to a MongoDB JSON schema.
        Supports:
            - string, integer, number, boolean, list, dict
    """

    properties = pydantic_schema.get("properties", {})
    required = pydantic_schema.get("required", [])

    # Convert properties
    mongo_props = {
        _normalize_field_name(name): _convert_field(field)
        for name, field in properties.items()
    }

    # Filter required fields (exclude optionals)
    required_fields = [
        _normalize_field_name(name)
        for name in required
        if _is_required(properties.get(name, {}))
    ]

    result: dict = {
        "bsonType": "object",
        "properties": mongo_props
    }

    # MongoDB doesn't allow empty required array
    if required_fields:
        result["required"] = required_fields

    return result

