from pathlib import Path

import tree_sitter_ruby
from tree_sitter import Language

from textual.app import App, ComposeResult
from textual.widgets import TextArea

ruby_language = Language(tree_sitter_ruby.language())
ruby_highlight_query = (Path(__file__).parent / "ruby_highlights.scm").read_text()

ruby_code = """\
class Greeter
  def initialize(name)
    @name = name
  end

  def say_hello
    puts "Hello, #{@name}!"
  end
end
"""


class TextAreaCustomLanguage(App):
    def compose(self) -> ComposeResult:
        text_area = TextArea.code_editor(text=ruby_code)

        # Register the Ruby language and highlight query
        text_area.register_language("ruby", ruby_language, ruby_highlight_query)

        # Switch to Ruby
        text_area.language = "ruby"
        yield text_area


if __name__ == "__main__":
    app = TextAreaCustomLanguage()
    app.run()
