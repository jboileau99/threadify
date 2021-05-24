import os
import sys
import types
import logging
from queue import Queue
from threading import Thread
from collections import deque
from typing import Iterable, Type


class Threadify:

    def __init__(self, function, data=None, max_threads=None, logger=None):
        self.function = function
        self.data = data
        self.max_threads = max_threads
        self.logger = logger

        self.q = Queue()
        self.threads = []

    ### Properties and their related private methods ###

    @property
    def function(self):
        return self._function

    @function.setter
    def function(self, value):
        if type(value) is not types.FunctionType:
            raise TypeError(f"function arguement must be of type {str(types.FunctionType)}")
        else:
            self._function = value

    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, value):
        try:
            iter(value)
            self._data = value
        except TypeError as e:
            # Raise a more detailed exception
            raise TypeError(f"Type {type(value).__name__} is not iterable, data passed to threads must be iterable")

    @property
    def max_threads(self):
        return self._max_threads

    @max_threads.setter
    def max_threads(self, value):
        self._max_threads = value if value is not None else self._determine_max_threads()

    def _determine_max_threads(self):
        """Figure out the max threads a machine should run"""
        return 10 # For now lets just do 10 threads until we figure out how to determine this

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, value):
        if value is None:
            self._get_default_logger()
        elif type(value) is not logging.Logger:
            raise TypeError(f"logger arguement must either be empty or type {str(logging.Logger)}")
        else:
            self._logger = value
    
    def _get_default_logger(self):
        """Get a default logger for the multithreaded function if one wasn't passed in"""

        log_name = self.function.__name__
        log_format = '[%(asctime)s][%(levelname)s][%(thread)s] %(message)s'
        log_fp = os.path.dirname(os.path.realpath(sys.argv[0]))

        logger = logging.getLogger(log_name)
        # Setup the format for both file and console streams
        formatter = logging.Formatter(log_format, "%H:%M:%S")
        # Setup file logger stream
        file_handler = logging.FileHandler(filename=log_fp, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        # Setup console logger stream
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.ERROR)
        # Add both handlers to this log
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        logger.setLevel(logging.INFO)

        return logger
    
    ### Threading methods ###

    def go(self):
        
        # Fill queue with data
        self.q.queue = deque(self.data) # 3 orders of mag. faster than [self.q.put(i) for i in self.data] for 1mil. items
        
        # Set up threads and add stoppers to queue
        for i in range(self.max_threads):
            new_thread = Thread(target=self.single_thread) # TODO: Add arguement support
            new_thread.start()
            self.threads.append(new_thread)
        
        self.q.join()
        for i in range(self.max_threads):
            self.q.put(None)

        for t in self.threads:
            t.join()

    def single_thread(self):

        while True:
            
            # Get more data or stop processing if stopper reached
            item = self.q.get()
            if item is None:
                break

            # Execute function and store results/errors
            try:
                result = self.function(item)
                # Add result to output iterable here --> what kind of object? input must be mapped to output somehow
            except Exception as e:
                pass # TODO: log error here, will have to pass logger into each thread as arg

            self.q.task_done() # q.join will block until # of q.task_done() calls == # of q.puts()
            # TODO DUE TO THE ABOVE DOES USING q.queue = deque(l) even work?? 