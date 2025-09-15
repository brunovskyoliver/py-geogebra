import threading
from queue import Queue

results = Queue()


def worker():
    while True:
        value = heavy_computation()
        results.put(value)


threading.Thread(target=worker, daemon=True).start()


def poll_results():
    while not results.empty():
        value = results.get_nowait()
        # update UI or state
    root.after(100, poll_results)


poll_results()
