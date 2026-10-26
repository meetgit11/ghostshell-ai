"""
GhostShell — A Haunted AI Terminal
Flask backend that connects to Ollama for local AI inference.

No user data is stored. No external AI services are contacted.
"""

import requests
from flask import Flask, render_template, request, jsonify

import config

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

EXPLAIN_PROMPT = """You are GhostShell, a haunted terminal spirit dwelling inside the server. Explain this terminal command in a spooky developer style.

Rules:
- Explain what the command does, its common flags, and any dangers. DO NOT execute it.
- Use brief eerie metaphors (cursed processes, phantom files, spectral signals).
- Keep explanations accurate, helpful, and concise (under 80-100 words).
- End with one brief ghostly warning or tip.

Command to explain:
{command}"""

STORY_PROMPT = """You are GhostShell, a spectral storyteller in the terminal.
Write a punchy micro-horror story (under 100-120 words) about programming, debugging, or technology.

Rules:
- Incorporate the user's theme into a tale of digital dread.
- Mention real developer concepts (segfaults, race conditions, memory leaks, uncommitted changes).
- Build quick tension and end with a chilling final punchline.

Theme: {theme}"""


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def check_ollama_running():
    """Check if the Ollama service is reachable."""
    try:
        resp = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=5)
        return resp.status_code == 200
    except requests.ConnectionError:
        return False
    except requests.Timeout:
        return False
    except Exception:
        return False


def check_model_available():
    """Check if the configured model is available in Ollama."""
    try:
        resp = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=5)
        if resp.status_code != 200:
            return False
        models = resp.json().get("models", [])
        model_names = [m.get("name", "") for m in models]
        # Match with or without :latest tag
        target = config.OLLAMA_MODEL
        return any(
            name == target or name == f"{target}:latest" or name.startswith(f"{target}:")
            for name in model_names
        )
    except Exception:
        return False


def query_ollama(prompt, max_tokens=None):
    """Send a prompt to Ollama and return the response text."""
    options = {
        "num_ctx": config.OLLAMA_NUM_CTX,
        "num_predict": max_tokens or config.OLLAMA_MAX_TOKENS,
        "temperature": 0.7,
    }
    if config.OLLAMA_NUM_GPU is not None and config.OLLAMA_NUM_GPU >= 0:
        options["num_gpu"] = config.OLLAMA_NUM_GPU

    payload = {
        "model": config.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": options,
    }
    resp = requests.post(
        f"{config.OLLAMA_HOST}/api/generate",
        json=payload,
        timeout=config.OLLAMA_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json().get("response", "").strip()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Serve the haunted terminal interface."""
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    """Return the status of Ollama and the configured model."""
    ollama_running = check_ollama_running()
    model_available = check_model_available() if ollama_running else False

    status = "ready" if (ollama_running and model_available) else "unavailable"

    return jsonify({
        "status": status,
        "ollama_running": ollama_running,
        "model_available": model_available,
        "model_name": config.OLLAMA_MODEL,
        "ollama_host": config.OLLAMA_HOST,
    })


@app.route("/api/explain", methods=["POST"])
def explain_command():
    """Explain a terminal command in spooky style without executing it."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    command = data.get("command", "").strip()
    if not command:
        return jsonify({"error": "No command provided."}), 400
    if len(command) > config.MAX_COMMAND_LENGTH:
        return jsonify({
            "error": f"Command too long. Maximum {config.MAX_COMMAND_LENGTH} characters."
        }), 400

    # Check Ollama availability
    if not check_ollama_running():
        return jsonify({
            "error": "Ollama is not running. Start it with: ollama serve"
        }), 503
    if not check_model_available():
        return jsonify({
            "error": f"Model '{config.OLLAMA_MODEL}' not found. Pull it with: ollama pull {config.OLLAMA_MODEL}"
        }), 503

    try:
        prompt = EXPLAIN_PROMPT.format(command=command)
        explanation = query_ollama(prompt)
        return jsonify({"explanation": explanation})
    except requests.Timeout:
        return jsonify({"error": "The spirits took too long to respond. Try again."}), 504
    except requests.ConnectionError:
        return jsonify({"error": "Lost connection to the spirit realm (Ollama)."}), 503
    except Exception as e:
        return jsonify({"error": f"A dark error occurred: {str(e)}"}), 500


@app.route("/api/story", methods=["POST"])
def generate_story():
    """Generate a ghost story about programming."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    theme = data.get("theme", "").strip()
    if not theme:
        return jsonify({"error": "No theme provided."}), 400
    if len(theme) > config.MAX_THEME_LENGTH:
        return jsonify({
            "error": f"Theme too long. Maximum {config.MAX_THEME_LENGTH} characters."
        }), 400

    if not check_ollama_running():
        return jsonify({
            "error": "Ollama is not running. Start it with: ollama serve"
        }), 503
    if not check_model_available():
        return jsonify({
            "error": f"Model '{config.OLLAMA_MODEL}' not found. Pull it with: ollama pull {config.OLLAMA_MODEL}"
        }), 503

    try:
        prompt = STORY_PROMPT.format(theme=theme)
        story = query_ollama(prompt)
        return jsonify({"story": story})
    except requests.Timeout:
        return jsonify({"error": "The spirits took too long to respond. Try again."}), 504
    except requests.ConnectionError:
        return jsonify({"error": "Lost connection to the spirit realm (Ollama)."}), 503
    except Exception as e:
        return jsonify({"error": f"A dark error occurred: {str(e)}"}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n[GhostShell] Awakening...")
    print(f"   Model : {config.OLLAMA_MODEL}")
    print(f"   Ollama: {config.OLLAMA_HOST}")
    print(f"   Server: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print()
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
    )
