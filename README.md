# CineRate 🎬

CineRate is a premium, lightweight, and modern full-stack Movie Review and Rating web application built with Python (Flask) and a vanilla HTML5/CSS3/JavaScript frontend. It uses a local SQLite database and features a high-fidelity glassmorphic user interface.

## Features
- **Cinematic Dark Theme**: Premium slate and indigo color palette with responsive card grid layouts.
- **Seeded Movie Database**: Automatically starts with a curated catalog of 20 iconic movies.
- **Interactive Ratings & Reviews**: Clickable star selector (1-5 stars) and detailed reviews history list.
- **Real-Time Search & Filtering**: Instant, debounced title search and quick genre-navigation tabs.
- **Community Statistics**: Real-time calculated insights (Total movies, total reviews, highest-rated title, and community average).

---

## Installation & Setup

Ensure you have **Python 3.12+** installed on your system.

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Configure Virtual Environment & Install Dependencies
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```
After executing the server script, navigate to `http://127.0.0.1:5000` in your web browser.

---

## Directory Structure
```text
.
├── app.py                  # Flask server and REST API endpoints
├── database.py             # SQLite helper functions and initial seed data
├── requirements.txt        # Python package dependencies
├── .gitignore              # Files ignored by Git (venv, movies.db, cache)
├── README.md               # Project documentation
└── static/                 # Static frontend assets
    ├── index.html          # HTML structure
    ├── styles.css          # Premium responsive styling
    └── app.js              # Client-side controller
```
