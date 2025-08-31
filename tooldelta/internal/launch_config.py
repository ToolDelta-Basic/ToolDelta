from dataclasses import dataclass


@dataclass
class LaunchConfig:
    restart_delay: int = -1
