# 🏆 TC Corp – Employee Recognition & Reward System

A full-stack web application built with Flask and MySQL that allows employees to recognize and reward each other, while providing managers with the tools to approve recognitions, review feedback, and maintain a fair and motivating workplace culture.

## 🚀 Features

### 🔐 Authentication
- Secure login and registration
- Manager registration option with role-based access
- Session handling with access protection

### 👥 Employee Functionality
- Submit peer recognitions with badge selection and personalized messages
- Receive feedback from others
- Track achievements and recognition history
- Clean, modern, responsive UI

### 👨‍💼 Manager Functionality
- Approve or deny recognitions before they are sent to Slack
- View pending recognitions with decision buttons
- View anonymous employee feedback reports
- Clear recognitions weekly with one click

### 📊 Reporting & Insights
- Leaderboard showing top recognized employees
- Full recognition reports with timestamps, badges, and messages
- Filtered views for manager use only

### 📡 Slack Integration
- Recognition and reward messages are sent directly to Slack via webhooks
- New member registration and feedback also alert designated Slack channels

---

## 🛠️ Technologies Used

- **Frontend:** HTML, CSS (custom and responsive), Jinja2 templating
- **Backend:** Python (Flask)
- **Database:** MySQL (via SQLAlchemy ORM)
- **Authentication:** Secure login & password hashing using Werkzeug
- **APIs:** Slack Webhooks Integration
- **Hosting:** Currently hosted locally (can deploy via Heroku or Render)

---

## 🧑‍💻 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/
