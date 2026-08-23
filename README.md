# DomainAI ✦ AI-Powered Domain Name Generator

DomainAI is a sleek, modern Flask web application that helps researchers and founders generate creative website names using Google's Gemini AI and instantly checks their domain name availability.

## Features

- **AI Name Generation**: Uses Gemini (`gemini-2.5-flash`) via the modern `google-genai` SDK to invent creative, brandable names tailored to your project description.
- **Domain Availability Checker**: Combines `python-whois` queries with dynamic `rdap.org` API fallbacks for robust and reliable domain availability checks (Available, Registered, or Could Not Verify).
- **User Authentication**: Secure user registration and login forms with hashed passwords (`werkzeug.security`).
- **Research Dashboard**: Summary statistics of your runs, most active domain extensions, and quick actions to launch new searches.
- **Query History Log**: Automatically logs all search configurations and results for authenticated users with expandable timeline cards and quick clipboard copying.
- **Modern Responsive Design**: A beautifully polished UI matching premium design aesthetics with interactive character counters and a modal loading screen.

## Project Structure

```text
projet stage/
│
├── app.py                # Flask main configuration & db initialization
├── generator.py          # Gemini AI API wrapper & prompt parser
├── checker.py            # WHOIS and RDAP domain checker functions
├── models.py             # User and SearchHistory database models
├── routes.py             # Route handlers for web UI and authentication
│
├── .env                  # Environment keys (e.g. Gemini API Key)
├── .gitignore            # Excludes env files and databases from Git
├── requirements.txt      # List of Python library dependencies
│
├── templates/            # HTML templates extending base layout
│   ├── base.html         # Global layout (navbar, footer, notifications)
│   ├── index.html        # Domain generator request page
│   ├── result.html       # Domain availability checklist page
│   ├── login.html        # Authentication screens (Login/Register tabs)
│   ├── dashboard.html    # Logged-in user stats and quick history list
│   └── history.html      # Detail view of past generations
│
└── static/               # Style sheets, JS files and media
    ├── css/
    │   └── style.css     # Global CSS stylesheets
    └── js/
        └── script.js     # Client-side scripts
```

## Setup Instructions

### 1. Prerequisites
Make sure you have **Python 3.8+** installed on your system.

### 2. Configure Virtual Environment
If you haven't already, navigate to the project directory and create a Python virtual environment:
```powershell
python -m venv venv
```

Activate the environment:
*   **Windows (PowerShell)**:
    ```powershell
    .\venv\Scripts\Activate.ps1
    ```
*   **macOS / Linux**:
    ```bash
    source venv/bin/activate
    ```

### 3. Install Dependencies
Install all required libraries using the requirements file:
```powershell
pip install -r requirements.txt
```

### 4. Setup Gemini API Key
Create a file named `.env` in the root of the project directory and insert your Gemini API Key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Launch the Application
Start the Flask development server:
```powershell
python app.py
```

Open your browser and navigate to: `http://127.0.0.1:5000`

---

## Technical Details

- **Database**: Automatic SQLite initialization inside an `instance/` folder. Re-creating tables dynamically on startup if not present.
- **Security**: Raw password hashing protection on the server level using SHA256 hashes.
- **Domain Verification**: Direct socket checks for rapid lookup and fallback to HTTPS APIs for maximum extension compatibility (`.com`, `.net`, `.org`, `.ma`, `.io`, `.ai`).
