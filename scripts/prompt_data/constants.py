from enum import StrEnum


class Language(StrEnum):
    EN = "en"
    FI = "fi"


ENCODING = "utf-8"
DENOTIONS = {
    key: f"//{value}:"
    for key, value in {
        "file": "FILE",
        "instructions": "INS",
        "feedback": "FDBC",
    }.items()
}
SYSTEM_MESSAGE_CONTENT = (
    f"You are a programming assignment grader tasked with evaluating student "
    f"submissions based on the following criteria: correctness, code quality, "
    f"and adherence to assignment requirements. Ignore extensive use of white "
    f"space, as it could be due to formatting or removed comments during the "
    f"anonymization process. In the prompt: The beginning of the code file is "
    f"denoted by {DENOTIONS["file"]}. Grading instructions are denoted by "
    f"{DENOTIONS["instructions"]}. The feedback base is denoted by "
    f"{DENOTIONS["feedback"]}. In the feedback files '+' denotes positive "
    f"feedback & '-' negative feedback (typically a reason why points were "
    f"deducted). '*' is either negative feedback or a suggestion, but not a "
    f"reason for deducting points. "
)
