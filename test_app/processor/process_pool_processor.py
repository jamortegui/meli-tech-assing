from concurrent.futures import ProcessPoolExecutor


class Processor():
    # Interface that creates a new process to process the file in the background

    COMPLETED = "Completed!"
    PENDING = "Pending"

    def __init__(self, task_fn):
        self.task_fn = task_fn
        self._task = None

    def lauch_task(self, *args, **kwargs):
        if self._task is None:
            excecutor = ProcessPoolExecutor(1)
            self._task = excecutor.submit(self.task_fn, *args, **kwargs)
            excecutor.shutdown(wait=False)

    @property
    def status(self):
        if self._task is None():
            raise AttributeError("The task has not been launched yet.")
        elif self._task.done():
            return Processor.COMPLETED
        else:
            return Processor.PENDING
    
    @property
    def result(self):
        if self._task is None():
            raise AttributeError("The task has not been launched yet.")
        elif self._task.done():
            return self._task.result()
        else:
            return
