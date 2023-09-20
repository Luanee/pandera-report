from typing import TypedDict


class QualityColumnsOptions(TypedDict):
    """
    TypedDict representing options for quality columns.

    Attributes:
        issues (str): The name of the column containing quality issues.
        status (str): The name of the column containing quality status.
    """

    issues: str
    status: str


class QualityStatusOptions(TypedDict):
    """
    TypedDict representing options for quality status.

    Attributes:
        valid (str): The valid quality status.
        invalid (str): The invalid quality status.
        none (str): The none quality status.
    """

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
