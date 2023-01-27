# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.11.0] - Unreleased

### Added

- Added the coroutines `Animator.wait_until_complete` and `pilot.wait_for_scheduled_animations` that allow waiting for all current and scheduled animations https://github.com/Textualize/textual/issues/1658
- Added the method `Animator.is_being_animated` that checks if an attribute of an object is being animated or is scheduled for animation

### Changed

- Breaking change: `TreeNode` can no longer be imported from `textual.widgets`; it is now available via `from textual.widgets.tree import TreeNode`. https://github.com/Textualize/textual/pull/1637

### Fixed

- Fixed stuck screen  https://github.com/Textualize/textual/issues/1632
- Fixed relative units in `grid-rows` and `grid-columns` being computed with respect to the wrong dimension https://github.com/Textualize/textual/issues/1406
- Fixed bug with animations that were triggered back to back, where the second one wouldn't start https://github.com/Textualize/textual/issues/1372
- Fixed bug with animations that were scheduled where all but the first would be skipped https://github.com/Textualize/textual/issues/1372
- Programmatically setting `overflow_x`/`overflow_y` refreshes the layout correctly https://github.com/Textualize/textual/issues/1616
- Fixed double-paste into `Input` https://github.com/Textualize/textual/issues/1657
- Added a workaround for an apparent Windows Terminal paste issue https://github.com/Textualize/textual/issues/1661

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

### Added

- Added "inherited bindings" -- BINDINGS classvar will be merged with base classes, unless inherit_bindings is set to False
- Added `Tree` widget which replaces `TreeControl`.
- Added widget `Placeholder` https://github.com/Textualize/textual/issues/1200.

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
