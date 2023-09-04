import pytest

from textual._slug import TrackedSlugs, slug


@pytest.mark.parametrize(
    "text, expected",
    [
        ("test", "test"),
        ("Test", "test"),
        (" Test ", "test"),
        ("-test-", "-test-"),
        ("!test!", "test"),
        ("test!!test", "testtest"),
        ("test! !test", "test-test"),
        ("test test", "test-test"),
        ("test  test", "test-test"),
        ("test      test", "test-test"),
        ("test!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~test", "test-_test"),
        ("tëst", "tëst"),
        ("test🤷🏻‍♀️test", "test test"),
    ],
)
def test_simple_slug(text: str, expected: str) -> None:
    """The simple slug function should produce the expected slug."""
    assert slug(text) == expected


def test_tracked_slugs() -> None:
    """The tracked slugging class should produce the expected slugs."""
    unique = TrackedSlugs()
    assert unique.slug("test") == "test"
    assert unique.slug("test") == "test-1"
    assert unique.slug("tester") == "tester"
    assert unique.slug("test") == "test-2"
    assert unique.slug("tester") == "tester-1"
