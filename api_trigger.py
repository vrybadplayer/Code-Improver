"""Flask API server for Automatic Code Improver - n8n integration endpoints."""

import os
import logging
from flask import Flask, request, jsonify
from pathlib import Path

from config import get_config
from rag import get_rag_client
from iteration_record import (
    get_record_path, load_record, save_record, create_draft_record,
    complete_record, read_record_for_rag, list_iterations
)
from ollama_client import get_ollama_client

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__)
    config = get_config()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.logging.level),
        format=config.logging.format
    )

    rag_client = get_rag_client()
    ollama_client = get_ollama_client()

    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Health check endpoint - verifies Ollama and ChromaDB connectivity."""
        ollama_healthy = ollama_client.check_health()
        chromadb_healthy = False

        try:
            # Try to list collections to verify ChromaDB
            rag_client.client.list_collections()
            chromadb_healthy = True
        except Exception as e:
            logger.warning(f"ChromaDB health check failed: {e}")

        status = "healthy" if ollama_healthy and chromadb_healthy else "degraded"
        return jsonify({
            "status": status,
            "ollama": "connected" if ollama_healthy else "disconnected",
            "chromadb": "connected" if chromadb_healthy else "disconnected",
            "flask": "running"
        }), 200 if status == "healthy" else 503

    @app.route("/api/prompt", methods=["GET"])
    def get_prompt():
        """Read the prompt file from ./data/prompt.md."""
        config = get_config()
        prompt_path = Path(config.paths.prompt_file)

        if not prompt_path.exists():
            logger.warning(f"Prompt file not found: {prompt_path}")
            return jsonify({"error": "Prompt file not found"}), 404

        try:
            content = prompt_path.read_text(encoding="utf-8")
            return jsonify({"prompt": content}), 200
        except Exception as e:
            logger.error(f"Failed to read prompt file: {e}")
            return jsonify({"error": "Failed to read prompt file"}), 500

    @app.route("/api/ingest", methods=["POST"])
    def ingest_record():
        data = request.get_json()
        if not data or "record_path" not in data:
            return jsonify({"error": "Missing record_path in request"}), 400

        record_path = data["record_path"]
        task_name = data.get("task_name", config.pipeline.default_task_name)

        try:
            success = rag_client.ingest_record(task_name, record_path)
            if not success:
                # Explicit failure — return a non-200 status
                return jsonify({
                    "success": False,
                    "task_name": task_name,
                    "error": "Ingest returned False — check Flask logs for the reason"
                }), 422
            return jsonify({"success": True, "task_name": task_name}), 200
        except FileNotFoundError:
            return jsonify({"error": f"File not found: {record_path}"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/context", methods=["GET"])
    def get_context():
        """Retrieve RAG context for a task and query."""
        task_name = request.args.get("task_name", config.pipeline.default_task_name)
        query = request.args.get("query", "")
        top_k = request.args.get("top_k", type=int)

        if not query:
            return jsonify({"error": "Missing query parameter"}), 400

        try:
            chunks = rag_client.retrieve_context(task_name, query, top_k)
            return jsonify({"chunks": chunks, "task_name": task_name}), 200
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/iteration/<task_name>/<int:iteration_id>", methods=["GET"])
    def get_iteration(task_name: str, iteration_id: int):
        """Read an iteration record."""
        try:
            record = load_record(task_name, iteration_id)
            if record is None:
                return jsonify({"error": "Iteration record not found"}), 404

            return jsonify({
                "task": record.task,
                "iteration_id": record.iteration_id,
                "loc": record.loc,
                "desc": record.desc,
                "improvements": record.improvements
            }), 200
        except Exception as e:
            logger.error(f"Failed to read iteration record: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/iteration/<task_name>/<int:iteration_id>", methods=["POST"])
    def save_iteration(task_name: str, iteration_id: int):
        """Save an iteration record (draft or complete)."""
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing request body"}), 400

        try:
            # Create or update record
            if "loc" in data or "desc" in data:
                # Complete record from Coding Agent
                record = load_record(task_name, iteration_id)
                if record is None:
                    record = create_draft_record(task_name, iteration_id)
                record = complete_record(record, data.get("loc", ""), data.get("desc", ""))
                if "improvements" in data:
                    record.improvements = data["improvements"]
            else:
                # Draft record from Audit Agent
                record = create_draft_record(
                    task_name,
                    iteration_id,
                    data.get("improvements", "")
                )

            save_record(record)
            return jsonify({
                "success": True,
                "task": record.task,
                "iteration_id": record.iteration_id,
                "path": str(get_record_path(task_name, iteration_id))
            }), 200

        except Exception as e:
            logger.error(f"Failed to save iteration record: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/ensure_dir", methods=["POST"])
    def ensure_dir():
        data = request.get_json()
        dir_path = data.get("path")
        if not dir_path:
            return jsonify({"error": "Missing path"}), 400
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return jsonify({"success": True, "path": dir_path}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app


def main():
    """Run the Flask server."""
    config = get_config()
    app = create_app()

    logger.info(f"Starting Flask server on {config.flask.host}:{config.flask.port}")
    app.run(
        host=config.flask.host,
        port=config.flask.port,
        debug=config.flask.debug
    )


if __name__ == "__main__":
    main()