"""Anonymizes C++ files by saving them to a separate path without the comments

Assumes the following directory structure:
<root>/
├── <course 1>/
│   └── student_repositories/
│       ├── <assignment 1>/
│       │   ├── <TUNI ID 1>/
│       │   │   └── src/
│       │   │       ├── *.h
│       │   │       ├── *.cpp
│       │   │       ├── *.ui
│       │   │       └── ...
│       │   └── <TUNI ID n>/
│       │       └── ...
│       └── <assignment n>/
│           └── ...
└── <course n>/
    └── ...

Usage:
python clean_repositories.py <root>
"""

import argparse
import os
import re
import shutil


COMMENT_PATTERN = re.compile(
    r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
    re.DOTALL | re.MULTILINE,
)


def on_rm_error(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def remove_comments(text):
    def replacer(match):
        s = match.group(0)

        if s.startswith("/"):
            return ""  # note: a space and not an empty string
        else:
            return s

    return re.sub(COMMENT_PATTERN, replacer, text)


def remove_comments_from_file(file_path, destination):
    with open(file_path, "r", encoding="ISO-8859-1") as file:
        source_code = file.read()

    with open(destination, "w", encoding="ISO-8859-1") as file:
        file.write(remove_comments(source_code))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("root")

    args = parser.parse_args()

    for course_dir in os.listdir(args.root):
        course_path = os.path.join(args.root, course_dir)

        if os.path.isdir(course_path):
            projects_path = os.path.join(course_path, "student_repositories")

            for project_dir in os.listdir(projects_path):
                project_path = os.path.join(projects_path, project_dir)

                for student_dir in os.listdir(project_path):
                    student_path = os.path.join(project_path, student_dir)
                    src_path = os.path.join(student_path, "src")
                    destination = os.path.join(student_path, "anonymized")

                    if os.path.isdir(destination):
                        shutil.rmtree(destination, onexc=on_rm_error)

                    os.mkdir(destination)

                    for file in os.listdir(src_path):
                        if not file.endswith((".cpp", ".hh")):
                            continue

                        remove_comments_from_file(
                            os.path.join(src_path, file),
                            os.path.join(destination, file),
                        )
