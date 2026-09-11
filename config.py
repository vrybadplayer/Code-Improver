"""Configuration module for Automatic Code Improver."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class PathsConfig:
    prompt_file: str
    iterations_dir: str
    vector_store_dir: str
    source_output_dir: str
    prompts_dir: str

    def __post_init__(self):
        self.prompt_file = os.path.expanduser(self.prompt_file)
        self.iterations_dir = os.path.expanduser(self.iterations_dir)
        self.vector_store_dir = os.path.expanduser(self.vector_store_dir)
        self.source_output_dir = os.path.expanduser(self.source_output_dir)
        self.prompts_dir = os.path.expanduser(self.prompts_dir)


@dataclass
class OllamaConfig:
    base_url: str
    audit_agent_model: str
    coding_agent_model: str
    embeddings_model: str
    audit_agent_timeout: int
    coding_agent_timeout: int
    embeddings_timeout: int


@dataclass
class FlaskConfig:
    host: str
    port: int
    debug: bool


@dataclass
class ChromaDBConfig:
    persist_directory: str
    collection_prefix: str

    def __post_init__(self):
        self.persist_directory = os.path.expanduser(self.persist_directory)


@dataclass
class RAGConfig:
    chunk_size: int
    chunk_overlap: int
    top_k: int


@dataclass
class PipelineConfig:
    max_iterations: int
    default_task_name: str


@dataclass
class LoggingConfig:
    level: str
    format: str


@dataclass
class Config:
    paths: PathsConfig
    ollama: OllamaConfig
    flask: FlaskConfig
    chromadb: ChromaDBConfig
    rag: RAGConfig
    pipeline: PipelineConfig
    logging: LoggingConfig


def load_config(config_path: str = "config.yaml") -> Config:
    """Load and validate configuration from YAML file."""
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)

    paths = PathsConfig(**data["paths"])
    ollama = OllamaConfig(
        base_url=data["ollama"]["base_url"],
        audit_agent_model=data["ollama"]["models"]["audit_agent"],
        coding_agent_model=data["ollama"]["models"]["coding_agent"],
        embeddings_model=data["ollama"]["models"]["embeddings"],
        audit_agent_timeout=data["ollama"]["timeouts"]["audit_agent_seconds"],
        coding_agent_timeout=data["ollama"]["timeouts"]["coding_agent_seconds"],
        embeddings_timeout=data["ollama"]["timeouts"]["embeddings_seconds"],
    )
    flask = FlaskConfig(**data["flask"])
    chromadb = ChromaDBConfig(**data["chromadb"])
    rag = RAGConfig(**data["rag"])
    pipeline = PipelineConfig(**data["pipeline"])
    logging_cfg = LoggingConfig(**data["logging"])

    return Config(
        paths=paths,
        ollama=ollama,
        flask=flask,
        chromadb=chromadb,
        rag=rag,
        pipeline=pipeline,
        logging=logging_cfg,
    )


def get_config(config_path: str = "config.yaml") -> Config:
    """Get configuration instance (cached)."""
    if not hasattr(get_config, "_config"):
        get_config._config = load_config(config_path)
    return get_config._config


def reset_config():
    """Reset cached configuration (useful for testing)."""
    if hasattr(get_config, "_config"):
        del get_config._config