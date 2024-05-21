from __future__ import annotations

import rich.repr
from rich.text import Text

from textual.app import ComposeResult

from .. import events
from ..containers import ScrollableContainer
from ..reactive import reactive
from ..widgets import Label


@rich.repr.auto
class FooterKey(Label):
    COMPONENT_CLASSES = {
        "footer-key--key",
        "footer-key--description",
    }

    DEFAULT_CSS = """
    FooterKey {
        background: $panel;        
        color: $text-muted;
    
        .footer-key--key {     
            color: $secondary;                   
            background: $panel;
            text-style: bold;
           
            
        }

        &:light .footer-key--key {
            color: $primary; 
        }        

        &:hover {
            background: $panel-darken-2;
            color: $text;
            .footer-key--key { 
                background: $panel-darken-2;              
            }            
        }

        &.-disabled {    
            text-style: dim;
            background: $panel;
            &:hover {
                .footer-key--key {            
                    background: $panel;
                }    
            }        
        }
                   
    }
    """

    capitalize_keys = reactive(False)
    ctrl_to_caret = reactive(True)
    compact = reactive(True)

    def __init__(
        self, key: str, description: str, action: str, disabled: bool = False
    ) -> None:
        self.key = key
        self.description = description
        self.action = action
        self._disabled = disabled
        super().__init__(classes="-disabled" if disabled else "")

    def render(self) -> Text:
        key_style = self.get_component_rich_style("footer-key--key")
        description_style = self.get_component_rich_style("footer-key--description")
        key = self.key
        if self.capitalize_keys:
            key = key.upper()
        if key.lower().startswith("ctrl+"):
            key = "^" + key.split("+", 1)[1]
        description = self.description
        if self.compact:
            label_text = Text.assemble(
                (key, key_style), " ", (description, description_style)
            )
        else:
            label_text = Text.assemble(
                (f" {key} ", key_style), (description, description_style), " "
            )
        label_text.stylize_before(self.rich_style)
        return label_text

    def get_content_height(
        self, container: events.Size, viewport: events.Size, width: int
    ) -> int:
        return 1

    async def on_mouse_up(self) -> None:
        if self._disabled:
            self.app.bell()
        else:
            await self.app.check_bindings(self.key)

    def _watch_compact(self, compact: bool) -> None:
        self.set_class(compact, "-compact")


@rich.repr.auto
class Footer(ScrollableContainer):
    DEFAULT_CSS = """
    Footer {
        layout: grid;
        grid-columns: auto;
        
        background: $panel;
        color: $text;
        dock: bottom;
        height: 1;
        scrollbar-size: 0 0;

        &.-compact {
            grid-gutter: 1;
        }
        
    }
    """

    capitalize_keys = reactive(False)
    """Capitalize the keys."""
    ctrl_to_caret = reactive(True)
    """Convert ctrl+ prefix to ^"""
    compact = reactive(False)
    """Display in compact style."""

    def compose(self) -> ComposeResult:
        bindings = [
            (binding, enabled)
            for (_, binding, enabled) in self.screen.active_bindings.values()
            if binding.show
        ]
        self.styles.grid_size_columns = len(bindings)
        for binding, enabled in bindings:
            yield FooterKey(
                binding.key_display or binding.key,
                binding.description,
                binding.action,
                disabled=not enabled,
            ).data_bind(
                Footer.capitalize_keys,
                Footer.ctrl_to_caret,
                Footer.compact,
            )

    def on_mount(self) -> None:
        def bindings_changed(screen) -> None:
            self.call_next(self.recompose)

        self.screen.bindings_updated_signal.subscribe(self, bindings_changed)

    def watch_compact(self, compact: bool) -> None:
        self.set_class(compact, "-compact")
