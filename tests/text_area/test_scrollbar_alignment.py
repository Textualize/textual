from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import TextArea, Tree, OptionList, Static
from textual.containers import VerticalScroll


class _ScrollbarDemo(App[None]):
	"""Minimal app to exercise vertical scrollbar alignment.

	The widgets chosen mirror the original report (TextArea, Tree, OptionList, VerticalScroll)
	and are intentionally given enough content to show a vertical scrollbar.
	"""

	CSS = """
	Screen > * {
		width: 1fr;
		height: 1fr;
		border: none;
		background: $surface;
	}
	"""

	def compose(self) -> ComposeResult:
		yield TextArea(id="ta")
		yield Tree("", id="tree")
		yield OptionList(id="ol")
		yield VerticalScroll(id="vs")

	def on_mount(self) -> None:
		# TextArea content
		self.query_one(TextArea).load_text("\n".join(f"Line {n}" for n in range(200)))

		# Tree content
		tree = self.query_one(Tree)
		tree.root.expand()
		for n in range(200):
			tree.root.add(f"Node {n}")

		# OptionList content
		self.query_one(OptionList).add_options(f"Option {n}" for n in range(200))

		# VerticalScroll content
		self.query_one("#vs").mount_all(*(Static(f"Item {n}") for n in range(200)))


async def test_textarea_scrollbar_aligns_with_peers():
	"""TextArea's vertical scrollbar should align with Tree, OptionList, and VerticalScroll.

	We check the right-most edge of each widget's region; if they match, the scrollbars 
	are visually aligned to the same gutter.
	"""
	app = _ScrollbarDemo()
	async with app.run_test() as pilot:
		# Let layout settle
		await pilot.pause(0.05)

		ta = app.query_one("#ta")
		tree = app.query_one("#tree")
		ol = app.query_one("#ol")
		vs = app.query_one("#vs")

		# Sanity: all should be showing vertical scrollbars given the content size
		assert ta.show_vertical_scrollbar, "TextArea should show vertical scrollbar"
		assert tree.show_vertical_scrollbar, "Tree should show vertical scrollbar"
		assert ol.show_vertical_scrollbar, "OptionList should show vertical scrollbar"
		assert vs.show_vertical_scrollbar, "VerticalScroll should show vertical scrollbar"

		right_edges = [w.region.right for w in (ta, tree, ol, vs)]
		assert len(set(right_edges)) == 1, (
			"Expected aligned scrollbars: right edges differ "
			f"{right_edges}"
		)
