def partition_will(pred, values):
    if not values:
        return [], []
    if len(values) == 1:
        return ([], values) if pred(values[0]) else (values, [])
    values = sorted(values, key=pred)
    lower = 0
    upper = len(values) - 1
    index = (lower + upper) // 2
    while True:
        value = pred(values[index])
        if value and not pred(values[index - 1]):
            return values[:index], values[index:]
        if value:
            upper = index
        else:
            lower = index

        index = (lower + upper) // 2


def partition_more_iter(pred, iterable):
    """
    Returns a 2-tuple of iterables derived from the input iterable.
    The first yields the items that have ``pred(item) == False``.
    The second yields the items that have ``pred(item) == True``.

        >>> is_odd = lambda x: x % 2 != 0
        >>> iterable = range(10)
        >>> even_items, odd_items = partition(is_odd, iterable)
        >>> list(even_items), list(odd_items)
        ([0, 2, 4, 6, 8], [1, 3, 5, 7, 9])

    If *pred* is None, :func:`bool` is used.

        >>> iterable = [0, 1, False, True, '', ' ']
        >>> false_items, true_items = partition(None, iterable)
        >>> list(false_items), list(true_items)
        ([0, False, ''], [1, True, ' '])

    """
    if pred is None:
        pred = bool

    evaluations = ((pred(x), x) for x in iterable)
    t1, t2 = tee(evaluations)
    return (
        (x for (cond, x) in t1 if not cond),
        (x for (cond, x) in t2 if cond),
    )
