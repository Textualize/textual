# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.1.11] - Unreleased

### Changed

- Changed message handlers to use prefix handle\_
- Renamed messages to drop the Message suffix
- Events now bubble by default

### Added

- Added App.measure
- Added auto_width to Vertical Layout, WindowView, an ScrollView
- Added big_table.py example

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
