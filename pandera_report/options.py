from typing import TypedDict


class QualityColumnsOptions(TypedDict):
    issues: str
    status: str


class QualityStatusOptions(TypedDict):
    valid: str
    invalid: str
    none: str

DEFAULT_QUALITY_ISSUES_COLUMN = "quality_issues"
DEFAULT_QUALITY_STATUS_COLUMN = "quality_status"


QUALITY_COLUMNS_OPTIONS: QualityColumnsOptions = {
    "issues": DEFAULT_QUALITY_ISSUES_COLUMN, 
    "status": DEFAULT_QUALITY_STATUS_COLUMN,
}

QUALITY_STATUS_OPTIONS: QualityStatusOptions = {
    "valid": "Valid", 
    "invalid": "Invalid", 
    "none": "None",
}
