import argparse
import os
import csv


def get_points(rows: list[list[str]], index: int) -> tuple[str, ...]:
    return tuple(row[index] for row in rows)


def get_combined_scores(
    results_dir: str, results_filename: str
) -> list[tuple[str, ...]]:
    combined_scores: list[tuple[str, ...]] = []
    actual_points = ()

    for i, dir in enumerate(os.listdir(results_dir)):
        results_path = os.path.join(results_dir, dir)

        if not os.path.isdir(results_path):
            continue

        print(f"{i + 1}.\t{dir}")

        with open(os.path.join(results_path, results_filename), "r") as file:
            rows = list(csv.reader(file, delimiter=","))

            combined_scores.append(get_points(rows, 0))

            if not len(actual_points):
                actual_points = get_points(rows, 1)

    combined_scores.append(actual_points)
    return combined_scores


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("results_dir")
    parser.add_argument("output_file")

    args = parser.parse_args()

    with open(
        args.output_file,
        "w",
        newline="",
    ) as file:
        csv.writer(file).writerows(
            get_combined_scores(args.results_dir, "overall_points_comparison.csv")
        )


if __name__ == "__main__":
    main()
