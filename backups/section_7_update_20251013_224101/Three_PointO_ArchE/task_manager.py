from typing import Dict, Any, List

class TaskManager:
    """
    Manages tasks within a workflow, including their dependencies and status.
    """
    def __init__(self, tasks: Dict[str, Any]):
        self.tasks = tasks
        self.task_statuses = {key: "pending" for key in tasks}

    def get_ready_tasks(self) -> List[str]:
        """
        Returns a list of tasks whose dependencies have been met.
        """
        ready_tasks = []
        for task_id, task in self.tasks.items():
            if self.task_statuses[task_id] == "pending":
                dependencies = task.get("dependencies", [])
                if all(self.task_statuses.get(dep) == "completed" for dep in dependencies):
                    ready_tasks.append(task_id)
        return ready_tasks

    def update_task_status(self, task_id: str, status: str):
        """Updates the status of a task."""
        if task_id in self.task_statuses:
            self.task_statuses[task_id] = status 