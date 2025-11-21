## Linux Console

The Linux console has limited capabilities, to maintain back compatibility with legacy VGA hardware. It supports unicode but colours are restricted and the fonts have very limited numbers of glyphs. There is a choice of 256 glyphs with 16 colors or 512 glyphs with 8 colors. Textual really needs more than 8 colors, so a font with 256 glyphs is needed. The console uses fonts in a special PSF file type; these are often in the directory /usr/share/consolefonts/.

Textual uses line drawing and block characters to render the widgets. Many of the widely available font files lack a full set of block drawing characters, and this gives a poor appearance. The Unifoundry project have a 512 glyph font that includes all the characters needed, but this only gives you eight colors. A subset of the Unifoundry font has been developed for use with textual and you can find it at [font-for-textual](https://github.com/jsatchell/font-for-textual).
