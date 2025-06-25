import os
import email
import json
import google.generativeai as genai
from email import policy
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials

GEMINI_API_KEY = "AIzaSyAGL96xP4pKGiHkIyUkBrCMMpFltia8gvc"
SPREADSHEET_ID = '1pcdM68E-5Ecvd0K3z62ZhteO9fDDfPUvKj4YaPeD9qM'
SHEET_RANGE = 'Sheet1!A2'
GOOGLE_CREDENTIALS_FILE = 'email snapper.json'
EMAIL_FOLDER = 'emails'

try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
except Exception as e:
    print(f"Failed to configure Gemini. Check your API Key. Error: {e}")
    exit()

def extract_text_from_eml(file_path):
    try:
        with open(file_path, 'rb') as f:
            msg = email.message_from_binary_file(f, policy=policy.default)
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain" and part.get_payload(decode=True):
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        break
            else:
                if msg.get_payload(decode=True):
                    body = msg.get_payload(decode=True).decode(errors='ignore')
        return {
            'sender': msg.get('From', 'N/A'),
            'date': msg.get('Date', 'N/A'),
            'subject': msg.get('Subject', 'N/A'),
            'body': body
        }
    except Exception as e:
        print(f"Error reading email file {file_path}: {e}")
        return None

def extract_shipping_data(text_data):
    prompt = f"""
You are an expert assistant for a logistics company. Your task is to extract key information from an email and return it as a single, valid JSON object.
Do not include any text, notes, or markdown formatting (like ```json) before or after the JSON object.

The fields to extract are exactly as follows:
- "FROM email id": The email address of the sender.
- "DATE & time received": The date the email was sent.
- "Shipping line": The name of the shipping company (e.g., Maersk, COSCO, ONE). If not found, use "N/A".
- "FROM port": The port of origin. If not found, use "N/A".
- "to PORT": The port of destination. If not found, use "N/A".
- "20 prices": The price for a 20' container (e.g., "USD 800"). If not found, use "N/A".
- "40 prices": The price for a 40' container (e.g., "USD 1200"). If not found, use "N/A".

--- EMAIL CONTENT ---
{text_data}
--- END CONTENT ---
"""
    try:
        response = model.generate_content(prompt)

        if not response.candidates or response.candidates[0].finish_reason.name not in ["STOP", "MAX_TOKENS"]:
            print(f"API call failed or was blocked. Feedback: {response.prompt_feedback}")
            return None

        json_text = response.text.strip()
        print("AI raw response:", json_text)
        
        if json_text.startswith("```json"):
            json_text = json_text[7:-3].strip()
        
        return json.loads(json_text)

    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON. Reason: {e}. Response was: {json_text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred with the Gemini API call: {e}")
        return None

def upload_to_google_sheets(data_rows):
    try:
        creds = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=creds)
        
        headers = ["FROM email id", "DATE & time received", "Shipping line", "FROM port", "to PORT", "20 prices", "40 prices"]
        
        values = [
            [row.get(header, "") for header in headers] for row in data_rows
        ]

        print("Uploading these rows:", values)
        body = {'values': values}
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_RANGE,
            valueInputOption='RAW',
            body=body
        ).execute()
        print(f"{result.get('updates', {}).get('updatedCells', 0)} cells appended.")

    except FileNotFoundError:
        print(f"Error: Credentials file not found at '{GOOGLE_CREDENTIALS_FILE}'")
    except HttpError as e:
        print(f"An error occurred with the Google Sheets API: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during sheet upload: {e}")

if __name__ == "__main__":
    results = []
    if not os.path.exists(EMAIL_FOLDER):
        print(f"Error: '{EMAIL_FOLDER}' folder does not exist. Please create it and add .eml files.")
        exit()

    for filename in os.listdir(EMAIL_FOLDER):
        if filename.lower().endswith('.eml'):
            file_path = os.path.join(EMAIL_FOLDER, filename)
            print(f"\n--- Processing {filename} ---")
            raw_data = extract_text_from_eml(file_path)
            
            if raw_data and raw_data['body']:
                full_text = f"Subject: {raw_data['subject']}\nFrom: {raw_data['sender']}\nDate: {raw_data['date']}\n\n{raw_data['body']}"
                structured_data = extract_shipping_data(full_text)
                
                if structured_data:
                    results.append(structured_data)
                else:
                    print(f"Could not extract structured data from {filename}.")
            else:
                print(f"Skipping {filename} due to read error or empty body.")

    if results:
        print("\nUploading all extracted data to Google Sheets...")
        upload_to_google_sheets(results)
        print("Done.")
    else:
        print("\nNo valid data was extracted from the email files to upload.")