import argparse
import json
import sys
from pathlib import Path

from src.task_assigner import TaskAssignmentModel


def parse_args():
    parser = argparse.ArgumentParser(
        description="Назначение задач проекта на участников команды по эмбеддингам."
    )
    parser.add_argument("--project-id", required=True, help="ID проекта, например P001")
    parser.add_argument(
        "--format",
        choices=["json", "pretty"],
        default="pretty",
        help="Формат вывода результата",
    )
    return parser.parse_args()


def print_pretty(result):
    print(f"\nПроект: {result['project_title']} ({result['project_id']})")
    print(f"Домен: {result['project_domain']}")
    print(
        f"Покрытие команды: {result['team_coverage']['assigned_members']}/"
        f"{result['team_coverage']['total_members']}"
    )
    print(f"Всего задач: {len(result['assignments'])}\n")

    for index, assignment in enumerate(result["assignments"], start=1):
        alternatives = ", ".join(
            f"{item['name']} ({item['role']})={item['score']}"
            for item in assignment["top_alternatives"]
        )
        print(f"{index}. {assignment['task_title']} [{assignment['task_id']}]")
        print(
            f"   priority={assignment['priority']} | difficulty={assignment['difficulty']} | "
            f"hours={assignment['estimated_hours']}"
        )
        for assignee in assignment["assigned_to"]:
            print(
                f"   -> {assignee['name']} ({assignee['role']}, id={assignee['student_id']}, "
                f"type={assignee['responsibility']})"
            )
            print(f"      Почему: {assignee['why']}")
        print(f"   Альтернативы: {alternatives}")
        print()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    root = Path(__file__).resolve().parent
    model = TaskAssignmentModel(
        projects_path=root / "data" / "projects.json",
        team_path=root / "data" / "team.json",
    )
    result = model.assign_project(args.project_id)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_pretty(result)


if __name__ == "__main__":
    main()
