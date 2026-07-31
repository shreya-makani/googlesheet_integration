import os
import json
import logging
from quantum.CoreEngine import CoreEngine
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
    DATASET_KEY,
    HEADERS_KEY,
    ROWS_KEY,
    SHEET_NAME_KEY,
    TOTAL_ROWS_KEY,
    TOTAL_COLUMNS_KEY
)
from google_sheets_fetcher import fetch_sheet_data


class MyMachine(CoreEngine):
    input_data = {}
    dependent_machine_data = {}

    def receiving(self, input_data, dependent_machine_data, callback):
        data = {}
        error_list = []
        try:
            data = self.get_final_data() or {}
            error_list = self.get_error_list() or []
            self.input_data = input_data
            self.dependent_machine_data = dependent_machine_data
            
            # Store Google Sheets credentials from input
            self.google_sheet_id = self.input_data.get(GOOGLE_SHEET_ID_KEY, "")
            self.google_api_key = self.input_data.get(GOOGLE_API_KEY_KEY, "")
            self.google_sheet_range = self.input_data.get(GOOGLE_SHEET_RANGE_KEY, "")
            
            # Log received parameters (without exposing API key)
            self.machine_logger.info(f"Received Google Sheet ID: {self.google_sheet_id}")
            self.machine_logger.info(f"Received sheet range: {self.google_sheet_range}")
            self.machine_logger.info(f"API key received: {'Yes' if self.google_api_key else 'No'}")
            
        except Exception as e:
            error_list.append(f"Error in receiving: {str(e)}")
            self.machine_logger.error(f"Receiving error: {str(e)}")
        finally:
            callback(data, error_list)

    def pre_processing(self, callback):
        data = {}
        error_list = []
        try:
            data = self.get_final_data() or {}
            error_list = self.get_error_list() or []
            
            # Validate that required fields are present
            validation_errors = []
            
            if not self.google_sheet_id:
                validation_errors.append("Google Sheet ID is required but not provided")
            
            if not self.google_api_key:
                validation_errors.append("Google API key is required but not provided")
            
            if not self.google_sheet_range:
                validation_errors.append("Google Sheet range is required but not provided")
            
            if validation_errors:
                for error in validation_errors:
                    error_list.append(error)
                    self.machine_logger.error(error)
            else:
                self.machine_logger.info("All required Google Sheets parameters are present")
            
        except Exception as e:
            error_list.append(f"Error in pre-processing: {str(e)}")
            self.machine_logger.error(f"Pre-processing error: {str(e)}")
        finally:
            callback(data, error_list)

    def processing(self, callback):
        data = {}
        error_list = []
        try:
            data = self.get_final_data() or {}
            error_list = self.get_error_list() or []
            
            # Only proceed if we have all required credentials
            if not error_list:
                self.machine_logger.info("Starting Google Sheets data fetch")
                
                # Call the Google Sheets fetcher with runtime credentials
                envelope = fetch_sheet_data(
                    sheet_id=self.google_sheet_id,
                    api_key=self.google_api_key,
                    sheet_range=self.google_sheet_range,
                    logger=self.machine_logger
                )
                
                # Check the envelope status
                if envelope[STATUS_KEY] == STATUS_SUCCESS:
                    self.machine_logger.info("Successfully fetched data from Google Sheets")
                    
                    # Extract the result from the envelope
                    result = envelope[RESULT_KEY]
                    
                    # Extract dataset and metadata
                    if DATASET_KEY in result:
                        dataset = result[DATASET_KEY]
                        data[DATASET_KEY] = dataset
                        
                        # Also extract headers and rows separately if present
                        if HEADERS_KEY in dataset:
                            data[HEADERS_KEY] = dataset[HEADERS_KEY]
                            self.machine_logger.info(f"Extracted {len(dataset[HEADERS_KEY])} headers")
                        
                        if ROWS_KEY in dataset:
                            data[ROWS_KEY] = dataset[ROWS_KEY]
                            self.machine_logger.info(f"Extracted {len(dataset[ROWS_KEY])} rows")
                    
                    # Extract metadata if present
                    if METADATA_KEY in envelope:
                        metadata = envelope[METADATA_KEY]
                        data[METADATA_KEY] = metadata
                        
                        # Log metadata details
                        if SHEET_NAME_KEY in metadata:
                            self.machine_logger.info(f"Sheet name: {metadata[SHEET_NAME_KEY]}")
                        if TOTAL_ROWS_KEY in metadata:
                            self.machine_logger.info(f"Total rows: {metadata[TOTAL_ROWS_KEY]}")
                        if TOTAL_COLUMNS_KEY in metadata:
                            self.machine_logger.info(f"Total columns: {metadata[TOTAL_COLUMNS_KEY]}")
                    
                else:
                    # Handle error status
                    error_msg = envelope[ERROR_KEY]
                    error_list.append(error_msg)
                    self.machine_logger.error(f"Google Sheets fetch failed: {error_msg}")
            else:
                self.machine_logger.warning("Skipping processing due to validation errors")
            
        except Exception as e:
            error_list.append(f"Error in processing: {str(e)}")
            self.machine_logger.error(f"Processing error: {str(e)}")
        finally:
            callback(data, error_list)

    def post_processing(self, callback):
        data = {}
        error_list = []
        try:
            data = self.get_final_data() or {}
            error_list = self.get_error_list() or []
            
            # Ensure output structure is clean and consistent
            if DATASET_KEY in data:
                dataset = data[DATASET_KEY]
                
                # Ensure dataset has both headers and rows keys even if empty
                if HEADERS_KEY not in dataset:
                    dataset[HEADERS_KEY] = []
                if ROWS_KEY not in dataset:
                    dataset[ROWS_KEY] = []
                
                # Log final dataset statistics
                self.machine_logger.info(f"Final dataset contains {len(dataset[HEADERS_KEY])} headers and {len(dataset[ROWS_KEY])} rows")
            
            # Ensure metadata exists even if empty
            if METADATA_KEY not in data:
                data[METADATA_KEY] = {
                    SHEET_NAME_KEY: "",
                    TOTAL_ROWS_KEY: 0,
                    TOTAL_COLUMNS_KEY: 0
                }
            
        except Exception as e:
            error_list.append(f"Error in post-processing: {str(e)}")
            self.machine_logger.error(f"Post-processing error: {str(e)}")
        finally:
            callback(data, error_list)

    def packaging_shipping(self, callback):
        data = {}
        error_list = []
        try:
            data = self.get_final_data() or {}
            error_list = self.get_error_list() or []
            
            # Final packaging - ensure all expected output keys are present
            output_structure = {
                DATASET_KEY: data.get(DATASET_KEY, {HEADERS_KEY: [], ROWS_KEY: []}),
                HEADERS_KEY: data.get(HEADERS_KEY, []),
                ROWS_KEY: data.get(ROWS_KEY, []),
                METADATA_KEY: data.get(METADATA_KEY, {
                    SHEET_NAME_KEY: "",
                    TOTAL_ROWS_KEY: 0,
                    TOTAL_COLUMNS_KEY: 0
                })
            }
            
            # Update data with final structure
            data.update(output_structure)
            
            # Log final output summary
            if not error_list:
                self.machine_logger.info("Successfully packaged Google Sheets data for output")
            else:
                self.machine_logger.warning(f"Completed with {len(error_list)} errors")
        
        except Exception as e:
            error_list.append(f"Error in packaging: {str(e)}")
            self.machine_logger.error(f"Packaging error: {str(e)}")
        finally:
            callback(data, error_list)

if __name__ == '__main__':
    machine = MyMachine()
    machine.start()