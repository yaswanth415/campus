# CampusFix — Web Version

This version follows the uploaded Campus Maintenance Complaint & Tracking System specification:
- Python
- Flask web GUI
- SQLite
- Pandas
- Matplotlib
- Complaint registration, viewing, search and tracking
- Admin-only status updates
- Admin-only maintenance details
- Reports and charts
- CSV export

## Important

Tkinter is a desktop GUI toolkit. It cannot itself be served as an HTTPS website.
Because you asked for a website and an HTTPS deployment link, this implementation uses Flask for the web GUI while keeping the requested Python + SQLite + Pandas + Matplotlib stack.

## 1. Open in VS Code

Open this folder in VS Code.

## 2. Create/activate a virtual environment

Windows PowerShell:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.venv\Scripts\Activate.ps1
```

## 3. Install packages

```powershell
pip install -r requirements.txt
```

## 4. Run

```powershell
python app.py
```

Open:
http://127.0.0.1:5000

## 5. Admin login

Default development credentials:
- Username: `admin`
- Password: `CampusFix@123`

Change these before deployment using environment variables:
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `SECRET_KEY`

The public can register complaints and view/search tickets.
Only the authenticated admin can:
- update Pending / In Progress / Resolved
- add maintenance details
- export the complaint CSV

## 6. HTTPS deployment

Recommended simple deployment: Render.

Build command:
```text
pip install -r requirements.txt
```

Start command:
```text
gunicorn app:app
```

Set these environment variables in the deployment service:
```text
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_strong_password
SECRET_KEY=your_long_random_secret
```

After deployment, the hosting provider gives you an HTTPS URL such as:
`https://your-campusfix-name.onrender.com`

Do not put a real password in source code or upload `.env` files to GitHub.

## Project structure

```text
CampusFix_Web/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── campus.db          # generated automatically
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── register.html
│   ├── success.html
│   ├── tickets.html
│   ├── ticket_detail.html
│   ├── admin_login.html
│   ├── admin.html
│   ├── maintenance.html
│   └── reports.html
└── static/
    └── css/
        └── style.css
```
