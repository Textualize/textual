# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.32.0] - 2023-08-03

### Added

- Added widgets.Log
- Added Widget.is_vertical_scroll_end, Widget.is_horizontal_scroll_end, Widget.is_vertical_scrollbar_grabbed, Widget.is_horizontal_scrollbar_grabbed

### Changed

- Breaking change: Renamed TextLog to RichLog

## [0.31.0] - 2023-08-01

### Added

- Added App.begin_capture_print, App.end_capture_print, Widget.begin_capture_print, Widget.end_capture_print https://github.com/Textualize/textual/issues/2952
- Added the ability to run async methods as thread workers https://github.com/Textualize/textual/pull/2938
- Added `App.stop_animation` https://github.com/Textualize/textual/issues/2786
- Added `Widget.stop_animation` https://github.com/Textualize/textual/issues/2786

### Changed

- Breaking change: Creating a thread worker now requires that a `thread=True` keyword argument is passed https://github.com/Textualize/textual/pull/2938
- Breaking change: `Markdown.load` no longer captures all errors and returns a `bool`, errors now propagate https://github.com/Textualize/textual/issues/2956
- Breaking change: the default style of a `DataTable` now has `max-height: 100%` https://github.com/Textualize/textual/issues/2959

### Fixed

- Fixed a crash when a `SelectionList` had a prompt wider than itself https://github.com/Textualize/textual/issues/2900
- Fixed a bug where `Click` events were bubbling up from `Switch` widgets https://github.com/Textualize/textual/issues/2366
- Fixed a crash when using empty CSS variables https://github.com/Textualize/textual/issues/1849
- Fixed issue with tabs in TextLog https://github.com/Textualize/textual/issues/3007
- Fixed a bug with `DataTable` hover highlighting https://github.com/Textualize/textual/issues/2909

## [0.30.0] - 2023-07-17

### Added

- Added `DataTable.remove_column` method https://github.com/Textualize/textual/pull/2899
- Added notifications https://github.com/Textualize/textual/pull/2866
- Added `on_complete` callback to scroll methods https://github.com/Textualize/textual/pull/2903

### Fixed

- Fixed CancelledError issue with timer https://github.com/Textualize/textual/issues/2854
- Fixed Toggle Buttons issue with not being clickable/hoverable https://github.com/Textualize/textual/pull/2930


## [0.29.0] - 2023-07-03

### Changed

- Factored dev tools (`textual` command) in to external lib (`textual-dev`).

### Added

- Updated `DataTable.get_cell` type hints to accept string keys https://github.com/Textualize/textual/issues/2586
- Added `DataTable.get_cell_coordinate` method
- Added `DataTable.get_row_index` method https://github.com/Textualize/textual/issues/2587
- Added `DataTable.get_column_index` method
- Added can-focus pseudo-class to target widgets that may receive focus
- Make `Markdown.update` optionally awaitable https://github.com/Textualize/textual/pull/2838
- Added `default` parameter to `DataTable.add_column` for populating existing rows https://github.com/Textualize/textual/pull/2836
- Added can-focus pseudo-class to target widgets that may receive focus

### Fixed

- Fixed crash when columns were added to populated `DataTable` https://github.com/Textualize/textual/pull/2836
- Fixed issues with opacity on Screens https://github.com/Textualize/textual/issues/2616
- Fixed style problem with selected selections in a non-focused selection list https://github.com/Textualize/textual/issues/2768
- Fixed sys.stdout and sys.stderr being None https://github.com/Textualize/textual/issues/2879

## [0.28.1] - 2023-06-20

### Fixed

- Fixed indented code blocks not showing up in `Markdown` https://github.com/Textualize/textual/issues/2781
- Fixed inline code blocks in lists showing out of order in `Markdown` https://github.com/Textualize/textual/issues/2676
- Fixed list items in a `Markdown` being added to the focus chain https://github.com/Textualize/textual/issues/2380
- Fixed `Tabs` posting unnecessary messages when removing non-active tabs https://github.com/Textualize/textual/issues/2807
- call_after_refresh will preserve the sender within the callback https://github.com/Textualize/textual/pull/2806

### Added

- Added a method of allowing third party code to handle unhandled tokens in `Markdown` https://github.com/Textualize/textual/pull/2803
- Added `MarkdownBlock` as an exported symbol in `textual.widgets.markdown` https://github.com/Textualize/textual/pull/2803

### Changed

- Tooltips are now inherited, so will work with compound widgets


## [0.28.0] - 2023-06-19

### Added

- The devtools console now confirms when CSS files have been successfully loaded after a previous error https://github.com/Textualize/textual/pull/2716
- Class variable `CSS` to screens https://github.com/Textualize/textual/issues/2137
- Class variable `CSS_PATH` to screens https://github.com/Textualize/textual/issues/2137
- Added `cursor_foreground_priority` and `cursor_background_priority` to `DataTable` https://github.com/Textualize/textual/pull/2736
- Added Region.center
- Added `center` parameter to `Widget.scroll_to_region`
- Added `origin_visible` parameter to `Widget.scroll_to_region`
- Added `origin_visible` parameter to `Widget.scroll_to_center`
- Added `TabbedContent.tab_count` https://github.com/Textualize/textual/pull/2751
- Added `TabbedContent.add_pane` https://github.com/Textualize/textual/pull/2751
- Added `TabbedContent.remove_pane` https://github.com/Textualize/textual/pull/2751
- Added `TabbedContent.clear_panes` https://github.com/Textualize/textual/pull/2751
- Added `TabbedContent.Cleared` https://github.com/Textualize/textual/pull/2751

### Fixed

- Fixed setting `TreeNode.label` on an existing `Tree` node not immediately refreshing https://github.com/Textualize/textual/pull/2713
- Correctly implement `__eq__` protocol in DataTable https://github.com/Textualize/textual/pull/2705
- Fixed exceptions in Pilot tests being silently ignored https://github.com/Textualize/textual/pull/2754
- Fixed issue where internal data of `OptionList` could be invalid for short window after `clear_options` https://github.com/Textualize/textual/pull/2754
- Fixed `Tooltip` causing a `query_one` on a lone `Static` to fail https://github.com/Textualize/textual/issues/2723
- Nested widgets wouldn't lose focus when parent is disabled https://github.com/Textualize/textual/issues/2772
- Fixed the `Tabs` `Underline` highlight getting "lost" in some extreme situations https://github.com/Textualize/textual/pull/2751

### Changed

- Breaking change: The `@on` decorator will now match a message class and any child classes https://github.com/Textualize/textual/pull/2746
- Breaking change: Styles update to checkbox, radiobutton, OptionList, Select, SelectionList, Switch https://github.com/Textualize/textual/pull/2777
- `Tabs.add_tab` is now optionally awaitable https://github.com/Textualize/textual/pull/2778
- `Tabs.add_tab` now takes `before` and `after` arguments to position a new tab https://github.com/Textualize/textual/pull/2778
- `Tabs.remove_tab` is now optionally awaitable https://github.com/Textualize/textual/pull/2778
- Breaking change: `Tabs.clear` has been changed from returning `self` to being optionally awaitable https://github.com/Textualize/textual/pull/2778

## [0.27.0] - 2023-06-01

### Fixed

- Fixed zero division error https://github.com/Textualize/textual/issues/2673
- Fix `scroll_to_center` when there were nested layers out of view (Compositor full_map not populated fully) https://github.com/Textualize/textual/pull/2684
- Fix crash when `Select` widget value attribute was set in `compose` https://github.com/Textualize/textual/pull/2690
- Issue with computing progress in workers https://github.com/Textualize/textual/pull/2686
- Issues with `switch_screen` not updating the results callback appropriately https://github.com/Textualize/textual/issues/2650
- Fixed incorrect mount order https://github.com/Textualize/textual/pull/2702

### Added

- `work` decorator accepts `description` parameter to add debug string https://github.com/Textualize/textual/issues/2597
- Added `SelectionList` widget https://github.com/Textualize/textual/pull/2652
- `App.AUTO_FOCUS` to set auto focus on all screens https://github.com/Textualize/textual/issues/2594
- Option to `scroll_to_center` to ensure we don't scroll such that the top left corner of the widget is not visible https://github.com/Textualize/textual/pull/2682
- Added `Widget.tooltip` property https://github.com/Textualize/textual/pull/2670
- Added `Region.inflect` https://github.com/Textualize/textual/pull/2670
- `Suggester` API to compose with widgets for automatic suggestions https://github.com/Textualize/textual/issues/2330
- `SuggestFromList` class to let widgets get completions from a fixed set of options https://github.com/Textualize/textual/pull/2604
- `Input` has a new component class `input--suggestion` https://github.com/Textualize/textual/pull/2604
- Added `Widget.remove_children` https://github.com/Textualize/textual/pull/2657
- Added `Validator` framework and validation for `Input` https://github.com/Textualize/textual/pull/2600
- Ability to have private and public validate methods https://github.com/Textualize/textual/pull/2708
- Ability to have private compute methods https://github.com/Textualize/textual/pull/2708
- Added `message_hook` to App.run_test https://github.com/Textualize/textual/pull/2702
- Added `Sparkline` widget https://github.com/Textualize/textual/pull/2631

### Changed

- `Placeholder` now sets its color cycle per app https://github.com/Textualize/textual/issues/2590
- Footer now clears key highlight regardless of whether it's in the active screen or not https://github.com/Textualize/textual/issues/2606
- The default Widget repr no longer displays classes and pseudo-classes (to reduce noise in logs). Add them to your `__rich_repr__` method if needed. https://github.com/Textualize/textual/pull/2623
- Setting `Screen.AUTO_FOCUS` to `None` will inherit `AUTO_FOCUS` from the app instead of disabling it https://github.com/Textualize/textual/issues/2594
- Setting `Screen.AUTO_FOCUS` to `""` will disable it on the screen https://github.com/Textualize/textual/issues/2594
- Messages now have a `handler_name` class var which contains the name of the default handler method.
- `Message.control` is now a property instead of a class variable. https://github.com/Textualize/textual/issues/2528
- `Tree` and `DirectoryTree` Messages no longer accept a `tree` parameter, using `self.node.tree` instead. https://github.com/Textualize/textual/issues/2529
- Keybinding <kbd>right</kbd> in `Input` is also used to accept a suggestion if the cursor is at the end of the input https://github.com/Textualize/textual/pull/2604
- `Input.__init__` now accepts a `suggester` attribute for completion suggestions https://github.com/Textualize/textual/pull/2604
- Using `switch_screen` to switch to the currently active screen is now a no-op https://github.com/Textualize/textual/pull/2692
- Breaking change: removed `reactive.py::Reactive.var` in favor of `reactive.py::var` https://github.com/Textualize/textual/pull/2709/

### Removed

- `Placeholder.reset_color_cycle`
- Removed `Widget.reset_focus` (now called `Widget.blur`) https://github.com/Textualize/textual/issues/2642

## [0.26.0] - 2023-05-20

### Added

- Added `Widget.can_view`

### Changed

- Textual will now scroll focused widgets to center if not in view

## [0.25.0] - 2023-05-17

### Changed

- App `title` and `sub_title` attributes can be set to any type https://github.com/Textualize/textual/issues/2521
- `DirectoryTree` now loads directory contents in a worker https://github.com/Textualize/textual/issues/2456
- Only a single error will be written by default, unless in dev mode ("debug" in App.features) https://github.com/Textualize/textual/issues/2480
- Using `Widget.move_child` where the target and the child being moved are the same is now a no-op https://github.com/Textualize/textual/issues/1743
- Calling `dismiss` on a screen that is not at the top of the stack now raises an exception https://github.com/Textualize/textual/issues/2575
- `MessagePump.call_after_refresh` and `MessagePump.call_later` will now return `False` if the callback could not be scheduled. https://github.com/Textualize/textual/pull/2584

### Fixed

- Fixed `ZeroDivisionError` in `resolve_fraction_unit` https://github.com/Textualize/textual/issues/2502
- Fixed `TreeNode.expand` and `TreeNode.expand_all` not posting a `Tree.NodeExpanded` message https://github.com/Textualize/textual/issues/2535
- Fixed `TreeNode.collapse` and `TreeNode.collapse_all` not posting a `Tree.NodeCollapsed` message https://github.com/Textualize/textual/issues/2535
- Fixed `TreeNode.toggle` and `TreeNode.toggle_all` not posting a `Tree.NodeExpanded` or `Tree.NodeCollapsed` message https://github.com/Textualize/textual/issues/2535
- `footer--description` component class was being ignored https://github.com/Textualize/textual/issues/2544
- Pasting empty selection in `Input` would raise an exception https://github.com/Textualize/textual/issues/2563
- `Screen.AUTO_FOCUS` now focuses the first _focusable_ widget that matches the selector https://github.com/Textualize/textual/issues/2578
- `Screen.AUTO_FOCUS` now works on the default screen on startup https://github.com/Textualize/textual/pull/2581
- Fix for setting dark in App `__init__` https://github.com/Textualize/textual/issues/2583
- Fix issue with scrolling and docks https://github.com/Textualize/textual/issues/2525
- Fix not being able to use CSS classes with `Tab` https://github.com/Textualize/textual/pull/2589

### Added

- Class variable `AUTO_FOCUS` to screens https://github.com/Textualize/textual/issues/2457
- Added `NULL_SPACING` and `NULL_REGION` to geometry.py

## [0.24.1] - 2023-05-08

### Fixed

- Fix TypeError in code browser

## [0.24.0] - 2023-05-08

### Fixed

- Fixed crash when creating a `DirectoryTree` starting anywhere other than `.`
- Fixed line drawing in `Tree` when `Tree.show_root` is `True` https://github.com/Textualize/textual/issues/2397
- Fixed line drawing in `Tree` not marking branches as selected when first getting focus https://github.com/Textualize/textual/issues/2397

### Changed

- The DataTable cursor is now scrolled into view when the cursor coordinate is changed programmatically https://github.com/Textualize/textual/issues/2459
- run_worker exclusive parameter is now `False` by default https://github.com/Textualize/textual/pull/2470
- Added `always_update` as an optional argument for `reactive.var`
- Made Binding description default to empty string, which is equivalent to show=False https://github.com/Textualize/textual/pull/2501
- Modified Message to allow it to be used as a dataclass https://github.com/Textualize/textual/pull/2501
- Decorator `@on` accepts arbitrary `**kwargs` to apply selectors to attributes of the message https://github.com/Textualize/textual/pull/2498

### Added

- Property `control` as alias for attribute `tabs` in `Tabs` messages https://github.com/Textualize/textual/pull/2483
- Experimental: Added "overlay" rule https://github.com/Textualize/textual/pull/2501
- Experimental: Added "constrain" rule https://github.com/Textualize/textual/pull/2501
- Added textual.widgets.Select https://github.com/Textualize/textual/pull/2501
- Added Region.translate_inside https://github.com/Textualize/textual/pull/2501
- `TabbedContent` now takes kwargs `id`, `name`, `classes`, and `disabled`, upon initialization, like other widgets https://github.com/Textualize/textual/pull/2497
- Method `DataTable.move_cursor` https://github.com/Textualize/textual/issues/2472
- Added `OptionList.add_options` https://github.com/Textualize/textual/pull/2508
- Added `TreeNode.is_root` https://github.com/Textualize/textual/pull/2510
- Added `TreeNode.remove_children` https://github.com/Textualize/textual/pull/2510
- Added `TreeNode.remove` https://github.com/Textualize/textual/pull/2510
- Added classvar `Message.ALLOW_SELECTOR_MATCH` https://github.com/Textualize/textual/pull/2498
- Added `ALLOW_SELECTOR_MATCH` to all built-in messages associated with widgets https://github.com/Textualize/textual/pull/2498
- Markdown document sub-widgets now reference the container document
- Table of contents of a markdown document now references the document
- Added the `control` property to messages
  - `DirectoryTree.FileSelected`
  - `ListView`
    - `Highlighted`
    - `Selected`
  - `Markdown`
    - `TableOfContentsUpdated`
    - `TableOfContentsSelected`
    - `LinkClicked`
  - `OptionList`
    - `OptionHighlighted`
    - `OptionSelected`
  - `RadioSet.Changed`
  - `TabContent.TabActivated`
  - `Tree`
    - `NodeSelected`
    - `NodeHighlighted`
    - `NodeExpanded`
    - `NodeCollapsed`

## [0.23.0] - 2023-05-03

### Fixed

- Fixed `outline` top and bottom not handling alpha - https://github.com/Textualize/textual/issues/2371
- Fixed `!important` not applying to `align` https://github.com/Textualize/textual/issues/2420
- Fixed `!important` not applying to `border` https://github.com/Textualize/textual/issues/2420
- Fixed `!important` not applying to `content-align` https://github.com/Textualize/textual/issues/2420
- Fixed `!important` not applying to `outline` https://github.com/Textualize/textual/issues/2420
- Fixed `!important` not applying to `overflow` https://github.com/Textualize/textual/issues/2420
- Fixed `!important` not applying to `scrollbar-size` https://github.com/Textualize/textual/issues/2420
- Fixed `outline-right` not being recognised https://github.com/Textualize/textual/issues/2446
- Fixed OSError when a file system is not available https://github.com/Textualize/textual/issues/2468

### Changed

- Setting attributes with a `compute_` method will now raise an `AttributeError` https://github.com/Textualize/textual/issues/2383
- Unknown psuedo-selectors will now raise a tokenizer error (previously they were silently ignored) https://github.com/Textualize/textual/pull/2445
- Breaking change: `DirectoryTree.FileSelected.path` is now always a `Path` https://github.com/Textualize/textual/issues/2448
- Breaking change: `Directorytree.load_directory` renamed to `Directorytree._load_directory` https://github.com/Textualize/textual/issues/2448
- Unknown pseudo-selectors will now raise a tokenizer error (previously they were silently ignored) https://github.com/Textualize/textual/pull/2445

### Added

- Watch methods can now optionally be private https://github.com/Textualize/textual/issues/2382
- Added `DirectoryTree.path` reactive attribute https://github.com/Textualize/textual/issues/2448
- Added `DirectoryTree.FileSelected.node` https://github.com/Textualize/textual/pull/2463
- Added `DirectoryTree.reload` https://github.com/Textualize/textual/issues/2448
- Added textual.on decorator https://github.com/Textualize/textual/issues/2398

## [0.22.3] - 2023-04-29

### Fixed

- Fixed `textual run` on Windows https://github.com/Textualize/textual/issues/2406
- Fixed top border of button hover state

## [0.22.2] - 2023-04-29

### Added

- Added `TreeNode.tree` as a read-only public attribute https://github.com/Textualize/textual/issues/2413

### Fixed

- Fixed superfluous style updates for focus-within pseudo-selector

## [0.22.1] - 2023-04-28

### Fixed

- Fixed timer issue https://github.com/Textualize/textual/issues/2416
- Fixed `textual run` issue https://github.com/Textualize/textual/issues/2391

## [0.22.0] - 2023-04-27

### Fixed

- Fixed broken fr units when there is a min or max dimension https://github.com/Textualize/textual/issues/2378
- Fixed plain text in Markdown code blocks with no syntax being difficult to read https://github.com/Textualize/textual/issues/2400

### Added

- Added `ProgressBar` widget https://github.com/Textualize/textual/pull/2333

### Changed

- All `textual.containers` are now `1fr` in relevant dimensions by default https://github.com/Textualize/textual/pull/2386


## [0.21.0] - 2023-04-26

### Changed

- `textual run` execs apps in a new context.
- Textual console no longer parses console markup.
- Breaking change: `Container` no longer shows required scrollbars by default https://github.com/Textualize/textual/issues/2361
- Breaking change: `VerticalScroll` no longer shows a required horizontal scrollbar by default
- Breaking change: `HorizontalScroll` no longer shows a required vertical scrollbar by default
- Breaking change: Renamed `App.action_add_class_` to `App.action_add_class`
- Breaking change: Renamed `App.action_remove_class_` to `App.action_remove_class`
- Breaking change: `RadioSet` is now a single focusable widget https://github.com/Textualize/textual/pull/2372
- Breaking change: Removed `containers.Content` (use `containers.VerticalScroll` now)

### Added

- Added `-c` switch to `textual run` which runs commands in a Textual dev environment.
- Breaking change: standard keyboard scrollable navigation bindings have been moved off `Widget` and onto a new base class for scrollable containers (see also below addition) https://github.com/Textualize/textual/issues/2332
- `ScrollView` now inherits from `ScrollableContainer` rather than `Widget` https://github.com/Textualize/textual/issues/2332
- Containers no longer inherit any bindings from `Widget` https://github.com/Textualize/textual/issues/2331
- Added `ScrollableContainer`; a container class that binds the common navigation keys to scroll actions (see also above breaking change) https://github.com/Textualize/textual/issues/2332

### Fixed

- Fixed dark mode toggles in a "child" screen not updating a "parent" screen https://github.com/Textualize/textual/issues/1999
- Fixed "panel" border not exposed via CSS
- Fixed `TabbedContent.active` changes not changing the actual content https://github.com/Textualize/textual/issues/2352
- Fixed broken color on macOS Terminal https://github.com/Textualize/textual/issues/2359

## [0.20.1] - 2023-04-18

### Fix

- New fix for stuck tabs underline https://github.com/Textualize/textual/issues/2229

## [0.20.0] - 2023-04-18

### Changed

- Changed signature of Driver. Technically a breaking change, but unlikely to affect anyone.
- Breaking change: Timer.start is now private, and returns None. There was no reason to call this manually, so unlikely to affect anyone.
- A clicked tab will now be scrolled to the center of its tab container https://github.com/Textualize/textual/pull/2276
- Style updates are now done immediately rather than on_idle https://github.com/Textualize/textual/pull/2304
- `ButtonVariant` is now exported from `textual.widgets.button` https://github.com/Textualize/textual/issues/2264
- `HorizontalScroll` and `VerticalScroll` are now focusable by default https://github.com/Textualize/textual/pull/2317

### Added

- Added `DataTable.remove_row` method https://github.com/Textualize/textual/pull/2253
- option `--port` to the command `textual console` to specify which port the console should connect to https://github.com/Textualize/textual/pull/2258
- `Widget.scroll_to_center` method to scroll children to the center of container widget https://github.com/Textualize/textual/pull/2255 and https://github.com/Textualize/textual/pull/2276
- Added `TabActivated` message to `TabbedContent` https://github.com/Textualize/textual/pull/2260
- Added "panel" border style https://github.com/Textualize/textual/pull/2292
- Added `border-title-color`, `border-title-background`, `border-title-style` rules https://github.com/Textualize/textual/issues/2289
- Added `border-subtitle-color`, `border-subtitle-background`, `border-subtitle-style` rules https://github.com/Textualize/textual/issues/2289

### Fixed

- Fixed order styles are applied in DataTable - allows combining of renderable styles and component classes https://github.com/Textualize/textual/pull/2272
- Fixed key combos with up/down keys in some terminals https://github.com/Textualize/textual/pull/2280
- Fix empty ListView preventing bindings from firing https://github.com/Textualize/textual/pull/2281
- Fix `get_component_styles` returning incorrect values on first call when combined with pseudoclasses https://github.com/Textualize/textual/pull/2304
- Fixed `active_message_pump.get` sometimes resulting in a `LookupError` https://github.com/Textualize/textual/issues/2301

## [0.19.1] - 2023-04-10

### Fixed

- Fix viewport units using wrong viewport size  https://github.com/Textualize/textual/pull/2247
- Fixed layout not clearing arrangement cache https://github.com/Textualize/textual/pull/2249


## [0.19.0] - 2023-04-07

### Added

- Added support for filtering a `DirectoryTree` https://github.com/Textualize/textual/pull/2215

### Changed

- Allowed border_title and border_subtitle to accept Text objects
- Added additional line around titles
- When a container is auto, relative dimensions in children stretch the container. https://github.com/Textualize/textual/pull/2221
- DataTable page up / down now move cursor

### Fixed

- Fixed margin not being respected when width or height is "auto" https://github.com/Textualize/textual/issues/2220
- Fixed issue which prevent scroll_visible from working https://github.com/Textualize/textual/issues/2181
- Fixed missing tracebacks on Windows https://github.com/Textualize/textual/issues/2027

## [0.18.0] - 2023-04-04

### Added

- Added Worker API https://github.com/Textualize/textual/pull/2182

### Changed

- Breaking change: Markdown.update is no longer a coroutine https://github.com/Textualize/textual/pull/2182

### Fixed

- `RadioSet` is now far less likely to report `pressed_button` as `None` https://github.com/Textualize/textual/issues/2203

## [0.17.3] - 2023-04-02

### [Fixed]

- Fixed scrollable area not taking in to account dock https://github.com/Textualize/textual/issues/2188

## [0.17.2] - 2023-04-02

### [Fixed]

- Fixed bindings persistance https://github.com/Textualize/textual/issues/1613
- The `Markdown` widget now auto-increments ordered lists https://github.com/Textualize/textual/issues/2002
- Fixed modal bindings https://github.com/Textualize/textual/issues/2194
- Fix binding enter to active button https://github.com/Textualize/textual/issues/2194

### [Changed]

- tab and shift+tab are now defined on Screen.

## [0.17.1] - 2023-03-30

### Fixed

- Fix cursor not hiding on Windows https://github.com/Textualize/textual/issues/2170
- Fixed freeze when ctrl-clicking links https://github.com/Textualize/textual/issues/2167 https://github.com/Textualize/textual/issues/2073

## [0.17.0] - 2023-03-29

### Fixed

- Issue with parsing action strings whose arguments contained quoted closing parenthesis https://github.com/Textualize/textual/pull/2112
- Issues with parsing action strings with tuple arguments https://github.com/Textualize/textual/pull/2112
- Issue with watching for CSS file changes https://github.com/Textualize/textual/pull/2128
- Fix for tabs not invalidating https://github.com/Textualize/textual/issues/2125
- Fixed scrollbar layers issue https://github.com/Textualize/textual/issues/1358
- Fix for interaction between pseudo-classes and widget-level render caches https://github.com/Textualize/textual/pull/2155

### Changed

- DataTable now has height: auto by default. https://github.com/Textualize/textual/issues/2117
- Textual will now render strings within renderables (such as tables) as Console Markup by default. You can wrap your text with rich.Text() if you want the original behavior. https://github.com/Textualize/textual/issues/2120
- Some widget methods now return `self` instead of `None` https://github.com/Textualize/textual/pull/2102:
  - `Widget`: `refresh`, `focus`, `reset_focus`
  - `Button.press`
  - `DataTable`: `clear`, `refresh_coordinate`, `refresh_row`, `refresh_column`, `sort`
  - `Placehoder.cycle_variant`
  - `Switch.toggle`
  - `Tabs.clear`
  - `TextLog`: `write`, `clear`
  - `TreeNode`: `expand`, `expand_all`, `collapse`, `collapse_all`, `toggle`, `toggle_all`
  - `Tree`: `clear`, `reset`
- Screens with alpha in their background color will now blend with the background. https://github.com/Textualize/textual/pull/2139
- Added "thick" border style. https://github.com/Textualize/textual/pull/2139
- message_pump.app will now set the active app if it is not already set.
- DataTable now has max height set to 100vh

### Added

- Added auto_scroll attribute to TextLog https://github.com/Textualize/textual/pull/2127
- Added scroll_end switch to TextLog.write https://github.com/Textualize/textual/pull/2127
- Added `Widget.get_pseudo_class_state` https://github.com/Textualize/textual/pull/2155
- Added Screen.ModalScreen which prevents App from handling bindings. https://github.com/Textualize/textual/pull/2139
- Added TEXTUAL_LOG env var which should be a path that Textual will write verbose logs to (textual devtools is generally preferred) https://github.com/Textualize/textual/pull/2148
- Added textual.logging.TextualHandler logging handler
- Added Query.set_classes, DOMNode.set_classes, and `classes` setter for Widget https://github.com/Textualize/textual/issues/1081
- Added `OptionList` https://github.com/Textualize/textual/pull/2154

## [0.16.0] - 2023-03-22

### Added
- Added `parser_factory` argument to `Markdown` and `MarkdownViewer` constructors https://github.com/Textualize/textual/pull/2075
- Added `HorizontalScroll` https://github.com/Textualize/textual/issues/1957
- Added `Center` https://github.com/Textualize/textual/issues/1957
- Added `Middle` https://github.com/Textualize/textual/issues/1957
- Added `VerticalScroll` (mimicking the old behaviour of `Vertical`) https://github.com/Textualize/textual/issues/1957
- Added `Widget.border_title` and `Widget.border_subtitle` to set border (sub)title for a widget https://github.com/Textualize/textual/issues/1864
- Added CSS styles `border_title_align` and `border_subtitle_align`.
- Added `TabbedContent` widget https://github.com/Textualize/textual/pull/2059
- Added `get_child_by_type` method to widgets / app https://github.com/Textualize/textual/pull/2059
- Added `Widget.render_str` method https://github.com/Textualize/textual/pull/2059
- Added TEXTUAL_DRIVER environment variable

### Changed

- Dropped "loading-indicator--dot" component style from LoadingIndicator https://github.com/Textualize/textual/pull/2050
- Tabs widget now sends Tabs.Cleared when there is no active tab.
- Breaking change: changed default behaviour of `Vertical` (see `VerticalScroll`) https://github.com/Textualize/textual/issues/1957
- The default `overflow` style for `Horizontal` was changed to `hidden hidden` https://github.com/Textualize/textual/issues/1957
- `DirectoryTree` also accepts `pathlib.Path` objects as the path to list https://github.com/Textualize/textual/issues/1438

### Removed

- Removed `sender` attribute from messages. It's now just private (`_sender`). https://github.com/Textualize/textual/pull/2071

### Fixed

- Fixed borders not rendering correctly. https://github.com/Textualize/textual/pull/2074
- Fix for error when removing nodes. https://github.com/Textualize/textual/issues/2079

## [0.15.1] - 2023-03-14

### Fixed

- Fixed how the namespace for messages is calculated to facilitate inheriting messages https://github.com/Textualize/textual/issues/1814
- `Tab` is now correctly made available from `textual.widgets`. https://github.com/Textualize/textual/issues/2044

## [0.15.0] - 2023-03-13

### Fixed

- Fixed container not resizing when a widget is removed https://github.com/Textualize/textual/issues/2007
- Fixes issue where the horizontal scrollbar would be incorrectly enabled https://github.com/Textualize/textual/pull/2024

## [0.15.0] - 2023-03-13

### Changed

- Fixed container not resizing when a widget is removed https://github.com/Textualize/textual/issues/2007
- Fixed issue where the horizontal scrollbar would be incorrectly enabled https://github.com/Textualize/textual/pull/2024
- Fixed `Pilot.click` not correctly creating the mouse events https://github.com/Textualize/textual/issues/2022
- Fixes issue where the horizontal scrollbar would be incorrectly enabled https://github.com/Textualize/textual/pull/2024
- Fixes for tracebacks not appearing on exit https://github.com/Textualize/textual/issues/2027

### Added

- Added a LoadingIndicator widget https://github.com/Textualize/textual/pull/2018
- Added Tabs Widget https://github.com/Textualize/textual/pull/2020

### Changed

- Breaking change: Renamed Widget.action and App.action to Widget.run_action and App.run_action
- Added `shift`, `meta` and `control` arguments to `Pilot.click`.

## [0.14.0] - 2023-03-09

### Changed

- Breaking change: There is now only `post_message` to post events, which is non-async, `post_message_no_wait` was dropped. https://github.com/Textualize/textual/pull/1940
- Breaking change: The Timer class now has just one method to stop it, `Timer.stop` which is non sync https://github.com/Textualize/textual/pull/1940
- Breaking change: Messages don't require a `sender` in their constructor https://github.com/Textualize/textual/pull/1940
- Many messages have grown a `control` property which returns the control they relate to. https://github.com/Textualize/textual/pull/1940
- Updated styling to make it clear DataTable grows horizontally https://github.com/Textualize/textual/pull/1946
- Changed the `Checkbox` character due to issues with Windows Terminal and Windows 10 https://github.com/Textualize/textual/issues/1934
- Changed the `RadioButton` character due to issues with Windows Terminal and Windows 10 and 11 https://github.com/Textualize/textual/issues/1934
- Changed the `Markdown` initial bullet character due to issues with Windows Terminal and Windows 10 and 11 https://github.com/Textualize/textual/issues/1982
- The underscore `_` is no longer a special alias for the method `pilot.press`

### Added

- Added `data_table` attribute to DataTable events https://github.com/Textualize/textual/pull/1940
- Added `list_view` attribute to `ListView` events https://github.com/Textualize/textual/pull/1940
- Added `radio_set` attribute to `RadioSet` events https://github.com/Textualize/textual/pull/1940
- Added `switch` attribute to `Switch` events https://github.com/Textualize/textual/pull/1940
- Added `hover` and `click` methods to `Pilot` https://github.com/Textualize/textual/pull/1966
- Breaking change: Added `toggle_button` attribute to RadioButton and Checkbox events, replaces `input` https://github.com/Textualize/textual/pull/1940
- A percentage alpha can now be applied to a border https://github.com/Textualize/textual/issues/1863
- Added `Color.multiply_alpha`.
- Added `ContentSwitcher` https://github.com/Textualize/textual/issues/1945

### Fixed

- Fixed bug that prevented pilot from pressing some keys https://github.com/Textualize/textual/issues/1815
- DataTable race condition that caused crash https://github.com/Textualize/textual/pull/1962
- Fixed scrollbar getting "stuck" to cursor when cursor leaves window during drag https://github.com/Textualize/textual/pull/1968 https://github.com/Textualize/textual/pull/2003
- DataTable crash when enter pressed when table is empty https://github.com/Textualize/textual/pull/1973

## [0.13.0] - 2023-03-02

### Added

- Added `Checkbox` https://github.com/Textualize/textual/pull/1872
- Added `RadioButton` https://github.com/Textualize/textual/pull/1872
- Added `RadioSet` https://github.com/Textualize/textual/pull/1872

### Changed

- Widget scrolling methods (such as `Widget.scroll_home` and `Widget.scroll_end`) now perform the scroll after the next refresh https://github.com/Textualize/textual/issues/1774
- Buttons no longer accept arbitrary renderables https://github.com/Textualize/textual/issues/1870

### Fixed

- Scrolling with cursor keys now moves just one cell https://github.com/Textualize/textual/issues/1897
- Fix exceptions in watch methods being hidden on startup https://github.com/Textualize/textual/issues/1886
- Fixed scrollbar size miscalculation https://github.com/Textualize/textual/pull/1910
- Fixed slow exit on some terminals https://github.com/Textualize/textual/issues/1920

## [0.12.1] - 2023-02-25

### Fixed

- Fix for batch update glitch https://github.com/Textualize/textual/pull/1880

## [0.12.0] - 2023-02-24

### Added

- Added `App.batch_update` https://github.com/Textualize/textual/pull/1832
- Added horizontal rule to Markdown https://github.com/Textualize/textual/pull/1832
- Added `Widget.disabled` https://github.com/Textualize/textual/pull/1785
- Added `DOMNode.notify_style_update` to replace `messages.StylesUpdated` message https://github.com/Textualize/textual/pull/1861
- Added `DataTable.show_row_labels` reactive to show and hide row labels https://github.com/Textualize/textual/pull/1868
- Added `DataTable.RowLabelSelected` event, which is emitted when a row label is clicked https://github.com/Textualize/textual/pull/1868
- Added `MessagePump.prevent` context manager to temporarily suppress a given message type https://github.com/Textualize/textual/pull/1866

### Changed

- Scrolling by page now adds to current position.
- Markdown lists have been polished: a selection of bullets, better alignment of numbers, style tweaks https://github.com/Textualize/textual/pull/1832
- Added alternative method of composing Widgets https://github.com/Textualize/textual/pull/1847
- Added `label` parameter to `DataTable.add_row` https://github.com/Textualize/textual/pull/1868
- Breaking change: Some `DataTable` component classes were renamed - see PR for details https://github.com/Textualize/textual/pull/1868

### Removed

- Removed `screen.visible_widgets` and `screen.widgets`
- Removed `StylesUpdate` message. https://github.com/Textualize/textual/pull/1861

### Fixed

- Numbers in a descendant-combined selector no longer cause an error https://github.com/Textualize/textual/issues/1836
- Fixed superfluous scrolling when focusing a docked widget https://github.com/Textualize/textual/issues/1816
- Fixes walk_children which was returning more than one screen https://github.com/Textualize/textual/issues/1846
- Fixed issue with watchers fired for detached nodes https://github.com/Textualize/textual/issues/1846

## [0.11.1] - 2023-02-17

### Fixed

- DataTable fix issue where offset cache was not being used https://github.com/Textualize/textual/pull/1810
- DataTable scrollbars resize correctly when header is toggled https://github.com/Textualize/textual/pull/1803
- DataTable location mapping cleared when clear called https://github.com/Textualize/textual/pull/1809

## [0.11.0] - 2023-02-15

### Added

- Added `TreeNode.expand_all` https://github.com/Textualize/textual/issues/1430
- Added `TreeNode.collapse_all` https://github.com/Textualize/textual/issues/1430
- Added `TreeNode.toggle_all` https://github.com/Textualize/textual/issues/1430
- Added the coroutines `Animator.wait_until_complete` and `pilot.wait_for_scheduled_animations` that allow waiting for all current and scheduled animations https://github.com/Textualize/textual/issues/1658
- Added the method `Animator.is_being_animated` that checks if an attribute of an object is being animated or is scheduled for animation
- Added more keyboard actions and related bindings to `Input` https://github.com/Textualize/textual/pull/1676
- Added App.scroll_sensitivity_x and App.scroll_sensitivity_y to adjust how many lines the scroll wheel moves the scroll position https://github.com/Textualize/textual/issues/928
- Added Shift+scroll wheel and ctrl+scroll wheel to scroll horizontally
- Added `Tree.action_toggle_node` to toggle a node without selecting, and bound it to <kbd>Space</kbd> https://github.com/Textualize/textual/issues/1433
- Added `Tree.reset` to fully reset a `Tree` https://github.com/Textualize/textual/issues/1437
- Added `DataTable.sort` to sort rows https://github.com/Textualize/textual/pull/1638
- Added `DataTable.get_cell` to retrieve a cell by column/row keys https://github.com/Textualize/textual/pull/1638
- Added `DataTable.get_cell_at` to retrieve a cell by coordinate https://github.com/Textualize/textual/pull/1638
- Added `DataTable.update_cell` to update a cell by column/row keys https://github.com/Textualize/textual/pull/1638
- Added `DataTable.update_cell_at` to update a cell at a coordinate  https://github.com/Textualize/textual/pull/1638
- Added `DataTable.ordered_rows` property to retrieve `Row`s as they're currently ordered https://github.com/Textualize/textual/pull/1638
- Added `DataTable.ordered_columns` property to retrieve `Column`s as they're currently ordered https://github.com/Textualize/textual/pull/1638
- Added `DataTable.coordinate_to_cell_key` to find the key for the cell at a coordinate https://github.com/Textualize/textual/pull/1638
- Added `DataTable.is_valid_coordinate` https://github.com/Textualize/textual/pull/1638
- Added `DataTable.is_valid_row_index` https://github.com/Textualize/textual/pull/1638
- Added `DataTable.is_valid_column_index` https://github.com/Textualize/textual/pull/1638
- Added attributes to events emitted from `DataTable` indicating row/column/cell keys https://github.com/Textualize/textual/pull/1638
- Added `DataTable.get_row` to retrieve the values from a row by key https://github.com/Textualize/textual/pull/1786
- Added `DataTable.get_row_at` to retrieve the values from a row by index https://github.com/Textualize/textual/pull/1786
- Added `DataTable.get_column` to retrieve the values from a column by key https://github.com/Textualize/textual/pull/1786
- Added `DataTable.get_column_at` to retrieve the values from a column by index https://github.com/Textualize/textual/pull/1786
- Added `DataTable.HeaderSelected` which is posted when header label clicked https://github.com/Textualize/textual/pull/1788
- Added `DOMNode.watch` and `DOMNode.is_attached` methods  https://github.com/Textualize/textual/pull/1750
- Added `DOMNode.css_tree` which is a renderable that shows the DOM and CSS https://github.com/Textualize/textual/pull/1778
- Added `DOMNode.children_view` which is a view on to a nodes children list, use for querying https://github.com/Textualize/textual/pull/1778
- Added `Markdown` and `MarkdownViewer` widgets.
- Added `--screenshot` option to `textual run`

### Changed

- Breaking change: `TreeNode` can no longer be imported from `textual.widgets`; it is now available via `from textual.widgets.tree import TreeNode`. https://github.com/Textualize/textual/pull/1637
- `Tree` now shows a (subdued) cursor for a highlighted node when focus has moved elsewhere https://github.com/Textualize/textual/issues/1471
- `DataTable.add_row` now accepts `key` argument to uniquely identify the row https://github.com/Textualize/textual/pull/1638
- `DataTable.add_column` now accepts `key` argument to uniquely identify the column https://github.com/Textualize/textual/pull/1638
- `DataTable.add_row` and `DataTable.add_column` now return lists of keys identifying the added rows/columns https://github.com/Textualize/textual/pull/1638
- Breaking change: `DataTable.get_cell_value` renamed to `DataTable.get_value_at` https://github.com/Textualize/textual/pull/1638
- `DataTable.row_count` is now a property https://github.com/Textualize/textual/pull/1638
- Breaking change: `DataTable.cursor_cell` renamed to `DataTable.cursor_coordinate` https://github.com/Textualize/textual/pull/1638
  - The method `validate_cursor_cell` was renamed to `validate_cursor_coordinate`.
  - The method `watch_cursor_cell` was renamed to `watch_cursor_coordinate`.
- Breaking change: `DataTable.hover_cell` renamed to `DataTable.hover_coordinate` https://github.com/Textualize/textual/pull/1638
  - The method `validate_hover_cell` was renamed to `validate_hover_coordinate`.
- Breaking change: `DataTable.data` structure changed, and will be made private in upcoming release https://github.com/Textualize/textual/pull/1638
- Breaking change: `DataTable.refresh_cell` was renamed to `DataTable.refresh_coordinate` https://github.com/Textualize/textual/pull/1638
- Breaking change: `DataTable.get_row_height` now takes a `RowKey` argument instead of a row index https://github.com/Textualize/textual/pull/1638
- Breaking change: `DataTable.data` renamed to `DataTable._data` (it's now private) https://github.com/Textualize/textual/pull/1786
- The `_filter` module was made public (now called `filter`) https://github.com/Textualize/textual/pull/1638
- Breaking change: renamed `Checkbox` to `Switch` https://github.com/Textualize/textual/issues/1746
- `App.install_screen` name is no longer optional https://github.com/Textualize/textual/pull/1778
- `App.query` now only includes the current screen https://github.com/Textualize/textual/pull/1778
- `DOMNode.tree` now displays simple DOM structure only https://github.com/Textualize/textual/pull/1778
- `App.install_screen` now returns None rather than AwaitMount https://github.com/Textualize/textual/pull/1778
- `DOMNode.children` is now a simple sequence, the NodesList is exposed as `DOMNode._nodes` https://github.com/Textualize/textual/pull/1778
- `DataTable` cursor can now enter fixed columns https://github.com/Textualize/textual/pull/1799

### Fixed

- Fixed stuck screen  https://github.com/Textualize/textual/issues/1632
- Fixed programmatic style changes not refreshing children layouts when parent widget did not change size https://github.com/Textualize/textual/issues/1607
- Fixed relative units in `grid-rows` and `grid-columns` being computed with respect to the wrong dimension https://github.com/Textualize/textual/issues/1406
- Fixed bug with animations that were triggered back to back, where the second one wouldn't start https://github.com/Textualize/textual/issues/1372
- Fixed bug with animations that were scheduled where all but the first would be skipped https://github.com/Textualize/textual/issues/1372
- Programmatically setting `overflow_x`/`overflow_y` refreshes the layout correctly https://github.com/Textualize/textual/issues/1616
- Fixed double-paste into `Input` https://github.com/Textualize/textual/issues/1657
- Added a workaround for an apparent Windows Terminal paste issue https://github.com/Textualize/textual/issues/1661
- Fixed issue with renderable width calculation https://github.com/Textualize/textual/issues/1685
- Fixed issue with app not processing Paste event https://github.com/Textualize/textual/issues/1666
- Fixed glitch with view position with auto width inputs https://github.com/Textualize/textual/issues/1693
- Fixed `DataTable` "selected" events containing wrong coordinates when mouse was used https://github.com/Textualize/textual/issues/1723

### Removed

- Methods `MessagePump.emit` and `MessagePump.emit_no_wait` https://github.com/Textualize/textual/pull/1738
- Removed `reactive.watch` in favor of DOMNode.watch.

## [0.10.1] - 2023-01-20

### Added

- Added Strip.text property https://github.com/Textualize/textual/issues/1620

### Fixed

- Fixed `textual diagnose` crash on older supported Python versions. https://github.com/Textualize/textual/issues/1622

### Changed

- The default filename for screenshots uses a datetime format similar to ISO8601, but with reserved characters replaced by underscores https://github.com/Textualize/textual/pull/1518


## [0.10.0] - 2023-01-19

### Added

- Added `TreeNode.parent` -- a read-only property for accessing a node's parent https://github.com/Textualize/textual/issues/1397
- Added public `TreeNode` label access via `TreeNode.label` https://github.com/Textualize/textual/issues/1396
- Added read-only public access to the children of a `TreeNode` via `TreeNode.children` https://github.com/Textualize/textual/issues/1398
- Added `Tree.get_node_by_id` to allow getting a node by its ID https://github.com/Textualize/textual/pull/1535
- Added a `Tree.NodeHighlighted` message, giving a `on_tree_node_highlighted` event handler https://github.com/Textualize/textual/issues/1400
- Added a `inherit_component_classes` subclassing parameter to control whether component classes are inherited from base classes https://github.com/Textualize/textual/issues/1399
- Added `diagnose` as a `textual` command https://github.com/Textualize/textual/issues/1542
- Added `row` and `column` cursors to `DataTable` https://github.com/Textualize/textual/pull/1547
- Added an optional parameter `selector` to the methods `Screen.focus_next` and `Screen.focus_previous` that enable using a CSS selector to narrow down which widgets can get focus https://github.com/Textualize/textual/issues/1196

### Changed

- `MouseScrollUp` and `MouseScrollDown` now inherit from `MouseEvent` and have attached modifier keys. https://github.com/Textualize/textual/pull/1458
- Fail-fast and print pretty tracebacks for Widget compose errors https://github.com/Textualize/textual/pull/1505
- Added Widget._refresh_scroll to avoid expensive layout when scrolling https://github.com/Textualize/textual/pull/1524
- `events.Paste` now bubbles https://github.com/Textualize/textual/issues/1434
- Improved error message when style flag `none` is mixed with other flags (e.g., when setting `text-style`) https://github.com/Textualize/textual/issues/1420
- Clock color in the `Header` widget now matches the header color https://github.com/Textualize/textual/issues/1459
- Programmatic calls to scroll now optionally scroll even if overflow styling says otherwise (introduces a new `force` parameter to all the `scroll_*` methods) https://github.com/Textualize/textual/issues/1201
- `COMPONENT_CLASSES` are now inherited from base classes https://github.com/Textualize/textual/issues/1399
- Watch methods may now take no parameters
- Added `compute` parameter to reactive
- A `TypeError` raised during `compose` now carries the full traceback
- Removed base class `NodeMessage` from which all node-related `Tree` events inherited

### Fixed

- The styles `scrollbar-background-active` and `scrollbar-color-hover` are no longer ignored https://github.com/Textualize/textual/pull/1480
- The widget `Placeholder` can now have its width set to `auto` https://github.com/Textualize/textual/pull/1508
- Behavior of widget `Input` when rendering after programmatic value change and related scenarios https://github.com/Textualize/textual/issues/1477 https://github.com/Textualize/textual/issues/1443
- `DataTable.show_cursor` now correctly allows cursor toggling https://github.com/Textualize/textual/pull/1547
- Fixed cursor not being visible on `DataTable` mount when `fixed_columns` were used https://github.com/Textualize/textual/pull/1547
- Fixed `DataTable` cursors not resetting to origin on `clear()` https://github.com/Textualize/textual/pull/1601
- Fixed TextLog wrapping issue https://github.com/Textualize/textual/issues/1554
- Fixed issue with TextLog not writing anything before layout https://github.com/Textualize/textual/issues/1498
- Fixed an exception when populating a child class of `ListView` purely from `compose` https://github.com/Textualize/textual/issues/1588
- Fixed freeze in tests https://github.com/Textualize/textual/issues/1608
- Fixed minus not displaying as symbol https://github.com/Textualize/textual/issues/1482

## [0.9.1] - 2022-12-30

### Added

- Added textual._win_sleep for Python on Windows < 3.11 https://github.com/Textualize/textual/pull/1457

## [0.9.0] - 2022-12-30

### Added

- Added textual.strip.Strip primitive
- Added textual._cache.FIFOCache
- Added an option to clear columns in DataTable.clear() https://github.com/Textualize/textual/pull/1427

### Changed

- Widget.render_line now returns a Strip
- Fix for slow updates on Windows
- Bumped Rich dependency

## [0.8.2] - 2022-12-28

### Fixed

- Fixed issue with TextLog.clear() https://github.com/Textualize/textual/issues/1447

## [0.8.1] - 2022-12-25

### Fixed

- Fix for overflowing tree issue https://github.com/Textualize/textual/issues/1425

## [0.8.0] - 2022-12-22

### Fixed

- Fixed issues with nested auto dimensions https://github.com/Textualize/textual/issues/1402
- Fixed watch method incorrectly running on first set when value hasn't changed and init=False https://github.com/Textualize/textual/pull/1367
- `App.dark` can now be set from `App.on_load` without an error being raised  https://github.com/Textualize/textual/issues/1369
- Fixed setting `visibility` changes needing a `refresh` https://github.com/Textualize/textual/issues/1355

### Added

- Added `textual.actions.SkipAction` exception which can be raised from an action to allow parents to process bindings.
- Added `textual keys` preview.
- Added ability to bind to a character in addition to key name. i.e. you can bind to "." or "full_stop".
- Added TextLog.shrink attribute to allow renderable to reduce in size to fit width.

### Changed

- Deprecated `PRIORITY_BINDINGS` class variable.
- Renamed `char` to `character` on Key event.
- Renamed `key_name` to `name` on Key event.
- Queries/`walk_children` no longer includes self in results by default https://github.com/Textualize/textual/pull/1416

## [0.7.0] - 2022-12-17

### Added

- Added `PRIORITY_BINDINGS` class variable, which can be used to control if a widget's bindings have priority by default. https://github.com/Textualize/textual/issues/1343

### Changed

- Renamed the `Binding` argument `universal` to `priority`. https://github.com/Textualize/textual/issues/1343
- When looking for bindings that have priority, they are now looked from `App` downwards. https://github.com/Textualize/textual/issues/1343
- `BINDINGS` on an `App`-derived class have priority by default. https://github.com/Textualize/textual/issues/1343
- `BINDINGS` on a `Screen`-derived class have priority by default. https://github.com/Textualize/textual/issues/1343
- Added a message parameter to Widget.exit

### Fixed

- Fixed validator not running on first reactive set https://github.com/Textualize/textual/pull/1359
- Ensure only printable characters are used as key_display https://github.com/Textualize/textual/pull/1361


## [0.6.0] - 2022-12-11

https://textual.textualize.io/blog/2022/12/11/version-060

### Added

- Added "inherited bindings" -- BINDINGS classvar will be merged with base classes, unless inherit_bindings is set to False
- Added `Tree` widget which replaces `TreeControl`.
- Added widget `Placeholder` https://github.com/Textualize/textual/issues/1200.
- Added `ListView` and `ListItem` widgets https://github.com/Textualize/textual/pull/1143

### Changed

- Rebuilt `DirectoryTree` with new `Tree` control.
- Empty containers with a dimension set to `"auto"` will now collapse instead of filling up the available space.
- Container widgets now have default height of `1fr`.
- The default `width` of a `Label` is now `auto`.

### Fixed

- Type selectors can now contain numbers https://github.com/Textualize/textual/issues/1253
- Fixed visibility not affecting children https://github.com/Textualize/textual/issues/1313
- Fixed issue with auto width/height and relative children https://github.com/Textualize/textual/issues/1319
- Fixed issue with offset applied to containers https://github.com/Textualize/textual/issues/1256
- Fixed default CSS retrieval for widgets with no `DEFAULT_CSS` that inherited from widgets with `DEFAULT_CSS` https://github.com/Textualize/textual/issues/1335
- Fixed merging of `BINDINGS` when binding inheritance is set to `None` https://github.com/Textualize/textual/issues/1351

## [0.5.0] - 2022-11-20

### Added

- Add get_child_by_id and get_widget_by_id, remove get_child https://github.com/Textualize/textual/pull/1146
- Add easing parameter to Widget.scroll_* methods https://github.com/Textualize/textual/pull/1144
- Added Widget.call_later which invokes a callback on idle.
- `DOMNode.ancestors` no longer includes `self`.
- Added `DOMNode.ancestors_with_self`, which retains the old behaviour of
  `DOMNode.ancestors`.
- Improved the speed of `DOMQuery.remove`.
- Added DataTable.clear
- Added low-level `textual.walk` methods.
- It is now possible to `await` a `Widget.remove`.
  https://github.com/Textualize/textual/issues/1094
- It is now possible to `await` a `DOMQuery.remove`. Note that this changes
  the return value of `DOMQuery.remove`, which used to return `self`.
  https://github.com/Textualize/textual/issues/1094
- Added Pilot.wait_for_animation
- Added `Widget.move_child` https://github.com/Textualize/textual/issues/1121
- Added a `Label` widget https://github.com/Textualize/textual/issues/1190
- Support lazy-instantiated Screens (callables in App.SCREENS) https://github.com/Textualize/textual/pull/1185
- Display of keys in footer has more sensible defaults https://github.com/Textualize/textual/pull/1213
- Add App.get_key_display, allowing custom key_display App-wide https://github.com/Textualize/textual/pull/1213

### Changed

- Watchers are now called immediately when setting the attribute if they are synchronous. https://github.com/Textualize/textual/pull/1145
- Widget.call_later has been renamed to Widget.call_after_refresh.
- Button variant values are now checked at runtime. https://github.com/Textualize/textual/issues/1189
- Added caching of some properties in Styles object

### Fixed

- Fixed DataTable row not updating after add https://github.com/Textualize/textual/issues/1026
- Fixed issues with animation. Now objects of different types may be animated.
- Fixed containers with transparent background not showing borders https://github.com/Textualize/textual/issues/1175
- Fixed auto-width in horizontal containers https://github.com/Textualize/textual/pull/1155
- Fixed Input cursor invisible when placeholder empty https://github.com/Textualize/textual/pull/1202
- Fixed deadlock when removing widgets from the App https://github.com/Textualize/textual/pull/1219

## [0.4.0] - 2022-11-08

https://textual.textualize.io/blog/2022/11/08/version-040/#version-040

### Changed

- Dropped support for mounting "named" and "anonymous" widgets via
  `App.mount` and `Widget.mount`. Both methods now simply take one or more
  widgets as positional arguments.
- `DOMNode.query_one` now raises a `TooManyMatches` exception if there is
  more than one matching node.
  https://github.com/Textualize/textual/issues/1096
- `App.mount` and `Widget.mount` have new `before` and `after` parameters https://github.com/Textualize/textual/issues/778

### Added

- Added `init` param to reactive.watch
- `CSS_PATH` can now be a list of CSS files https://github.com/Textualize/textual/pull/1079
- Added `DOMQuery.only_one` https://github.com/Textualize/textual/issues/1096
- Writes to stdout are now done in a thread, for smoother animation. https://github.com/Textualize/textual/pull/1104

## [0.3.0] - 2022-10-31

### Fixed

- Fixed issue where scrollbars weren't being unmounted
- Fixed fr units for horizontal and vertical layouts https://github.com/Textualize/textual/pull/1067
- Fixed `textual run` breaking sys.argv https://github.com/Textualize/textual/issues/1064
- Fixed footer not updating styles when toggling dark mode
- Fixed how the app title in a `Header` is centred https://github.com/Textualize/textual/issues/1060
- Fixed the swapping of button variants https://github.com/Textualize/textual/issues/1048
- Fixed reserved characters in screenshots https://github.com/Textualize/textual/issues/993
- Fixed issue with TextLog max_lines https://github.com/Textualize/textual/issues/1058

### Changed

- DOMQuery now raises InvalidQueryFormat in response to invalid query strings, rather than cryptic CSS error
- Dropped quit_after, screenshot, and screenshot_title from App.run, which can all be done via auto_pilot
- Widgets are now closed in reversed DOM order
- Input widget justify hardcoded to left to prevent text-align interference
- Changed `textual run` so that it patches `argv` in more situations
- DOM classes and IDs are now always treated fully case-sensitive https://github.com/Textualize/textual/issues/1047

### Added

- Added Unmount event
- Added App.run_async method
- Added App.run_test context manager
- Added auto_pilot to App.run and App.run_async
- Added Widget._get_virtual_dom to get scrollbars
- Added size parameter to run and run_async
- Added always_update to reactive
- Returned an awaitable from push_screen, switch_screen, and install_screen https://github.com/Textualize/textual/pull/1061

## [0.2.1] - 2022-10-23

### Changed

- Updated meta data for PyPI

## [0.2.0] - 2022-10-23

### Added

- CSS support
- Too numerous to mention
## [0.1.18] - 2022-04-30

### Changed

- Bump typing extensions

## [0.1.17] - 2022-03-10

### Changed

- Bumped Rich dependency

## [0.1.16] - 2022-03-10

### Fixed

- Fixed escape key hanging on Windows

## [0.1.15] - 2022-01-31

### Added

- Added Windows Driver

## [0.1.14] - 2022-01-09

### Changed

- Updated Rich dependency to 11.X

## [0.1.13] - 2022-01-01

### Fixed

- Fixed spurious characters when exiting app
- Fixed increasing delay when exiting

## [0.1.12] - 2021-09-20

### Added

- Added geometry.Spacing

### Fixed

- Fixed calculation of virtual size in scroll views

## [0.1.11] - 2021-09-12

### Changed

- Changed message handlers to use prefix handle\_
- Renamed messages to drop the Message suffix
- Events now bubble by default
- Refactor of layout

### Added

- Added App.measure
- Added auto_width to Vertical Layout, WindowView, an ScrollView
- Added big_table.py example
- Added easing.py example

## [0.1.10] - 2021-08-25

### Added

- Added keyboard control of tree control
- Added Widget.gutter to calculate space between renderable and outside edge
- Added margin, padding, and border attributes to Widget

### Changed

- Callbacks may be async or non-async.
- Event handler event argument is optional.
- Fixed exception in clock example https://github.com/willmcgugan/textual/issues/52
- Added Message.wait() which waits for a message to be processed
- Key events are now sent to widgets first, before processing bindings

## [0.1.9] - 2021-08-06

### Added

- Added hover over and mouse click to activate keys in footer
- Added verbosity argument to Widget.log

### Changed

- Simplified events. Remove Startup event (use Mount)
- Changed geometry.Point to geometry.Offset and geometry.Dimensions to geometry.Size

## [0.1.8] - 2021-07-17

### Fixed

- Fixed exiting mouse mode
- Fixed slow animation

### Added

- New log system

## [0.1.7] - 2021-07-14

### Changed

- Added functionality to calculator example.
- Scrollview now shows scrollbars automatically
- New handler system for messages that doesn't require inheritance
- Improved traceback handling

[0.31.0]: https://github.com/Textualize/textual/compare/v0.30.0...v0.31.0
[0.30.0]: https://github.com/Textualize/textual/compare/v0.29.0...v0.30.0
[0.29.0]: https://github.com/Textualize/textual/compare/v0.28.1...v0.29.0
[0.28.1]: https://github.com/Textualize/textual/compare/v0.28.0...v0.28.1
[0.28.0]: https://github.com/Textualize/textual/compare/v0.27.0...v0.28.0
[0.27.0]: https://github.com/Textualize/textual/compare/v0.26.0...v0.27.0
[0.26.0]: https://github.com/Textualize/textual/compare/v0.25.0...v0.26.0
[0.25.0]: https://github.com/Textualize/textual/compare/v0.24.1...v0.25.0
[0.24.1]: https://github.com/Textualize/textual/compare/v0.24.0...v0.24.1
[0.24.0]: https://github.com/Textualize/textual/compare/v0.23.0...v0.24.0
[0.23.0]: https://github.com/Textualize/textual/compare/v0.22.3...v0.23.0
[0.22.3]: https://github.com/Textualize/textual/compare/v0.22.2...v0.22.3
[0.22.2]: https://github.com/Textualize/textual/compare/v0.22.1...v0.22.2
[0.22.1]: https://github.com/Textualize/textual/compare/v0.22.0...v0.22.1
[0.22.0]: https://github.com/Textualize/textual/compare/v0.21.0...v0.22.0
[0.21.0]: https://github.com/Textualize/textual/compare/v0.20.1...v0.21.0
[0.20.1]: https://github.com/Textualize/textual/compare/v0.20.0...v0.20.1
[0.20.0]: https://github.com/Textualize/textual/compare/v0.19.1...v0.20.0
[0.19.1]: https://github.com/Textualize/textual/compare/v0.19.0...v0.19.1
[0.19.0]: https://github.com/Textualize/textual/compare/v0.18.0...v0.19.0
[0.18.0]: https://github.com/Textualize/textual/compare/v0.17.4...v0.18.0
[0.17.3]: https://github.com/Textualize/textual/compare/v0.17.2...v0.17.3
[0.17.2]: https://github.com/Textualize/textual/compare/v0.17.1...v0.17.2
[0.17.1]: https://github.com/Textualize/textual/compare/v0.17.0...v0.17.1
[0.17.0]: https://github.com/Textualize/textual/compare/v0.16.0...v0.17.0
[0.16.0]: https://github.com/Textualize/textual/compare/v0.15.1...v0.16.0
[0.15.1]: https://github.com/Textualize/textual/compare/v0.15.0...v0.15.1
[0.15.0]: https://github.com/Textualize/textual/compare/v0.14.0...v0.15.0
[0.14.0]: https://github.com/Textualize/textual/compare/v0.13.0...v0.14.0
[0.13.0]: https://github.com/Textualize/textual/compare/v0.12.1...v0.13.0
[0.12.1]: https://github.com/Textualize/textual/compare/v0.12.0...v0.12.1
[0.12.0]: https://github.com/Textualize/textual/compare/v0.11.1...v0.12.0
[0.11.1]: https://github.com/Textualize/textual/compare/v0.11.0...v0.11.1
[0.11.0]: https://github.com/Textualize/textual/compare/v0.10.1...v0.11.0
[0.10.1]: https://github.com/Textualize/textual/compare/v0.10.0...v0.10.1
[0.10.0]: https://github.com/Textualize/textual/compare/v0.9.1...v0.10.0
[0.9.1]: https://github.com/Textualize/textual/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/Textualize/textual/compare/v0.8.2...v0.9.0
[0.8.2]: https://github.com/Textualize/textual/compare/v0.8.1...v0.8.2
[0.8.1]: https://github.com/Textualize/textual/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/Textualize/textual/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/Textualize/textual/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/Textualize/textual/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/Textualize/textual/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Textualize/textual/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Textualize/textual/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/Textualize/textual/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/Textualize/textual/compare/v0.1.18...v0.2.0
[0.1.18]: https://github.com/Textualize/textual/compare/v0.1.17...v0.1.18
[0.1.17]: https://github.com/Textualize/textual/compare/v0.1.16...v0.1.17
[0.1.16]: https://github.com/Textualize/textual/compare/v0.1.15...v0.1.16
[0.1.15]: https://github.com/Textualize/textual/compare/v0.1.14...v0.1.15
[0.1.14]: https://github.com/Textualize/textual/compare/v0.1.13...v0.1.14
[0.1.13]: https://github.com/Textualize/textual/compare/v0.1.12...v0.1.13
[0.1.12]: https://github.com/Textualize/textual/compare/v0.1.11...v0.1.12
[0.1.11]: https://github.com/Textualize/textual/compare/v0.1.10...v0.1.11
[0.1.10]: https://github.com/Textualize/textual/compare/v0.1.9...v0.1.10
[0.1.9]: https://github.com/Textualize/textual/compare/v0.1.8...v0.1.9
[0.1.8]: https://github.com/Textualize/textual/compare/v0.1.7...v0.1.8
[0.1.7]: https://github.com/Textualize/textual/releases/tag/v0.1.7
