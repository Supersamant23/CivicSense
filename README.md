# 🏛️ Civic Sense

Civic Sense is a full-stack web application designed to help voters understand political manifestos. It uses AI to analyze complex policy documents, simplifies them, and generates a personalized quiz to help users find which manifesto aligns with their views.

This project was built for the OpenAI Hackathon.

🚀 Project Architecture

This project follows a modern full-stack architecture:

Backend: A Python-based API server built with Flask. It handles AI analysis, data storage (JSON), and quiz logic.

Frontend: A modern, reactive web interface built with React and Vite.

🏃‍♂️ How to Run the Application

To run the app, you will need to start two separate servers: one for the backend API and one for the frontend website.

You will need two terminals open.

1. Backend Setup (/backend)

The backend server is responsible for all logic, data, and AI processing.

Navigate to the Backend:

cd backend


Create and Activate a Virtual Environment:

# Create the environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Activate it (macOS/Linux)
source venv/bin/activate


Install Dependencies:

pip install -r requirements.txt


Set Up Environment Variables:
You must provide your OpenAI API key.

Rename the .env.example file to .env (or create a new .env file).

Add your API key:

OPENAI_API_KEY=sk-YourActualKeyHere


🚨 One-Time Data Generation (Do This First!) 🚨

Before you can run the app, you must use the AI to analyze your source documents.

Add Your Documents:
Place your manifesto PDF files (e.g., cong.pdf) inside the /backend/inputs/ directory.

Run the Analysis Script:
This script reads the PDFs, calls the OpenAI API, and creates manifestos.json.

python scripts/1_run_analysis.py


Generate the Quiz:
This script reads the new manifestos.json and creates the qq.json quiz file.

python scripts/2_generate_quiz.py


▶️ Run the Backend Server

After the data is generated, you can start the API server.

python app.py


The backend server will now be running on http://127.0.0.1:5000.

2. Frontend Setup (/frontend)

The frontend is the React website that the user interacts with.

Navigate to the Frontend:
(In a new terminal)

cd frontend


Install Dependencies:

npm install


Run the Frontend Dev Server:

npm run dev


The frontend server will now be running on http://localhost:5173 (or a similar port).

✅ You're All Set!

Open your web browser and go to http://localhost:5173. You should see the full Civic Sense application running, pulling its quiz questions directly from your backend.