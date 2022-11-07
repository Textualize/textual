# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.4.0] - Unreleased

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
