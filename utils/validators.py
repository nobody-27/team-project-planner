import json
from typing import Dict, Any
from .exceptions import ValidationError

def validate_json_string(json_str: str) -> Dict[str, Any]:
    """Validate and parse JSON string - handles all the input parsing"""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON format: {str(e)}")

def validate_string_length(value: str, field_name: str, max_length: int):
    """Validate string length constraint - requirements were very specific about these limits"""
    if len(value) > max_length:
        raise ValidationError(f"{field_name} exceeds maximum length of {max_length} characters")

def validate_required_fields(data: Dict[str, Any], required_fields: list):
    """Validate that all required fields are present"""
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

def validate_id_format(id_value: str):
    """Validate ID format (UUID)"""
    import uuid
    try:
        uuid.UUID(id_value)
    except ValueError:
        raise ValidationError(f"Invalid ID format: {id_value}")