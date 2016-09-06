from abc import ABCMeta, abstractmethod


class DeduplicationBackend(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def check_duplicate(self, task, args, kwargs, **options):
        pass

    @abstractmethod
    def task_created(self, task, args, kwargs, result, **options):
        pass
