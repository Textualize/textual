"""Provides a simple Label widget."""

from __future__ import annotations

from typing import Literal

from textual.visual import VisualType
from textual.widgets._static import Static

LabelVariant = Literal["success", "error", "warning", "primary", "secondary", "accent"]


class Label(Static):
    """A simple label widget for displaying text-oriented renderables."""

    DEFAULT_CSS = """
    Label {
        width: auto;
        height: auto;
        min-height: 1;

        &.success {
            color: $text-success;
            background: $success-muted;
        }
        &.error {
            color: $text-error;
            background: $error-muted;
        }
        &.warning {
            color: $text-warning;
            background: $warning-muted;
        }
        &.primary {
            color: $text-primary;
            background: $primary-muted;
        }
        &.secondary {
            color: $text-secondary;
            background: $secondary-muted;
        }
        &.accent {
            color: $text-accent;
            background: $accent-muted;
        }
    }
    """

    def __init__(
        self,
        # TODO: Should probably be renamed to `content`.
        renderable: VisualType = "",
        *,
        variant: LabelVariant | None = None,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            renderable,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        if variant:
            self.add_class(variant)
