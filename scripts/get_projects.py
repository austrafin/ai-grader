import argparse
from typing import Optional, TypedDict
import requests
import json


class Namespace(TypedDict):
    id: int
    name: str
    path: str
    kind: str
    full_path: str
    parent_id: Optional[int]
    avatar_url: Optional[str]
    web_url: str


class SimplifiedProject(TypedDict):
    description: Optional[str]
    name_with_namespace: str


class Project(SimplifiedProject):
    id: int
    description: Optional[str]
    name: str
    name_with_namespace: str
    path: str
    path_with_namespace: str
    created_at: str
    default_branch: str
    tag_list: tuple[str]
    topics: tuple[str]
    ssh_url_to_repo: str
    http_url_to_repo: str
    web_url: str
    readme_url: str
    forks_count: int
    avatar_url: Optional[str]
    star_count: int
    last_activity_at: str
    namespace: Namespace


Response = list[Project]


def get_projects(api_token: str) -> Response:
    projects: Response = []
    next_link = None

    while True:
        if next_link:
            response = requests.get(next_link)
        else:
            response = requests.get(
                "https://course-gitlab.tuni.fi/api/v4/projects",
                params={
                    "order_by": "name",
                    "sort": "asc",
                    "per_page": 100,
                    "private_token": api_token,
                    "simple": True,
                },
            )

        if response.status_code != 200:
            response.raise_for_status()

        print(
            f"{response.headers.get('X-Page', 1)}/{response.headers.get('X-Total-Pages', 1)}"
        )
        projects.extend(response.json())
        next_link = None

        for link in response.headers.get("Link", "").split(","):
            if 'rel="next"' in link:
                next_link = link.split(";")[0].strip(" <>")
                break

        if not next_link:
            break

    return projects


def write_json_file(output_path: str, data: Response | list[SimplifiedProject]):
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("api_token")
    parser.add_argument("output_path")
    parser.add_argument("simplified_output_path")

    args = parser.parse_args()
    projects = get_projects(args.api_token)

    write_json_file(args.output_path, projects)
    write_json_file(
        args.simplified_output_path,
        [
            {
                "name_with_namespace": project["name_with_namespace"],
                "description": project["description"],
            }
            for project in projects
        ],
    )


if __name__ == "__main__":
    main()
