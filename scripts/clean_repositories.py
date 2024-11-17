"""Removes all but code files from the repositories and unifies the directory
structure

Assumes the following directory structure:
<repositories_path>/
├── <TUNI ID 1>/
│   ├── student/
│   │   ├── <project_round_dir>/
│   │   │   ├── <project_assignment_dir>/
│   │   │   │   ├── *.h
│   │   │   │   ├── *.cpp
│   │   │   │   └── *.ui
│   │   │   ├── ...
│   │   │   └── n/
│   │   │       └── ...
│   │   └── ...
│   └── ...
├── ...
└── <TUNI ID n>/
    └── ...

Usage:
python clean_repositories.py <repositories_path> <project_round_dir> <project_assignment_dir>

Example:
python clean_repositories.py C:/courses/2023_autumn/student_repositories/project_1 04 checkers
"""

import argparse
import os
import shutil

from typing import TypedDict
from utils import on_rm_error


class ToBeDeleted(TypedDict):
    exact: tuple[str, ...]
    prefixes: tuple[str, ...]


SRC_DIR = "src"
STUDENT_DIR = "student"
ALLOWED_EXTENSIONS = (".cpp", ".hh", ".ui")
TO_BE_DELETED: ToBeDeleted = {
    "exact": (
        ".idea",
        ".vscode",
        "arrows",
        "assets",
        "base",
        "binairo_documentation",
        "build",
        "cashier",
        "dicepictures",
        "diceresources",
        "foods",
        "text_files",
        "fruits",
        "gfx",
        "highscores",
        "icons",
        "images",
        "img",
        "kortit",
        "kuvat",
        "libraryuusi",
        "main.dsym",
        "matto",
        "mines",
        "mysteerimatto",
        "numbertiles",
        "ohj2png",
        "pics",
        "pictures",
        "rec",
        "recources",
        "resource",
        "resource_images",
        "recourses",
        "resources",
        "resurssit",
        "res",
        "scores",
        "snek",
        "untitled",
        "yliopisto",
    ),
    "prefixes": (
        ".qtc",
        "build-",
        "card",
        "cmake",
        "debug",
        "https_",
    ),
}


def delete_dir_or_file(path: str):
    if os.path.isdir(path):
        shutil.rmtree(path, onexc=on_rm_error)  # type: ignore
    else:
        os.remove(path)


def safe_delete_directory(dir_name: str, filepath: str) -> bool:
    """Deletes the directory only if its name is not unknown"""
    if dir_name in (TO_BE_DELETED["exact"]) or dir_name.startswith(
        TO_BE_DELETED["prefixes"]
    ):
        delete_dir_or_file(filepath)
        return True
    else:
        # Print the directory path for manual inspection
        print(filepath)
        return False


def delete_directories(
    repositories_path: str, project_round_dir: str, project_assignment_dir: str
):
    for repository_dir in os.listdir(repositories_path):
        repository_path = os.path.join(repositories_path, repository_dir)
        project_student_dir = project_assignment_path = os.path.join(
            repository_path, STUDENT_DIR
        )
        src_path = os.path.join(repository_path, SRC_DIR)
        project_assignment_path = os.path.join(
            project_student_dir, project_round_dir, project_assignment_dir
        )

        if os.path.isdir(src_path) and not os.path.isdir(project_student_dir):
            # Already processed before
            continue

        move_files = True

        for dir in os.listdir(repository_path):
            path = os.path.join(repository_path, dir)

            if dir != STUDENT_DIR:
                delete_dir_or_file(path)
                continue

            for round_dir in os.listdir(path):
                round_path = os.path.join(path, round_dir)

                if round_dir != project_round_dir:
                    delete_dir_or_file(round_path)
                    continue

                for assignment_dir in os.listdir(round_path):
                    assignment_path = os.path.join(round_path, assignment_dir)

                    if assignment_dir != project_assignment_dir:
                        delete_dir_or_file(assignment_path)
                        continue

                    for file in os.listdir(assignment_path):
                        filepath = os.path.join(assignment_path, file)

                        if os.path.isdir(filepath):
                            safe_delete_directory(file.lower(), filepath)
                        elif not file.endswith(ALLOWED_EXTENSIONS):
                            delete_dir_or_file(filepath)

        if move_files:
            os.mkdir(src_path)

            for item in os.listdir(project_assignment_path):
                shutil.move(os.path.join(project_assignment_path, item), src_path)

            delete_dir_or_file(project_student_dir)
        else:
            print("Files not moved due to unresolved directories")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("repositories_path")
    parser.add_argument("project_round_dir")
    parser.add_argument("project_assignment_dir")

    args = parser.parse_args()

    delete_directories(
        args.repositories_path, args.project_round_dir, args.project_assignment_dir
    )


if __name__ == "__main__":
    main()
