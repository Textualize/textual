import pytest

from textual._etc import Sample, Samples, TimeToCompletion


def test_sample_max_size_only() -> None:
    """Adding samples to the Samples class with no time window should restrict to count."""
    samples = Samples(10, None)
    assert len(samples) == 0
    for n in range(20):
        samples.append(Sample(n, n))
    assert len(samples) == 10


def test_sample_max_time_only() -> None:
    """Adding samples to the Samples class with only a time window should restrict by time."""
    samples = Samples(None, 10)
    assert len(samples) == 0
    for n in range(20):
        samples.append(Sample(n, n))
    assert len(samples) == 10


def test_sample_no_max() -> None:
    """Adding samples to the Samples class with no constraints should keep going."""
    samples = Samples(None, None)
    assert len(samples) == 0
    for n in range(20):
        samples.append(Sample(n, n))
    assert len(samples) == 20


def test_out_of_time_samples_should_keep_a_sample():
    """If we run out of time on samples, we should keep the latest sample."""
    samples = Samples(10, 1)
    assert len(samples) == 0
    for n in range(20):
        samples.append(Sample(n, n + 100))
    assert len(samples) == 1
    assert samples[0].moment == 119


def test_size() -> None:
    """The number of samples should respect the window size."""
    time_to_completion = TimeToCompletion(20, sample_window_size=10)
    for n in range(20):
        assert len(time_to_completion) == min(n, 10)
        time_to_completion.record(n, n)


def test_no_go_backwards() -> None:
    """It should not be possible to go backwards in time."""
    time_to_completion = TimeToCompletion(10)
    time_to_completion.record(2)
    with pytest.raises(ValueError):
        time_to_completion.record(1)


def test_no_go_past_end() -> None:
    """It should not be possible to go past the destination value."""
    with pytest.raises(ValueError):
        TimeToCompletion(1).record(2)


def test_estimate() -> None:
    """Test the time to completion calculation."""
    time_to_completion = TimeToCompletion(100)
    for n in range(10):
        time_to_completion.record(n, n)
    assert time_to_completion.estimated_time_to_complete == 91


def test_estimate_small_window() -> None:
    """Test the time to completion calculation."""
    time_to_completion = TimeToCompletion(100, sample_window_size=5)
    for n in range(10):
        time_to_completion.record(n, n)
    assert time_to_completion.estimated_time_to_complete == 91


def test_estimate_bigger_step() -> None:
    """Test the time to completion calculation."""
    time_to_completion = TimeToCompletion(100)
    for n in range(0, 10, 2):
        time_to_completion.record(n, n)
    assert time_to_completion.estimated_time_to_complete == 92


def test_estimate_no_samples() -> None:
    """Time to completion should be 0 of no samples exist."""
    assert TimeToCompletion(100).estimated_time_to_complete == 0
