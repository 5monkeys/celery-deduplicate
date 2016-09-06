import logging

from celery_deduplicate.backends.helpers import get_key
from .base import DeduplicationBackend

_log = logging.getLogger(__name__)

TASKS = {}


class MemoryBackend(DeduplicationBackend):
    def check_duplicate(self, task, args, kwargs, **options):
        include, exclude = options.pop('include'), options.pop('exclude')
        task_key = get_key(task, args, kwargs,
                           include=include,
                           exclude=exclude)

        active_task_id = TASKS.get(task_key)

        if active_task_id is not None:
            _log.debug('Found duplicate %r for key %r in cache',
                       active_task_id,
                       task_key)
            # Assure that the task has not failed to remove its lock
            result = task.AsyncResult(active_task_id)
            if not result.ready():
                return result
            else:
                _log.warning('Duplicate %r for key %r found in cache, '
                             'but task is ready()',
                             active_task_id,
                             task_key)
        else:
            _log.debug('No duplicate for key %r', task_key)

    def task_created(self, task, args, kwargs, result, **options):
        timeout = options.pop('timeout')
        if timeout is not None:
            raise Exception('timeout not supported by MemoryBackend')
        include, exclude = options.pop('include'), options.pop('exclude')
        task_key = get_key(task, args, kwargs,
                           include=include,
                           exclude=exclude)
        TASKS[task_key] = result.id
