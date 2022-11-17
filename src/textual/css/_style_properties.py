"""
Style properties are descriptors which allow the ``Styles`` object to accept different types when
setting attributes. This gives the developer more freedom in how to express style information.

Descriptors also play nicely with Mypy, which is aware that attributes can have different types
when setting and getting.

"""

from __future__ import annotations

from typing import Generic, Iterable, NamedTuple, TypeVar, TYPE_CHECKING, cast

import rich.repr
from rich.style import Style

from ._help_text import (
    border_property_help_text,
    layout_property_help_text,
    fractional_property_help_text,
    offset_property_help_text,
    style_flags_property_help_text,
)
from ._help_text import (
    spacing_wrong_number_of_values_help_text,
    scalar_help_text,
    string_enum_help_text,
    color_property_help_text,
)
from .._border import normalize_border_value
from ..color import Color, ColorParseError
from ._error_tools import friendly_list
from .constants import NULL_SPACING, VALID_STYLE_FLAGS
from .errors import StyleTypeError, StyleValueError
from .scalar import (
    get_symbols,
    UNIT_SYMBOL,
    Unit,
    Scalar,
    ScalarOffset,
    ScalarParseError,
    percentage_string_to_float,
)
from .transition import Transition
from ..geometry import Spacing, SpacingDimensions, clamp

if TYPE_CHECKING:
    from .._layout import Layout
    from .styles import Styles, StylesBase

from .types import DockEdge, EdgeType, AlignHorizontal, AlignVertical

BorderDefinition = (
    "Sequence[tuple[EdgeType, str | Color] | None] | tuple[EdgeType, str | Color]"
)

PropertyGetType = TypeVar("PropertyGetType")
PropertySetType = TypeVar("PropertySetType")


class GenericProperty(Generic[PropertyGetType, PropertySetType]):
    def __init__(self, default: PropertyGetType, layout: bool = False) -> None:
        self.default = default
        self.layout = layout

    def validate_value(self, value: object) -> PropertyGetType:
        """Validate the setter value

        Args:
            value (object): The value being set.

        Returns:
            PropertyType: The value to be set.
        """
        # Raise StyleValueError here
        return cast(PropertyGetType, value)

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.name = name

    def __get__(
        self, obj: StylesBase, objtype: type[StylesBase] | None = None
    ) -> PropertyGetType:
        return cast(PropertyGetType, obj.get_rule(self.name, self.default))

    def __set__(self, obj: StylesBase, value: PropertySetType | None) -> None:
        _rich_traceback_omit = True
        if value is None:
            obj.clear_rule(self.name)
            obj.refresh(layout=self.layout)
            return
        new_value = self.validate_value(value)
        if obj.set_rule(self.name, new_value):
            obj.refresh(layout=self.layout)


class IntegerProperty(GenericProperty[int, int]):
    def validate_value(self, value: object) -> int:
        if isinstance(value, (int, float)):
            return int(value)
        else:
            raise StyleValueError(f"Expected a number here, got f{value}")


class BooleanProperty(GenericProperty[bool, bool]):
    """A property that requires a True or False value."""

    def validate_value(self, value: object) -> bool:
        return bool(value)


class ScalarProperty:
    """Descriptor for getting and setting scalar properties. Scalars are numeric values with a unit, e.g. "50vh"."""

    def __init__(
        self,
        units: set[Unit] | None = None,
        percent_unit: Unit = Unit.WIDTH,
        allow_auto: bool = True,
    ) -> None:
        self.units: set[Unit] = units or {*UNIT_SYMBOL}
        self.percent_unit = percent_unit
        self.allow_auto = allow_auto
        super().__init__()

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.name = name

    def __get__(
        self, obj: StylesBase, objtype: type[StylesBase] | None = None
    ) -> Scalar | None:
        """Get the scalar property

        Args:
            obj (Styles): The ``Styles`` object
            objtype (type[Styles]): The ``Styles`` class

        Returns:
            The Scalar object or ``None`` if it's not set.
        """
        value = obj.get_rule(self.name)
        return value

    def __set__(
        self, obj: StylesBase, value: float | int | Scalar | str | None
    ) -> None:
        """Set the scalar property

        Args:
            obj (Styles): The ``Styles`` object.
            value (float | int | Scalar | str | None): The value to set the scalar property to.
                You can directly pass a float or int value, which will be interpreted with
                a default unit of Cells. You may also provide a string such as ``"50%"``,
                as you might do when writing CSS. If a string with no units is supplied,
                Cells will be used as the unit. Alternatively, you can directly supply
                a ``Scalar`` object.

        Raises:
            StyleValueError: If the value is of an invalid type, uses an invalid unit, or
                cannot be parsed for any other reason.
        """
        _rich_traceback_omit = True
        if value is None:
            obj.clear_rule(self.name)
            obj.refresh(layout=True)
            return
        if isinstance(value, (int, float)):
            new_value = Scalar(float(value), Unit.CELLS, Unit.WIDTH)
        elif isinstance(value, Scalar):
            new_value = value
        elif isinstance(value, str):
            try:
                new_value = Scalar.parse(value)
            except ScalarParseError:
                raise StyleValueError(
                    "unable to parse scalar from {value!r}",
                    help_text=scalar_help_text(
                        property_name=self.name, context="inline"
                    ),
                )
        else:
            raise StyleValueError("expected float, int, Scalar, or None")

        if (
            new_value is not None
            and new_value.unit == Unit.AUTO
            and not self.allow_auto
        ):
            raise StyleValueError("'auto' not allowed here")

        if new_value is not None and new_value.unit != Unit.AUTO:
            if new_value.unit not in self.units:
                raise StyleValueError(
                    f"{self.name} units must be one of {friendly_list(get_symbols(self.units))}"
                )
            if new_value.is_percent:
                new_value = Scalar(
                    float(new_value.value), self.percent_unit, Unit.WIDTH
                )
        if obj.set_rule(self.name, new_value):
            obj.refresh(layout=True)


class ScalarListProperty:
    def __set_name__(self, owner: Styles, name: str) -> None:
        self.name = name

    def __get__(
        self, obj: StylesBase, objtype: type[StylesBase] | None = None
    ) -> tuple[Scalar, ...] | None:
        value = obj.get_rule(self.name)
        return value

    def __set__(
        self, obj: StylesBase, value: str | Iterable[str | float] | None
    ) -> None:
        if value is None:
            obj.clear_rule(self.name)
            obj.refresh(layout=True)
            return
        parse_values: Iterable[str | float]
        if isinstance(value, str):
            parse_values = value.split()
        else:
            parse_values = value

        scalars = []
        for parse_value in parse_values:
            if isinstance(parse_value, (int, float)):
                scalars.append(Scalar.from_number(parse_value))
            else:
                scalars.append(
                    Scalar.parse(parse_value)
                    if isinstance(parse_value, str)
                    else parse_value
                )
        if obj.set_rule(self.name, tuple(scalars)):
            obj.refresh(layout=True)


class BoxProperty:
    """Descriptor for getting and setting outlines and borders along a single edge.
    For example "border-right", "outline-bottom", etc.
    """

    def __init__(self, default_color: Color) -> None:
        self._default_color = default_color

    def __set_name__(self, owner: StylesBase, name: str) -> None:
        self.name = name
        _type, edge = name.split("_")
        self._type = _type
        self.edge = edge

    def __get__(
        self, obj: StylesBase, objtype: type[StylesBase] | None = None
    ) -> tuple[EdgeType, Color]:
        """Get the box property

        Args:
            obj (Styles): The ``Styles`` object
            objtype (type[Styles]): The ``Styles`` class

        Returns:
            A ``tuple[EdgeType, Style]`` containing the string type of the box and
                it's style. Example types are "rounded", "solid", and "dashed".
        """
        box_type, color = obj.get_rule(self.name) or ("", self._default_color)
        if box_type in {"none", "hidden"}:
            box_type = ""
        return (box_type, color)

    def __set__(self, obj: Styles, border: tuple[EdgeType, str | Color] | None):
        """Set the box property

        Args:
            obj (Styles): The ``Styles`` object.
            value (tuple[EdgeType, str | Color | Style], optional): A 2-tuple containing the type of box to use,
                e.g. "dashed", and the ``Style`` to be used. You can supply the ``Style`` directly, or pass a
                ``str`` (e.g. ``"blue on #f0f0f0"`` ) or ``Color`` instead.

        Raises:
            StyleSyntaxError: If the string supplied for the color has invalid syntax.
        """
        _rich_traceback_omit = True

        if border is None:
            if obj.clear_rule(self.name):
                obj.refresh(layout=True)
        else:
            _type, color = border
            new_value = border
            if isinstance(color, str):
                try:
                    new_value = (_type, Color.parse(color))
                except ColorParseError as error:
                    raise StyleValueError(
                        str(error),
                        help_text=border_property_help_text(
                            self.name, context="inline"
                        ),
                    )
            elif isinstance(color, Color):
                new_value = (_type, color)
            current_value: tuple[str, Color] = cast(
                "tuple[str, Color]", obj.get_rule(self.name)
            )
            has_edge = current_value and current_value[0]
            new_edge = bool(_type)
            if obj.set_rule(self.name, new_value):
                obj.refresh(layout=has_edge != new_edge)


@rich.repr.auto
class Edges(NamedTuple):
    """Stores edges for border / outline."""

    top: tuple[EdgeType, Color]
    right: tuple[EdgeType, Color]
    bottom: tuple[EdgeType, Color]
    left: tuple[EdgeType, Color]

    def __bool__(self) -> bool:
        (top, _), (right, _), (bottom, _), (left, _) = self
        return bool(top or right or bottom or left)

    def __rich_repr__(self) -> rich.repr.Result:
        top, right, bottom, left = self
        if top[0]:
            yield "top", top
        if right[0]:
            yield "right", right
        if bottom[0]:
            yield "bottom", bottom
        if left[0]:
            yield "left", left

    @property
    def spacing(self) -> Spacing:
        """Get spacing created by borders.

        Returns:
            tuple[int, int, int, int]: Spacing for top, right, bottom, and left.
        """
        (top, _), (right, _), (bottom, _), (left, _) = self
        return Spacing(
            1 if top else 0,
            1 if right else 0,
            1 if bottom else 0,
            1 if left else 0,
        )


class BorderProperty:
    """Descriptor for getting and setting full borders and outlines.

    Args:
        layout (bool): True if the layout should be refreshed after setting, False otherwise.

    """

    def __init__(self, layout: bool) -> None:
        self._layout = layout

    def __set_name__(self, owner: StylesBase, name: str) -> None:
        self.name = name
        self._properties = (
            f"{name}_top",
            f"{name}_right",
            f"{name}_bottom",
            f"{name}_left",
        )

    def __get__(
        self, obj: StylesBase, objtype: type[StylesBase] | None = None
    ) -> Edges:
        """Get the border

        Args:
            obj (Styles): The ``Styles`` object
            objtype (type[Styles]): The ``Styles`` class

        Returns:
            An ``Edges`` object describing the type and style of each edge.
        """
        top, right, bottom, left = self._properties

        border = Edges(
            getattr(obj, top),
            getattr(obj, right),
            getattr(obj, bottom),
            getattr(obj, left),
        )
        return border

    def __set__(
        self,
        obj: StylesBase,
        border: BorderDefinition | None,
    ) -> None:
        """Set the border

        Args:
            obj (Styles): The ``Styles`` object.
            border (Sequence[tuple[EdgeType, str | Color | Style] | None] | tuple[EdgeType, str | Color | Style] | None):
                A ``tuple[EdgeType, str | Color | Style]`` representing the type of box to use and the ``Style`` to apply
                to the box.
                Alternatively, you can supply a sequence of these tuples and they will be applied per-edge.
                If the sequence is of length 1, all edges will be decorated according to the single element.
                If the sequence is length 2, the first ``tuple`` will be applied to the top and bottom edges.
                If the sequence is length 4, the tuples will be applied to the edges in the order: top, right, bottom, left.

        Raises:
            StyleValueError: When the supplied ``tuple`` is not of valid length (1, 2, or 4).
        """
        _rich_traceback_omit = True
        top, right, bottom, left = self._properties

        border_spacing = Edges(
            getattr(obj, top),
            getattr(obj, right),
            getattr(obj, bottom),
            getattr(obj, left),
        ).spacing

        def check_refresh() -> None:
            """Check if an update requires a layout"""
            if not self._layout:
                obj.refresh()
            else:
                layout = (
                    Edges(
                        getattr(obj, top),
                        getattr(obj, right),
                        getattr(obj, bottom),
                        getattr(obj, left),
                    ).spacing
                    != border_spacing
                )
                obj.refresh(layout=layout)

        if border is None:
            clear_rule = obj.clear_rule
            clear_rule(top)
            clear_rule(right)
            clear_rule(bottom)
            clear_rule(left)
            check_refresh()
            return
        if isinstance(border, tuple) and len(border) == 2:
            _border = normalize_border_value(border)
            setattr(obj, top, _border)
            setattr(obj, right, _border)
            setattr(obj, bottom, _border)
            setattr(obj, left, _border)
            check_refresh()
            return

        count = len(border)
        if count == 1:
            _border = normalize_border_value(border[0])
            setattr(obj, top, _border)
            setattr(obj, right, _border)
            setattr(obj, bottom, _border)
            setattr(obj, left, _border)
        elif count == 2:
            _border1, _border2 = (
                normalize_border_value(border[0]),
                normalize_border_value(border[1]),
            )
            setattr(obj, top, _border1)
            setattr(obj, bottom, _border1)
            setattr(obj, right, _border2)
            setattr(obj, left, _border2)
        elif count == 4:
            _border1, _border2, _border3, _border4 = (
                normalize_border_value(border[0]),
                normalize_border_value(border[1]),
                normalize_border_value(border[2]),
                normalize_border_value(border[3]),
            )
            setattr(obj, top, _border1)
            setattr(obj, right, _border2)
            setattr(obj, bottom, _border3)
            setattr(obj, left, _border4)
        else:
            raise StyleValueError(
                "expected 1, 2, or 4 values",
                help_text=border_property_help_text(self.name, context="inline"),
            )
        check_refresh()


class SpacingProperty:
    """Descriptor for getting and setting spacing properties (e.g. padding and margin)."""

    def __set_name__(self, owner: StylesBase, name: str) -> None:
        self.name = name

    def __get__(
        self, obj: StylesBase, objtype: type[StylesBase] | None = None
    ) -> Spacing:
        """Get the Spacing

        Args:
            obj (Styles): The ``Styles`` object
            objtype (type[Styles]): The ``Styles`` class

        Returns:
            Spacing: The Spacing. If unset, returns the null spacing ``(0, 0, 0, 0)``.
        """
        return obj.get_rule(self.name, NULL_SPACING)

    def __set__(self, obj: StylesBase, spacing: SpacingDimensions | None):
        """Set the Spacing

        Args:
            obj (Styles): The ``Styles`` object.
            style (Style | str, optional): You can supply the ``Style`` directly, or a
                string (e.g. ``"blue on #f0f0f0"``).

        Raises:
            ValueError: When the value is malformed, e.g. a ``tuple`` with a length that is
                not 1, 2, or 4.
        """
        _rich_traceback_omit = True
        if spacing is None:
            if obj.clear_rule(self.name):
                obj.refresh(layout=True)
        else:
            try:
                unpacked_spacing = Spacing.unpack(spacing)
            except ValueError as error:
                raise StyleValueError(
                    str(error),
                    help_text=spacing_wrong_number_of_values_help_text(
                        property_name=self.name,
                        num_values_supplied=len(spacing),
                        context="inline",
                    ),
                )
            if obj.set_rule(self.name, unpacked_spacing):
                obj.refresh(layout=True)


class DockProperty:
    """Descriptor for getting and setting the dock property. The dock property
    allows you to specify which edge you want to fix a Widget to.
    """

    def __get__(
        self, obj: StylesBase, objtype: type[StylesBase] | None = None
    ) -> DockEdge:
        """Get the Dock property

        Args:
            obj (Styles): The ``Styles`` object.
            objtype (type[Styles]): The ``Styles`` class.

        Returns:
            str: The dock name as a string, or "" if the rule is not set.
        """
        return cast(DockEdge, obj.get_rule("dock", ""))

    def __set__(self, obj: Styles, dock_name: str | None):
        """Set the Dock property

        Args:
            obj (Styles): The ``Styles`` object
            dock_name (str | None): The name of the dock to attach this widget to
        """
        _rich_traceback_omit = True
        if obj.set_rule("dock", dock_name):
            obj.refresh(layout=True)


class LayoutProperty:
    """Descriptor for getting and setting layout."""

    def __set_name__(self, owner: StylesBase, name: str) -> None:
        self.name = name

    def __get__(
        self, obj: StylesBase, objtype: type[StylesBase] | None = None
    ) -> Layout | None:
        """
        Args:
            obj (Styles): The Styles object
            objtype (type[Styles]): The Styles class
        Returns:
            The ``Layout`` object.
        """
        return obj.get_rule(self.name)

    def __set__(self, obj: StylesBase, layout: str | Layout | None):
        """
        Args:
            obj (Styles): The Styles object.
            layout (str | Layout): The layout to use. You can supply the name of the layout
                or a ``Layout`` object.
        """

        from ..layouts.factory import (
            get_layout,
            Layout,
            MissingLayout,
        )  # Prevents circular import

        _rich_traceback_omit = True
        if layout is None:
            if obj.clear_rule("layout"):
                obj.refresh(layout=True)
        elif isinstance(layout, Layout):
            if obj.set_rule("layout", layout):
                obj.refresh(layout=True)
        else:
            try:
                layout_object = get_layout(layout)
            except MissingLayout as error:
                raise StyleValueError(
                    str(error),
                    help_text=layout_property_help_text(self.name, context="inline"),
                )
            if obj.set_rule("layout", layout_object):
                obj.refresh(layout=True)


class OffsetProperty:
    """Descriptor for getting and setting the offset property.
    Offset consists of two values, x and y, that a widget's position
    will be adjusted by before it is rendered.
    """

    def __set_name__(self, owner: StylesBase, name: str) -> None:
        self.name = name

    def __get__(
        self, obj: StylesBase, objtype: type[StylesBase] | None = None
    ) -> ScalarOffset:
        """Get the offset

        Args:
            obj (Styles): The ``Styles`` object.
            objtype (type[Styles]): The ``Styles`` class.

        Returns:
            ScalarOffset: The ``ScalarOffset`` indicating the adjustment that
                will be made to widget position prior to it being rendered.
        """
        return obj.get_rule(self.name, ScalarOffset.null())

    def __set__(
        self, obj: StylesBase, offset: tuple[int | str, int | str] | ScalarOffset | None
    ):
        """Set the offset

        Args:
            obj: The ``Styles`` class
            offset: A ScalarOffset object, or a 2-tuple of the form ``(x, y)`` indicating
                the x and y offsets. When the ``tuple`` form is used, x and y can be specified
                as either ``int`` or ``str``. The string format allows you to also specify
                any valid scalar unit e.g. ``("0.5vw", "0.5vh")``.

        Raises:
            ScalarParseError: If any of the string values supplied in the 2-tuple cannot
                be parsed into a Scalar. For example, if you specify a non-existent unit.
        """
        _rich_traceback_omit = True
        if offset is None:
            if obj.clear_rule(self.name):
                obj.refresh(layout=True)
        elif isinstance(offset, ScalarOffset):
            if obj.set_rule(self.name, offset):
                obj.refresh(layout=True)
        else:
            x, y = offset

            try:
                scalar_x = (
                    Scalar.parse(x, Unit.WIDTH)
                    if isinstance(x, str)
                    else Scalar(float(x), Unit.CELLS, Unit.WIDTH)
                )
                scalar_y = (
                    Scalar.parse(y, Unit.HEIGHT)
                    if isinstance(y, str)
                    else Scalar(float(y), Unit.CELLS, Unit.HEIGHT)
                )
            except ScalarParseError as error:
                raise StyleValueError(
                    str(error), help_text=offset_property_help_text(context="inline")
                )

            _offset = ScalarOffset(scalar_x, scalar_y)

            if obj.set_rule(self.name, _offset):
                obj.refresh(layout=True)


class StringEnumProperty:
    """Descriptor for getting and setting string properties and ensuring that the set
    value belongs in the set of valid values.
    """

    def __init__(self, valid_values: set[str], default: str, layout=False) -> None:
        self._valid_values = valid_values
        self._default = default
        self._layout = layout

    def __set_name__(self, owner: StylesBase, name: str) -> None:
        self.name = name

    def __get__(self, obj: StylesBase, objtype: type[StylesBase] | None = None) -> str:
        """Get the string property, or the default value if it's not set

        Args:
            obj (Styles): The ``Styles`` object.
            objtype (type[Styles]): The ``Styles`` class.

        Returns:
            str: The string property value
        """
        return obj.get_rule(self.name, self._default)

    def __set__(self, obj: StylesBase, value: str | None = None):
        """Set the string property and ensure it is in the set of allowed values.

        Args:
            obj (Styles): The ``Styles`` object
            value (str, optional): The string value to set the property to.

        Raises:
            StyleValueError: If the value is not in the set of valid values.
        """
        _rich_traceback_omit = True
        if value is None:
            if obj.clear_rule(self.name):
                obj.refresh(layout=self._layout)
        else:
            if value not in self._valid_values:
                raise StyleValueError(
                    f"{self.name} must be one of {friendly_list(self._valid_values)} (received {value!r})",
                    help_text=string_enum_help_text(
                        self.name,
                        valid_values=list(self._valid_values),
                        context="inline",
                    ),
                )
            if obj.set_rule(self.name, value):
                obj.refresh(layout=self._layout)


class NameProperty:
    """Descriptor for getting and setting name properties."""

    def __set_name__(self, owner: StylesBase, name: str) -> None:
        self.name = name

    def __get__(self, obj: StylesBase, objtype: type[StylesBase] | None) -> str:
        """Get the name property

        Args:
            obj (Styles): The ``Styles`` object.
            objtype (type[Styles]): The ``Styles`` class.

        Returns:
            str: The name
        """
        return obj.get_rule(self.name, "")

    def __set__(self, obj: StylesBase, name: str | None):
        """Set the name property

        Args:
            obj: The ``Styles`` object
            name: The name to set the property to

        Raises:
            StyleTypeError: If the value is not a ``str``.
        """
        _rich_traceback_omit = True
        if name is None:
            if obj.clear_rule(self.name):
                obj.refresh(layout=True)
        else:
            if not isinstance(name, str):
                raise StyleTypeError(f"{self.name} must be a str")
            if obj.set_rule(self.name, name):
                obj.refresh(layout=True)


class NameListProperty:
    def __set_name__(self, owner: StylesBase, name: str) -> None:
        self.name = name

    def __get__(
        self, obj: StylesBase, objtype: type[StylesBase] | None = None
    ) -> tuple[str, ...]:
        return cast("tuple[str, ...]", obj.get_rule(self.name, ()))

    def __set__(self, obj: StylesBase, names: str | tuple[str] | None = None):
        _rich_traceback_omit = True
        if names is None:
            if obj.clear_rule(self.name):
                obj.refresh(layout=True)
        elif isinstance(names, str):
            if obj.set_rule(
                self.name, tuple(name.strip().lower() for name in names.split(" "))
            ):
                obj.refresh(layout=True)
        elif isinstance(names, tuple):
            if obj.set_rule(self.name, names):
                obj.refresh(layout=True)


class ColorProperty:
    """Descriptor for getting and setting color properties."""

    def __init__(self, default_color: Color | str, background: bool = False) -> None:
        self._default_color = Color.parse(default_color)
        self._is_background = background

    def __set_name__(self, owner: StylesBase, name: str) -> None:
        self.name = name

    def __get__(
        self, obj: StylesBase, objtype: type[StylesBase] | None = None
    ) -> Color:
        """Get a ``Color``.

        Args:
            obj (Styles): The ``Styles`` object.
            objtype (type[Styles]): The ``Styles`` class.

        Returns:
            Color: The Color
        """
        return cast(Color, obj.get_rule(self.name, self._default_color))

    def __set__(self, obj: StylesBase, color: Color | str | None):
        """Set the Color

        Args:
            obj (Styles): The ``Styles`` object
            color (Color | str | None): The color to set. Pass a ``Color`` instance directly,
                or pass a ``str`` which will be parsed into a color (e.g. ``"red""``, ``"rgb(20, 50, 80)"``,
                ``"#f4e32d"``).

        Raises:
            ColorParseError: When the color string is invalid.
        """
        _rich_traceback_omit = True
        if color is None:
            if obj.clear_rule(self.name):
                obj.refresh(children=self._is_background)
        elif isinstance(color, Color):
            if obj.set_rule(self.name, color):
                obj.refresh(children=self._is_background)

        elif isinstance(color, str):
            alpha = 1.0
            parsed_color = Color(255, 255, 255)
            for token in color.split():
                if token.endswith("%"):
                    try:
                        alpha = percentage_string_to_float(token)
                    except ValueError:
                        raise StyleValueError(f"invalid percentage value '{token}'")
                    continue
                try:
                    parsed_color = Color.parse(token)
                except ColorParseError as error:
                    raise StyleValueError(
                        f"Invalid color value '{token}'",
                        help_text=color_property_help_text(
                            self.name, context="inline", error=error
                        ),
                    )
            parsed_color = parsed_color.with_alpha(alpha)
            if obj.set_rule(self.name, parsed_color):
                obj.refresh(children=self._is_background)
        else:
            raise StyleValueError(f"Invalid color value {color}")


class StyleFlagsProperty:
    """Descriptor for getting and set style flag properties (e.g. ``bold italic underline``)."""

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.name = name

    def __get__(
        self, obj: StylesBase, objtype: type[StylesBase] | None = None
    ) -> Style:
        """Get the ``Style``

        Args:
            obj (Styles): The ``Styles`` object.
            objtype (type[Styles]): The ``Styles`` class.

        Returns:
            Style: The ``Style`` object
        """
        return obj.get_rule(self.name, Style.null())

    def __set__(self, obj: StylesBase, style_flags: Style | str | None):
        """Set the style using a style flag string

        Args:
            obj (Styles): The ``Styles`` object.
            style_flags (str, optional): The style flags to set as a string. For example,
                ``"bold italic"``.

        Raises:
            StyleValueError: If the value is an invalid style flag
        """
        _rich_traceback_omit = True
        if style_flags is None:
            if obj.clear_rule(self.name):
                obj.refresh()
        elif isinstance(style_flags, Style):
            if obj.set_rule(self.name, style_flags):
                obj.refresh()
        else:
            words = [word.strip() for word in style_flags.split(" ")]
            valid_word = VALID_STYLE_FLAGS.__contains__
            for word in words:
                if not valid_word(word):
                    raise StyleValueError(
                        f"unknown word {word!r} in style flags",
                        help_text=style_flags_property_help_text(
                            self.name, word, context="inline"
                        ),
                    )
            style = Style.parse(style_flags)
            if obj.set_rule(self.name, style):
                obj.refresh()


class TransitionsProperty:
    """Descriptor for getting transitions properties"""

    def __get__(
        self, obj: StylesBase, objtype: type[StylesBase] | None = None
    ) -> dict[str, Transition]:
        """Get a mapping of properties to the transitions applied to them.

        Args:
            obj (Styles): The ``Styles`` object.
            objtype (type[Styles]): The ``Styles`` class.

        Returns:
            dict[str, Transition]: A ``dict`` mapping property names to the ``Transition`` applied to them.
                e.g. ``{"offset": Transition(...), ...}``. If no transitions have been set, an empty ``dict``
                is returned.
        """
        return obj.get_rule("transitions", {})

    def __set__(self, obj: Styles, transitions: dict[str, Transition] | None) -> None:
        _rich_traceback_omit = True
        if transitions is None:
            obj.clear_rule("transitions")
        else:
            obj.set_rule("transitions", transitions.copy())


class FractionalProperty:
    """Property that can be set either as a float (e.g. 0.1) or a
    string percentage (e.g. '10%'). Values will be clamped to the range (0, 1).
    """

    def __init__(self, default: float = 1.0):
        self.default = default

    def __set_name__(self, owner: StylesBase, name: str) -> None:
        self.name = name

    def __get__(self, obj: StylesBase, type: type[StylesBase]) -> float:
        """Get the property value as a float between 0 and 1

        Args:
            obj (Styles): The ``Styles`` object.
            objtype (type[Styles]): The ``Styles`` class.

        Returns:
            float: The value of the property (in the range (0, 1))
        """
        return cast(float, obj.get_rule(self.name, self.default))

    def __set__(self, obj: StylesBase, value: float | str | None) -> None:
        """Set the property value, clamping it between 0 and 1.

        Args:
            obj (Styles): The Styles object.
            value (float|str|None): The value to set as a float between 0 and 1, or
                as a percentage string such as '10%'.
        """
        _rich_traceback_omit = True
        name = self.name
        if value is None:
            if obj.clear_rule(name):
                obj.refresh()
            return

        if isinstance(value, float):
            float_value = value
        elif isinstance(value, str) and value.endswith("%"):
            float_value = float(Scalar.parse(value).value) / 100
        else:
            raise StyleValueError(
                f"{self.name} must be a str (e.g. '10%') or a float (e.g. 0.1)",
                help_text=fractional_property_help_text(name, context="inline"),
            )
        if obj.set_rule(name, clamp(float_value, 0, 1)):
            obj.refresh()


class AlignProperty:
    """Combines the horizontal and vertical alignment properties in to a single property."""

    def __set_name__(self, owner: StylesBase, name: str) -> None:
        self.horizontal = f"{name}_horizontal"
        self.vertical = f"{name}_vertical"

    def __get__(
        self, obj: StylesBase, type: type[StylesBase]
    ) -> tuple[AlignHorizontal, AlignVertical]:
        horizontal = getattr(obj, self.horizontal)
        vertical = getattr(obj, self.vertical)
        return (horizontal, vertical)

    def __set__(
        self, obj: StylesBase, value: tuple[AlignHorizontal, AlignVertical]
    ) -> None:
        horizontal, vertical = value
        setattr(obj, self.horizontal, horizontal)
        setattr(obj, self.vertical, vertical)
