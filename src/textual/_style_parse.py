from textual._context import active_app
from textual.color import Color
from textual.css.parse import substitute_references
from textual.css.tokenize import tokenize_style, tokenize_values
from textual.style import Style

STYLES = {"bold", "dim", "italic", "underline", "reverse", "strike"}
STYLE_ABBREVIATIONS = {
    "b": "bold",
    "d": "dim",
    "i": "italic",
    "u": "underline",
    "r": "reverse",
    "s": "strike",
}


def style_parse(style_text: str, variables: dict[str, str] | None) -> Style:
    """Parse a Textual style definition.

    Note that variables should be `None` when called within a running app. This is so that
    this method can use a style cache from the app. Supply a variables dict only for testing.

    Args:
        style_text: String containing style definition.
        variables: Variables to use, or `None` for variables from active app.

    Returns:
        Style instance.
    """
    styles: dict[str, bool | None] = {style: None for style in STYLES}

    color: Color | None = None
    background: Color | None = None
    is_background: bool = False
    style_state: bool = True

    data: dict[str, str] = {}
    meta: dict[str, object] = {}

    if variables is None:
        try:
            app = active_app.get()
        except LookupError:
            reference_tokens = {}
        else:
            reference_tokens = app.stylesheet._variable_tokens
    else:
        reference_tokens = tokenize_values(variables)

    for token in substitute_references(
        tokenize_style(
            style_text,
            read_from=("inline style", ""),
        ),
        reference_tokens,
    ):
        name = token.name
        value = token.value

        if name == "color":
            token_color = Color.parse(value)
            if is_background:
                background = token_color
            else:
                color = token_color
        elif name == "token":
            if value == "not":
                style_state = False
            elif value == "auto":
                if is_background:
                    background = Color.automatic()
                else:
                    color = Color.automatic()
            elif value == "on":
                is_background = True
            elif value == "link":
                data["link"] = style_text[token.end[-1] :]
                break
            elif value in STYLES:
                styles[value] = style_state
                style_state = True
            elif value in STYLE_ABBREVIATIONS:
                styles[STYLE_ABBREVIATIONS[value]] = style_state
                style_state = True
            else:
                if is_background:
                    background = Color.parse(value)
                else:
                    color = Color.parse(value)
        elif name in ("key_value", "key_value_quote", "key_value_double_quote"):
            key, _, value = value.partition("=")
            if name in ("key_value_quote", "key_value_double_quote"):
                value = value[1:-1]
            if key.startswith("@"):
                meta[key[1:]] = value
            else:
                data[key] = value
        elif name == "percent" or (name == "scalar" and value.endswith("%")):
            percent = int(value.rstrip("%")) / 100.0
            if is_background:
                if background is not None:
                    background = background.multiply_alpha(percent)
            else:
                if color is not None:
                    color = color.multiply_alpha(percent)

    parsed_style = Style(background, color, link=data.get("link", None), **styles)
    if meta:
        parsed_style += Style.from_meta(meta)
    return parsed_style


if __name__ == "__main__":
    variables = {"accent": "red"}
    print(style_parse("blue 20%", None))

    # print(
    #     style_parse(
    #         "bold not underline red $accent rgba(10,20,30,3) on black not italic link=https://www.willmcgugan.com",
    #         variables,
    #     )
    # )

    # print(style_parse("auto on ansi_red s 20% @click=app.bell('hello')", variables))
