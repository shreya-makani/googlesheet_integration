"""
Google Sheets Fetcher Module for Googlesheet_Integration machine.

This module handles Google Sheets API authentication and data fetching.
It validates credentials, connects to Google Sheets API v4, fetches data
from specified ranges, and returns structured datasets.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Union
import requests
from urllib.parse import quote

from contracts import (
    GOOGLE_SHEET_ID_KEY,
    GOOGLE_API_KEY_KEY,
    GOOGLE_SHEET_RANGE_KEY,
    STATUS_KEY,
    ACTION_KEY,
    RESULT_KEY,
    ERROR_KEY,
    METADATA_KEY,
    STATUS_SUCCESS,
    STATUS_ERROR,
    ACTION_FETCH_GOOGLE_SHEET_DATA,
    DATASET_KEY,
    HEADERS_KEY,
    ROWS_KEY,
    SHEET_NAME_KEY,
    TOTAL_ROWS_KEY,
    TOTAL_COLUMNS_KEY
)

# Module logger
logger = logging.getLogger(__name__)


class GoogleSheetsAPIError(Exception):
    """Custom exception for Google Sheets API errors."""
    pass


class GoogleSheetsValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_google_sheet_id(sheet_id: str) -> None:
    """
    Validate Google Sheet ID format.
    
    Args:
        sheet_id: The Google Sheet ID to validate
        
    Raises:
        GoogleSheetsValidationError: If sheet ID is invalid
    """
    if not sheet_id:
        raise GoogleSheetsValidationError("Google Sheet ID cannot be empty")
    
    if not isinstance(sheet_id, str):
        raise GoogleSheetsValidationError(f"Google Sheet ID must be a string, got {type(sheet_id).__name__}")
    
    # Google Sheet IDs are typically 44 characters long and contain alphanumeric chars, hyphens, and underscores
    if len(sheet_id) < 10 or len(sheet_id) > 100:
        raise GoogleSheetsValidationError(f"Google Sheet ID length {len(sheet_id)} is outside expected range (10-100)")
    
    # Basic character validation
    if not re.match(r'^[a-zA-Z0-9_-]+$', sheet_id):
        raise GoogleSheetsValidationError("Google Sheet ID contains invalid characters")


def validate_api_key(api_key: str) -> None:
    """
    Validate Google API key format.
    
    Args:
        api_key: The Google API key to validate
        
    Raises:
        GoogleSheetsValidationError: If API key is invalid
    """
    if not api_key:
        raise GoogleSheetsValidationError("Google API key cannot be empty")
    
    if not isinstance(api_key, str):
        raise GoogleSheetsValidationError(f"Google API key must be a string, got {type(api_key).__name__}")
    
    # Google API keys are typically 39 characters long
    if len(api_key) < 20 or len(api_key) > 100:
        raise GoogleSheetsValidationError(f"Google API key length {len(api_key)} is outside expected range (20-100)")
    
    # Basic format check - API keys usually start with "AIza"
    if not re.match(r'^[A-Za-z0-9_-]+$', api_key):
        raise GoogleSheetsValidationError("Google API key contains invalid characters")


def validate_sheet_range(sheet_range: str) -> None:
    """
    Validate Google Sheets A1 notation range.
    
    Args:
        sheet_range: The sheet range in A1 notation
        
    Raises:
        GoogleSheetsValidationError: If range is invalid
    """
    if not sheet_range:
        raise GoogleSheetsValidationError("Sheet range cannot be empty")
    
    if not isinstance(sheet_range, str):
        raise GoogleSheetsValidationError(f"Sheet range must be a string, got {type(sheet_range).__name__}")
    
    # Basic A1 notation validation
    # Examples: A1, A1:B10, Sheet1!A1:B10, 'Sheet Name'!A1:B10
    a1_pattern = r"^('[^']+!'|[A-Za-z0-9_]+!)?[A-Z]+[0-9]+(:[A-Z]+[0-9]+)?$"
    
    # Remove quotes for validation if present
    test_range = sheet_range
    if test_range.startswith("'") and "!'" in test_range:
        test_range = test_range.replace("'", "")
    
    if not re.match(a1_pattern, test_range):
        # Could be just a sheet name or more complex range
        # Allow for now but log warning
        if logger:
            logger.warning(f"Sheet range '{sheet_range}' may not be in standard A1 notation")


def parse_sheet_name_from_range(sheet_range: str) -> str:
    """
    Extract sheet name from range if present.
    
    Args:
        sheet_range: The sheet range in A1 notation
        
    Returns:
        Sheet name if found, otherwise 'Sheet1'
    """
    if '!' in sheet_range:
        sheet_part = sheet_range.split('!')[0]
        # Remove quotes if present
        if sheet_part.startswith("'") and sheet_part.endswith("'"):
            return sheet_part[1:-1]
        return sheet_part
    return 'Sheet1'


def call_google_sheets_api(sheet_id: str, api_key: str, sheet_range: str, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    Call Google Sheets API v4 to fetch data.
    
    Args:
        sheet_id: Google Sheet ID
        api_key: Google API key
        sheet_range: Range in A1 notation
        logger: Optional logger instance
        
    Returns:
        API response as dictionary
        
    Raises:
        GoogleSheetsAPIError: If API call fails
    """
    # Construct API URL
    base_url = "https://sheets.googleapis.com/v4/spreadsheets"
    encoded_range = quote(sheet_range, safe='')
    url = f"{base_url}/{sheet_id}/values/{encoded_range}"
    
    # Add API key as query parameter
    params = {
        'key': api_key,
        'valueRenderOption': 'FORMATTED_VALUE',
        'dateTimeRenderOption': 'FORMATTED_STRING'
    }
    
    if logger:
        logger.info(f"Calling Google Sheets API for sheet {sheet_id}, range {sheet_range}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Bad request')
            raise GoogleSheetsAPIError(f"Invalid request: {error_msg}")
        elif response.status_code == 401:
            raise GoogleSheetsAPIError("Invalid API key or unauthorized access")
        elif response.status_code == 403:
            raise GoogleSheetsAPIError("Access forbidden. Check API key permissions and sheet sharing settings")
        elif response.status_code == 404:
            raise GoogleSheetsAPIError(f"Sheet ID '{sheet_id}' not found or range '{sheet_range}' does not exist")
        elif response.status_code == 429:
            raise GoogleSheetsAPIError("Rate limit exceeded. Please try again later")
        else:
            raise GoogleSheetsAPIError(f"API request failed with status {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        raise GoogleSheetsAPIError("Request timed out while fetching data from Google Sheets")
    except requests.exceptions.ConnectionError as e:
        raise GoogleSheetsAPIError(f"Connection error while accessing Google Sheets API: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise GoogleSheetsAPIError(f"Request error: {str(e)}")


def transform_api_response_to_dataset(api_response: Dict[str, Any], logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    Transform Google Sheets API response to structured dataset.
    
    Args:
        api_response: Raw API response from Google Sheets
        logger: Optional logger instance
        
    Returns:
        Dictionary with headers and rows
    """
    # Extract values from response
    values = api_response.get('values', [])
    
    if not values:
        # Empty range - return empty dataset
        if logger:
            logger.info("Sheet range is empty, returning empty dataset")
        return {
            HEADERS_KEY: [],
            ROWS_KEY: []
        }
    
    # First row as headers if multiple rows exist
    if len(values) > 1:
        headers = values[0] if values[0] else []
        rows = values[1:] if len(values) > 1 else []
        
        # Ensure all rows have same number of columns as headers
        num_cols = len(headers)
        normalized_rows = []
        for row in rows:
            if len(row) < num_cols:
                # Pad with empty strings
                normalized_row = row + [''] * (num_cols - len(row))
            elif len(row) > num_cols:
                # Truncate extra columns
                normalized_row = row[:num_cols]
            else:
                normalized_row = row
            normalized_rows.append(normalized_row)
        
        if logger:
            logger.info(f"Transformed data: {len(headers)} headers, {len(normalized_rows)} rows")
        
        return {
            HEADERS_KEY: headers,
            ROWS_KEY: normalized_rows
        }
    else:
        # Single row - treat as data row with no headers
        if logger:
            logger.info("Single row found, treating as data with no headers")
        return {
            HEADERS_KEY: [],
            ROWS_KEY: values
        }


def fetch_sheet_data(sheet_id: str, api_key: str, sheet_range: str, logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """
    Fetch data from Google Sheets using provided credentials and range.
    
    This is the main exposed function that orchestrates validation,
    API calling, and data transformation.
    
    Args:
        sheet_id: Google Sheet ID
        api_key: Google API key for authentication
        sheet_range: Range in A1 notation (e.g., 'Sheet1!A1:D10')
        logger: Optional logger instance for logging
        
    Returns:
        Internal result envelope with status, action, result, error, and metadata
    """
    # Use module logger if no logger provided
    if logger is None:
        logger = globals().get('logger')
    
    try:
        # Step 1: Validate inputs
        if logger:
            logger.info("Validating Google Sheets credentials and range")
        
        validate_google_sheet_id(sheet_id)
        validate_api_key(api_key)
        validate_sheet_range(sheet_range)
        
        # Step 2: Call Google Sheets API
        if logger:
            logger.info(f"Fetching data from Google Sheet {sheet_id}, range {sheet_range}")
        
        api_response = call_google_sheets_api(sheet_id, api_key, sheet_range, logger)
        
        # Step 3: Transform response to dataset
        dataset = transform_api_response_to_dataset(api_response, logger)
        
        # Step 4: Extract metadata
        sheet_name = parse_sheet_name_from_range(sheet_range)
        total_rows = len(dataset[ROWS_KEY])
        total_columns = len(dataset[HEADERS_KEY]) if dataset[HEADERS_KEY] else (
            len(dataset[ROWS_KEY][0]) if dataset[ROWS_KEY] else 0
        )
        
        # Step 5: Build successful result envelope
        result = {
            DATASET_KEY: dataset
        }
        
        metadata = {
            SHEET_NAME_KEY: sheet_name,
            TOTAL_ROWS_KEY: total_rows,
            TOTAL_COLUMNS_KEY: total_columns
        }
        
        if logger:
            logger.info(f"Successfully fetched {total_rows} rows and {total_columns} columns from sheet '{sheet_name}'")
        
        return {
            STATUS_KEY: STATUS_SUCCESS,
            ACTION_KEY: ACTION_FETCH_GOOGLE_SHEET_DATA,
            RESULT_KEY: result,
            ERROR_KEY: "",
            METADATA_KEY: metadata
        }
        
    except GoogleSheetsValidationError as e:
        error_msg = f"Validation error: {str(e)}"
        if logger:
            logger.error(error_msg)
        return {
            STATUS_KEY: STATUS_ERROR,
            ACTION_KEY: ACTION_FETCH_GOOGLE_SHEET_DATA,
            RESULT_KEY: {},
            ERROR_KEY: error_msg,
            METADATA_KEY: {}
        }
        
    except GoogleSheetsAPIError as e:
        error_msg = f"Google Sheets API error: {str(e)}"
        if logger:
            logger.error(error_msg)
        return {
            STATUS_KEY: STATUS_ERROR,
            ACTION_KEY: ACTION_FETCH_GOOGLE_SHEET_DATA,
            RESULT_KEY: {},
            ERROR_KEY: error_msg,
            METADATA_KEY: {}
        }
        
    except Exception as e:
        # Catch any unexpected errors
        error_msg = f"Unexpected error fetching Google Sheet data: {str(e)}"
        if logger:
            logger.error(error_msg, exc_info=True)
        return {
            STATUS_KEY: STATUS_ERROR,
            ACTION_KEY: ACTION_FETCH_GOOGLE_SHEET_DATA,
            RESULT_KEY: {},
            ERROR_KEY: error_msg,
            METADATA_KEY: {}
        }