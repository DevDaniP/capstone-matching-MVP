# Capstone Matching MVP

Reads survey responses from a Google Sheet ([Form link](https://forms.gle/7FqcxKCf5QBYoocc7)), converts them into structured preferences, runs `main.py` to generate optimal team assignments, and writes the results (including scores) back to the same spreadsheet under a separate tab.

---

## 🧩 Overview

**Workflow:**  
Google Form → “Form Responses 1” tab → `main.py` → “Team Results” tab

- **Input:** A Google Sheet tab containing names, ranked project preferences, and teammate preferences/avoid lists.  
- **Algorithm:** A greedy matching algorithm that forms the most compatible teams based on combined preferences.  
- **Output:** A “Team Results” tab showing each team’s members, assigned project, and compatibility score.

---

## ⚙️ Setup

There are three main parts to set up before running the script: the **Google Form**, the **Google Sheet**, and your **local environment**.

### 1. Google Form
Create a Google Form that collects:
- Participant names  
- Project rankings  
- Teammate preferences  
- Teammate avoid lists  

You can use [this example form](https://forms.gle/7FqcxKCf5QBYoocc7) as a reference.

### 2. Google Sheet
Link your form to a Google Sheet (via **Responses → Link to Sheets**).  
This ensures:
- Each new form response is added automatically.
- Columns follow a consistent format expected by the script.

### 3. Local Environment
This project requires **Python 3.9+**.

Install dependencies:
```bash
pip install -r requirements.txt
```

Then copy `credentials.example.json` → `credentials.json` and fill in your real service account credentials to enable Google Sheets API access.

---

## 🔧 Configuration

Edit the top of `main.py`:
```python
SPREADSHEET_ID = 'YOUR_SHEET_ID_HERE'     # from the sheet URL between /d/ and /edit
INPUT_RANGE    = 'Form Responses 1!A1:AL6' # adjust rows/cols as needed
OUTPUT_RANGE   = "'Team Results'!A1"       # quoted because of the space
```

**Tips:**
- `INPUT_RANGE` should include all columns with responses.  
- The script will create the “Team Results” tab automatically if it doesn’t exist.

---

## ▶️ Usage

Run the program:
```bash
python src/main.py
```

When it finishes:
- Team assignments, project matches, and scores will print to the console.
- The same data will be written automatically to the “Team Results” tab in your linked Google Sheet.

---

## 🧰 File Structure

```
project/
├─ src/
│  ├─ main.py
│  ├─ matching_algorithm.py
├─ tests/
│  ├─ test.py
├─ credentials.example.json
├─ requirements.txt
└─ README.md
```

---

## 🧠 Notes

- Keep your real `credentials.json` **out of version control**. Add this line to `.gitignore`:
  ```
  credentials.json
  ```
- Use `credentials.example.json` as a safe template for collaborators.
- If the script fails to write results, ensure:
  - The spreadsheet is shared with your service account email.
  - The sheet names in `INPUT_RANGE` and `OUTPUT_RANGE` are spelled exactly as in Google Sheets.
