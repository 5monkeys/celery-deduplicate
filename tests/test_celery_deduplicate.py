from celery import Celery
from celery_deduplicate import deduplicate_task
from celery_deduplicate.backends.memory import MemoryBackend

app = Celery('tasks', broker='amqp://guest@localhost:5672//',
             backend='amqp://guest@localhost:5672//')

deduplicated_task = deduplicate_task(task_decorator=app.task,
                                     backend=MemoryBackend)


@deduplicated_task
def task_foo(foo):
    return foo


def test_deduplicated_task():
    task_ids_1 = {result.id for result in [task_foo.delay(1),
                                           task_foo.delay(1)]}
    assert len(task_ids_1) == 1

    task_ids_2 = {result.id for result in [task_foo.delay(2),
                                           task_foo.delay(2)]}
    assert len(task_ids_2) == 1
    assert len(task_ids_1 | task_ids_2) == 2
