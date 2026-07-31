"""
Contracts module for Googlesheet_Integration machine.

Single source of truth for all cross-file dictionary keys and constants.
This module defines all shared constants used across multiple Python files
to ensure consistency and prevent string literal duplication.
"""

# Google Sheets Input Keys
GOOGLE_SHEET_ID_KEY = 'google_sheet_id'
GOOGLE_API_KEY_KEY = 'google_api_key'
GOOGLE_SHEET_RANGE_KEY = 'google_sheet_range'

# Internal Result Envelope Keys
STATUS_KEY = 'status'
ACTION_KEY = 'action'
RESULT_KEY = 'result'
ERROR_KEY = 'error'
METADATA_KEY = 'metadata'

# Status Values
STATUS_SUCCESS = 'success'
STATUS_ERROR = 'error'

# Action Values
ACTION_FETCH_GOOGLE_SHEET_DATA = 'fetch_google_sheet_data'

# Dataset Output Keys
DATASET_KEY = 'dataset'
HEADERS_KEY = 'headers'
ROWS_KEY = 'rows'

# Metadata Keys
SHEET_NAME_KEY = 'sheet_name'
TOTAL_ROWS_KEY = 'total_rows'
TOTAL_COLUMNS_KEY = 'total_columns'

# Collections for validation and iteration
INPUT_KEYS = (
    GOOGLE_SHEET_ID_KEY,
    GOOGLE_API_KEY_KEY,
    GOOGLE_SHEET_RANGE_KEY
)

ENVELOPE_KEYS = (
    STATUS_KEY,
    ACTION_KEY,
    RESULT_KEY,
    ERROR_KEY,
    METADATA_KEY
)

DATASET_STRUCTURE_KEYS = (
    HEADERS_KEY,
    ROWS_KEY
)

METADATA_STRUCTURE_KEYS = (
    SHEET_NAME_KEY,
    TOTAL_ROWS_KEY,
    TOTAL_COLUMNS_KEY
)

STATUS_VALUES = (
    STATUS_SUCCESS,
    STATUS_ERROR
)

ACTION_VALUES = (
    ACTION_FETCH_GOOGLE_SHEET_DATA,
)

OUTPUT_KEYS = (
    DATASET_KEY,
)