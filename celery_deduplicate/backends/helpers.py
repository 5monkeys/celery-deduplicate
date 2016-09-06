import inspect

from celery_deduplicate.helpers import repr_call


def get_key(task, args, kwargs, include=(), exclude=()):
    if not include and not exclude:
        return repr_call(task.run, args, kwargs, func_name=task.name)

    call_args = inspect.getcallargs(task.run, *args, **kwargs)

    if include and exclude:
        raise ValueError('Can\'t both include and exclude')

    if include:
        call_args = {key: value
                     for key, value in call_args.items()
                     if key in include}
    elif exclude:
        call_args = {key: value
                     for key, value in call_args.items()
                     if key not in exclude}

    args_str = ', '.join('{}={!r}'.format(key, value)
                         for key, value in call_args.items())

    return '{name}({args})'.format(name=task.name,
                                   args=args_str)
