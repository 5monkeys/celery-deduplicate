import inspect


def repr_call(func, positional, named, func_name=None, omit=()):
    """
    Creates a string that approximates what you would see in
    Sphinx-generated documentation.

    Example:
    >>> args = ('func_value', 'func_name_value')
    >>> kwargs = {'foo': 'bar'}
    >>> repr_call(repr_call, 'not_repr_call', *args, **kwargs)
    "not_repr_call(func='func_value, func_name='func_name_value', bar='baz')'

    @param Callable[Any, ...] func: The function to inspect for signature
    @param positional: Positional argument values for the call
    @param named: Named argument values for the call
    @param Optional[str] func_name: The name shown for the function in the
        output.
    @param omit:
    @return:
    """
    if func_name is None:
        func_name = func.__name__

    spec = inspect.getargspec(func)
    call_args = inspect.getcallargs(func, *positional, **named)

    args = inspect.formatargvalues(spec.args, spec.varargs, spec.keywords,
                                   call_args)

    return '{name}({args})'.format(name=func_name,
                                   args=args)
