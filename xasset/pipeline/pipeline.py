from dataclasses import dataclass, field


@dataclass
class PipelineConfig:
    scene_type: str
    stages: list[str]
    stage_configs: dict[str, dict] = field(default_factory=dict)
