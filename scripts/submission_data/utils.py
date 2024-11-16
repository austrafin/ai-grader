import re

from .types import Points
from .constants import OverallSolution


def get_points(score_headings: tuple[str, ...], feedback: str) -> str:
    for score_heading in score_headings:
        match = re.search(rf"{score_heading}: (-?\d+)", feedback)

        if match:
            return match.group(1)

    return ""


def get_points_from_feedback(feedback: str) -> Points:
    return {
        "overall_solution": get_points(
            (OverallSolution.FI, OverallSolution.EN), feedback
        ),
        "style": get_points(("OHJELMOINTITYYLI", "PROGRAMMING STYLE"), feedback),
    }
