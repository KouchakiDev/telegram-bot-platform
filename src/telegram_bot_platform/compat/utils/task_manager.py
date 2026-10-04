import time
import threading
from typing import Callable, Dict
import logging
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger

@dataclass
class Task:
    func: Callable
    delay_minutes: int
    name: str
    last_run: float = 0
    running: bool = False


class ThreadManager:
    def __init__(self, check_interval_sec: int = 300, log_file: str = "thread_manager.log"):
        """Legacy-compatible behavior preserved for this callable."""
        self.tasks: Dict[str, Task] = {}
        self.lock = threading.RLock()
        self.running = True
        self.logger = self._setup_logger(log_file)
        self.check_interval = check_interval_sec

        # Internal implementation note: legacy behavior is preserved during modernization.
        self.monitor_thread = threading.Thread(
            target=self._monitor_tasks,
            name="ThreadManager_Monitor",
            daemon=True
        )
        self.monitor_thread.start()

        self.logger.info("ThreadManager initialized")

    def _setup_logger(self, log_file: str):
        """Legacy-compatible behavior preserved for this callable."""
        logger = CustomLogger("thredmanager")
        # logger = logging.getLogger("ThreadManager")
        
        # logger.setLevel(logging.INFO)
        # handler = RotatingFileHandler(
        #     log_file, maxBytes=5*1024*1024, backupCount=3)
        # formatter = logging.Formatter(
        #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # handler.setFormatter(formatter)
        # logger.addHandler(handler)
        return logger

    def add_task(self, func: Callable, delay_minutes: int, name: str) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        with self.lock:
            if name in self.tasks:
                self.logger.warning(f"Task '{name}' already exists")
                return False

            if delay_minutes <= 0:
                self.logger.error("Delay must be positive")
                raise ValueError("Delay must be positive")

            # Internal implementation note: legacy behavior is preserved during modernization.
            self.logger.info(f"Running initial execution for task: {name}")
            func()

            self.tasks[name] = Task(
                func=func,
                delay_minutes=delay_minutes,
                name=name,
                last_run=time.time()  # Internal implementation note: legacy behavior is preserved during modernization.
            )
            self.logger.info(f"Task added: {name} (every {delay_minutes} min)")
            return True
    def update_task(self, name: str, new_delay_minutes: int) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        with self.lock:
            if name not in self.tasks:
                self.logger.warning(f"Task '{name}' not found for update")
                return False
    
            if new_delay_minutes <= 0:
                self.logger.error("Delay must be positive")
                raise ValueError("Delay must be positive")
    
            self.tasks[name].delay_minutes = new_delay_minutes
            self.logger.info(f"Task '{name}' rescheduled → every {new_delay_minutes} min")
            return True
    
    def remove_task(self, name: str) -> bool:
        """Legacy-compatible behavior preserved for this callable."""
        with self.lock:
            if name not in self.tasks:
                self.logger.warning(f"Task '{name}' not found")
                return False

            del self.tasks[name]
            self.logger.info(f"Task removed: {name}")
            return True

    def _task_runner(self, task: Task):
        """Legacy-compatible behavior preserved for this callable."""
        while self.running and task.name in self.tasks:
            try:
                current_time = time.time()
                if current_time - task.last_run >= task.delay_minutes * 60:
                    task.running = True
                    task.last_run = current_time

                    self.logger.info(f"Starting task: {task.name}")
                    task.func()
                    self.logger.info(f"Completed task: {task.name}")

                    task.running = False

            except Exception as e:
                self.logger.error(
                    f"Error in task '{task.name}': {str(e)}",
                    exc_info=True
                )
                task.running = False

            # Sleep in small intervals to allow for quick shutdown
            for _ in range(task.delay_minutes * 60):
                if not self.running or task.name not in self.tasks:
                    break
                time.sleep(1)

    def _monitor_tasks(self):
        """Legacy-compatible behavior preserved for this callable."""
        self.logger.info("Task monitor started")
        while self.running:
            with self.lock:
                active_threads = {t.name for t in threading.enumerate()}

                for name, task in self.tasks.items():
                    thread_name = f"TaskThread_{name}"

                    # Internal implementation note: legacy behavior is preserved during modernization.
                    if thread_name not in active_threads and self.running:
                        new_thread = threading.Thread(
                            target=self._task_runner,
                            args=(task,),
                            name=thread_name,
                            daemon=True
                        )
                        new_thread.start()
                        self.logger.debug(f"Started thread for task: {name}")

            # Sleep in intervals for quick shutdown
            for _ in range(self.check_interval):
                if not self.running:
                    break
                time.sleep(1)

    def stop(self):
        """Legacy-compatible behavior preserved for this callable."""
        with self.lock:
            self.running = False
            self.tasks.clear()
            self.logger.info("ThreadManager stopped gracefully")

    def get_task_status(self) -> Dict[str, dict]:
        """Legacy-compatible behavior preserved for this callable."""
        with self.lock:
            return {
                name: {
                    "running": task.running,
                    "last_run": task.last_run,
                    "next_run": task.last_run + task.delay_minutes * 60,
                    "delay_minutes": task.delay_minutes
                }
                for name, task in self.tasks.items()
            }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


# Internal implementation note: legacy behavior is preserved during modernization.
if __name__ == "__main__":
    def sample_task():
        print("Sample task is running...")
        time.sleep(2)

    with ThreadManager() as manager:
        manager.add_task(sample_task, 1, "sample_task")
        time.sleep(10)  # Internal implementation note: legacy behavior is preserved during modernization.

    # Internal implementation note: legacy behavior is preserved during modernization.
    status = manager.get_task_status()
    print("Task status:", status)
