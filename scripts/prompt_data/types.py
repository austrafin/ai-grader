from typing import TypedDict
from .constants import Language


class TrainingDataEntry(TypedDict):
    source_code_path: str
    user_prompt: str
    feedback: str


TrainingData = dict[Language, dict[str, dict[str, list[TrainingDataEntry]]]]


class LogEntry(TypedDict):
    training_entries: int
    validation_entries: int


Summary = dict[Language, dict[str, dict[str, LogEntry]]]
