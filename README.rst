==================
celery-deduplicate
==================

Avoids queueing a new task if an identical task is already queued.

-----
Usage
-----

The simples possible case. Uses ``celery.shared_task`` and the default
deduplication backend. This example also highlights a case where you would 
typically not like to deduplicate a task.

.. code-block:: python

    import tempfile
    from celery_deduplicate import deduplicate_task


    @deduplicate_task()
    def increment_number_in_file(filename):
        value = int(open(filename).read())
        new_value = value + 1
        open(filename).write(new_value)

        return new_value


    with tempfile.NamedTemporaryFile() as fd:
        # Prepare the file
        fd.write('0')
        fd.flush()

        first_result = increment_number_in_file.delay(fd.name)
        second_result = increment_number_in_file.delay(fd.name)

        # They both have the same Task ID
        assert first_result.id == second_result.id

        # The task only runs once since the second call to
        # increment_number_in_file.delay() deduplicates the task
        print('first result, should be 1: {}'.format(first_result.get()))
        print('second result, should be 1: {}'.format(second_result.get()))
        print('file contains: {}'.format(open(fd.name).read()))
