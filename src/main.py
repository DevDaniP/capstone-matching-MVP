import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_google_sheets_service():
    """Initialize and return Google Sheets service using hardcoded service account info."""
    try:    
        service_account_info = {
    "type": "service_account",
    "project_id": "CS469-Clark",
    "private_key_id": "7d17a05d7d1755039562b75ecadc22d220928968",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCdtHV6eQOH49b3\nqiO6Jc9+PXMLgDBA5k9mZF2/Jik63BqKUxFx6bUsTIGAP/n+xxVQ3HWznCUcMw9q\nsTIeOFKzaJpt9I8XUQl/oD1/fyBramzxDGbdpsxgY+WP1E4gLD+pVxh8wfUWM26/\no+tbBXPQQfg16exlOinxRa8yi9RxfO/KF4okS9U0sHEdVS/nTaSVmhcYzVWSTiUF\nZUc939WWtGLi2edmdfS2vmJq6s550mCRvdngj06SzZhpcl5L43OiS7Tyw4JPoWyv\nY0SWBRn3uuQE49b7XMovPUBzCweEk6EFskMcvp2J/FkeXIVmyXrXa2dKshXSvfp5\n6tmQDaE5AgMBAAECggEAEvNn1+se1NTjiii0g7Pzdn9lNGaXuyocic4Ebenks8wA\nlyAFoqNWQBfZdVM6yWDxsMvX4QN3JNJbRz46gDh9x6K0Rq5IBkyYpZuDMwT7HQKm\n9g3AIWE1LLK/F++H4S8wCeYLbUJ+yceDHB2oiew3zzjTiOGupI4UEt2FgL9zgfI0\ng1EgYLc4+xbqdRNRYnNvy681/b8ny7Zj1PgUg7vrymnnkbje0VDvZ/DFVlRXGr2S\nb4cve9RImL1tP5pvwgzqydPcDPl2bZpohkYDXd488aJSA/ZOgngZJGzafBfswIxE\n5X94Mj8As/iiUNJNUsoIcRFpyuZrwWa7aqOaZRX5+QKBgQDNtzCeME5/0K3J4ZAC\nSW/5SIRNbOLiVWA8p3Tzg+I8ltMxxtrdaklm9fbj1Z0a7FFVxT5yB2dbcjclLIog\nXVLkHABL7N6R+KKAPJzFQXWqcH1HoJgrs8cV94AZK5BBuSM2fEDQ/t7YMzd3XLB7\n82s3wKLoKVZ8HtocvnmIkxo+CwKBgQDEQPb32wmb9o2k9VMx+uUHfyJYigzQSXL7\nkRBJdeLT4/ot2WMIhuuJ7qEjds0aJtOMh3zb4qfREguw28mvUhPsxcUINoo4utQp\nmoCpzzWl1w6uzZAiW8MutQTxEiJDJXL4QFtDum4Y2WFb7xMOa9Nw0ou5hgjWzJRJ\nAKuOYaTcSwKBgAcJl04yFN1mhCt93fFWFdCPXIdRjEl15j7s86FJB7pO5pazWNVu\nR2iQTYvpyOAc6YNnpgU8n5qPQ7ev2GHXD3jiRFhUmCCiQtzkNfDBloboJkEHC22j\nTtI/j1BNHzhAXyYEBiugLHt09RbOQvNalnZnzqrmjyDb5VZKZdn4PlOVAoGARIAU\nc+DNUtXVDN3gQxK6vEog19yfqlfovWwdzjZKjQEHAtfc3E4TippzPiiqYFVrA6MK\n7skHIE93Ky0cEYjJkZxaMIqw5io4Aal+/UZpCFCvPE5d39A9qWDfr7FPqjY5EfOM\np3A8G4pMlEU3VpJGRBwJTyE8lpTjsTN9rf3hCE8CgYBC9xURl/tNim3h2rvdJspY\nPaGi/Jd5zalpzl2KJX6TdSmaJH0t4NgwXEuQOD2E/usivkzKBf8Et9alS4FT2vq3\no9aUM0HRBm6YmJjHsx3xBjGnC1jrbaV5t9LHWHqNNMyF13iPDSVyhoRm7DSBCwA8\ndKD3CQao2ED03Yjvnru62g==\n-----END PRIVATE KEY-----\n",
    "client_email": "capstone-mvp-sheets@cs469-clark.iam.gserviceaccount.com",
    "client_id": "108641928393358442443",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/capstone-mvp-sheets@cs469-clark.iam.gserviceaccount.com"
}

    
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
    RANGE_NAME = 'Form Responses 1!A1:AJ2'
    
    data = read_spreadsheet_data(SPREADSHEET_ID, RANGE_NAME)
    if data:
        print("Spreadsheet data:")
        for row in data:
            print(row)
        
        # Convert to pandas DataFrame
        # First row as headers, remaining rows as data
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
        else:
            # If only one row, treat it as data with default column names
            df = pd.DataFrame(data)
        
        print("\nDataFrame:")
        print(df)
        print(f"\nDataFrame shape: {df.shape}")
    else:
        # Create empty DataFrame if no data
        df = pd.DataFrame()
        print("No data retrieved, created empty DataFrame")
        print(df)