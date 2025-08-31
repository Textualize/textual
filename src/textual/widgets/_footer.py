from __future__ import annotations

from collections import defaultdict
from itertools import groupby
from typing import TYPE_CHECKING

import rich.repr
from rich.text import Text

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label

if TYPE_CHECKING:
    from textual.screen import Screen


@rich.repr.auto
class FooterKey(Widget):
    ALLOW_SELECT = False
    COMPONENT_CLASSES = {
        "footer-key--key",
        "footer-key--description",
    }

    DEFAULT_CSS = """
    FooterKey {
        width: auto;
        height: 1;
        background: $footer-item-background;
        .footer-key--key {
            color: $footer-key-foreground;
            background: $footer-key-background;
            text-style: bold;
            padding: 0 1;
        }

        .footer-key--description {
            padding: 0 1 0 0;
            color: $footer-description-foreground;
            background: $footer-description-background;
        }

        &:hover {
            color: $footer-key-foreground;
            background: $block-hover-background;
        }

        &.-disabled {
            text-style: dim;
        }

        &.-compact {
            .footer-key--key {
                padding: 0;
            }
            .footer-key--description {
                padding: 0 0 0 1;
            }
        }
    }
    """

    compact = reactive(True)
    """Display compact style."""

    def __init__(
        self,
        key: str,
        key_display: str,
        description: str,
        action: str,
        disabled: bool = False,
        tooltip: str = "",
        classes="",
    ) -> None:
        self.key = key
        self.key_display = key_display
        self.description = description
        self.action = action
        self._disabled = disabled
        if disabled:
            classes += " -disabled"
        super().__init__(classes=classes)
        if tooltip:
            self.tooltip = tooltip

    def render(self) -> Text:
        key_style = self.get_component_rich_style("footer-key--key")
        description_style = self.get_component_rich_style("footer-key--description")
        key_display = self.key_display
        key_padding = self.get_component_styles("footer-key--key").padding
        description_padding = self.get_component_styles(
            "footer-key--description"
        ).padding
        description = self.description
        if description:
            label_text = Text.assemble(
                (
                    " " * key_padding.left + key_display + " " * key_padding.right,
                    key_style,
                ),
                (
                    " " * description_padding.left
                    + description
                    + " " * description_padding.right,
                    description_style,
                ),
            )
        else:
            label_text = Text.assemble((key_display, key_style))

        label_text.stylize_before(self.rich_style)
        return label_text

    async def on_mouse_down(self) -> None:
        if self._disabled:
            self.app.bell()
        else:
            self.app.simulate_key(self.key)

    def _watch_compact(self, compact: bool) -> None:
        self.set_class(compact, "-compact")


class FooterLabel(Label):
    """Text displayed in the footer (used by binding groups)."""


@rich.repr.auto
class Footer(ScrollableContainer, can_focus=False, can_focus_children=False):
    ALLOW_SELECT = False
    DEFAULT_CSS = """
    Footer {
        layout: horizontal;        
        color: $footer-foreground;
        background: $footer-background;
        dock: bottom;
        height: 1;
        scrollbar-size: 0 0;
        &.-compact {
            grid-gutter: 1;
        }
        FooterKey.-command-palette  {
            dock: right;
            padding-right: 1;
            border-left: vkey $foreground 20%;
        }
        HorizontalGroup.binding-group {            
            width: auto;
            height: 1;
            layout: horizontal;
        }

        &:ansi {
            background: ansi_default;
            .footer-key--key {
                background: ansi_default;
                color: ansi_magenta;
            }
            .footer-key--description {
                background: ansi_default;
                color: ansi_default;
            }
            FooterKey:hover {
                text-style: underline;
                background: ansi_default;
                color: ansi_default;
                .footer-key--key {
                    background: ansi_default;
                }
            }
            FooterKey.-command-palette {
                background: ansi_default;
                border-left: vkey ansi_black;
            }
        }
        FooterKey.-grouped {
            margin: 0 1;
        }
        FooterLabel {
            margin: 0 1;
            background: red;
            color: $footer-description-foreground;
            background: $footer-description-background;
        }
    }
    """

    compact = reactive(False)
    """Display in compact style."""
    _bindings_ready = reactive(False, repaint=False)
    """True if the bindings are ready to be displayed."""
    show_command_palette = reactive(True)
    """Show the key to invoke the command palette."""
    combine_groups = reactive(True)
    """Combine bindings in the same group?"""

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        show_command_palette: bool = True,
    ) -> None:
        """A footer to show key bindings.

        Args:
            *children: Child widgets.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
            show_command_palette: Show key binding to invoke the command palette, on the right of the footer.
        """
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.set_reactive(Footer.show_command_palette, show_command_palette)

    def compose(self) -> ComposeResult:
        if not self._bindings_ready:
            return
        active_bindings = self.screen.active_bindings
        bindings = [
            (binding, enabled, tooltip)
            for (_, binding, enabled, tooltip) in active_bindings.values()
            if binding.show
        ]
        action_to_bindings: defaultdict[str, list[tuple[Binding, bool, str]]]
        action_to_bindings = defaultdict(list)
        for binding, enabled, tooltip in bindings:
            action_to_bindings[binding.action].append((binding, enabled, tooltip))

        self.styles.grid_size_columns = len(action_to_bindings)

        for group, multi_bindings_iterable in groupby(
            action_to_bindings.values(),
            lambda multi_bindings: multi_bindings[0][0].group,
        ):
            if group is not None:
                for multi_bindings in multi_bindings_iterable:
                    binding, enabled, tooltip = multi_bindings[0]
                    yield FooterKey(
                        binding.key,
                        self.app.get_key_display(binding),
                        "",
                        binding.action,
                        disabled=not enabled,
                        tooltip=tooltip or binding.description,
                        classes="-grouped",
                    ).data_bind(Footer.compact)
                yield FooterLabel(group.description)
            else:
                for multi_bindings in multi_bindings_iterable:
                    binding, enabled, tooltip = multi_bindings[0]
                    yield FooterKey(
                        binding.key,
                        self.app.get_key_display(binding),
                        binding.description,
                        binding.action,
                        disabled=not enabled,
                        tooltip=tooltip,
                    ).data_bind(Footer.compact)
        if self.show_command_palette and self.app.ENABLE_COMMAND_PALETTE:
            try:
                _node, binding, enabled, tooltip = active_bindings[
                    self.app.COMMAND_PALETTE_BINDING
                ]
            except KeyError:
                pass
            else:
                yield FooterKey(
                    binding.key,
                    self.app.get_key_display(binding),
                    binding.description,
                    binding.action,
                    classes="-command-palette",
                    disabled=not enabled,
                    tooltip=binding.tooltip or binding.description,
                )

    async def bindings_changed(self, screen: Screen) -> None:
        self._bindings_ready = True
        if not screen.app.app_focus:
            return
        if self.is_attached and screen is self.screen:
            await self.recompose()

    def _on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        if self.allow_horizontal_scroll:
            self.release_anchor()
            if self._scroll_right_for_pointer(animate=True):
                event.stop()
                event.prevent_default()

    def _on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        if self.allow_horizontal_scroll:
            self.release_anchor()
            if self._scroll_left_for_pointer(animate=True):
                event.stop()
                event.prevent_default()

    def on_mount(self) -> None:
        self.call_next(self.bindings_changed, self.screen)

        def bindings_changed(screen: Screen) -> None:
            """Update bindings after a short delay to avoid flicker."""
            self.call_after_refresh(self.bindings_changed, screen)

        self.screen.bindings_updated_signal.subscribe(self, bindings_changed)

    def on_unmount(self) -> None:
        self.screen.bindings_updated_signal.unsubscribe(self)

    def watch_compact(self, compact: bool) -> None:
        self.set_class(compact, "-compact")
