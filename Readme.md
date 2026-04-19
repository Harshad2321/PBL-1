# Nurture — AI Parenting Simulation Game

> A locally-hosted AI game where you play as a parent navigating real family challenges, powered by Mistral 7B running on Ollama. No cloud. No API costs. Runs entirely on your machine.

---

## 🎥 Demo Video

https://github.com/Harshad2321/PBL-1/raw/main/DEMO%20VIDEO.mp4

> 📥 [Click here to download and watch the demo](https://github.com/Harshad2321/PBL-1/raw/main/DEMO%20VIDEO.mp4)

---

## 🔗 LinkedIn Post

[Read the full story behind this project](https://www.linkedin.com/posts/harshad-agrawal-486964322_nurture-aigame-edtech-activity-7451515374677868544-_Cgw)

---

## 🧠 What is Nurture?

Nurture is an AI-powered parenting simulation game built in GameMaker Studio 2.  
You play as a parent (father or mother) making daily decisions that affect your relationship with an AI co-parent — powered by Mistral 7B running locally via Ollama.

The AI tracks 4 emotional states in real time:

- **Trust** — does your partner believe in you?
- **Resentment** — are tensions building?
- **Closeness** — how emotionally connected are you?
- **Stress** — how overwhelmed is your AI partner?

Every choice you make shifts these values. The AI reacts, remembers, and responds accordingly — making each playthrough feel different.

---

## 🏗️ Architecture

```
GameMaker Studio 2 (GML)
        │
        │  HTTP requests (JSON)
        ▼
FastAPI Server (Python) — api_server.py
        │
        ▼
NurtureGame (Python backend in PBL-1/nurture/)
        │
        ▼
Ollama — mistral:7b-instruct-v0.3-q4_K_M (runs locally)
```

---

## 🚀 How to Run

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- GameMaker Studio 2 (to run the game frontend)

### Step 1 — Pull the AI model
```bash
ollama pull mistral:7b-instruct-v0.3-q4_K_M
```

### Step 2 — Install Python dependencies
```bash
cd PBL-1
pip install -r requirements.txt
```

### Step 3 — Start the backend server
```bash
cd PBL-1
uvicorn api_server:app --host 127.0.0.1 --port 8000
```

### Step 4 — Run the game
Open `PBL.yyp` in GameMaker Studio 2 and press **Run**.

---

## 📁 Project Structure

```
NUTURE/
├── PBL-1/                      ← Python backend
│   └── nurture/                ← Core game logic
│       ├── main.py             ← NurtureGame class
│       ├── story_engine.py
│       ├── core/
│       └── utils/
│           └── llm_interface.py  ← Ollama connection
├── objects/                    ← GameMaker objects
├── scripts/                    ← GameMaker GML scripts
├── sprites/                    ← Game assets
├── rooms/                      ← Game rooms/scenes
└── PBL.yyp                     ← GameMaker project file
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Game Engine | GameMaker Studio 2 (GML) |
| Backend | Python, FastAPI, Uvicorn |
| AI Model | Mistral 7B (mistral:7b-instruct-v0.3-q4_K_M) |
| AI Runtime | Ollama (local) |
| Communication | REST API (HTTP/JSON) |

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/start` | Start a new game session |
| POST | `/choose` | Submit a choice (1, 2, or 3) |
| POST | `/message` | Send a free-text message to the AI |
| GET | `/status` | Get current emotional state values |
| POST | `/end_conversation` | End the day and get summary |

---

## 👥 Team

- **Harshad Agrawal** — [LinkedIn](https://www.linkedin.com/in/harshad-agrawal-486964322)
- **Parth Kosthi** — Co-developer

**Mentor:** Prof. Sumanto Dutta  
**Institution:** Symbiosis Institute of Technology, Pune  
**Semester:** 4th Semester — Project Based Learning (PBL 1)  
**Department:** AI & Machine Learning  

---

## 🏆 Presented At

**Industry Conclave 2026** — AI & Machine Learning Department, SIT Pune  
Presented to industry experts **Shekhar Anand Jha** and **Amol Mahajan**

---

## 🔮 What's Next

The industry experts told us something that stuck:  
*"This isn't just a game. This is an EdTech platform waiting to happen."*

We're building Nurture into a platform where parents, counselors, and students can simulate real emotional conversations, develop empathy, and learn how relationships actually work. **Powered by AI. Grounded in psychology.**

---

## 📄 License

This project was developed as part of academic coursework at SIT Pune.  
Feel free to explore, fork, and build on it.