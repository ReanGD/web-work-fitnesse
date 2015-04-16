# -*- coding: utf-8 -*-

import logging

from Queue import Queue
from threading import Thread

logger = logging.getLogger(__name__)

class Worker(Thread):
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()
    
    def run(self):
        while True:
            name, func, args, kargs = self.tasks.get()
            logger.info("start task: %s" % name)
            try:
                func(*args, **kargs)
            except Exception, e:
                logger.error("finish task %s with error: %s" % (name, str(e)))
            finally:
                logger.error("finish task %s success" % name)
                self.tasks.task_done()

class ThreadPool:
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, name, func, *args, **kargs):
        self.tasks.put((name, func, args, kargs))

    def join(self):
        self.tasks.join()

import_pool = ThreadPool(1)

if __name__ == "__main__":
    pass
