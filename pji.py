from dataclasses import dataclass
from typing import List
import time
import random


@dataclass
class Task:
    id: int
    name: str
    priority: int
    completed: bool = False


class TaskManager:
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, name: str, priority: int) -> None:
        task_id = len(self.tasks) + 1
        self.tasks.append(Task(task_id, name, priority))

    def process_tasks(self) -> None:
        for task in sorted(self.tasks, key=lambda t: t.priority):
            self._execute(task)

    def _execute(self, task: Task) -> None:
        print(f"[INFO] Executando tarefa #{task.id} — {task.name}")
        time.sleep(random.uniform(0.3, 0.8))
        task.completed = True
        print(f"[OK] Tarefa #{task.id} finalizada\n")


def main():
    manager = TaskManager()

    manager.add_task("Carregar configurações", priority=1)
    manager.add_task("Validar dados de entrada", priority=2)
    manager.add_task("Inicializar módulos", priority=3)
    manager.add_task("Executar rotina principal", priority=4)

    manager.process_tasks()


if __name__ == "__main__":
    main()
