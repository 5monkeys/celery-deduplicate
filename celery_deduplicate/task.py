from __future__ import absolute_import

import logging

import celery
from celery import shared_task

from celery_deduplicate.backends.django_cache import DjangoCacheBackend

_log = logging.getLogger(__name__)


class DeduplicateTask(celery.Task):
    """
    A celery Task class that tries to avoid having multiple tasks queued for
    the same job.

    Usage:

    >>> from celery import shared_task
    >>> set_foo_call_count = 0
    >>> foo = None
    >>> @shared_task(base=DeduplicateTask)
    >>> def set_foo(value):
    ...     global foo, set_foo_call_count
    ...     set_foo_call_count += 1
    ...     foo = value
    ...     return 'foo has been set to {}'.format(value)
    >>> # Trigger task for set_foo(value='bar')
    >>> first_result = set_foo.delay('bar')
    >>> # Trigger it again, this time no new task will be queued, and we
    >>> # will receive the AsyncResult for the previously queued task
    >>> second_result = set_foo.delay('bar')
    >>> assert first_result.id == second_result.id
    """
    def __init__(self):
        self.deduplicate_options = {}
        super(celery.Task, self).__init__()

    def set_deduplicate_options(self, **options):
        self.deduplicate_options = options

    def run(self, *args, **kwargs):
        return super(DeduplicateTask, self).run(*args, **kwargs)

    def apply_async(self, args=None, kwargs=None, **options):
        if 'backend' not in self.deduplicate_options:
            raise ValueError('deduplicate_backend is not set')
        else:
            backend = self.deduplicate_options['backend']()

        result = backend.check_duplicate(self, args, kwargs,
                                         **self.deduplicate_options)
        if result is not None:
            return result

        result = super(DeduplicateTask, self).apply_async(args, kwargs,
                                                          **options)

        backend.task_created(self, args, kwargs, result,
                             **self.deduplicate_options)
        return result


def deduplicate_task(task_decorator=shared_task,
                     include=(),
                     exclude=(),
                     backend=DjangoCacheBackend,
                     timeout=None,
                     **task_kwargs):
    """
    Example:

    >>> from myproject.celery import app
    >>> deduplicated_task = deduplicate_task(app.task)
    >>> @deduplicated_task
    >>> def do_foo(bar):
    ...     return bar
    @param include: Args to include in deduplication
    @param exclude: Args to exclude in deduplication
    @param task_decorator: The base task decorator, e.g. ``app.task`` or
    ``shared_task``.
    @param timeout: Deduplication timeout. If a duplicate task was created
    more than ``timeout`` seconds ago, a duplicate task will be executed.
    @param backend: The deduplication backend to use.
    @return:
    """
    deduplicate_options = {
        'timeout': timeout,
        'include': include,
        'exclude': exclude,
        'backend': backend,
    }
    _task_decorator = task_decorator(base=DeduplicateTask, force_evaluate=True,
                                     **task_kwargs)

    def decorator(func):
        task = _task_decorator(func)
        task.set_deduplicate_options(**deduplicate_options)
        return task

    return decorator
