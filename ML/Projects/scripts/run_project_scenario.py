from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from student_recsys.data_generation import load_settings
from student_recsys.features import build_user_embedding, parse_embedding, parse_weight_map, split_pipe

REACTIONS = {
    "open": "opened project details",
    "like": "liked the project",
    "share": "shared the project",
    "long_view": "spent a long time on project",
    "skip_fast": "skipped quickly",
    "disengage": "negative reaction",
}

REACTION_ALIASES = {
    "o": "open",
    "l": "like",
    "s": "share",
    "v": "long_view",
    "k": "skip_fast",
    "d": "disengage",
}


class ProjectScenarioRunner:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.settings = load_settings(root)
        self.data_dir = root / "data" / "projects"
        self.user_profiles_path = self.data_dir / "user_profiles.csv"
        self.project_catalog_path = self.data_dir / "project_catalog.csv"
        self.reactions_path = self.data_dir / "user_project_reactions.csv"

        self.user_profiles = pd.read_csv(self.user_profiles_path)
        self.project_catalog = pd.read_csv(self.project_catalog_path)
        self.reactions = pd.read_csv(self.reactions_path)
        self.session_seen: set[str] = set()

    def run(self, student_id: str, max_projects: int) -> None:
        if student_id not in set(self.user_profiles["user_id"]):
            available = ", ".join(self.user_profiles["user_id"].head(10).tolist())
            raise ValueError(f"Unknown student_id `{student_id}`. Example ids: {available}")

        print(f"Interactive project scenario for {student_id}")
        print("The script picks the best project, waits for your reaction, updates weights, and finds the next one.\n")

        for step in range(1, max_projects + 1):
            project = self.recommend_best_project(student_id)
            if project is None:
                print("No more suitable unseen projects for this session.")
                break

            before_snapshot = self.get_profile_snapshot(student_id)
            print(self.render_profile(before_snapshot, "CURRENT PROFILE"))
            print(self.render_project(project, step))

            reaction = self.read_reaction()
            if reaction == "q":
                print("Scenario finished.")
                break

            self.apply_reaction(student_id, project, reaction)
            self.session_seen.add(str(project["project_id"]))
            after_snapshot = self.get_profile_snapshot(student_id)
            print(f"Saved reaction `{reaction}` for `{project['project_title']}`.")
            print(self.render_profile(after_snapshot, "UPDATED PROFILE"))
            print()

    def recommend_best_project(self, student_id: str) -> dict[str, object] | None:
        user = self._get_user_row(student_id)
        history = self.reactions[self.reactions["user_id"] == student_id].copy()
        cards_for_embedding = self.project_catalog.rename(
            columns={"project_id": "card_id", "required_skills": "skills_required"}
        )
        user_embedding = build_user_embedding(user, history.rename(columns={"project_id": "card_id"}), cards_for_embedding)
        interest_weights = parse_weight_map(user["interest_weights"])
        skill_weights = parse_weight_map(user["skill_weights"])
        seen_projects = set(history["project_id"].tolist()) | self.session_seen

        scored_rows: list[dict[str, object]] = []
        for _, project in self.project_catalog.iterrows():
            project_id = str(project["project_id"])
            if project_id in seen_projects:
                continue

            topics = set(split_pipe(project["topics"]))
            required = set(split_pipe(project["required_skills"]))
            gained = set(split_pipe(project["skills_gained"]))
            role = set(split_pipe(project["role_skills"]))

            topic_match = sum(interest_weights.get(tag, 0.0) for tag in topics)
            required_skill_match = sum(skill_weights.get(tag, 0.0) for tag in required)
            gained_skill_match = sum(skill_weights.get(tag, 0.0) for tag in gained)
            role_skill_match = sum(skill_weights.get(tag, 0.0) for tag in role)
            readiness_score = 0.7 * required_skill_match + 0.3 * gained_skill_match

            project_embedding = np.array(parse_embedding(project["embedding_vector"]), dtype=float)
            embedding_similarity = self._cosine_similarity(user_embedding, project_embedding)
            commitment_fit = self._commitment_fit(str(user["experience_level"]), str(project["expected_commitment"]))
            maturity_fit = self._maturity_fit(str(user["experience_level"]), str(project["project_maturity"]))
            language_fit = 1.0 if user["preferred_language"] == project["language"] else 0.0
            region_fit = 1.0 if user["region"] == project["location"] else 0.0
            format_fit = 1.0 if project["format"] in split_pipe(user["preferred_formats"]) else 0.0

            final_score = (
                1.0 * topic_match
                + 1.35 * required_skill_match
                + 0.55 * gained_skill_match
                + 0.8 * role_skill_match
                + 1.1 * readiness_score
                + 1.2 * embedding_similarity
                + 0.5 * commitment_fit
                + 0.45 * maturity_fit
                + 0.2 * language_fit
                + 0.15 * region_fit
                + 0.15 * format_fit
            )

            payload = project.to_dict()
            payload.update(
                {
                    "topic_match_score": round(topic_match, 4),
                    "required_skill_match_score": round(required_skill_match, 4),
                    "gained_skill_match_score": round(gained_skill_match, 4),
                    "role_skill_match_score": round(role_skill_match, 4),
                    "readiness_score": round(readiness_score, 4),
                    "embedding_similarity": round(embedding_similarity, 4),
                    "commitment_fit": round(commitment_fit, 4),
                    "maturity_fit": round(maturity_fit, 4),
                    "final_score": round(final_score, 4),
                }
            )
            scored_rows.append(payload)

        if not scored_rows:
            return None
        scored = pd.DataFrame(scored_rows).sort_values("final_score", ascending=False)
        return scored.iloc[0].to_dict()

    def apply_reaction(self, student_id: str, project: dict[str, object], reaction: str) -> None:
        user_index = self.user_profiles.index[self.user_profiles["user_id"] == student_id][0]
        user = self.user_profiles.loc[user_index].copy()
        interest_weights = parse_weight_map(user["interest_weights"])
        skill_weights = parse_weight_map(user["skill_weights"])
        personalization = self.settings["personalization"]
        base_delta = float(personalization["reaction_weight_updates"].get(reaction, 0.0))
        min_weight = float(personalization["min_profile_weight"])
        max_weight = float(personalization["max_profile_weight"])

        for topic in split_pipe(project["topics"]):
            start = interest_weights.get(topic, float(personalization["cold_start_interest_weight"]))
            interest_weights[topic] = round(float(np.clip(start + base_delta * 0.85, min_weight, max_weight)), 4)

        for skill in split_pipe(project["required_skills"]):
            start = skill_weights.get(skill, float(personalization["cold_start_skill_weight"]))
            skill_weights[skill] = round(float(np.clip(start + base_delta * 1.25, min_weight, max_weight)), 4)

        for skill in split_pipe(project["role_skills"]):
            start = skill_weights.get(skill, float(personalization["cold_start_skill_weight"]))
            skill_weights[skill] = round(float(np.clip(start + base_delta * 1.0, min_weight, max_weight)), 4)

        for skill in split_pipe(project["skills_gained"]):
            start = skill_weights.get(skill, float(personalization["cold_start_skill_weight"]))
            skill_weights[skill] = round(float(np.clip(start + base_delta * 0.7, min_weight, max_weight)), 4)

        self.user_profiles.at[user_index, "interests"] = "|".join(sorted(interest_weights))
        self.user_profiles.at[user_index, "skills"] = "|".join(sorted(skill_weights))
        self.user_profiles.at[user_index, "interest_weights"] = self._serialize_weight_map(interest_weights)
        self.user_profiles.at[user_index, "skill_weights"] = self._serialize_weight_map(skill_weights)

        updated_user = self.user_profiles.loc[user_index]
        cards_for_embedding = self.project_catalog.rename(
            columns={"project_id": "card_id", "required_skills": "skills_required"}
        )
        history = self.reactions[self.reactions["user_id"] == student_id].rename(columns={"project_id": "card_id"})
        new_embedding = build_user_embedding(updated_user, history, cards_for_embedding).tolist()
        self.user_profiles.at[user_index, "user_embedding"] = json.dumps(new_embedding)
        self.user_profiles.to_csv(self.user_profiles_path, index=False)

        reaction_record = {
            "user_id": student_id,
            "project_id": project["project_id"],
            "shown_at": datetime.now(UTC).isoformat(),
            "session_depth": int(
                self.reactions[self.reactions["user_id"] == student_id]["session_depth"].max()
                if not self.reactions[self.reactions["user_id"] == student_id].empty
                else 0
            )
            + 1,
            "topic_match_score": project["topic_match_score"],
            "required_skill_match_score": project["required_skill_match_score"],
            "gained_skill_match_score": project["gained_skill_match_score"],
            "role_skill_match_score": project["role_skill_match_score"],
            "readiness_score": project["readiness_score"],
            "open": int(reaction == "open"),
            "like": int(reaction == "like"),
            "share": int(reaction == "share"),
            "long_view": int(reaction == "long_view"),
            "skip_fast": int(reaction == "skip_fast"),
            "disengage": int(reaction == "disengage"),
        }
        self.reactions = pd.concat([self.reactions, pd.DataFrame([reaction_record])], ignore_index=True)
        self.reactions.to_csv(self.reactions_path, index=False)

    def get_profile_snapshot(self, student_id: str, top_n: int = 5) -> dict[str, list[tuple[str, float]]]:
        user = self._get_user_row(student_id)
        interest_weights = parse_weight_map(user["interest_weights"])
        skill_weights = parse_weight_map(user["skill_weights"])
        return {
            "interests": sorted(interest_weights.items(), key=lambda item: item[1], reverse=True)[:top_n],
            "skills": sorted(skill_weights.items(), key=lambda item: item[1], reverse=True)[:top_n],
        }

    def _get_user_row(self, student_id: str) -> pd.Series:
        return self.user_profiles[self.user_profiles["user_id"] == student_id].iloc[0]

    @staticmethod
    def _serialize_weight_map(weight_map: dict[str, float]) -> str:
        return pd.Series(weight_map).sort_index().round(4).to_json()

    @staticmethod
    def _cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
        if left.size == 0 or right.size == 0:
            return 0.0
        denom = float(np.linalg.norm(left) * np.linalg.norm(right)) or 1.0
        return float(np.dot(left, right) / denom)

    @staticmethod
    def _commitment_fit(experience_level: str, expected_commitment: str) -> float:
        fit_map = {
            "newcomer": {"low": 1.0, "medium": 0.7, "high": 0.25},
            "junior": {"low": 0.9, "medium": 0.9, "high": 0.5},
            "mid": {"low": 0.6, "medium": 0.95, "high": 0.9},
            "senior": {"low": 0.5, "medium": 0.85, "high": 1.0},
        }
        return fit_map.get(experience_level, {}).get(expected_commitment, 0.5)

    @staticmethod
    def _maturity_fit(experience_level: str, project_maturity: str) -> float:
        fit_map = {
            "newcomer": {"idea": 1.0, "mvp": 0.75, "growth": 0.45},
            "junior": {"idea": 0.9, "mvp": 0.9, "growth": 0.65},
            "mid": {"idea": 0.65, "mvp": 0.95, "growth": 0.95},
            "senior": {"idea": 0.6, "mvp": 0.9, "growth": 1.0},
        }
        return fit_map.get(experience_level, {}).get(project_maturity, 0.5)

    @staticmethod
    def render_profile(snapshot: dict[str, list[tuple[str, float]]], title: str) -> str:
        interests = ", ".join(f"{name} ({weight:.2f})" for name, weight in snapshot["interests"]) or "-"
        skills = ", ".join(f"{name} ({weight:.2f})" for name, weight in snapshot["skills"]) or "-"
        return "\n".join(
            [
                title,
                f"Top interests : {interests}",
                f"Top skills    : {skills}",
                "-" * 88,
            ]
        )

    @staticmethod
    def render_project(project: dict[str, object], position: int) -> str:
        lines = [
            "=" * 88,
            f"PROJECT {position}",
            "-" * 88,
            f"ID                  : {project['project_id']}",
            f"Title               : {project['project_title']}",
            f"Summary             : {project['project_summary']}",
            f"Topics              : {', '.join(split_pipe(project['topics']))}",
            f"Required skills     : {', '.join(split_pipe(project['required_skills']))}",
            f"Skills gained       : {', '.join(split_pipe(project['skills_gained']))}",
            f"Role skills         : {', '.join(split_pipe(project['role_skills']))}",
            f"Maturity            : {project['project_maturity']}",
            f"Commitment          : {project['expected_commitment']}",
            f"Collaboration       : {project['collaboration_mode']}",
            f"Difficulty          : {project['difficulty_level']}",
            f"Format              : {project['format']}",
            f"Language            : {project['language']}",
            f"Location            : {project['location']}",
            f"Organization        : {project['host_organization']}",
            "",
            "MATCH SIGNALS",
            f"Topic match         : {float(project['topic_match_score']):.4f}",
            f"Required skill match: {float(project['required_skill_match_score']):.4f}",
            f"Gained skill match  : {float(project['gained_skill_match_score']):.4f}",
            f"Role skill match    : {float(project['role_skill_match_score']):.4f}",
            f"Readiness score     : {float(project['readiness_score']):.4f}",
            f"Embedding similarity: {float(project['embedding_similarity']):.4f}",
            f"Commitment fit      : {float(project['commitment_fit']):.4f}",
            f"Maturity fit        : {float(project['maturity_fit']):.4f}",
            f"Final score         : {float(project['final_score']):.4f}",
            "=" * 88,
        ]
        return "\n".join(lines)

    @staticmethod
    def read_reaction() -> str:
        print("Available reactions:")
        for key, description in REACTIONS.items():
            print(f"  - {key:<10} ({description})")
        print("  - q          (quit)")
        while True:
            raw_value = input("Reaction > ").strip().lower()
            if raw_value == "q":
                return "q"
            reaction = REACTION_ALIASES.get(raw_value, raw_value)
            if reaction in REACTIONS:
                return reaction
            print("Unknown reaction. Use one of the listed values.")


def read_student_id(provided_student_id: str | None, available_ids: list[str]) -> str:
    if provided_student_id:
        return provided_student_id
    print("Enter student id.")
    print(f"Examples: {', '.join(available_ids[:10])}")
    return input("student_id > ").strip()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interactive project recommendation scenario by student id.")
    parser.add_argument("--student-id")
    parser.add_argument("--max-projects", type=int, default=10)
    args = parser.parse_args()

    runner = ProjectScenarioRunner(ROOT)
    student_id = read_student_id(args.student_id, runner.user_profiles["user_id"].tolist())
    runner.run(student_id=student_id, max_projects=args.max_projects)
