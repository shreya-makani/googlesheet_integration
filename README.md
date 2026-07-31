# Google Sheets Integration - Quantum Machine Node

## Overview
This Quantum Machine Node seamlessly connects to Google Sheets and extracts structured data from specified ranges. It transforms spreadsheet data into a standardized format ready for downstream processing in your ETL workflow.

## Key Features
- **Direct Google Sheets Access**: Securely connects to any Google Sheet using API authentication
- **Flexible Range Selection**: Extract specific data ranges using standard A1 notation (e.g., A1:D100)
- **Structured Data Output**: Automatically separates headers and rows for easy data manipulation
- **Metadata Enrichment**: Provides sheet statistics including total rows and columns processed

## Configuration Guide
To configure this machine in the Quantum Datalytica platform, you'll need to provide:

- **Google Sheet ID**: The unique identifier from your Google Sheet URL (found between /d/ and /edit in the URL)
- **Google API Key**: Your Google Cloud Platform API key with Sheets API enabled
- **Sheet Range**: The data range to extract in A1 notation (e.g., "Sheet1!A1:E50" or just "A:E" for all rows)

## Expected Output
This node produces a structured dataset containing:
- A complete dataset object with separated headers and data rows
- Individual headers array for column identification
- Rows array with all data records
- Metadata including the sheet name, total row count, and total column count

The output format is optimized for direct consumption by downstream analytics, transformation, or storage nodes in your quantum workflow.