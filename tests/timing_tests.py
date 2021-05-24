import timeit

# Setup:
setup = 'from queue import Queue;from collections import deque;l = list(range(1000000)); q = Queue()'
repeat_times = 100

# Statements to test
statements = [
    '[q.put(i) for i in l]',
    'q.queue = deque(l)'
]

# Test each statement and output results
for s in statements:
    results = timeit.repeat(stmt=s, setup=setup, number=1, repeat=repeat_times)
    avg_time = sum(results) / len(results)
    print(f'"{s}" took {avg_time:.10f}s on average over {repeat_times} tests.')