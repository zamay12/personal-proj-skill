from pathlib import Path

from novel_continuation_agent import __version__
from novel_continuation_agent.models import AgentStatus, PipelineStage, ProjectPaths


def build_status(root: Path | None = None) -> AgentStatus:
    project_root = root or Path.cwd()
    paths = ProjectPaths(root=project_root).resolve_from_root()
    return AgentStatus(
        version=__version__,
        stages=list(PipelineStage),
        paths=paths,
    )


def list_pipeline_stage_names() -> list[str]:
    return [stage.value for stage in PipelineStage]
