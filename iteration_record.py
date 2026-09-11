"""Iteration record management for Automatic Code Improver."""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

from config import get_config

logger = logging.getLogger(__name__)


@dataclass
class IterationRecord:
    """Represents an iteration record with all required fields."""
    task: str
    iteration_id: int
    loc: str = ""
    desc: str = ""
    improvements: str = ""

    def to_markdown(self) -> str:
        """Convert record to markdown format."""
        lines = [
            f"TASK: {self.task}",
            f"ITERATION_ID: {self.iteration_id}",
            f"LOC:",
            self.loc if self.loc else "",
            f"DESC:",
            self.desc if self.desc else "",
            f"IMPROVEMENTS:",
            self.improvements if self.improvements else "",
        ]
        return "\n".join(lines)

    @classmethod
    def from_markdown(cls, content: str) -> "IterationRecord":
        """Parse record from markdown format."""
        lines = content.strip().split("\n")
        record = cls(task="", iteration_id=0)
        current_field = None
        field_content = []

        for line in lines:
            if line.startswith("TASK:"):
                if current_field and field_content:
                    setattr(record, current_field.lower(), "\n".join(field_content).strip())
                current_field = "loc" if "LOC" in record.__dict__ else None
                record.task = line[5:].strip()
                field_content = []
            elif line.startswith("ITERATION_ID:"):
                if current_field and field_content:
                    setattr(record, current_field.lower(), "\n".join(field_content).strip())
                record.iteration_id = int(line[13:].strip())
                field_content = []
            elif line.startswith("LOC:"):
                if current_field and field_content:
                    setattr(record, current_field.lower(), "\n".join(field_content).strip())
                current_field = "loc"
                field_content = []
            elif line.startswith("DESC:"):
                if current_field and field_content:
                    setattr(record, current_field.lower(), "\n".join(field_content).strip())
                current_field = "desc"
                field_content = []
            elif line.startswith("IMPROVEMENTS:"):
                if current_field and field_content:
                    setattr(record, current_field.lower(), "\n".join(field_content).strip())
                current_field = "improvements"
                field_content = []
            else:
                if current_field:
                    field_content.append(line)

        # Handle last field
        if current_field and field_content:
            setattr(record, current_field.lower(), "\n".join(field_content).strip())

        return record

    def is_draft(self) -> bool:
        """Check if this is a draft record (empty LOC and DESC)."""
        return not self.loc.strip() and not self.desc.strip()


def get_record_path(task_name: str, iteration_id: int) -> Path:
    """Get the file path for an iteration record."""
    config = get_config()
    iterations_dir = Path(config.paths.iterations_dir)
    task_dir = iterations_dir / task_name
    task_dir.mkdir(parents=True, exist_ok=True)
    return task_dir / f"Iteration_{iteration_id}.md"


def create_draft_record(task_name: str, iteration_id: int, improvements: str = "") -> IterationRecord:
    """Create a draft iteration record (from Audit Agent)."""
    record = IterationRecord(
        task=task_name,
        iteration_id=iteration_id,
        improvements=improvements
    )
    return record


def complete_record(record: IterationRecord, loc: str, desc: str) -> IterationRecord:
    """Complete a draft record with code and description (from Coding Agent)."""
    record.loc = loc
    record.desc = desc
    return record


def save_record(record: IterationRecord) -> Path:
    """Save iteration record to file."""
    record_path = get_record_path(record.task, record.iteration_id)
    content = record.to_markdown()
    record_path.write_text(content, encoding="utf-8")
    logger.info(f"Saved iteration record to {record_path}")
    return record_path


def load_record(task_name: str, iteration_id: int) -> Optional[IterationRecord]:
    """Load iteration record from file."""
    record_path = get_record_path(task_name, iteration_id)
    if not record_path.exists():
        logger.warning(f"Record not found: {record_path}")
        return None
    content = record_path.read_text(encoding="utf-8")
    return IterationRecord.from_markdown(content)


def read_record_for_rag(task_name: str, iteration_id: int) -> str:
    """Read record content for RAG ingestion (full text)."""
    record = load_record(task_name, iteration_id)
    if record is None:
        return ""
    return record.to_markdown()


def list_iterations(task_name: str) -> list:
    """List all iteration IDs for a task."""
    config = get_config()
    task_dir = Path(config.paths.iterations_dir) / task_name
    if not task_dir.exists():
        return []
    iterations = []
    for file_path in task_dir.glob("Iteration_*.md"):
        try:
            iteration_id = int(file_path.stem.split("_")[1])
            iterations.append(iteration_id)
        except (IndexError, ValueError):
            continue
    return sorted(iterations)