from textual.widgets import Link

TEST_URL = "http://example.com"


async def test_link_url_defaults_to_text():
    link = Link(TEST_URL)
    assert link.url == TEST_URL


async def test_empty_link_updates_url_with_text():
    link = Link("")
    link.text = TEST_URL
    assert link.url == TEST_URL


async def test_empty_link_updates_text_with_url():
    link = Link("")
    link.url = TEST_URL
    assert link.text == TEST_URL
