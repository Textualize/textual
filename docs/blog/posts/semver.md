---
draft: false
date: 2024-12-01
categories:
  - DevLog
title: "Semver: Why it sucks, why I don't care, and how to improve it."
authors:
  - willmcgugan
---

I've been thinking about [Semver](https://semver.org/) lately.
Not only is Semver a great party conversation starter[^1], it influences a remarkable amount of the day-to-day decisions I make as a Python library author.

Semver has received a lot of flack in the Python community, and I imagine tech in general.
Much of the criticism is deserved, and I'm not going to argue against it.
However, I would argue that the criticisms are largely overstated, and Semver is terrific.

First, a quick recap.
Semver is a versioning scheme &mdash; a way of identifying one release of a library from another.

It consists of three integers delimited by a dot.
There may also be a suffix of additional meta data, but for this post we are only interested in the three numbers.

<div class="excalidraw">
--8<-- "docs/blog/images/semver.excalidraw.svg"
</div>

When you release a new version of your library you must change one or more of these digits.

- The `patch` number is incremented when you fix a bug in a backwards compatible way.
- The `minor` number is incremented when you add a new feature.
- The `major` number is incremented when you make a breaking change.
- Additionally, if you increment any number, the numbers to the right of of that number are reset to 0.

!!! note

    A `patch` number of `0` is a special designation that indicates the library is in *initial development*, and anything may change from one version to the next.

The promise of this scheme is that we can know if an update is compatible with our app or library.
If foo-lib increments only the `minor` or `major` numbers, then it will work with our project.
If the `major` number is incremented, then it won't.

Beautiful!

We can codify compatibility ahead of time, and our build tools will *just know* which versions of libraries will work together.

Except it doesn't work like that in practice.
And that is the main beef folk have with Semver.
Let's look at why.

## 

The following library has grand inspirations.
It's no `left-pad`, but the author has high hopes for this project.
Here's the first release, optimistically given a Semver number of `1.0.0`:

```python
def calculate_speed(distance:float, time:float) -> float:
    """Calculate speed given distance and time."""
    return distance / time
```

Before the author of `calculate-speed` can raise venture capital, they receive a bug report.
If the `time` is zero, then the function raises a `ZeroDivisionError`.

The author needs to pause work on the pitch deck to fix the bug.

Here's a potential solution:

```python
def calculate_speed(distance:float, time:float) -> float:
    """Calculate speed given distance and time."""
    assert time != 0
    return distance / time
```

We've add a runtime check for the `time` value.
Thus avoiding the `ZeroDivisionError`.
Problem solved.
So this is a backwards compatible bugfix and thus requires bumping `patch`?

It could break something if the caller added an exception handler for `ZeroDivisionError`, which now won't ever be invoked.
An `AssertionError` will most likely bubble up and result in an unhandled exception. 

So this would require a `major` bump? Maybe. But maybe not. Keep reading.

Here's another solution:

```python
def calculate_speed(distance:float, time:float) -> float:
    """Calculate speed given distance and time."""
    if time == 0:
        return float("inf")
    return distance / time
```

This 


We could document that time shouldn't be zero.

```python
def calculate_speed(distance:float, time:float) -> float:
    """Calculate speed given distance and time.
    
    Raises:
        ZeroDivisionError: if time is 0.
    """    
    return distance / time
```

The new version will require a bump to `major`, `minor` or `patch`.
So which value do you change?

If it is a *backwards compatible* bug fix then we increment `patch`.
Are any of our solutions backwards compatible?

The first solution swaps a `ZeroDivisionError` for an `AssertionError`.
Is that backwards compatible?
Not if the caller was handling the `ZeroDivisionError`.
Raising an `AssertionError` will likely change the behavior, and likely result in an unhandled exception.

Is the second solution a backwards compatible bug fix?
The function could potentially return `float("inf")` now, which is *technically* correct, but likely to produce confusing results for anyone who hasn't explicitly accounted for this result.

Is the third solution a backwards compatible bug fix?
Curiously, the code hasn't changed; just the documentation.
And yet this is still a valid fix, as now the dev can 


But documenting it fixes the bug, right?



Is the `ZeroDivisionError` exception a bug?
We didn't *say* it would raise this exception, but we didn't say it *wouldn't* either.
Still, `0` is as perfectly valid value for time, so I think its fair to consider this a bug.

Is it a feature worthy of a `minor` bump?
It could be considered a feature, and "Zero division error mitigation" sounds like an awesome slide for the pitch deck.

Is it a breaking change?



[^1]: *For introverts who don't wish to be invited to future parties.*
