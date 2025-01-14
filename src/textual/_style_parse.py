from textual.color import TRANSPARENT, Color
from textual.css.parse import substitute_references
from textual.css.tokenize import tokenize_style, tokenize_values
from textual.visual import Style

STYLES = {"bold", "dim", "italic", "underline", "reverse", "strike"}


def style_parse(style_text: str, variables: dict[str, str]) -> Style:
    styles: dict[str, bool | None] = {style: None for style in STYLES}

    color: Color = TRANSPARENT
    background: Color = TRANSPARENT
    is_background: bool = False
    style_state: bool = True

    data: dict[str, str] = {}
    meta: dict[str, object] = {}

    reference_tokens = tokenize_values(variables)

    for token in substitute_references(
        tokenize_style(style_text, read_from="foo"), reference_tokens
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
            elif value in STYLES:
                styles[value] = style_state
                style_state = False
            else:
                token_color = Color.parse(value)
                if is_background:
                    background = token_color
                else:
                    color = token_color

        elif name == "key_value":
            key, _, value = value.partition("=")
            if key.startswith("@"):
                meta[key[1:]] = value
            else:
                data[key] = value
        elif name == "percent":
            percent = int(value.rstrip("%")) / 100
            if is_background:
                background = background.multiply_alpha(percent)
            else:
                color = background.multiply_alpha(percent)

    parsed_style = Style(background, color, link=data.get("link", None), **styles)
    if meta:
        parsed_style += Style.from_meta(meta)
    return parsed_style


if __name__ == "__main__":
    variables = {"accent": "red"}
    print(
        style_parse(
            "bold not underline red $accent rgba(10,20,30,3) on black not italic link=https://www.willmcgugan.com",
            variables,
        )
    )

    print(style_parse("auto on red 20% @click=app.bell('hello')", variables))
