# Talentryx AI Resume Builder

Talentryx is a comprehensive, AI-powered resume building application designed to help users create ATS-friendly, professional resumes with ease. By leveraging advanced machine learning algorithms and NLP, Talentryx offers intelligent resume parsing, job recommendation, and AI-driven content generation, coupled with a seamless rich-text editing experience.

## Key Features

- **AI Copilot:** Intelligent content generation, resume parsing, and personalized job recommendations.
- **Rich Text Editor:** Built with Quill.js, allowing selective formatting (bold, italic, lists, etc.) while maintaining a professional layout.
- **ATS-Friendly Export:** Generate perfectly formatted PDFs (via `pdfkit`/`reportlab`) that preserve styling and pass Applicant Tracking Systems (ATS).
- **Resume Analysis & Multi-Career Paths:** Analyzes existing resumes to match with target job descriptions and supports multiple career profiles.
- **Admin Dashboard:** Secure, session-based admin authentication to manage users and view application analytics.
- **Feedback System:** Collects user feedback and sends automated email notifications to administrators using Flask-Mail.
- **Interview Preparation:** Provides tailored interview questions based on the user's profile and resume.

## Tech Stack

- **Backend:** Python, Flask, Flask-Mail, Werkzeug
- **Database:** MySQL (via `mysql-connector-python`)
- **Frontend:** HTML, CSS, JavaScript, Quill.js
- **AI & NLP:** OpenAI API, Scikit-learn, NLTK, Pandas, Numpy
- **Document Processing:** PDFKit, ReportLab, pdfminer.six, python-docx

## Prerequisites

- **Python:** Version 3.8 or higher.
- **MySQL:** A running instance of MySQL server.
- **wkhtmltopdf:** Required by `pdfkit` for generating PDFs. Make sure it is installed and added to your system's PATH.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd Talentryx-ai-resume-builder
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup:**
   - Create a MySQL database (e.g., `resume_builder`).
   - Run the database setup script (if applicable) or rely on the application's initialization:
     ```bash
     python setup_db.py
     ```

## Configuration

Create a `.env` file in the root directory and configure the following environment variables:

```env
# Flask Settings
SECRET_KEY=your_secret_key

# Database Settings
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=resume_builder

# Email Configuration (for Admin Notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=your_email@gmail.com

# AI API Keys
OPENAI_API_KEY=your_openai_api_key
```

## Running the Application

1. **Start the Flask server:**
   ```bash
   python run.py
   ```
   *(Or using Flask CLI: `flask run`)*

2. **Access the application:**
   Open your web browser and navigate to `http://localhost:5000`.

## Project Structure

```
Talentryx/
│
├── app/                    # Application source code
│   ├── database/           # Database connection and queries
│   ├── models/             # Data models
│   ├── routes/             # Blueprint routes (auth, resume, admin, etc.)
│   ├── services/           # Business logic and AI services
│   ├── static/             # CSS, JS, and Images
│   ├── templates/          # HTML templates
│   └── utils/              # Helper functions
│
├── uploads/                # User uploaded files
├── config.py               # Application configuration classes
├── run.py                  # Entry point for the application
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables
```
