from __future__ import annotations

from typing import cast
from textual._typing import Final, Literal

FEATURES: Final = {"devtools", "debug", "headless"}

FeatureFlag = Literal["devtools", "debug", "headless"]


def parse_features(features: str) -> frozenset[FeatureFlag]:
    """Parse features env var

    Args:
        features (str): Comma separated feature flags

    Returns:
        frozenset[FeatureFlag]: A frozen set of known features.
    """

    features_set = frozenset(
        feature.strip().lower() for feature in features.split(",") if feature.strip()
    ).intersection(FEATURES)

    return cast("frozenset[FeatureFlag]", features_set)
