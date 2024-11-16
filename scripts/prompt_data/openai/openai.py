import json
from enum import StrEnum
from ..constants import SYSTEM_MESSAGE_CONTENT
from ..types import Language
from typing import TypedDict


class Role(StrEnum):
    System = "system"
    User = "user"
    Assistant = "assistant"


class Message(TypedDict):
    role: Role
    content: str


class LogEntry(TypedDict):
    training_entries: int
    validation_entries: int


Summary = dict[Language, dict[str, dict[str, LogEntry]]]


def get_message(role: Role, content: str) -> Message:
    return {
        "role": role,
        "content": content,
    }


def get_training_prompt(user_prompt: str, parsed_feedback: str) -> str:
    return (
        json.dumps(
            {
                "messages": [
                    get_message(Role.System, SYSTEM_MESSAGE_CONTENT),
                    get_message(Role.User, user_prompt),
                    get_message(Role.Assistant, parsed_feedback),
                ]
            },
            ensure_ascii=False,
        )
        + "\n"
    )
