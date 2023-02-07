from __future__ import annotations

from typing import TYPE_CHECKING, cast

from typing_extensions import Literal

if TYPE_CHECKING:
    from typing_extensions import Final

FEATURES: Final = {"devtools", "debug", "headless"}

FeatureFlag = Literal["devtools", "debug", "headless"]


def parse_features(features: str) -> frozenset[FeatureFlag]:
    """Parse features env var

    Args:
        features: Comma separated feature flags

    Returns:
        A frozen set of known features.
    """

    features_set = frozenset(
        feature.strip().lower() for feature in features.split(",") if feature.strip()
    ).intersection(FEATURES)

    return cast("frozenset[FeatureFlag]", features_set)
