"""
Style properties are descriptors which allow the ``Styles`` object to accept different types when
setting attributes. This gives the developer more freedom in how to express style information.

Descriptors also play nicely with Mypy, which is aware that attributes can have different types
when setting and getting.

"""

from __future__ import annotations


from typing import Iterable, NamedTuple, Sequence, TYPE_CHECKING

import rich.repr
from rich.color import Color
from rich.style import Style

from ._error_tools import friendly_list
from .constants import NULL_SPACING
from .errors import StyleTypeError, StyleValueError
from .scalar import (
    get_symbols,
    UNIT_SYMBOL,
    Unit,
    Scalar,
    ScalarOffset,
    ScalarParseError,
)
from .transition import Transition
from ..geometry import Spacing, SpacingDimensions

if TYPE_CHECKING:
    from ..layout import Layout
    from .styles import Styles
    from .styles import DockGroup

from .._box import BoxType

BorderDefinition = (
    Sequence[tuple[BoxType, str | Color | Style] | None]
    | tuple[BoxType, str | Color | Style]
)


class ScalarProperty:
    """Descriptor for getting and setting scalar properties. Scalars are numeric values with a unit, e.g. "50vh"."""

    def __init__(
        self, units: set[Unit] | None = None, percent_unit: Unit = Unit.WIDTH
    ) -> None:
        self.units: set[Unit] = units or {*UNIT_SYMBOL}
        self.percent_unit = percent_unit
        super().__init__()

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.name = name

    def __get__(
        self, obj: Styles, objtype: type[Styles] | None = None
    ) -> Scalar | None:
        """Get the scalar property

        Args:
            obj (Styles): The ``Styles`` object
            objtype (type[Styles]): The ``Styles`` class

        Returns:
            The Scalar object or ``None`` if it's not set.
        """
        value = obj._rules.get(self.name)
        return value

    def __set__(self, obj: Styles, value: float | Scalar | str | None) -> None:
        """Set the scalar property

        Args:
            obj (Styles): The ``Styles`` object.
            value (float | Scalar | str | None): The value to set the scalar property to.
                You can directly pass a float value, which will be interpreted with
                a default unit of Cells. You may also provide a string such as ``"50%"``,
                as you might do when writing CSS. If a string with no units is supplied,
                Cells will be used as the unit. Alternatively, you can directly supply
                a ``Scalar`` object.

        Raises:
            StyleValueError: If the value is of an invalid type, uses an invalid unit, or
                cannot be parsed for any other reason.
        """
        if value is None:
            obj._rules.pop(self.name, None)
            return
        if isinstance(value, float):
            new_value = Scalar(float(value), Unit.CELLS, Unit.WIDTH)
        elif isinstance(value, Scalar):
            new_value = value
        elif isinstance(value, str):
            try:
                new_value = Scalar.parse(value)
            except ScalarParseError:
                raise StyleValueError("unable to parse scalar from {value!r}")
        else:
            raise StyleValueError("expected float, Scalar, or None")
        if new_value is not None and new_value.unit not in self.units:
            raise StyleValueError(
                f"{self.name} units must be one of {friendly_list(get_symbols(self.units))}"
            )
        if new_value is not None and new_value.is_percent:
            new_value = Scalar(float(new_value.value), self.percent_unit, Unit.WIDTH)
        obj._rules[self.name] = new_value
        obj.refresh()


class BoxProperty:
    """Descriptor for getting and setting outlines and borders along a single edge.
    For example "border-right", "outline-bottom", etc.
    """

    DEFAULT = ("", Style())

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.name = name
        _type, edge = name.split("_")
        self._type = _type
        self.edge = edge

    def __get__(
        self, obj: Styles, objtype: type[Styles] | None = None
    ) -> tuple[BoxType, Style]:
        """Get the box property

        Args:
            obj (Styles): The ``Styles`` object
            objtype (type[Styles]): The ``Styles`` class

        Returns:
            A ``tuple[BoxType, Style]`` containing the string type of the box and
                it's style. Example types are "rounded", "solid", and "dashed".
        """
        value = obj._rules.get(self.name) or self.DEFAULT
        return value

    def __set__(self, obj: Styles, border: tuple[BoxType, str | Color | Style] | None):
        """Set the box property

        Args:
            obj (Styles): The ``Styles`` object.
            value (tuple[BoxType, str | Color | Style], optional): A 2-tuple containing the type of box to use,
                e.g. "dashed", and the ``Style`` to be used. You can supply the ``Style`` directly, or pass a
                ``str`` (e.g. ``"blue on #f0f0f0"`` ) or ``Color`` instead.

        Raises:
            StyleSyntaxError: If the string supplied for the color has invalid syntax.
        """
        if border is None:
            obj._rules.pop(self.name, None)
        else:
            _type, color = border
            if isinstance(color, str):
                new_value = (_type, Style.parse(color))
            elif isinstance(color, Color):
                new_value = (_type, Style.from_color(color))
            else:
                new_value = (_type, Style.from_color(Color.parse(color)))
            obj._rules[self.name] = new_value
        obj.refresh()


@rich.repr.auto
class Edges(NamedTuple):
    """Stores edges for border / outline."""

    top: tuple[BoxType, Style]
    right: tuple[BoxType, Style]
    bottom: tuple[BoxType, Style]
    left: tuple[BoxType, Style]

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

    def spacing(self) -> tuple[int, int, int, int]:
        """Get spacing created by borders.

        Returns:
            tuple[int, int, int, int]: Spacing for top, right, bottom, and left.
        """
        top, right, bottom, left = self
        return (
            1 if top[0] else 0,
            1 if right[0] else 0,
            1 if bottom[0] else 0,
            1 if left[0] else 0,
        )


class BorderProperty:
    """Descriptor for getting and setting full borders and outlines."""

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.name = name
        self._properties = (
            f"{name}_top",
            f"{name}_right",
            f"{name}_bottom",
            f"{name}_left",
        )

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> Edges:
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
        obj: Styles,
        border: BorderDefinition | None,
    ) -> None:
        """Set the border

        Args:
            obj (Styles): The ``Styles`` object.
            border (Sequence[tuple[BoxType, str | Color | Style] | None] | tuple[BoxType, str | Color | Style] | None):
                A ``tuple[BoxType, str | Color | Style]`` representing the type of box to use and the ``Style`` to apply
                to the box.
                Alternatively, you can supply a sequence of these tuples and they will be applied per-edge.
                If the sequence is of length 1, all edges will be decorated according to the single element.
                If the sequence is length 2, the first ``tuple`` will be applied to the top and bottom edges.
                If the sequence is length 4, the tuples will be applied to the edges in the order: top, right, bottom, left.

        Raises:
            StyleValueError: When the supplied ``tuple`` is not of valid length (1, 2, or 4).
        """
        top, right, bottom, left = self._properties
        obj.refresh()
        if border is None:
            setattr(obj, top, None)
            setattr(obj, right, None)
            setattr(obj, bottom, None)
            setattr(obj, left, None)
            return
        if isinstance(border, tuple):
            setattr(obj, top, border)
            setattr(obj, right, border)
            setattr(obj, bottom, border)
            setattr(obj, left, border)
            return
        count = len(border)
        if count == 1:
            _border = border[0]
            setattr(obj, top, _border)
            setattr(obj, right, _border)
            setattr(obj, bottom, _border)
            setattr(obj, left, _border)
        elif count == 2:
            _border1, _border2 = border
            setattr(obj, top, _border1)
            setattr(obj, right, _border1)
            setattr(obj, bottom, _border2)
            setattr(obj, left, _border2)
        elif count == 4:
            _border1, _border2, _border3, _border4 = border
            setattr(obj, top, _border1)
            setattr(obj, right, _border2)
            setattr(obj, bottom, _border3)
            setattr(obj, left, _border4)
        else:
            raise StyleValueError("expected 1, 2, or 4 values")


class StyleProperty:
    """Descriptor for getting and setting full borders and outlines."""

    DEFAULT_STYLE = Style()

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> Style:
        """Get the Style

        Args:
            obj (Styles): The ``Styles`` object
            objtype (type[Styles]): The ``Styles`` class

        Returns:
            A ``Style`` object.
        """
        has_rule = obj.has_rule

        style = Style.from_color(
            obj.text_color if has_rule("text_color") else None,
            obj.text_background if has_rule("text_background") else None,
        )
        if has_rule("text_style"):
            style += obj.text_style

        return style

    def __set__(self, obj: Styles, style: Style | str | None):
        """Set the Style

        Args:
            obj (Styles): The ``Styles`` object.
            style (Style | str, optional): You can supply the ``Style`` directly, or a
                string (e.g. ``"blue on #f0f0f0"``).

        Raises:
            StyleSyntaxError: When the supplied style string has invalid syntax.
        """
        obj.refresh()
        rules_set = obj._rules.__setitem__
        if style is None:
            rules = obj._rules
            rules.pop("text_color")
            rules.pop("text_background")
            rules.pop("text_style")
        elif isinstance(style, Style):
            if style.color:
                rules_set("text_color", style.color)
            if style.bgcolor:
                rules_set("text_background", style.bgcolor)
            if style.without_color:
                rules_set("text_style", style.without_color)
        elif isinstance(style, str):
            new_style = Style.parse(style)
            if new_style.color:
                rules_set("text_color", new_style.color)
            if new_style.bgcolor:
                rules_set("text_background", new_style.bgcolor)
            if new_style.without_color:
                rules_set("text_style", new_style.without_color)


class SpacingProperty:
    """Descriptor for getting and setting spacing properties (e.g. padding and margin)."""

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.name = name

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> Spacing:
        """Get the Spacing

        Args:
            obj (Styles): The ``Styles`` object
            objtype (type[Styles]): The ``Styles`` class

        Returns:
            Spacing: The Spacing. If unset, returns the null spacing ``(0, 0, 0, 0)``.
        """
        return obj._rules.get(self.name, NULL_SPACING)

    def __set__(self, obj: Styles, spacing: SpacingDimensions | None):
        """Set the Spacing

        Args:
            obj (Styles): The ``Styles`` object.
            style (Style | str, optional): You can supply the ``Style`` directly, or a
                string (e.g. ``"blue on #f0f0f0"``).

        Raises:
            ValueError: When the value is malformed, e.g. a ``tuple`` with a length that is
                not 1, 2, or 4.
        """
        obj.refresh(layout=True)
        if spacing is None:
            obj._rules.pop(self.name)
        else:
            obj._rules[self.name] = Spacing.unpack(spacing)


class DocksProperty:
    """Descriptor for getting and setting the docks property. This property
    is used to define docks and their location on screen.
    """

    def __get__(
        self, obj: Styles, objtype: type[Styles] | None = None
    ) -> tuple[DockGroup, ...]:
        """Get the Docks property

        Args:
            obj (Styles): The ``Styles`` object.
            objtype (type[Styles]): The ``Styles`` class.

        Returns:
            tuple[DockGroup, ...]: A ``tuple`` containing the defined docks.
        """
        return obj._rules.get("docks") or ()

    def __set__(self, obj: Styles, docks: Iterable[DockGroup] | None):
        """Set the Docks property

        Args:
            obj (Styles): The ``Styles`` object.
            docks (Iterable[DockGroup]): Iterable of DockGroups
        """
        obj.refresh(layout=True)
        if docks is None:
            obj._rules.pop("docks")
        else:
            obj._rules["docks"] = tuple(docks)


class DockProperty:
    """Descriptor for getting and setting the dock property. The dock property
    allows you to specify which dock you wish a Widget to be attached to. This
    should be used in conjunction with the "docks" property which lets you define
    the docks themselves, and where they are located on screen.
    """

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> str:
        """Get the Dock property

        Args:
            obj (Styles): The ``Styles`` object.
            objtype (type[Styles]): The ``Styles`` class.

        Returns:
            str: The dock name as a string, or "" if the rule is not set.
        """
        return obj._rules.get("dock") or "_default"

    def __set__(self, obj: Styles, spacing: str | None):
        """Set the Dock property

        Args:
            obj (Styles): The ``Styles`` object
            spacing (str | None): The spacing to use.
        """
        obj.refresh(layout=True)
        if spacing is None:
            obj._rules.pop("dock")
        else:
            obj._rules["dock"] = spacing


class LayoutProperty:
    """Descriptor for getting and setting layout."""

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.name = name

    def __get__(
        self, obj: Styles, objtype: type[Styles] | None = None
    ) -> Layout | None:
        """
        Args:
            obj (Styles): The Styles object
            objtype (type[Styles]): The Styles class
        Returns:
            The ``Layout`` object.
        """
        return obj._rules.get(self.name)

    def __set__(self, obj: Styles, layout: str | Layout | None):
        """
        Args:
            obj (Styles): The Styles object.
            layout (str | Layout): The layout to use. You can supply a the name of the layout
                or a ``Layout`` object.
        """

        from ..layouts.factory import get_layout, Layout  # Prevents circular import

        obj.refresh(layout=True)

        if layout is None:
            obj._rules.pop("layout")
        elif isinstance(layout, Layout):
            obj._rules["layout"] = layout
        else:
            obj._rules["layout"] = get_layout(layout)


class OffsetProperty:
    """Descriptor for getting and setting the offset property.
    Offset consists of two values, x and y, that a widget's position
    will be adjusted by before it is rendered.
    """

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.name = name

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> ScalarOffset:
        """Get the offset

        Args:
            obj (Styles): The ``Styles`` object.
            objtype (type[Styles]): The ``Styles`` class.

        Returns:
            ScalarOffset: The ``ScalarOffset`` indicating the adjustment that
                will be made to widget position prior to it being rendered.
        """
        return obj._rules.get(self.name, ScalarOffset.null())

    def __set__(
        self, obj: Styles, offset: tuple[int | str, int | str] | ScalarOffset | None
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
                be parsed into a Scalar. For example, if you specify an non-existent unit.
        """
        obj.refresh(layout=True)
        if offset is None:
            obj._rules.pop(self.name, None)
        elif isinstance(offset, ScalarOffset):
            obj._rules[self.name] = offset
        else:
            x, y = offset
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
            _offset = ScalarOffset(scalar_x, scalar_y)
            obj._rules[self.name] = _offset


class StringEnumProperty:
    """Descriptor for getting and setting string properties and ensuring that the set
    value belongs in the set of valid values.
    """

    def __init__(self, valid_values: set[str], default: str) -> None:
        self._valid_values = valid_values
        self._default = default

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.name = name

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> str:
        """Get the string property, or the default value if it's not set

        Args:
            obj (Styles): The ``Styles`` object.
            objtype (type[Styles]): The ``Styles`` class.

        Returns:
            str: The string property value
        """
        return obj._rules.get(self.name, self._default)

    def __set__(self, obj: Styles, value: str | None = None):
        """Set the string property and ensure it is in the set of allowed values.

        Args:
            obj (Styles): The ``Styles`` object
            value (str, optional): The string value to set the property to.

        Raises:
            StyleValueError: If the value is not in the set of valid values.
        """
        obj.refresh()
        if value is None:
            obj._rules.pop(self.name, None)
        else:
            if value not in self._valid_values:
                raise StyleValueError(
                    f"{self.name} must be one of {friendly_list(self._valid_values)}"
                )
            obj._rules[self.name] = value


class NameProperty:
    """Descriptor for getting and setting name properties."""

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.name = name

    def __get__(self, obj: Styles, objtype: type[Styles] | None) -> str:
        """Get the name property

        Args:
            obj (Styles): The ``Styles`` object.
            objtype (type[Styles]): The ``Styles`` class.

        Returns:
            str: The name
        """
        return obj._rules.get(self.name, "")

    def __set__(self, obj: Styles, name: str | None):
        """Set the name property

        Args:
            obj: The ``Styles`` object
            name: The name to set the property to

        Raises:
            StyleTypeError: If the value is not a ``str``.
        """
        obj.refresh(layout=True)
        if name is None:
            obj._rules.pop(self.name, None)
        else:
            if not isinstance(name, str):
                raise StyleTypeError(f"{self._name} must be a str")
            obj._rules[self.name] = name


class NameListProperty:
    def __set_name__(self, owner: Styles, name: str) -> None:
        self.name = name

    def __get__(
        self, obj: Styles, objtype: type[Styles] | None = None
    ) -> tuple[str, ...]:
        return obj._rules.get(self.name, ())

    def __set__(
        self, obj: Styles, names: str | tuple[str] | None = None
    ) -> str | tuple[str] | None:
        obj.refresh(layout=True)
        if names is None:
            obj._rules.pop(self.name, None)
        elif isinstance(names, str):
            obj._rules[self.name] = tuple(
                name.strip().lower() for name in names.split(" ")
            )
        elif isinstance(names, tuple):
            obj._rules[self.name] = names


class ColorProperty:
    """Descriptor for getting and setting color properties."""

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.name = name

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> Color:
        """Get the ``Color``, or ``Color.default()`` if no color is set.

        Args:
            obj (Styles): The ``Styles`` object.
            objtype (type[Styles]): The ``Styles`` class.

        Returns:
            Color: The Color
        """
        return obj._rules.get(self.name) or Color.default()

    def __set__(self, obj: Styles, color: Color | str | None):
        """Set the Color

        Args:
            obj (Styles): The ``Styles`` object
            color (Color | str | None): The color to set. Pass a ``Color`` instance directly,
                or pass a ``str`` which will be parsed into a color (e.g. ``"red""``, ``"rgb(20, 50, 80)"``,
                ``"#f4e32d"``).

        Raises:
            ColorParseError: When the color string is invalid.
        """
        obj.refresh()
        if color is None:
            obj._rules.pop(self.name, None)
        elif isinstance(color, Color):
            obj._rules[self.name] = color
        elif isinstance(color, str):
            obj._rules[self.name] = Color.parse(color)


class StyleFlagsProperty:
    """Descriptor for getting and set style flag properties (e.g. ``bold italic underline``)."""

    _VALID_PROPERTIES = {
        "not",
        "bold",
        "italic",
        "underline",
        "overline",
        "strike",
        "b",
        "i",
        "u",
        "o",
    }

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.name = name

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> Style:
        """Get the ``Style``

        Args:
            obj (Styles): The ``Styles`` object.
            objtype (type[Styles]): The ``Styles`` class.

        Returns:
            Style: The ``Style`` object
        """
        return obj._rules.get(self.name, Style.null())

    def __set__(self, obj: Styles, style_flags: str | None):
        """Set the style using a style flag string

        Args:
            obj (Styles): The ``Styles`` object.
            style_flags (str, optional): The style flags to set as a string. For example,
                ``"bold italic"``.

        Raises:
            StyleValueError: If the value is an invalid style flag
        """
        obj.refresh()
        if style_flags is None:
            obj._styles.pop(self.name, None)
        else:
            words = [word.strip() for word in style_flags.split(" ")]
            valid_word = self._VALID_PROPERTIES.__contains__
            for word in words:
                if not valid_word(word):
                    raise StyleValueError(
                        f"unknown word {word!r} in style flags, "
                        f"valid values are {friendly_list(self._VALID_PROPERTIES)}"
                    )
            style = Style.parse(style_flags)
            obj._rules[self.name] = style


class TransitionsProperty:
    """Descriptor for getting transitions properties"""

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.name = name

    def __get__(
        self, obj: Styles, objtype: type[Styles] | None = None
    ) -> dict[str, Transition]:
        """Get a mapping of properties to the the transitions applied to them.

        Args:
            obj (Styles): The ``Styles`` object.
            objtype (type[Styles]): The ``Styles`` class.

        Returns:
            dict[str, Transition]: A ``dict`` mapping property names to the ``Transition`` applied to them.
                e.g. ``{"offset": Transition(...), ...}``. If no transitions have been set, an empty ``dict``
                is returned.
        """
        return obj._rules.get(self.name, {})
