import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from matching_algorithm import create_capstone_teams 

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

def transform_data_for_algorithm(df):
    """Transform spreadsheet data into format needed by create_capstone_teams."""
    
    people = df['Please Enter Your Name.'].tolist()
    
    project_cols = [col for col in df.columns if col.startswith('Rank the projects')]
    projects = []
    for col in project_cols:
        project_name = col.split('[')[1].rstrip(']')
        projects.append(project_name)
    
    project_prefs = {}
    for idx, person in enumerate(people):
        project_prefs[person] = {}
        person_row = df.iloc[idx]
        for col in project_cols:
            project_name = col.split('[')[1].rstrip(']')
            ranking = person_row[col]
            if pd.notna(ranking):
                project_prefs[person][project_name] = 6 - int(ranking)
    

    teammate_rank_cols = [col for col in df.columns if col.startswith("Rank the people you'd like to work with")]
    teammate_avoid_cols = [col for col in df.columns if col.startswith("Choose three people you don't want")]
    
    teammate_prefs = {}
    for idx, person in enumerate(people):
        teammate_prefs[person] = {}
        person_row = df.iloc[idx]
        
        for col in teammate_rank_cols:
            teammate_name = person_row[col]
            if pd.notna(teammate_name) and teammate_name in people:
                rank_num = int(col.split('[Person ')[1].rstrip(']').strip())
        
                teammate_prefs[person][teammate_name] = max(1, 11 - rank_num)
       
        for col in teammate_avoid_cols:
            teammate_name = person_row[col]
            if pd.notna(teammate_name) and teammate_name in people:
                teammate_prefs[person][teammate_name] = 1  
    
    return people, teammate_prefs, projects, project_prefs

def write_to_spreadsheet(spreadsheet_id, range_name, values):
    """Write data to a Google Spreadsheet."""
    service = get_google_sheets_service()
    if not service:
        return False
    
    try:
        body = {'values': values}
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        print(f"{result.get('updatedCells')} cells updated.")
        return True
    except HttpError as error:
        print(f'An error occurred: {error}')
        return False
    
if __name__ == "__main__":
    
    SPREADSHEET_ID = '1yCtVanPpqrmO_nhFk4V6eecgrj1XmWSVq3w9ZclYS6Q'
    INPUT_RANGE = 'Form Responses 1!A1:AL100'
    OUTPUT_RANGE = 'Team Results!A1' 
    
    data = read_spreadsheet_data(SPREADSHEET_ID, INPUT_RANGE)
    if data:

        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
        else:
            df = pd.DataFrame(data)
        
        print(f"\nDataFrame shape: {df.shape}")
        
        people, teammate_prefs, projects, project_prefs = transform_data_for_algorithm(df)
        
        results, total_score = create_capstone_teams(
            people, teammate_prefs, projects, project_prefs
        )
        
        output_values = [['Team Members', 'Project', 'Score']]
        for team, project, score in results:
            output_values.append([', '.join(team), project, score])
        output_values.append(['', 'Overall Score', total_score])
        
        write_to_spreadsheet(SPREADSHEET_ID, OUTPUT_RANGE, output_values)
        
        print("\n=== Team Results ===")
        for team, project, score in results:
            print(f"Team: {team} → {project} (Score: {score}/100)")
        print(f"\nOverall Score: {total_score}/100")