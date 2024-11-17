import argparse
import json
import os
import shutil

from typing import Optional
from utils import on_rm_error


def delete_directories(project_dir: str, consent_file: str, students_file: str):
    with open(students_file, "r", encoding="utf-8") as file:
        usernames = {
            student["student_id"]: student["username"].split("@")[0]
            for student in json.load(file)
        }

    with open(consent_file, "r") as file:
        consents = {
            usernames[consent["StudentID"]]: {
                "student_id": consent["StudentID"],
                "has_given_consent": consent["field_0"] == "a",
            }
            for consent in json.load(file)
        }

    count = 0

    def delete_directory(student_id: Optional[str] = None):
        dir_path = os.path.join(project_dir, repository)

        if os.path.isdir(dir_path):
            print(f"Deleting directory: {dir_path} Student ID: {student_id}")
            shutil.rmtree(dir_path, onexc=on_rm_error)  # type: ignore

            nonlocal count
            count += 1
        else:
            print(f"Directory does not exist or is not a directory: {dir_path}")

    for repository in os.listdir(project_dir):
        if repository not in consents:
            delete_directory()
            continue

        consent = consents[repository]

        if consent["has_given_consent"]:
            continue

        delete_directory(consent["student_id"])

    print(f"Deleted {count} directories")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("projectdir")
    parser.add_argument("consentfile")
    parser.add_argument("studentsfile")

    args = parser.parse_args()

    delete_directories(args.projectdir, args.consentfile, args.studentsfile)


if __name__ == "__main__":
    main()
