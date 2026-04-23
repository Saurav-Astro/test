# ProXM - AI-Proctored Examination Platform 🛡️

ProXM is a secure, intelligent, and premium online examination platform designed for modern academic and recruitment needs. It features advanced AI-based proctoring, a rich faculty dashboard, and a seamless student assessment experience.

---

## 🚀 Features

### 🛡️ AI Proctoring System
- **Face Detection:** Real-time monitoring using `face-api.js`. Detects multiple faces, eye tracking, and absence.
- **Environment Control:** Camera preview with live status dots (Green=OK, Yellow=Warning).
- **Window Switch Ban:** Automatically logs violations if the student leaves the exam tab.
- **Keyboard Restrictions:** Blocks Ctrl, Alt, F-keys, and PrintScreen to prevent unauthorized access/copying.
- **Enforced Fullscreen:** Ensures the student remains within the exam environment.
- **Violation Auto-Submission:** Automatically submits the exam if the student exceeds the warning threshold.

### 📝 Assessment Engine
- **Multiple Choice Questions (MCQ):** Automated grading and randomization.
- **Integrated Coding Lab:** Built-in code editor (Monaco) with support for Python, JavaScript, Java, and C++.
- **Test Case Runner:** Real-time feedback for students with hidden/public test cases.
- **Per-Question Timer:** Individual countdowns for each question to manage pacing.

### 📊 Management Dashboards
- **Faculty Dashboard:** Full control over exam creation, question building, and live monitoring.
- **AI Proctoring Reports:** Detailed logs of every violation with timestamps for review.
- **Admin Panel:** System-level control over users, status toggles, and password overrides.

---

## 🛠️ Technology Stack
- **Frontend:** React, Vite, Vanilla CSS (Premium Dark Theme), `face-api.js`, Monaco Editor.
- **Backend:** Python (FastAPI), Beanie ODM (MongoDB), JWT Authentication.
- **Database:** MongoDB Atlas.
- **Code Execution:** Piston API Integration.

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.9+ 
- Node.js 16+
- MongoDB Atlas Account

### 2. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Create a `.env` file in the `backend/` directory with the following:
```env
MONGODB_URI=your_mongodb_atlas_uri
DB_NAME=proxm
JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256
FRONTEND_URL=http://localhost:5173
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Database Initialization
Once your IP is whitelisted in Atlas, run the following from the root directory to create the default admin:
```bash
source backend/venv/bin/activate
python3 init_db.py
```

---

## 🏃 Running the Application

### Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```
*API runs at `http://localhost:8000`*

### Start Frontend
```bash
cd frontend
npm run dev
```
*App runs at `http://localhost:5173`*

---

## 🔑 Access Credentials

- **Admin Account:** `admin@proxm.io` / `admin123`
- **Faculty Secret Key:** `PROXM_FACULTY_2026` (Use this on the signup page to create faculty accounts).

---

## 🔧 Important Troubleshooting
- **Database Connection Error:** If you see `SSL handshake failed`, ensure your current IP address is whitelisted in **Atlas → Network Access**.
- **Camera Access:** AI proctoring requires browser camera permissions. Ensure your browser allows camera access on the `/exam` routes.

---

Built with ❤️ by ProXM Team.