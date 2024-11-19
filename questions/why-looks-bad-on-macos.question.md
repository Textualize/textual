---
title: "Why doesn't Textual look good on macOS?"
alt_titles:
  - "looks bad on macOS"
  - "dashed lines on macOS"
  - "broken borders on macOS"
  - "pale colors on macOS"
  - "pale colours on macOS"
  - "mac terminal"
  - "macOS terminal"
---

You may find that the default macOS Terminal.app doesn't render Textual apps (and likely other TUIs) very well, particularly when it comes to box characters.
For instance, you may find it displays misaligned blocks and lines like this:

<img width="1042" alt="Screenshot 2023-06-19 at 10 43 02" src="https://github.com/Textualize/textual/assets/554369/e61f3876-3dd1-4ac8-b380-22922c89c7d6">

You can (mostly) fix this by opening settings -> profiles > Text tab, and changing the font settings.
We have found that Menlo Regular font, with a character spacing of 1 and line spacing of 0.805 produces reasonable results.
If you want to use another font, you may have to tweak the line spacing until you get good results.

<img width="737" alt="Screenshot 2023-06-19 at 10 44 00" src="https://github.com/Textualize/textual/assets/554369/0a052a93-b1fd-4327-9d33-d954b51a9ad2">

With these changes, Textual apps render more as intended:

<img width="1042" alt="Screenshot 2023-06-19 at 10 43 23" src="https://github.com/Textualize/textual/assets/554369/a0c4aa05-c509-4ac1-b0b8-e68ce4433f70">

Even with this *fix*, Terminal.app has a few limitations.
It is limited to 256 colors, and can be a little slow compared to more modern alternatives.
Fortunately there are a number of free terminal emulators for macOS which produces high quality results.

We recommend any of the following terminals:

- [iTerm2](https://iterm2.com/)
- [Kitty](https://sw.kovidgoyal.net/kitty/)
- [WezTerm](https://wezfurlong.org/wezterm/)

### Terminal.app colors

<img width="762" alt="Screenshot 2023-06-19 at 11 00 12" src="https://github.com/Textualize/textual/assets/554369/e0555d23-e141-4069-b318-f3965c880208">

### iTerm2 colors

<img width="1002" alt="Screenshot 2023-06-19 at 11 00 25" src="https://github.com/Textualize/textual/assets/554369/9a8cde57-5121-49a7-a2e0-5f6fc871b7a6">
