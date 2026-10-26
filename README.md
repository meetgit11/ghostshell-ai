<p align="center">
  <img src="https://em-content.zobj.net/source/apple/391/ghost_1f47b.png" width="80" alt="Ghost emoji">
</p>

<h1 align="center">GhostShell</h1>
<p align="center"><strong>A Haunted AI Terminal</strong></p>

<p align="center">
  A spooky developer assistant powered by local open-weight AI.<br>
  Built for the <a href="https://hacktoberfest.com">Hacktoberfest</a> Open-Source AI Challenge — <em>Ghost in the Machine</em>.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-green?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/flask-3.x-green?style=flat-square&logo=flask&logoColor=white" alt="Flask 3">
  <img src="https://img.shields.io/badge/ollama-local_AI-purple?style=flat-square" alt="Ollama">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="MIT License">
</p>

---

## 🎃 Overview

**GhostShell** is a Halloween-themed developer tool that brings spooky AI-powered features to your terminal. Ask it to explain any terminal command in a haunted, atmospheric style — or conjure ghost stories about programming, debugging, and technology.

Everything runs **100% locally** using [Ollama](https://ollama.com). No data leaves your machine. No cloud APIs. No accounts required.

---

## ✨ Features

### 💀 Haunted Command Explainer
Enter any terminal command and receive a technically accurate explanation delivered in a spooky, developer-themed style. Commands are **explained, never executed**.

### 📖 Ghost Story Generator
Provide a theme and GhostShell conjures a short horror story about programming — featuring real concepts like segfaults, race conditions, memory leaks, and haunted server rooms.

### 🖥️ Atmospheric Terminal UI
- Dark terminal aesthetic with green phosphor text
- CRT scanline overlay
- Floating ghost particles
- Typewriter text animation
- Responsive design (desktop & mobile)
- Real-time status indicator for Ollama connectivity

### 🔒 Privacy First
- All AI inference runs locally via Ollama
- No user prompts are stored
- No data is sent to third-party services
- No API keys or credentials exposed in frontend code

---

## 🏗️ Architecture

```
ghostshell-ai/
├── app.py              # Flask backend — routes, Ollama integration
├── config.py           # Configuration (env var driven)
├── requirements.txt    # Python dependencies
├── tests/
│   ├── test_app.py     # API endpoint & helper tests
│   └── test_config.py  # Configuration tests
├── templates/
│   └── index.html      # Single-page terminal UI
├── static/
│   ├── css/
│   │   └── style.css   # Dark theme, animations, CRT effects
│   └── js/
│       └── app.js      # Frontend logic, API calls, typewriter
├── LICENSE             # MIT
└── README.md           # You are here
```

**Data flow:**

```
Browser ──POST──▶ Flask API ──HTTP──▶ Ollama (localhost:11434)
                                          │
                                     Local LLM
                                          │
Browser ◀──JSON── Flask API ◀──JSON── Ollama
```

---

## 📋 Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| [Python](https://python.org) | 3.10+ | Backend runtime |
| [Ollama](https://ollama.com) | Latest | Local AI inference |
| An Ollama model | e.g. `llama3.2` | Language generation |

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/meetgit11/ghostshell-ai.git
cd ghostshell-ai
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install and configure Ollama

#### Install Ollama

- **Windows:** Download from [ollama.com/download](https://ollama.com/download)
- **macOS:** `brew install ollama` or download from [ollama.com](https://ollama.com)
- **Linux:** `curl -fsSL https://ollama.com/install.sh | sh`

#### Pull a model

```bash
ollama pull llama3.2
```

> **Note:** `llama3.2` (~2 GB) is the default. You can use any Ollama-compatible model — see [Configuration](#-configuration) below.

#### Start Ollama (if not already running)

```bash
ollama serve
```

On most systems Ollama starts automatically after installation. You can verify with:

```bash
ollama list
```

### 4. Run GhostShell

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

You should see the haunted terminal interface with a green "Connected" status indicator.

---

## ⚙️ Configuration

All settings are configurable via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `llama3.2` | Ollama model to use |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API URL |
| `OLLAMA_NUM_GPU` | `0` | GPU layers offloaded (0: CPU mode for broad compatibility, -1: auto) |
| `OLLAMA_NUM_CTX` | `1024` | Context window size (optimized for CPU memory bandwidth) |
| `OLLAMA_MAX_TOKENS`| `140` | Maximum tokens per response (keeps CPU inference fast) |
| `OLLAMA_TIMEOUT` | `180` | Ollama HTTP request timeout in seconds |
| `FLASK_HOST` | `127.0.0.1` | Flask bind address |
| `FLASK_PORT` | `5000` | Flask port |
| `FLASK_DEBUG` | `false` | Debug mode (never `true` in production) |

**Example — use a different model:**

```bash
# Windows PowerShell
$env:OLLAMA_MODEL = "mistral"
python app.py

# Linux / macOS
OLLAMA_MODEL=mistral python app.py
```

---

## 📸 Screenshots

> Screenshots will be added after first successful deployment.

<!-- 
![GhostShell UI](screenshots/main-ui.png)
![Command Explainer](screenshots/explainer.png)
![Ghost Story](screenshots/story.png)
-->

---

## 🧪 Running Tests

Tests use mocked Ollama responses — **no running Ollama instance required**.

```bash
pytest tests/ -v
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serve the terminal UI |
| `GET` | `/api/health` | Check Ollama & model status |
| `POST` | `/api/explain` | Explain a command (JSON: `{"command": "..."}`) |
| `POST` | `/api/story` | Generate a ghost story (JSON: `{"theme": "..."}`) |

### Example API call

```bash
curl -X POST http://127.0.0.1:5000/api/explain \
  -H "Content-Type: application/json" \
  -d '{"command": "rm -rf /"}'
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Ollama is not running" | Run `ollama serve` or install from [ollama.com](https://ollama.com) |
| "Model not found" | Run `ollama pull llama3.2` (or your configured model) |
| Slow responses | Larger models are slower. Try `llama3.2` (3B) for faster replies |
| Port already in use | Set `FLASK_PORT=8080` (or another free port) |
| Connection refused | Ensure Ollama is running on the expected host/port |

---

## ⚠️ Limitations

- Responses depend entirely on the local Ollama model — quality varies by model size and capability.
- First request after model load may be slower (model warm-up).
- The application does not execute commands — it only explains them.
- No conversation history or multi-turn chat.
- Requires a machine capable of running Ollama and an LLM (typically 4+ GB RAM).

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  👻 <em>The terminal remembers what you've deleted...</em> 👻
</p>
