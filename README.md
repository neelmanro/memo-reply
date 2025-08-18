# Memo Reply

An AI powered coding interview practice app.  
Built with Flask, SQLAlchemy, and OpenAI.  

## What it does

- Lets users sign up, log in, and practice coding problems in a clean web UI  
- Supports company and topic filters so practice feels focused  
- Generates DSA-style questions from a curated bank of 600+ problems  
- Provides an in-browser editor (Monaco) for writing solutions  
- Uses AI to instantly validate the user’s code with clear, minimal feedback  

## Why it’s interesting

Memo Reply makes interview prep feel calm and structured.  
Instead of endless random questions, users pick a company and topic, get exactly two clean examples, write code inline, and receive AI verdicts in seconds.  

## Tech stack

- **Backend**: Flask + SQLAlchemy  
- **Database**: MySQL (configurable via `DATABASE_URL`)  
- **AI**: OpenAI API for formatting questions and checking solutions  
- **Frontend**: HTML, CSS, and Monaco editor for an interactive coding pad  
- **Auth**: User accounts with hashed passwords via Werkzeug  

## Project status

Core features are live:
- Auth system  
- Question generation  
- In-browser code editor  
- AI feedback loop  

Next steps could include timed sessions, progress tracking, and saving solutions.  

---

✨ Memo Reply is built to show how AI can streamline coding interview prep into a smoother, more focused flow.  
