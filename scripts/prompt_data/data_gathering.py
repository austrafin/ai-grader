import os

from submission_data.constants import OverallSolution
from .openai import get_training_prompt
from .constants import DENOTIONS, ENCODING
from .types import Language, TrainingData, TrainingDataEntry, Summary
from typing import Optional


def get_parsed_feedback(feedback_form: str) -> str:
    """
    Skips unwanted parts of the feedback form and returns a the feedback in
    a condensed form
    """
    feedback = ""
    ignore_lines = True

    for line in feedback_form.splitlines():
        if ignore_lines:
            if line.startswith(
                (
                    "Saat 0 pistettä",
                    "You have received zero",
                    OverallSolution.EN,
                    OverallSolution.FI,
                )
            ):
                ignore_lines = False
            else:
                continue

        if line.startswith(("VERSIONHALLINNAN KÄYTTÖ", "VERSION CONTROL")):
            break

        if not line or line.startswith(
            (
                "\n",
                "===================================",
            )
        ):
            continue

        feedback += line + "\n"

    return feedback


def get_parsed_instructions(feedback_form_path: str) -> str:
    """
    Skips unwanted parts of the grading instruction file and returns the
    instructions a condensed form
    """
    instructions = ""

    with open(feedback_form_path, "r", encoding=ENCODING) as file:
        for line in file:
            if line.startswith("VERSIONHALLIN"):
                break

            if not line or line.startswith(
                (
                    "\n",
                    "----------------",
                )
            ):
                continue

            instructions += line

    return instructions


def get_feedback_from_file(course_assistant_path: str, student_id: str) -> str:
    with open(
        os.path.join(course_assistant_path, student_id, "palaute.txt"),
        "r",
        encoding=ENCODING,
    ) as file:
        return file.read()


def get_language(feedback_raw: str) -> Language | None:
    if "Assessed submission:" in feedback_raw:
        return Language.EN
    elif "Tarkastettu palautus:" in feedback_raw:
        return Language.FI


def get_assessment_texts(
    grading_instructions_path: str, project: str, language: Language
) -> tuple[str, str]:
    feedback_template = ""
    grading_instructions = ""

    for file in os.listdir(grading_instructions_path):
        file_path = os.path.join(grading_instructions_path, file)

        if file.startswith(f"{project}_palautepohja_{language}"):
            with open(
                file_path,
                "r",
                encoding=ENCODING,
            ) as feedback_template_file:
                feedback_template = f"{DENOTIONS["feedback"]}\n{get_parsed_feedback(feedback_template_file.read())}"
        elif file.startswith(f"{project}_pisteytysohje"):
            grading_instructions = (
                f"{DENOTIONS["instructions"]}\n{get_parsed_instructions(file_path)}"
            )

        if feedback_template and grading_instructions:
            break

    return feedback_template, grading_instructions


def get_user_prompt(
    feedback_base: str, grading_instructions: str, anonymized_path: str
) -> str:
    user_prompt = f"{feedback_base}\n{grading_instructions}\n"

    for source_file in os.listdir(anonymized_path):
        with open(
            os.path.join(anonymized_path, source_file),
            "r",
            encoding=ENCODING,
        ) as file:
            user_prompt += f"{DENOTIONS["file"]}{source_file}\n{file.read()}\n"

    return user_prompt


def get_training_data(
    courses_source_dir: str,
    code_files_dir: str,
    course: Optional[str] = None,
    max_entries: Optional[int] = None,
    target_language: Optional[Language] = None,
) -> TrainingData:
    """Creates a training data object which can be used to fine-tune an OpenAI
    model. Assumes the following directory structures:

    <courses_source_dir>/
    ├── <course 1>/
    │   └── arvioinnit/
    │       ├── pohjat/
    │       │   ├── projekti1_palautepohja_en.txt
    │       │   ├── projekti1_palautepohja_fi.txt
    │       │   ├── projekti1_pisteytysohje.txt
    │       │   ├── ...
    │       │   ├── projekti<n>_palautepohja_en.txt
    │       │   ├── projekti<n>_palautepohja_fi.txt
    │       │   └── projekti<n>_pisteytysohje.txt
    │       ├── projekti1/
    │       │   ├── <grader name>/
    │       │   │   ├── <TUNI ID>/
    │       │   │   │   └── palaute.txt
    │       │   │   ├── ...
    │       │   │   └── <TUNI ID>/
    │       │   │       └── ...
    │       │   ├── ...
    │       │   └── <grader name>/
    │       │       └── ...
    │       ├── ...
    │       └── projekti<n>/
    │           └── ...
    └── <course n>/
        └── ...

    <code_files_dir>/
    ├── <course>/
    │   └── student_repositories/
    │       ├── projekti1/
    │       │   ├── <TUNI ID>/
    │       │   │   └── anonymized/
    │       │   │       ├── *.h
    │       │   │       ├── *.cpp
    │       │   │       └── *.ui
    │       │   ├── ...
    │       │   └── <TUNI ID>/
    │       │       └── ...
    │       ├── ...
    │       └── projekti<n>/
    │           └── ...
    ├── ...
    └── <course>/
        └── ...
    """

    training_data: TrainingData = {
        Language.FI: {},
        Language.EN: {},
    }
    count = 0

    for course_dir in os.listdir(courses_source_dir):
        course_path = os.path.join(courses_source_dir, course_dir)

        if not os.path.isdir(course_path) or (course and course_dir != course):
            continue

        gradings_path = os.path.join(course_path, "arvioinnit")

        if not os.path.isdir(gradings_path):
            continue

        grading_instructions_path = os.path.join(gradings_path, "pohjat")

        training_data[Language.FI][course_dir] = {}
        training_data[Language.EN][course_dir] = {}

        for project in os.listdir(gradings_path):
            if not project.startswith("projekti"):
                continue

            project_path = os.path.join(gradings_path, project)

            for course_assistant in os.listdir(project_path):
                course_assistant_path = os.path.join(project_path, course_assistant)

                if not os.path.isdir(course_assistant_path):
                    continue

                for student_id in os.listdir(course_assistant_path):
                    if max_entries and count >= max_entries:
                        return training_data

                    destination_student_path = os.path.join(
                        code_files_dir,
                        course_dir,
                        "student_repositories",
                        project,
                        student_id,
                    )

                    if not os.path.isdir(destination_student_path):
                        continue

                    error = f"{course_dir}/{project}/{course_assistant}/{student_id}"
                    feedback_raw = get_feedback_from_file(
                        course_assistant_path, student_id
                    )
                    language = get_language(feedback_raw)

                    if not language:
                        raise Exception(f"Could not determine the language of {error}")
                    elif target_language and language != target_language:
                        continue

                    feedback_template, grading_instructions = get_assessment_texts(
                        grading_instructions_path, project, language
                    )

                    if not feedback_template:
                        raise Exception(f"Missing feedback_base of {error}")
                    elif not grading_instructions:
                        raise Exception(f"Missing grading_instructions of {error}")

                    parsed_feedback = get_parsed_feedback(feedback_raw)
                    anonymized_path = os.path.join(
                        destination_student_path, "anonymized"
                    )
                    user_prompt = get_user_prompt(
                        feedback_template,
                        grading_instructions,
                        anonymized_path,
                    )
                    count += 1
                    data: TrainingDataEntry = {
                        "source_code_path": anonymized_path,
                        "user_prompt": user_prompt,
                        "feedback": parsed_feedback,
                    }

                    if project in training_data[language][course_dir]:
                        training_data[language][course_dir][project].append(data)
                    else:
                        training_data[language][course_dir][project] = [data]

    return training_data


def get_total_lines(lines: str) -> int:
    # A newline character is added at the end of each data partition
    return len(lines.split("\n")) - 1


def get_formatted_training_data(
    training_data: TrainingData, training_data_percentage: float
) -> tuple[str, str, Summary]:
    training_partition = ""
    validation_partition = ""
    summary: Summary = {}

    for language, data_by_language in training_data.items():
        summary[language] = {}

        for course, data_by_course in data_by_language.items():
            summary[language][course] = {}

            for project, data in data_by_course.items():
                training_partition_lang, validation_partition_lang = (
                    get_training_data_strings(data, training_data_percentage)
                )
                training_partition += training_partition_lang
                validation_partition += validation_partition_lang
                summary[language][course][project] = {
                    "training_entries": get_total_lines(training_partition_lang),
                    "validation_entries": get_total_lines(validation_partition_lang),
                }

    return training_partition, validation_partition, summary


def get_training_data_strings(
    training_data: list[TrainingDataEntry], training_data_percentage: float
) -> tuple[str, str]:
    training_partition = ""
    validation_partition = ""
    training_partition_size = int(len(training_data) * training_data_percentage)

    for count, data in enumerate(training_data):
        prompt = get_training_prompt(data["user_prompt"], data["feedback"])

        if count < training_partition_size:
            training_partition += prompt
        else:
            validation_partition += prompt

    return training_partition, validation_partition
