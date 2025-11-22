# 🚀 AI Job Market Analyzer

**A Full-Stack BI & Career Intelligence Platform for the Israeli Tech Market.**

**The website link:**
(https://job-analyzer-one.vercel.app) *Note* The initial loading time may be delayed due to optimization for 
cost-efficiency on cloud services.

## 📖 About The Project

Finding a job in tech is data-driven. This project is an end-to-end system that scrapes live job data, analyzes market trends, and uses Generative AI (Google Gemini) to provide personalized CV analysis and "Smart Gap" detection for job seekers.

---

## 🛠️ Tech Stack & Architecture

This project demonstrates a production-grade microservices architecture deployed on the cloud.

| Component | Technology | Key Highlights |
|-----------|------------|----------------|
| **Frontend** | React.js | Built with **Mantine UI** & **Recharts** for interactive data visualization. Uses custom hooks for API management. |
| **Backend** | Python, FastAPI | Async API handling high-concurrency requests. Implements **CORSMiddleware** for secure cross-origin resource sharing. |
| **Database** | PostgreSQL | Managed cloud DB (Neon). Uses **Raw SQL** (via `psycopg2`) for optimized complex queries and aggregation. |
| **ETL Pipeline** | Python | Custom scraper using **ThreadPoolExecutor** for parallel processing. Handles HTML parsing and Regex data cleaning. |
| **AI Core** | Google Gemini | Utilizes **Pydantic** models to enforce strict JSON schemas on LLM outputs for structured analysis. |
| **DevOps** | Docker, CI/CD | Backend deployed on **Render**, Frontend on **Vercel**. Automated deployment pipeline via Git. |

---

## ✨ Key Features

* **📊 Real-Time Market Dashboard:** Visualizes the most demanded skills, experience levels, and job distribution in the Israeli High-Tech sector.
* **🧠 AI CV Analysis:** Upload a CV text to receive a structured breakdown of your profile, inferred seniority level, and detected skills.
* **📉 Smart Gap Analysis:** The system compares your profile against *live* market data to identify specific skill gaps preventing you from landing your target role.
* **🤖 Automated ETL:** A background scheduler (`APScheduler`) runs periodically to scrape, clean, and update the database with fresh job listings without freezing the main server.

---

## ⚙️ How It Works (Under the Hood)

1.  **Data Collection:** The scraper runs on a separate thread, fetching roughly 500+ jobs in parallel to minimize I/O blocking.
2.  **Data Processing:** Raw HTML is parsed, and skills are extracted using a hybrid approach (Regex keyword engine + AI inference).
3.  **Storage:** Data is normalized and stored in a PostgreSQL database using `INSERT ... ON CONFLICT` logic to handle duplicates.
4.  **Analysis:** When a user queries the API, complex SQL queries calculate the "Match Percentage" between the user's skills and the current active job listings.

---

## 🚀 Local Installation

To run this project locally on your machine:

### Prerequisites
* Python 3.11+
* Node.js & npm
* PostgreSQL (Local or Cloud URL)
* Google Gemini API Key

### 1. Backend Setup
# Clone the repo
`git clone [https://github.com/snoopki/Job-analyzer.git](https://github.com/snoopki/Job-analyzer.git)`
`cd Job-analyzer`

# Create virtual environment
`python -m venv .venv`
`source .venv/bin/activate  # On Windows use: .venv\Scripts\activate`

# Install dependencies
`pip install -r requirements.txt`

# Create .env file
`echo "DATABASE_URL=your_postgres_url" > .env`
`echo "GOOGLE_API_KEY=your_gemini_key" >> .env`

# Run Server
`python main.py`

2. Frontend Setup

# Open new terminal in project root
`cd frontend`
# Install dependencies
`npm install`
# Run React App
`npm start`
