

from flask import Flask, request, jsonify
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os

app = Flask(__name__)

def get_google_sheet():
    creds_path = os.getenv("GOOGLE_SHEET_CREDENTIALS_PATH")
    sheet_id = os.getenv("GOOGLE_SHEET_ID")    
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(creds_path, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.sheet1  


    headers = ["ID", "Name", "Address", "Contact", "Email"]
    if not worksheet.row_values(1): 
        worksheet.append_row(headers)

    return worksheet

@app.route('/submit', methods=['POST'])
def submit_data():
    try:
        data = request.json
        name = data.get('name')
        address = data.get('address')
        contact = data.get('contact')
        email = data.get('email')

        if not all([name, address, contact, email]):
            return jsonify({"status": "error", "message": "All fields are required."}), 400

        sheet = get_google_sheet()
        existing_emails = [row[4] for row in sheet.get_all_values()[1:]]  # Skip header
        if email in existing_emails:
            return jsonify({"status": "error", "message": "Email already exists."}), 400

        all_rows = sheet.get_all_values()
        last_id = int(all_rows[-1][0]) if len(all_rows) > 1 else 0  # Get the last ID or start at 0
        new_id = last_id + 1

        sheet.append_row([new_id, name, address, contact, email])

        return jsonify({"status": "success", "message": "Data submitted successfully."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
