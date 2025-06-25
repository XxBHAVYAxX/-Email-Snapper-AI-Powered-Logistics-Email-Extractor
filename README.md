# 📧 Email Snapper: AI-Powered Logistics Email Extractor

**Email Snapper** is a Python tool that automates the extraction of shipping rate details from `.eml` email files and uploads structured data directly to a Google Sheet using Google Sheets API and Gemini AI (Google Generative AI).

---

## ✨ Features

- Parses `.eml` files to extract:
  - Sender email
  - Date & time received
  - Subject and body
- Uses **Google Gemini AI** to extract structured shipping data:
  - Shipping line
  - Origin and destination ports
  - Pricing for 20' and 40' containers
- Automatically appends structured data to a Google Sheet
- Handles errors gracefully and logs informative messages

---

## 📁 Project Structure

```
.
├── email_AI.py               # Main script
├── email snapper.json        # Google Service Account credentials
├── emails/                   # Folder containing .eml files (user-provided)
├── README.md                 # You're reading it :)
```

---

## ⚙️ Requirements

- Python 3.7+
- A Google Cloud project with Sheets API enabled
- A Google Gemini API Key (Generative AI)
- `.eml` format email files

### Python Packages

Install dependencies via pip:

```bash
pip install google-api-python-client google-auth google-generativeai
```

---

## 🔐 Setup

### 1. Google Sheets

- Create a Google Sheet.
- Share edit access with your service account email from `email snapper.json`.
- Note down the **Spreadsheet ID**.

### 2. Gemini API Key

Get your Gemini API key from Google AI Studio:  
👉 [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

---

## 🛠️ Configuration

Edit these variables in `email_AI.py`:

```python
GEMINI_API_KEY = "<your-gemini-api-key>"
SPREADSHEET_ID = "<your-google-sheet-id>"
SHEET_RANGE = "Sheet1!A2"
GOOGLE_CREDENTIALS_FILE = "email snapper.json"
EMAIL_FOLDER = "emails"
```

---

## 📤 Usage

1. Place your `.eml` email files in the `emails/` folder.
2. Run the script:

```bash
python email_AI.py
```

3. The script will:
   - Parse each email
   - Use Gemini to extract shipping info
   - Upload the results to the configured Google Sheet

---

## 📦 Extracted Fields

| Field                  | Description                                |
|------------------------|--------------------------------------------|
| FROM email id          | Sender of the email                        |
| DATE & time received   | Date and time the email was received       |
| Shipping line          | Name of the shipping company               |
| FROM port              | Origin port                                |
| to PORT                | Destination port                           |
| 20 prices              | Price for 20' container (e.g., USD 800)   |
| 40 prices              | Price for 40' container (e.g., USD 1200)  |

---

## 🧠 How It Works

- Reads `.eml` files using Python's `email` module.
- Sends the text to Gemini with a carefully crafted prompt to extract structured data.
- Validates JSON responses and logs any parsing issues.
- Uses Google Sheets API to upload extracted rows.

---

## 🚫 Known Limitations

- Emails with unusual formatting or HTML-only bodies may yield incomplete results.
- Inconsistent pricing formats may confuse the AI.
- Only supports `.eml` files and plain-text extraction.

---

## 🔒 Security Note

Ensure `.json` credentials and API keys are **not committed to version control** (e.g., GitHub). Add to `.gitignore`:

```
email snapper.json
```

---

## 📬 Example `.eml` Structure

Make sure the `.eml` files contain:

- Sender, subject, and body with logistics-related content
- Pricing or port details mentioned explicitly in text

---

## 📈 Output Sample in Sheet

| FROM email id       | DATE & time received | Shipping line | FROM port | to PORT | 20 prices | 40 prices |
|---------------------|----------------------|---------------|-----------|---------|-----------|-----------|
| info@abc.com        | 2025-06-22 10:15 AM  | Maersk        | Haiphong  | Nhava Sheva | USD 850 | USD 1250 |

---

## 🧩 Future Enhancements

- Support for `.msg` and `.pdf` formats
- UI to upload emails manually
- Automated email polling from Gmail

---

## 🧑‍💻 Author

**Bhavya Kanojia**  
Email Snapper | © 2025  
Feel free to reach out for improvements or collaboration.
