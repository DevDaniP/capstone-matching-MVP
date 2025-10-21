import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_google_sheets_service():
    try:
        with open('credentials.json', 'r') as f:
            service_account_info = json.load(f)
        
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES)
        
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error initializing Google Sheets service: {e}")
        return None

def read_spreadsheet_data(spreadsheet_id, range_name):
    """Read data from a Google Spreadsheet."""
    service = get_google_sheets_service()
    if not service:
        return None
    
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])
        
        if not values:
            print('No data found.')
            return None
        
        return values
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

if __name__ == "__main__":
    SPREADSHEET_ID = '1yCtVanPpqrmO_nhFk4V6eecgrj1XmWSVq3w9ZclYS6Q'
    RANGE_NAME = 'Form Responses 1!A1:AL6'
    
    data = read_spreadsheet_data(SPREADSHEET_ID, RANGE_NAME)
    if data:
        print("Spreadsheet data:")
        for row in data:
            print(row)
        
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
        else:
            df = pd.DataFrame(data)
        
        print("\nDataFrame:")
        print(df)
        print(f"\nDataFrame shape: {df.shape}")
    else:
        df = pd.DataFrame()
        print("No data retrieved, created empty DataFrame")
        print(df)