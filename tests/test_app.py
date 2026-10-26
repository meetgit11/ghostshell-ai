"""
Tests for GhostShell Flask application.
Uses mocked Ollama responses — no running Ollama instance required.
"""

import json
from unittest.mock import patch, MagicMock

import pytest

from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# Index route
# ---------------------------------------------------------------------------

class TestIndex:
    def test_index_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"GhostShell" in resp.data
        assert b"text/html" in resp.content_type.encode()


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

class TestHealth:
    @patch("app.check_ollama_running", return_value=True)
    @patch("app.check_model_available", return_value=True)
    def test_health_ready(self, mock_model, mock_ollama, client):
        resp = client.get("/api/health")
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data["status"] == "ready"
        assert data["ollama_running"] is True
        assert data["model_available"] is True

    @patch("app.check_ollama_running", return_value=False)
    def test_health_ollama_down(self, mock_ollama, client):
        resp = client.get("/api/health")
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data["status"] == "unavailable"
        assert data["ollama_running"] is False
        assert data["model_available"] is False

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.check_model_available", return_value=False)
    def test_health_model_missing(self, mock_model, mock_ollama, client):
        resp = client.get("/api/health")
        data = json.loads(resp.data)
        assert data["status"] == "unavailable"
        assert data["ollama_running"] is True
        assert data["model_available"] is False


# ---------------------------------------------------------------------------
# Explain endpoint
# ---------------------------------------------------------------------------

class TestExplain:
    def test_explain_no_json(self, client):
        resp = client.post("/api/explain", data="not json",
                           content_type="text/plain")
        assert resp.status_code == 400

    def test_explain_empty_command(self, client):
        resp = client.post("/api/explain",
                           json={"command": ""},
                           content_type="application/json")
        assert resp.status_code == 400
        assert b"No command" in resp.data

    def test_explain_command_too_long(self, client):
        resp = client.post("/api/explain",
                           json={"command": "x" * 501},
                           content_type="application/json")
        assert resp.status_code == 400
        assert b"too long" in resp.data

    @patch("app.check_ollama_running", return_value=False)
    def test_explain_ollama_not_running(self, mock_ollama, client):
        resp = client.post("/api/explain",
                           json={"command": "ls"},
                           content_type="application/json")
        assert resp.status_code == 503

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.check_model_available", return_value=False)
    def test_explain_model_not_found(self, mock_model, mock_ollama, client):
        resp = client.post("/api/explain",
                           json={"command": "ls"},
                           content_type="application/json")
        assert resp.status_code == 503

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.check_model_available", return_value=True)
    @patch("app.query_ollama", return_value="Beware the listing of files...")
    def test_explain_success(self, mock_query, mock_model, mock_ollama, client):
        resp = client.post("/api/explain",
                           json={"command": "ls -la"},
                           content_type="application/json")
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert "explanation" in data
        assert "Beware" in data["explanation"]

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.check_model_available", return_value=True)
    @patch("app.query_ollama", side_effect=Exception("timeout"))
    def test_explain_ollama_error(self, mock_query, mock_model, mock_ollama, client):
        resp = client.post("/api/explain",
                           json={"command": "ls"},
                           content_type="application/json")
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# Story endpoint
# ---------------------------------------------------------------------------

class TestStory:
    def test_story_no_json(self, client):
        resp = client.post("/api/story", data="not json",
                           content_type="text/plain")
        assert resp.status_code == 400

    def test_story_empty_theme(self, client):
        resp = client.post("/api/story",
                           json={"theme": ""},
                           content_type="application/json")
        assert resp.status_code == 400
        assert b"No theme" in resp.data

    def test_story_theme_too_long(self, client):
        resp = client.post("/api/story",
                           json={"theme": "x" * 301},
                           content_type="application/json")
        assert resp.status_code == 400
        assert b"too long" in resp.data

    @patch("app.check_ollama_running", return_value=True)
    @patch("app.check_model_available", return_value=True)
    @patch("app.query_ollama", return_value="In the depths of the server room...")
    def test_story_success(self, mock_query, mock_model, mock_ollama, client):
        resp = client.post("/api/story",
                           json={"theme": "memory leak"},
                           content_type="application/json")
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert "story" in data
        assert "server room" in data["story"]


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------

class TestHelpers:
    @patch("app.requests.get")
    def test_check_ollama_running_success(self, mock_get, client):
        mock_get.return_value = MagicMock(status_code=200)
        from app import check_ollama_running
        assert check_ollama_running() is True

    @patch("app.requests.get", side_effect=ConnectionError)
    def test_check_ollama_running_connection_error(self, mock_get, client):
        from app import check_ollama_running
        assert check_ollama_running() is False

    @patch("app.requests.get")
    def test_check_model_available_found(self, mock_get, client):
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {
            "models": [{"name": "llama3.2:latest"}]
        }
        mock_get.return_value = mock_resp
        from app import check_model_available
        assert check_model_available() is True

    @patch("app.requests.get")
    def test_check_model_available_not_found(self, mock_get, client):
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {
            "models": [{"name": "mistral:latest"}]
        }
        mock_get.return_value = mock_resp
        from app import check_model_available
        assert check_model_available() is False

    @patch("app.requests.post")
    def test_query_ollama_payload(self, mock_post, client):
        mock_resp = MagicMock(status_code=200)
        mock_resp.json.return_value = {"response": "Spooky result"}
        mock_post.return_value = mock_resp
        from app import query_ollama
        res = query_ollama("Test prompt")
        assert res == "Spooky result"
        called_payload = mock_post.call_args[1]["json"]
        assert called_payload["model"] == "llama3.2"
        assert called_payload["options"]["num_gpu"] == 0
        assert called_payload["options"]["num_ctx"] == 1024
        assert called_payload["options"]["num_predict"] == 140
        assert called_payload["stream"] is False
