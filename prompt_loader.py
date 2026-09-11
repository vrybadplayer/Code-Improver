"""Prompt loader utility for Automatic Code Improver."""

import os
import logging
from pathlib import Path
from typing import Dict, Any
from config import get_config

logger = logging.getLogger(__name__)


def load_prompt_template(template_name: str) -> str:
    """Load a prompt template from the prompts directory."""
    config = get_config()
    template_path = Path(config.paths.prompts_dir) / template_name

    if not template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")

    content = template_path.read_text(encoding="utf-8")
    logger.debug(f"Loaded prompt template: {template_name}")
    return content


def render_prompt(template_name: str, variables: Dict[str, Any]) -> str:
    """Load and render a prompt template with variables."""
    template = load_prompt_template(template_name)

    # Simple variable substitution using {{variable}} syntax
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        template = template.replace(placeholder, str(value))

    logger.debug(f"Rendered prompt template: {template_name} with variables: {list(variables.keys())}")
    return template


def render_audit_prompt(
    task_name: str,
    iteration_id: int,
    code: str,
    context_chunks: list,
    quality_requirements: str,
    previous_improvements: str = ""
) -> str:
    """Render the Audit Agent prompt with all required variables."""
    context_text = ""
    if context_chunks:
        context_text = "\n\n".join([f"Context chunk {i+1}:\n{chunk['content']}" for i, chunk in enumerate(context_chunks)])
    else:
        context_text = "No previous iteration context available (first iteration)."

    return render_prompt("audit_prompt.md", {
        "task_name": task_name,
        "iteration_id": iteration_id,
        "code": code,
        "context": context_text,
        "quality_requirements": quality_requirements,
        "previous_improvements": previous_improvements
    })


def render_coding_prompt(
    task_name: str,
    iteration_id: int,
    audit_feedback: str,
    improvements: str,
    requirements: str,
    context_chunks: list
) -> str:
    """Render the Coding Agent prompt with all required variables."""
    context_text = ""
    if context_chunks:
        context_text = "\n\n".join([f"Context chunk {i+1}:\n{chunk['content']}" for i, chunk in enumerate(context_chunks)])
    else:
        context_text = "No previous iteration context available."

    return render_prompt("coding_prompt.md", {
        "task_name": task_name,
        "iteration_id": iteration_id,
        "audit_feedback": audit_feedback,
        "improvements": improvements,
        "requirements": requirements,
        "context": context_text
    })