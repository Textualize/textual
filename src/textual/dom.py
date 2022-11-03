from __future__ import annotations

import re
from collections import deque
from inspect import getfile
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Iterable,
    Iterator,
    Type,
    TypeVar,
    cast,
    overload,
)

import rich.repr
from rich.highlighter import ReprHighlighter
from rich.pretty import Pretty
from rich.style import Style
from rich.text import Text
from rich.tree import Tree

from ._context import NoActiveAppError
from ._node_list import NodeList
from .binding import Bindings, BindingType
from .color import BLACK, WHITE, Color
from .css._error_tools import friendly_list
from .css.constants import VALID_DISPLAY, VALID_VISIBILITY
from .css.errors import DeclarationError, StyleValueError
from .css.parse import parse_declarations
from .css.query import NoMatches
from .css.styles import RenderStyles, Styles
from .css.tokenize import IDENTIFIER
from .message_pump import MessagePump
from .timer import Timer

if TYPE_CHECKING:
    from .app import App
    from .css.query import DOMQuery
    from .screen import Screen
    from .widget import Widget

from textual._typing import Literal, TypeAlias

_re_identifier = re.compile(IDENTIFIER)

WalkMethod: TypeAlias = Literal["depth", "breadth"]


class BadIdentifier(Exception):
    """raised by check_identifiers."""


def check_identifiers(description: str, *names: str) -> None:
    """Validate identifier and raise an error if it fails.

    Args:
        description (str): Description of where identifier is used for error message.
        names (list[str]): Identifiers to check.

    Returns:
        bool: True if the name is valid.
    """
    match = _re_identifier.match
    for name in names:
        if match(name) is None:
            raise BadIdentifier(
                f"{name!r} is an invalid {description}; "
                "identifiers must contain only letters, numbers, underscores, or hyphens, and must not begin with a number."
            )


class DOMError(Exception):
    pass


class NoScreen(DOMError):
    pass


@rich.repr.auto
class DOMNode(MessagePump):
    """The base class for object that can be in the Textual DOM (App and Widget)"""

    # CSS defaults
    DEFAULT_CSS: ClassVar[str] = ""

    # Default classes argument if not supplied
    DEFAULT_CLASSES: str = ""

    # Virtual DOM nodes
    COMPONENT_CLASSES: ClassVar[set[str]] = set()

    # Mapping of key bindings
    BINDINGS: ClassVar[list[BindingType]] = []

    # True if this node inherits the CSS from the base class.
    _inherit_css: ClassVar[bool] = True
    # List of names of base classes that inherit CSS
    _css_type_names: ClassVar[frozenset[str]] = frozenset()

    def __init__(
        self,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self._classes = set()
        self._name = name
        self._id = None
        if id is not None:
            self.id = id

        _classes = classes.split() if classes else []
        check_identifiers("class name", *_classes)
        self._classes.update(_classes)

        self.children = NodeList()
        self._css_styles: Styles = Styles(self)
        self._inline_styles: Styles = Styles(self)
        self.styles = RenderStyles(self, self._css_styles, self._inline_styles)
        # A mapping of class names to Styles set in COMPONENT_CLASSES
        self._component_styles: dict[str, RenderStyles] = {}

        self._auto_refresh: float | None = None
        self._auto_refresh_timer: Timer | None = None
        self._css_types = {cls.__name__ for cls in self._css_bases(self.__class__)}
        self._bindings = Bindings(self.BINDINGS)
        self._has_hover_style: bool = False
        self._has_focus_within: bool = False

        super().__init__()

    @property
    def auto_refresh(self) -> float | None:
        return self._auto_refresh

    @auto_refresh.setter
    def auto_refresh(self, interval: float | None) -> None:
        if self._auto_refresh_timer is not None:
            self._auto_refresh_timer.stop_no_wait()
            self._auto_refresh_timer = None
        if interval is not None:
            self._auto_refresh_timer = self.set_interval(
                interval, self._automatic_refresh, name=f"auto refresh {self!r}"
            )
        self._auto_refresh = interval

    def _automatic_refresh(self) -> None:
        """Perform an automatic refresh (set with auto_refresh property)."""
        self.refresh()

    def __init_subclass__(cls, inherit_css: bool = True) -> None:
        super().__init_subclass__()
        cls._inherit_css = inherit_css
        css_type_names: set[str] = set()
        for base in cls._css_bases(cls):
            css_type_names.add(base.__name__)
        cls._css_type_names = frozenset(css_type_names)

    def get_component_styles(self, name: str) -> RenderStyles:
        """Get a "component" styles object (must be defined in COMPONENT_CLASSES classvar).

        Args:
            name (str): Name of the component.

        Raises:
            KeyError: If the component class doesn't exist.

        Returns:
            RenderStyles: A Styles object.
        """
        if name not in self._component_styles:
            raise KeyError(f"No {name!r} key in COMPONENT_CLASSES")
        styles = self._component_styles[name]
        return styles

    @property
    def _node_bases(self) -> Iterator[Type[DOMNode]]:
        """Get the DOMNode bases classes (including self.__class__)

        Returns:
            Iterator[Type[DOMNode]]: An iterable of DOMNode classes.
        """
        # Node bases are in reversed order so that the base class is lower priority
        return self._css_bases(self.__class__)

    @classmethod
    def _css_bases(cls, base: Type[DOMNode]) -> Iterator[Type[DOMNode]]:
        """Get the DOMNode base classes, which inherit CSS.

        Args:
            base (Type[DOMNode]): A DOMNode class

        Returns:
            Iterator[Type[DOMNode]]: An iterable of DOMNode classes.
        """
        _class = base
        while True:
            yield _class
            if not _class._inherit_css:
                break
            for _base in _class.__bases__:
                if issubclass(_base, DOMNode):
                    _class = _base
                    break
            else:
                break

    def _post_register(self, app: App) -> None:
        """Called when the widget is registered

        Args:
            app (App): Parent application.
        """

    def __rich_repr__(self) -> rich.repr.Result:
        yield "name", self._name, None
        yield "id", self._id, None
        if self._classes:
            yield "classes", " ".join(self._classes)

    def get_default_css(self) -> list[tuple[str, str, int]]:
        """Gets the CSS for this class and inherited from bases.

        Returns:
            list[tuple[str, str]]: a list of tuples containing (PATH, SOURCE) for this
                and inherited from base classes.
        """

        css_stack: list[tuple[str, str, int]] = []

        def get_path(base: Type[DOMNode]) -> str:
            """Get a path to the DOM Node"""
            try:
                return f"{getfile(base)}:{base.__name__}"
            except TypeError:
                return f"{base.__name__}"

        for tie_breaker, base in enumerate(self._node_bases):
            css = base.DEFAULT_CSS.strip()
            if css:
                css_stack.append((get_path(base), css, -tie_breaker))

        return css_stack

    @property
    def parent(self) -> DOMNode | None:
        """Get the parent node.

        Returns:
            DOMNode | None: The node which is the direct parent of this node.
        """

        return cast("DOMNode | None", self._parent)

    @property
    def screen(self) -> "Screen":
        """Get the screen that this node is contained within. Note that this may not be the currently active screen within the app."""
        # Get the node by looking up a chain of parents
        # Note that self.screen may not be the same as self.app.screen
        from .screen import Screen

        node = self
        while node and not isinstance(node, Screen):
            node = node._parent
        if not isinstance(node, Screen):
            raise NoScreen("node has no screen")
        return node

    @property
    def id(self) -> str | None:
        """The ID of this node, or None if the node has no ID.

        Returns:
            (str | None): A Node ID or None.
        """
        return self._id

    @id.setter
    def id(self, new_id: str) -> str:
        """Sets the ID (may only be done once).

        Args:
            new_id (str): ID for this node.

        Raises:
            ValueError: If the ID has already been set.

        """
        check_identifiers("id", new_id)

        if self._id is not None:
            raise ValueError(
                f"Node 'id' attribute may not be changed once set (current id={self._id!r})"
            )
        self._id = new_id
        return new_id

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def css_identifier(self) -> str:
        """A CSS selector that identifies this DOM node."""
        tokens = [self.__class__.__name__]
        if self.id is not None:
            tokens.append(f"#{self.id}")
        return "".join(tokens)

    @property
    def css_identifier_styled(self) -> Text:
        """A stylized CSS identifier."""
        tokens = Text.styled(self.__class__.__name__)
        if self.id is not None:
            tokens.append(f"#{self.id}", style="bold")
        if self.classes:
            tokens.append(".")
            tokens.append(".".join(class_name for class_name in self.classes), "italic")
        if self.name:
            tokens.append(f"[name={self.name}]", style="underline")
        return tokens

    @property
    def classes(self) -> frozenset[str]:
        """A frozenset of the current classes set on the widget.

        Returns:
            frozenset[str]: Set of class names.

        """
        return frozenset(self._classes)

    @property
    def pseudo_classes(self) -> frozenset[str]:
        """Get a set of all pseudo classes"""
        pseudo_classes = frozenset({*self.get_pseudo_classes()})
        return pseudo_classes

    @property
    def css_path_nodes(self) -> list[DOMNode]:
        """A list of nodes from the root to this node, forming a "path".

        Returns:
            list[DOMNode]: List of Nodes, starting with the root and ending with this node.
        """
        result: list[DOMNode] = [self]
        append = result.append

        node: DOMNode = self
        while isinstance(node._parent, DOMNode):
            node = node._parent
            append(node)
        return result[::-1]

    @property
    def _selector_names(self) -> list[str]:
        """Get a set of selectors applicable to this widget.

        Returns:
            set[str]: Set of selector names.
        """
        selectors: list[str] = [
            "*",
            *(f".{class_name}" for class_name in self._classes),
            *(f":{class_name}" for class_name in self.get_pseudo_classes()),
            *self._css_types,
        ]
        if self._id is not None:
            selectors.append(f"#{self._id}")
        return selectors

    @property
    def display(self) -> bool:
        """
        Check if this widget should display or not.

        Returns:
            bool: ``True`` if this DOMNode is displayed (``display != "none"``) otherwise ``False`` .
        """
        return self.styles.display != "none" and not (self._closing or self._closed)

    @display.setter
    def display(self, new_val: bool | str) -> None:
        """
        Args:
            new_val (bool | str): Shortcut to set the ``display`` CSS property.
                ``False`` will set ``display: none``. ``True`` will set ``display: block``.
                A ``False`` value will prevent the DOMNode from consuming space in the layout.
        """
        # TODO: This will forget what the original "display" value was, so if a user
        #  toggles to False then True, we'll reset to the default "block", rather than
        #  what the user initially specified.
        if isinstance(new_val, bool):
            self.styles.display = "block" if new_val else "none"
        elif new_val in VALID_DISPLAY:
            self.styles.display = new_val
        else:
            raise StyleValueError(
                f"invalid value for display (received {new_val!r}, "
                f"expected {friendly_list(VALID_DISPLAY)})",
            )

    @property
    def visible(self) -> bool:
        """Check if the node is visible or None.

        Returns:
            bool: True if the node is visible.
        """
        return self.styles.visibility != "hidden"

    @visible.setter
    def visible(self, new_value: bool) -> None:
        if isinstance(new_value, bool):
            self.styles.visibility = "visible" if new_value else "hidden"
        elif new_value in VALID_VISIBILITY:
            self.styles.visibility = new_value
        else:
            raise StyleValueError(
                f"invalid value for visibility (received {new_value!r}, "
                f"expected {friendly_list(VALID_VISIBILITY)})"
            )

    @property
    def tree(self) -> Tree:
        """Get a Rich tree object which will recursively render the structure of the node tree.

        Returns:
            Tree: A Rich object which may be printed.
        """
        from rich.columns import Columns
        from rich.console import Group
        from rich.panel import Panel

        from .widget import Widget

        def render_info(node: DOMNode) -> Columns:
            if isinstance(node, Widget):
                info = Columns(
                    [
                        Pretty(node),
                        highlighter(f"region={node.region!r}"),
                        highlighter(
                            f"virtual_size={node.virtual_size!r}",
                        ),
                    ]
                )
            else:
                info = Columns([Pretty(node)])
            return info

        highlighter = ReprHighlighter()
        tree = Tree(render_info(self))

        def add_children(tree, node):
            for child in node.children:
                info = render_info(child)
                css = child.styles.css
                if css:
                    info = Group(
                        info,
                        Panel.fit(
                            Text(child.styles.css),
                            border_style="dim",
                            title="css",
                            title_align="left",
                        ),
                    )
                branch = tree.add(info)
                if tree.children:
                    add_children(branch, child)

        add_children(tree, self)
        return tree

    @property
    def text_style(self) -> Style:
        """Get the text style object.

        A widget's style is influenced by its parent. for instance if a parent is bold, then
        the child will also be bold.

        Returns:
            Style: Rich Style object.
        """
        return Style.combine(
            node.styles.text_style for node in reversed(self.ancestors)
        )

    @property
    def rich_style(self) -> Style:
        """Get a Rich Style object for this DOMNode."""
        background = WHITE
        color = BLACK
        style = Style()
        for node in reversed(self.ancestors):
            styles = node.styles
            if styles.has_rule("background"):
                background += styles.background
            if styles.has_rule("color"):
                color = styles.color
            style += styles.text_style
            if styles.has_rule("auto_color") and styles.auto_color:
                color = background.get_contrast_text(color.a)
        style += Style.from_color(
            (background + color).rich_color, background.rich_color
        )
        return style

    @property
    def background_colors(self) -> tuple[Color, Color]:
        """Get the background color and the color of the parent's background.

        Returns:
            tuple[Color, Color]: Tuple of (base background, background)

        """
        base_background = background = BLACK
        for node in reversed(self.ancestors):
            styles = node.styles
            if styles.has_rule("background"):
                base_background = background
                background += styles.background
        return (base_background, background)

    @property
    def colors(self) -> tuple[Color, Color, Color, Color]:
        """Gets the Widgets foreground and background colors, and its parent's (base) colors.

        Returns:
            tuple[Color, Color, Color, Color]: Tuple of (base background, base color, background, color)
        """
        base_background = background = WHITE
        base_color = color = BLACK
        for node in reversed(self.ancestors):
            styles = node.styles
            if styles.has_rule("background"):
                base_background = background
                background += styles.background
            if styles.has_rule("color"):
                base_color = color
                if styles.auto_color:
                    color = background.get_contrast_text(color.a)
                else:
                    color = styles.color

        return (base_background, base_color, background, color)

    @property
    def ancestors(self) -> list[DOMNode]:
        """Get a list of Nodes by tracing ancestors all the way back to App."""
        nodes: list[MessagePump | None] = []
        add_node = nodes.append
        node: MessagePump | None = self
        while node is not None:
            add_node(node)
            node = node._parent
        return cast("list[DOMNode]", nodes)

    @property
    def displayed_children(self) -> list[Widget]:
        """The children which don't have display: none set.

        Returns:
            list[DOMNode]: Children of this widget which will be displayed.

        """
        return [child for child in self.children if child.display]

    def get_pseudo_classes(self) -> Iterable[str]:
        """Get any pseudo classes applicable to this Node, e.g. hover, focus.

        Returns:
            Iterable[str]: Iterable of strings, such as a generator.
        """
        return ()

    def reset_styles(self) -> None:
        """Reset styles back to their initial state"""
        from .widget import Widget

        for node in self.walk_children():
            node._css_styles.reset()
            if isinstance(node, Widget):
                node._set_dirty()
                node._layout_required = True

    def _add_child(self, node: Widget) -> None:
        """Add a new child node.

        Args:
            node (DOMNode): A DOM node.
        """
        self.children._append(node)
        node._attach(self)

    def _add_children(self, *nodes: Widget) -> None:
        """Add multiple children to this node.

        Args:
            *nodes (DOMNode): Positional args should be new DOM nodes.
        """
        _append = self.children._append
        for node in nodes:
            node._attach(self)
            _append(node)

    WalkType = TypeVar("WalkType")

    @overload
    def walk_children(
        self,
        filter_type: type[WalkType],
        *,
        with_self: bool = True,
        method: WalkMethod = "depth",
        reverse: bool = False,
    ) -> list[WalkType]:
        ...

    @overload
    def walk_children(
        self,
        *,
        with_self: bool = True,
        method: WalkMethod = "depth",
        reverse: bool = False,
    ) -> list[DOMNode]:
        ...

    def walk_children(
        self,
        filter_type: type[WalkType] | None = None,
        *,
        with_self: bool = True,
        method: WalkMethod = "depth",
        reverse: bool = False,
    ) -> list[DOMNode] | list[WalkType]:
        """Generate descendant nodes.

        Args:
            filter_type (type[WalkType] | None, optional): Filter only this type, or None for no filter.
                Defaults to None.
            with_self (bool, optional): Also yield self in addition to descendants. Defaults to True.
            method (Literal["breadth", "depth"], optional): One of "depth" or "breadth". Defaults to "depth".
            reverse (bool, optional): Reverse the order (bottom up). Defaults to False.

        Returns:
            list[DOMNode] | list[WalkType]: A list of nodes.

        """

        def walk_depth_first() -> Iterable[DOMNode]:
            """Walk the tree depth first (parents first)."""
            stack: list[Iterator[DOMNode]] = [iter(self.children)]
            pop = stack.pop
            push = stack.append
            check_type = filter_type or DOMNode

            if with_self and isinstance(self, check_type):
                yield self
            while stack:
                node = next(stack[-1], None)
                if node is None:
                    pop()
                else:
                    if isinstance(node, check_type):
                        yield node
                    if node.children:
                        push(iter(node.children))

        def walk_breadth_first() -> Iterable[DOMNode]:
            """Walk the tree breadth first (children first)."""
            queue: deque[DOMNode] = deque()
            popleft = queue.popleft
            extend = queue.extend
            check_type = filter_type or DOMNode

            if with_self and isinstance(self, check_type):
                yield self
            extend(self.children)
            while queue:
                node = popleft()
                if isinstance(node, check_type):
                    yield node
                extend(node.children)

        node_generator = (
            walk_depth_first() if method == "depth" else walk_breadth_first()
        )

        # We want a snapshot of the DOM at this point So that it doesn't
        # change mid-walk
        nodes = list(node_generator)
        if reverse:
            nodes.reverse()
        return nodes

    def get_child(self, id: str) -> DOMNode:
        """Return the first child (immediate descendent) of this node with the given ID.

        Args:
            id (str): The ID of the child.

        Returns:
            DOMNode: The first child of this node with the ID.

        Raises:
            NoMatches: if no children could be found for this ID
        """
        for child in self.children:
            if child.id == id:
                return child
        raise NoMatches(f"No child found with id={id!r}")

    ExpectType = TypeVar("ExpectType", bound="Widget")

    @overload
    def query(self, selector: str | None) -> DOMQuery[Widget]:
        ...

    @overload
    def query(self, selector: type[ExpectType]) -> DOMQuery[ExpectType]:
        ...

    def query(
        self, selector: str | type[ExpectType] | None = None
    ) -> DOMQuery[Widget] | DOMQuery[ExpectType]:
        """Get a DOM query matching a selector.

        Args:
            selector (str | type | None, optional): A CSS selector or `None` for all nodes. Defaults to None.

        Returns:
            DOMQuery: A query object.
        """
        from .css.query import DOMQuery

        query: str | None
        if isinstance(selector, str) or selector is None:
            query = selector
        else:
            query = selector.__name__

        return DOMQuery(self, filter=query)

    @overload
    def query_one(self, selector: str) -> Widget:
        ...

    @overload
    def query_one(self, selector: type[ExpectType]) -> ExpectType:
        ...

    @overload
    def query_one(self, selector: str, expect_type: type[ExpectType]) -> ExpectType:
        ...

    def query_one(
        self,
        selector: str | type[ExpectType],
        expect_type: type[ExpectType] | None = None,
    ) -> ExpectType | Widget:
        """Get the first Widget matching the given selector or selector type.

        Args:
            selector (str | type): A selector.
            expect_type (type | None, optional): Require the object be of the supplied type, or None for any type.
                Defaults to None.

        Returns:
            Widget | ExpectType: A widget matching the selector.
        """
        from .css.query import DOMQuery

        if isinstance(selector, str):
            query_selector = selector
        else:
            query_selector = selector.__name__
        query: DOMQuery[Widget] = DOMQuery(self, filter=query_selector)

        return query.only_one() if expect_type is None else query.only_one(expect_type)

    def set_styles(self, css: str | None = None, **update_styles) -> None:
        """Set custom styles on this object."""

        if css is not None:
            try:
                new_styles = parse_declarations(css, path="set_styles")
            except DeclarationError as error:
                raise DeclarationError(error.name, error.token, error.message) from None
            self._inline_styles.merge(new_styles)
            self.refresh(layout=True)

        styles = self.styles
        for key, value in update_styles.items():
            setattr(styles, key, value)

    def has_class(self, *class_names: str) -> bool:
        """Check if the Node has all the given class names.

        Args:
            *class_names (str): CSS class names to check.

        Returns:
            bool: ``True`` if the node has all the given class names, otherwise ``False``.
        """
        return self._classes.issuperset(class_names)

    def set_class(self, add: bool, *class_names: str) -> None:
        """Add or remove class(es) based on a condition.

        Args:
            add (bool):  Add the classes if True, otherwise remove them.
        """
        if add:
            self.add_class(*class_names)
        else:
            self.remove_class(*class_names)

    def add_class(self, *class_names: str) -> None:
        """Add class names to this Node.

        Args:
            *class_names (str): CSS class names to add.

        """
        check_identifiers("class name", *class_names)
        old_classes = self._classes.copy()
        self._classes.update(class_names)
        if old_classes == self._classes:
            return
        try:
            self.app.update_styles(self)
        except NoActiveAppError:
            pass

    def remove_class(self, *class_names: str) -> None:
        """Remove class names from this Node.

        Args:
            *class_names (str): CSS class names to remove.

        """
        check_identifiers("class name", *class_names)
        old_classes = self._classes.copy()
        self._classes.difference_update(class_names)
        if old_classes == self._classes:
            return
        try:
            self.app.update_styles(self)
        except NoActiveAppError:
            pass

    def toggle_class(self, *class_names: str) -> None:
        """Toggle class names on this Node.

        Args:
            *class_names (str): CSS class names to toggle.

        """
        check_identifiers("class name", *class_names)
        old_classes = self._classes.copy()
        self._classes.symmetric_difference_update(class_names)
        if old_classes == self._classes:
            return
        try:
            self.app.update_styles(self)
        except NoActiveAppError:
            pass

    def has_pseudo_class(self, *class_names: str) -> bool:
        """Check for pseudo class (such as hover, focus etc)"""
        has_pseudo_classes = self.pseudo_classes.issuperset(class_names)
        return has_pseudo_classes

    def refresh(self, *, repaint: bool = True, layout: bool = False) -> None:
        pass
