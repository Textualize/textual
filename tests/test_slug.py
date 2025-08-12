import pytest

from textual._slug import TrackedSlugs, slug, slug_for_tcss_id
from textual.dom import check_identifiers


@pytest.mark.xdist_group("group1")
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
        ("test  test", "test--test"),
        ("test          test", "test----------test"),
        ("--test", "--test"),
        ("test--", "test--"),
        ("--test--test--", "--test--test--"),
        ("test!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~test", "test-_test"),
        ("tëst", "t%C3%ABst"),
        ("test🙂test", "testtest"),
        ("test🤷test", "testtest"),
        ("test🤷🏻‍♀️test", "testtest"),
        ("test🤖test", "testtest"),
        ("test🧠test", "testtest"),
    ],
)
def test_simple_slug(text: str, expected: str) -> None:
    """The simple slug function should produce the expected slug."""
    assert slug(text) == expected


@pytest.fixture(scope="module")
def tracker() -> TrackedSlugs:
    return TrackedSlugs()


@pytest.mark.xdist_group("group2")
@pytest.mark.parametrize(
    "text, expected",
    [
        ("test", "test"),
        ("test", "test-1"),
        ("test", "test-2"),
        ("-test-", "-test-"),
        ("-test-", "-test--1"),
        ("test!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~test", "test-_test"),
        ("test!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~test", "test-_test-1"),
        ("tëst", "t%C3%ABst"),
        ("tëst", "t%C3%ABst-1"),
        ("tëst", "t%C3%ABst-2"),
        ("test🙂test", "testtest"),
        ("test🤷test", "testtest-1"),
        ("test🤷🏻‍♀️test", "testtest-2"),
        ("test", "test-3"),
        ("test", "test-4"),
        (" test ", "test-5"),
    ],
)
def test_tracked_slugs(tracker: TrackedSlugs, text: str, expected: str) -> None:
    """The tracked slugging class should produce the expected slugs."""
    assert tracker.slug(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("", "_"),
        (" ", "-"),
        ("5", "_5"),
        ("a", "a"),
        ("hello world", "hello-world"),
        ("🙂", "_1f642"),
        ("🙂🙂", "_1f6421f642"),
        ("Foo🙂", "foo1f642"),
        ("ß", "ss"),
    ],
)
def test_slug_for_tcss_id(text: str, expected: str) -> None:
    """Test the slug_for_tcss_id"""
    slug = slug_for_tcss_id(text)
    assert slug == expected
    check_identifiers(slug)
