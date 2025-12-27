from typing import List

import pydantic


class FileInfo(pydantic.BaseModel):
    filename: str
    description: str


class FileResult(pydantic.BaseModel):
    filename: str
    content: str


class FileList(pydantic.BaseModel):
    files: List[FileInfo]


class SpecCheckResult(pydantic.BaseModel):
    valid: bool
    """
    True if the specification matches the requirements. False otherwise.
    """
    reason: str
    """
    If the specification isn't matching the requirements, here's in contained,
    why it isn't matching.
    """


