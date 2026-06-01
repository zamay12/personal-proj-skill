from pathlib import Path

from novel_continuation_agent import __version__
from novel_continuation_agent.agent import build_status, list_pipeline_stage_names


def test_version_is_defined() -> None:
    assert __version__ == "0.1.0"


def test_pipeline_stages_include_core_workflow() -> None:
    stages = list_pipeline_stage_names()

    assert stages[0] == "import_text"
    assert stages[-1] == "revise_output"
    assert "generate_continuation" in stages
    assert len(stages) == 8


def test_build_status_resolves_project_paths(tmp_path: Path) -> None:
    status = build_status(tmp_path)

    assert status.project_name == "novel-continuation-agent"
    assert status.paths.outputs == tmp_path / "data/outputs"
    assert status.paths.knowledge_base == tmp_path / "kb"
    assert status.paths.prompts == tmp_path / "prompts"
