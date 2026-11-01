import subprocess
from datetime import datetime
from pathlib import Path

project_dir = Path(__file__).resolve().parents[1]
log_file = project_dir / "pipeline.log"

def run_step(name, command):
    started_at = datetime.now()
    print(f"Начинается: {name}")
    with log_file.open("a", encoding="utf-8") as log:
        log.write(f"\n{name}\n")
        log.write(f"Начало: {started_at}\n")
        result = subprocess.run(
            command,
            cwd=project_dir,
            stdout=log,
            stderr=subprocess.STDOUT,
        )

        finished_at = datetime.now()
        log.write(f"Конец: {finished_at}\n")
        log.write(f"Код завершения: {result.returncode}\n")
    if result.returncode != 0:
        print(f"Ошибка на шаге: {name}")
        print(f"Причина записана в {log_file}")
        raise SystemExit(1)

    print(f"Готово: {name}")
    print(f"Заняло: {finished_at - started_at}")
run_step(
    "Загрузка данных",
    ["docker", "compose", "run", "--rm", "loader"],
)
run_step(
    "Построение моделей и тесты",
    ["docker", "compose", "run", "--rm", "dbt", "build"],
)
print("Весь процесс завершён.")