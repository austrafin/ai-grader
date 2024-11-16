import argparse
import os
import json
from prompt_data import (
    ENCODING,
    get_formatted_training_data,
    get_total_lines,
    get_training_data,
)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("courses_source_dir")
    parser.add_argument("courses_destination_dir")
    parser.add_argument("training_data_output_file")
    parser.add_argument("validation_data_output_file")
    parser.add_argument("metainfo_output_file")
    parser.add_argument("--course")
    parser.add_argument("--max-entries")
    parser.add_argument("--target-language")
    parser.add_argument("--training-data-percentage")

    args = parser.parse_args()
    training_data = get_training_data(
        courses_source_dir=args.courses_source_dir,
        code_files_dir=args.courses_destination_dir,
        course=args.course,
        max_entries=int(args.max_entries) if args.max_entries else None,
        target_language=args.target_language,
    )
    training_data_percentage = (
        float(args.training_data_percentage) if args.training_data_percentage else 0.8
    )
    training_partition, validation_partition, summary = get_formatted_training_data(
        training_data, training_data_percentage
    )

    for output_file, data_file in (
        (args.training_data_output_file, training_partition),
        (args.validation_data_output_file, validation_partition),
        (args.metainfo_output_file, json.dumps(training_data, ensure_ascii=False)),
    ):
        with open(
            output_file,
            "w",
            encoding=ENCODING,
        ) as file:
            file.write(data_file)

    print(
        f"Total:\nTraining: {get_total_lines(training_partition)}\nValidation: {get_total_lines(validation_partition)}",
        json.dumps(summary, indent=2),
        sep=os.linesep,
    )


if __name__ == "__main__":
    main()
