from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class PipelineStage(str, Enum):
    IMPORT_TEXT = "import_text"
    SPLIT_CHAPTERS = "split_chapters"
    SUMMARIZE_CHAPTERS = "summarize_chapters"
    EXTRACT_KNOWLEDGE = "extract_knowledge"
    PLAN_PLOT = "plan_plot"
    GENERATE_CONTINUATION = "generate_continuation"
    REVIEW_CONSISTENCY = "review_consistency"
    REVISE_OUTPUT = "revise_output"


class ProjectPaths(BaseModel):
    root: Path = Field(default_factory=lambda: Path.cwd())
    raw_data: Path = Path("data/raw")
    processed_data: Path = Path("data/processed")
    outputs: Path = Path("data/outputs")
    knowledge_base: Path = Path("kb")
    vector_store: Path = Path("vector_store")
    prompts: Path = Path("prompts")
    skills: Path = Path("skills")

    def resolve_from_root(self) -> "ProjectPaths":
        return self.model_copy(
            update={
                "raw_data": self.root / self.raw_data,
                "processed_data": self.root / self.processed_data,
                "outputs": self.root / self.outputs,
                "knowledge_base": self.root / self.knowledge_base,
                "vector_store": self.root / self.vector_store,
                "prompts": self.root / self.prompts,
                "skills": self.root / self.skills,
            }
        )


class AgentStatus(BaseModel):
    project_name: str = "novel-continuation-agent"
    version: str
    stages: list[PipelineStage]
    paths: ProjectPaths
