"""Pandera Report for row-based reporting by using the power of pandera."""

from pandera_report.options import QualityColumnsOptions, QualityStatusOptions
from pandera_report.parser import DefaultFailureCaseParser, FailureCaseParser
from pandera_report.validator import DataFrameValidator
from pandera_report.version import __version__

__all__ = [
    # validator
    "DataFrameValidator",
    # parser
    "DefaultFailureCaseParser",
    "FailureCaseParser",
    # options
    "QualityStatusOptions",
    "QualityColumnsOptions",
    # version
    "__version__",
]
