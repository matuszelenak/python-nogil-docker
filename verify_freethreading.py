import time
import threading
import sys
from multiprocessing import cpu_count

# Check if Python was built with free-threading support
# In Python 3.13+, sys.flags.nogil should indicate this.
# For older experimental builds, other checks might have been needed.
def check_freethreading_support():
    """Checks and prints if free-threading (no GIL) is likely enabled."""
    if sys.version_info >= (3, 13):
        status = sys._is_gil_enabled()
        if status:
            print("GIL is currently enabled.")
        else:
            print("GIL is currently disabled.")
        return status
    else:
        print("Python version does not support GIL status detection.")
        return False

# A CPU-bound task
def cpu_bound_task(n):
    """Performs a CPU-intensive calculation."""
    total = 0
    for i in range(n):
        total += i * i
    return total

def run_workload(num_threads, work_per_thread):
    """
    Runs the CPU-bound task across a specified number of threads.
    """
    threads = []
    start_time = time.perf_counter()

    for _ in range(num_threads):
        thread = threading.Thread(target=cpu_bound_task, args=(work_per_thread,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.perf_counter()
    return end_time - start_time

if __name__ == "__main__":
    has_freethreading = check_freethreading_support()
    print("-" * 50)

    # Amount of work per thread (adjust as needed for your system)
    # Larger numbers will make the CPU-bound nature more apparent.
    WORK_PER_THREAD = 50_000_000

    # Get number of available CPU cores
    available_cores = cpu_count()
    print(f"Number of available CPU cores: {available_cores}")
    print(f"Work per thread: {WORK_PER_THREAD:,} iterations of sum of squares.")
    print("-" * 50)

    thread_counts_to_test = [1, 2, 4, max(4, available_cores // 2), available_cores, available_cores * 2]
    # Ensure unique and sorted thread counts
    thread_counts_to_test = sorted(list(set(tc for tc in thread_counts_to_test if tc > 0)))


    print("Running workload with different number of threads...\n")
    results = {}

    for n_threads in thread_counts_to_test:
        print(f"Testing with {n_threads} thread(s)...")
        duration = run_workload(n_threads, WORK_PER_THREAD)
        results[n_threads] = duration
        print(f"Duration with {n_threads} thread(s): {duration:.4f} seconds")
        print("-" * 30)

    print("\n--- Summary ---")
    if not results:
        print("No tests were run.")
    else:
        baseline_duration = results.get(1)
        if baseline_duration:
            print(f"Baseline (1 thread): {baseline_duration:.4f} seconds")
            for n_threads, duration in results.items():
                if n_threads > 1:
                    speedup = baseline_duration / duration
                    print(f"{n_threads} threads: {duration:.4f} seconds (Speedup: {speedup:.2f}x)")
        else:
            for n_threads, duration in results.items():
                print(f"{n_threads} threads: {duration:.4f} seconds")


    print("\n--- Interpretation ---")
    if has_freethreading:
        print("If free-threading is working effectively for this CPU-bound task:")
        print("  - You should observe a significant speedup as the number of threads increases, ")
        print("    up to the number of physical CPU cores.")
        print("  - Performance might not scale linearly beyond the number of physical cores due to overhead.")
    else:
        print("If Python is running with the GIL:")
        print("  - You will likely NOT see a significant speedup for this CPU-bound task,")
        print("    even with multiple threads, as only one thread can hold the GIL and execute Python bytecode at a time.")
        print("  - The execution time might even increase slightly with more threads due to locking overhead.")

    print("\nNote: Real-world application performance will vary based on the nature of the tasks (CPU-bound vs. I/O-bound) and the specifics of the free-threading implementation.")