import logging
import multiprocessing
import time
from typing import Callable, Any, List, Dict, Tuple, Optional
import queue

logger = logging.getLogger(__name__)

# --- Worker Function ---
def worker_process(task_queue: multiprocessing.Queue, result_queue: multiprocessing.Queue):
    """
    The fundamental unit of parallel execution. This function runs in a separate process,
    continuously fetching tasks from the queue, executing them, and putting the
    results back into the result queue.
    """
    logger.info(f"Worker process {multiprocessing.current_process().name} started.")
    while True:
        try:
            task_id, func, args, kwargs = task_queue.get(timeout=1.0)
            if func is None: # Sentinel value to signal shutdown
                break
            
            logger.debug(f"Worker {multiprocessing.current_process().name} executing task {task_id}")
            result = func(*args, **kwargs)
            result_queue.put((task_id, "success", result))

        except queue.Empty:
            continue # If the queue is empty, just loop and check again
        except Exception as e:
            logger.error(f"Error in worker {multiprocessing.current_process().name} executing task {task_id}: {e}", exc_info=True)
            result_queue.put((task_id, "error", str(e)))

    logger.info(f"Worker process {multiprocessing.current_process().name} shutting down.")


class TaskPoolManager:
    """
    The Engine of Parallelism. This manager abstracts the complexity of creating and
    managing a pool of worker processes to execute tasks concurrently. It is designed
    for high-throughput workloads, enabling ArchE to distribute independent tasks
    across multiple CPU cores for significantly enhanced performance.
    """

    def __init__(self, num_workers: Optional[int] = None):
        """
        Initializes the TaskPoolManager.

        Args:
            num_workers (int, optional): The number of worker processes to spawn.
                                         Defaults to the number of CPU cores.
        """
        self.num_workers = num_workers or multiprocessing.cpu_count()
        self.task_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.workers: List[multiprocessing.Process] = []
        self.is_running = False
        logger.info(f"[TaskPoolManager] Initialized with {self.num_workers} worker(s).")

    def start(self):
        """Starts the worker processes and the result collection."""
        if self.is_running:
            logger.warning("Task pool is already running.")
            return

        for i in range(self.num_workers):
            process = multiprocessing.Process(
                target=worker_process,
                args=(self.task_queue, self.result_queue),
                name=f"ArchE-Worker-{i+1}"
            )
            self.workers.append(process)
            process.start()
        
        self.is_running = True
        logger.info("Task pool started successfully.")

    def submit_task(self, task_id: Any, func: Callable, *args, **kwargs):
        """
        Submits a new task to the task queue to be executed by a worker.

        Args:
            task_id: A unique identifier for the task to track its result.
            func (Callable): The function to execute.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.
        """
        if not self.is_running:
            raise RuntimeError("Task pool is not running. Call start() before submitting tasks.")
        self.task_queue.put((task_id, func, args, kwargs))
        logger.debug(f"Task {task_id} submitted to the queue.")

    def get_results(self, num_results: int, timeout: Optional[float] = None) -> List[Tuple[Any, str, Any]]:
        """
        Retrieves a specified number of results from the result queue.

        Args:
            num_results (int): The number of results to wait for.
            timeout (float, optional): Maximum time to wait for each result in seconds.

        Returns:
            A list of tuples, where each tuple is (task_id, status, result).
        """
        if not self.is_running:
            return []
            
        results = []
        for _ in range(num_results):
            try:
                result = self.result_queue.get(timeout=timeout)
                results.append(result)
            except queue.Empty:
                logger.warning("Timeout occurred while waiting for results.")
                break
        return results

    def shutdown(self, graceful: bool = True):
        """
        Shuts down the worker processes.

        Args:
            graceful (bool): If True, waits for workers to finish their current tasks.
                           If False, terminates them immediately.
        """
        if not self.is_running:
            return

        # Signal workers to shut down by sending the sentinel value
        for _ in range(self.num_workers):
            self.task_queue.put((None, None, None, None))

        if graceful:
            for worker in self.workers:
                worker.join() # Wait for the process to finish
        else:
            for worker in self.workers:
                worker.terminate() # Forcefully stop the process

        self.is_running = False
        self.workers = []
        logger.info("Task pool has been shut down.")


# --- Test Harness ---
def sample_task(duration: float, value: Any) -> Any:
    """A simple task that simulates work by sleeping."""
    print(f"  > Task with value '{value}' running in {multiprocessing.current_process().name}...")
    time.sleep(duration)
    return f"Completed: {value}"

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("\n--- [1] Testing Scalable Framework ---")
    # Use 2 workers for the test
    pool_manager = TaskPoolManager(num_workers=2)
    
    try:
        # Start the pool
        pool_manager.start()

        # Submit some tasks
        print("\n--- Submitting 4 tasks to a pool of 2 workers ---")
        tasks_to_run = {
            "task1": (1.0, "A"),
            "task2": (0.5, "B"),
            "task3": (0.7, "C"),
            "task4": (0.3, "D")
        }
        for task_id, args in tasks_to_run.items():
            pool_manager.submit_task(task_id, sample_task, *args)
        
        # Collect the results
        print("\n--- Waiting for results ---")
        results = pool_manager.get_results(num_results=len(tasks_to_run), timeout=5.0)

        print("\n--- Collected Results ---")
        for task_id, status, result in sorted(results):
            print(f"  - ID: {task_id}, Status: {status}, Result: {result}")
        
        assert len(results) == len(tasks_to_run)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Shutdown the pool
        print("\n--- Shutting down the task pool ---")
        pool_manager.shutdown()

if __name__ == "__main__":
    # This is necessary for multiprocessing on some platforms (e.g., Windows)
    multiprocessing.freeze_support()
    main()
