from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score

from .schema import Paths


TARGETS = ["open", "like", "share", "long_view", "skip_fast", "disengage"]


def load_evaluation_bundle(root: Path) -> dict[str, Any]:
    paths = Paths(root)
    dataset = pd.read_csv(paths.ranked_training)
    ranker = joblib.load(paths.ranker_model)
    return {"dataset": dataset, "ranker": ranker}


def predict_ranker_scores(root: Path) -> pd.DataFrame:
    bundle = load_evaluation_bundle(root)
    dataset = bundle["dataset"]
    ranker = bundle["ranker"]
    feature_frame = dataset.reindex(columns=ranker["feature_columns"], fill_value=0.0)
    result = dataset.copy()
    for target, model in ranker["models"].items():
        probabilities = model.predict_proba(feature_frame)
        result[f"pred_{target}"] = probabilities[:, 1] if probabilities.shape[1] > 1 else 0.0
    return result


def summarize_ranker_quality(root: Path) -> pd.DataFrame:
    scored = predict_ranker_scores(root)
    rows: list[dict[str, Any]] = []
    for target in TARGETS:
        y_true = scored[target].astype(int)
        y_pred = scored[f"pred_{target}"].astype(float)
        rows.append(
            {
                "target": target,
                "positive_rate": float(y_true.mean()),
                "roc_auc": _safe_metric(roc_auc_score, y_true, y_pred),
                "average_precision": _safe_metric(average_precision_score, y_true, y_pred),
                "log_loss": _safe_metric(log_loss, y_true, y_pred),
                "brier_score": _safe_metric(brier_score_loss, y_true, y_pred),
                "prediction_mean": float(y_pred.mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("roc_auc", ascending=False).reset_index(drop=True)


def build_calibration_table(root: Path, target: str, bins: int = 10) -> pd.DataFrame:
    scored = predict_ranker_scores(root)
    prediction_column = f"pred_{target}"
    frame = scored[[target, prediction_column]].copy()
    frame["bin"] = pd.qcut(frame[prediction_column], q=min(bins, frame[prediction_column].nunique()), duplicates="drop")
    calibration = (
        frame.groupby("bin", observed=False)
        .agg(
            predicted_mean=(prediction_column, "mean"),
            actual_mean=(target, "mean"),
            sample_count=(target, "size"),
        )
        .reset_index()
    )
    calibration["bin"] = calibration["bin"].astype(str)
    return calibration


def summarize_feature_importance(root: Path, top_n: int = 10) -> pd.DataFrame:
    bundle = load_evaluation_bundle(root)
    ranker = bundle["ranker"]
    rows: list[dict[str, Any]] = []
    for target, model in ranker["models"].items():
        importances = getattr(model, "feature_importances_", None)
        if importances is None:
            continue
        pairs = list(zip(ranker["feature_columns"], importances))
        for feature_name, importance in sorted(pairs, key=lambda item: item[1], reverse=True)[:top_n]:
            rows.append({"target": target, "feature": feature_name, "importance": float(importance)})
    return pd.DataFrame(rows)


def summarize_retrieval_alignment(root: Path) -> pd.DataFrame:
    scored = predict_ranker_scores(root)
    rows = []
    for target in TARGETS:
        grouped = scored.groupby(target)["retrieval_similarity"].mean().to_dict()
        rows.append(
            {
                "target": target,
                "mean_similarity_when_0": float(grouped.get(0, 0.0)),
                "mean_similarity_when_1": float(grouped.get(1, 0.0)),
                "delta": float(grouped.get(1, 0.0) - grouped.get(0, 0.0)),
            }
        )
    return pd.DataFrame(rows).sort_values("delta", ascending=False).reset_index(drop=True)


def _safe_metric(metric_fn: Any, y_true: pd.Series, y_pred: pd.Series) -> float:
    try:
        if metric_fn is log_loss:
            clipped = np.clip(y_pred, 1e-6, 1 - 1e-6)
            return float(metric_fn(y_true, clipped))
        return float(metric_fn(y_true, y_pred))
    except ValueError:
        return float("nan")
