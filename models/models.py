import re
from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path


@dataclass
class PostInfo:
    url: str
    title: str
    page: int = 1
    index: int = 0

    @property
    def filename(self) -> str:
        filename = f"{self.title}_480p.mp4"
        return filename.replace('/', '_').replace('\\', '_').replace(':', '_')
    
    
