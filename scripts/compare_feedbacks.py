import argparse
from datetime import datetime
import json
import os
from time import sleep
from typing import Literal, TypedDict
from openai import OpenAI
from prompt_data import (
    TrainingData,
    ENCODING,
    SYSTEM_MESSAGE_CONTENT,
    get_training_data,
)
from prompt_data.openai import Role
from submission_data import Points, get_points_from_feedback

REQUEST_TIMEOUT_SECONDS = 60


class Feedback(TypedDict):
    message: str
    points: Points


class AIGradingEntry(TypedDict):
    source_code_path: str
    user_prompt: str
    ai_feedback: Feedback
    actual_feedback: Feedback


AIGradingEntries = list[AIGradingEntry]


def send_prompt(api_key: str, model: str, user_prompt: str) -> str:
    try:
        return str(
            OpenAI(api_key=api_key)
            .chat.completions.create(
                model=model,
                messages=[
                    {"role": Role.System, "content": SYSTEM_MESSAGE_CONTENT},
                    {"role": Role.User, "content": user_prompt},
                ],
            )
            .choices[0]
            .message.content
        )
    except Exception as e:
        print(e, f"Trying again in {REQUEST_TIMEOUT_SECONDS} seconds")
        sleep(REQUEST_TIMEOUT_SECONDS)

        return send_prompt(api_key, model, user_prompt)


def get_ai_gradings(
    api_key: str, model: str, training_data: TrainingData
) -> AIGradingEntries:
    ai_gradings: AIGradingEntries = []

    for courses in training_data.values():
        for projects in courses.values():
            for submission_data in projects.values():
                for entry in submission_data:
                    ai_grading = send_prompt(api_key, model, entry["user_prompt"])
                    ai_gradings.append(
                        {
                            "source_code_path": entry["source_code_path"],
                            "user_prompt": entry["user_prompt"],
                            "ai_feedback": {
                                "message": ai_grading,
                                "points": get_points_from_feedback(ai_grading),
                            },
                            "actual_feedback": {
                                "message": entry["feedback"],
                                "points": get_points_from_feedback(entry["feedback"]),
                            },
                        }
                    )

    return ai_gradings


def get_csv_line(
    ai_points: Points,
    actual_points: Points,
    key: Literal["overall_solution"] | Literal["style"],
) -> str:
    return f"{ai_points[key]},{actual_points[key]}\n"


def get_points_comparison(ai_gradings: AIGradingEntries) -> tuple[str, str]:
    overall_points = ""
    style_points = ""

    for grading in ai_gradings:
        ai_points = grading["ai_feedback"]["points"]
        actual_points = grading["actual_feedback"]["points"]
        overall_points += get_csv_line(ai_points, actual_points, "overall_solution")
        style_points += get_csv_line(ai_points, actual_points, "style")

    return overall_points, style_points


def save_results(
    output_dir: str,
    ai_gradings: AIGradingEntries,
    overall_points_comparison: str,
    style_points_comparison: str,
):
    pathname = f"{output_dir}/{datetime.now().strftime("%Y%m%d_%H%M%S")}"

    os.mkdir(pathname)

    for output_file, data_file in (
        ("results.json", json.dumps(ai_gradings, ensure_ascii=False)),
        ("overall_points_comparison.csv", overall_points_comparison),
        ("style_points_comparison.csv", style_points_comparison),
    ):
        with open(
            f"{pathname}/{output_file}",
            "w",
            encoding=ENCODING,
        ) as file:
            file.write(data_file)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("api_key")
    parser.add_argument("model")
    parser.add_argument("courses_source_dir")
    parser.add_argument("courses_destination_dir")
    parser.add_argument("results_output_dir")
    parser.add_argument("--course")
    parser.add_argument("--iterations", type=int, default=1)

    args = parser.parse_args()

    for _ in range(args.iterations):
        ai_gradings = get_ai_gradings(
            args.api_key,
            args.model,
            get_training_data(
                courses_source_dir=args.courses_source_dir,
                code_files_dir=args.courses_destination_dir,
                course=args.course,
            ),
        )
        overall_points, style_points = get_points_comparison(ai_gradings)

        save_results(args.results_output_dir, ai_gradings, overall_points, style_points)


if __name__ == "__main__":
    main()
