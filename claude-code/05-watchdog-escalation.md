# Watchdog и эскалация застрявших задач

## Проблема

Claude Code в автономном режиме может **незаметно застрять**:

- Зациклился в анализе архитектуры (читает один и тот же код)
- Ждёт ответа от несуществующего API
- Пытается решить неразрешимую проблему
- Попал в infinite loop размышлений

**Без мониторинга** задача может "висеть" часами, потребляя ресурсы.

## Концепция Watchdog

**Watchdog** — фоновый процесс, который мониторит прогресс задачи и детектирует застревание.

### Принцип работы

```
Task Start
    ↓
Watchdog: [Monitor every 30 sec]
    ↓
Check Progress Indicators:
  - Files changed?
  - Commits made?
  - Log growing?
  - CPU/Memory usage?
    ↓
  ┌─── Yes → Continue monitoring
  │
  └─── No (5 min) → ESCALATE
         ↓
    [Kill task]
         ↓
    [Notify / Retry / Switch agent]
```

## Progress Indicators (индикаторы прогресса)

### 1. File System Activity

**Метрика**: Timestamp последней модификации файлов в worktree

```python
def check_file_activity(worktree_path, threshold=300):
    """Check if any files modified in last 5 minutes"""
    recent_files = []

    for root, dirs, files in os.walk(worktree_path):
        # Skip .git directory
        dirs[:] = [d for d in dirs if d != '.git']

        for file in files:
            filepath = os.path.join(root, file)
            mtime = os.path.getmtime(filepath)

            if time.time() - mtime < threshold:
                recent_files.append({
                    "path": filepath,
                    "modified": datetime.fromtimestamp(mtime),
                    "age_seconds": time.time() - mtime
                })

    return len(recent_files) > 0, recent_files
```

**Плюсы**: Прямой индикатор работы (код изменяется)
**Минусы**: Агент может читать, не записывая (ложное срабатывание)

---

### 2. Git Commits

**Метрика**: Количество новых коммитов в worktree

```python
def check_git_activity(worktree_path, since_minutes=5):
    """Check if new commits made recently"""
    result = subprocess.run(
        ["git", "log", f"--since={since_minutes} minutes ago", "--oneline"],
        cwd=worktree_path,
        capture_output=True,
        text=True
    )

    commits = result.stdout.strip().split('\n') if result.stdout else []
    return len(commits) > 0, commits
```

**Плюсы**: Показывает осмысленный прогресс (готовые изменения)
**Минусы**: Агент может работать долго до первого коммита

---

### 3. Log Growth

**Метрика**: Размер лог-файла задачи растёт

```python
class LogGrowthMonitor:
    def __init__(self, log_path):
        self.log_path = log_path
        self.last_size = 0
        self.last_check = time.time()

    def check_growth(self, min_growth_bytes=100):
        """Check if log file growing"""
        if not os.path.exists(self.log_path):
            return False, "Log file not found"

        current_size = os.path.getsize(self.log_path)
        growth = current_size - self.last_size

        # Update state
        self.last_size = current_size
        elapsed = time.time() - self.last_check
        self.last_check = time.time()

        if growth >= min_growth_bytes:
            return True, f"Log grew by {growth} bytes in {elapsed:.1f}s"
        else:
            return False, f"Log stagnant (only {growth} bytes in {elapsed:.1f}s)"
```

**Плюсы**: Показывает что агент "думает" (выводит в лог)
**Минусы**: Агент может спамить одно и то же (infinite loop)

---

### 4. Process Resource Usage

**Метрика**: CPU и memory usage процесса агента

```python
import psutil

class ProcessMonitor:
    def __init__(self, pid):
        self.process = psutil.Process(pid)
        self.cpu_samples = []
        self.memory_samples = []

    def check_activity(self):
        """Check if process is actively working"""
        cpu_percent = self.process.cpu_percent(interval=1.0)
        memory_mb = self.process.memory_info().rss / 1024 / 1024

        self.cpu_samples.append(cpu_percent)
        self.memory_samples.append(memory_mb)

        # Keep last 10 samples
        self.cpu_samples = self.cpu_samples[-10:]
        self.memory_samples = self.memory_samples[-10:]

        # Check patterns
        avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples)

        if avg_cpu < 5:
            return False, "CPU usage very low (idle or waiting)"
        elif avg_cpu > 90:
            return None, "CPU usage very high (possible infinite loop)"
        else:
            return True, f"CPU usage normal ({avg_cpu:.1f}%)"
```

**Плюсы**: Детектирует idle (ждёт ответа) и infinite loops (CPU spike)
**Минусы**: Не показывает осмысленность работы (может жечь CPU впустую)

---

### 5. Tool Usage Patterns

**Метрика**: Какие tools вызывает агент

```python
class ToolUsageMonitor:
    def __init__(self, log_path):
        self.log_path = log_path
        self.tool_history = []

    def parse_recent_tools(self, last_n_lines=50):
        """Parse recent tool calls from log"""
        with open(self.log_path) as f:
            lines = f.readlines()[-last_n_lines:]

        tools = []
        for line in lines:
            if "tool:" in line.lower():
                # Extract tool name (format: "Using tool: Read")
                match = re.search(r'tool:\s*(\w+)', line, re.IGNORECASE)
                if match:
                    tools.append(match.group(1))

        self.tool_history.extend(tools)
        return tools

    def detect_patterns(self):
        """Detect problematic tool usage patterns"""
        recent = self.tool_history[-20:]  # Last 20 tool calls

        # Pattern 1: Repetitive reads of same file
        if recent.count("Read") > 10:
            files = self._extract_read_targets(recent)
            if len(set(files)) == 1:
                return "stuck_reading", f"Reading same file repeatedly: {files[0]}"

        # Pattern 2: Many Grep calls without progress
        if recent.count("Grep") > 8:
            return "stuck_searching", "Too many search operations without action"

        # Pattern 3: Excessive Bash calls
        if recent.count("Bash") > 15:
            return "stuck_executing", "Too many command executions"

        # Pattern 4: Only Task calls (spawning subagents)
        if all(t == "Task" for t in recent[-5:]):
            return "stuck_delegating", "Only spawning subagents, no direct work"

        return "healthy", "Tool usage looks normal"
```

**Плюсы**: Показывает **качественный** прогресс (не просто активность)
**Минусы**: Сложнее реализовать (парсинг логов, pattern matching)

---

## Composite Progress Indicator

Комбинированная метрика из нескольких индикаторов:

```python
class ProgressWatchdog:
    def __init__(self, task):
        self.task = task
        self.indicators = {
            "files": FileActivityIndicator(task["worktree_path"]),
            "commits": GitCommitIndicator(task["worktree_path"]),
            "log": LogGrowthMonitor(task["log_path"]),
            "process": ProcessMonitor(task["pid"]),
            "tools": ToolUsageMonitor(task["log_path"])
        }
        self.last_progress_time = time.time()

    def check_progress(self):
        """Check if task is making progress (composite)"""
        results = {}

        for name, indicator in self.indicators.items():
            has_progress, details = indicator.check()
            results[name] = {
                "progress": has_progress,
                "details": details
            }

        # Decision logic: ANY indicator shows progress → not stuck
        any_progress = any(r["progress"] for r in results.values())

        if any_progress:
            self.last_progress_time = time.time()
            return True, results

        # No progress detected
        stuck_duration = time.time() - self.last_progress_time

        if stuck_duration > 300:  # 5 minutes
            return False, {
                "stuck_duration": stuck_duration,
                "indicators": results
            }

        return None, results  # Uncertain (too early to tell)
```

---

## Escalation Strategies

Когда застревание детектировано, что делать?

### Strategy 1: Notify (уведомить)

Самый мягкий вариант — просто залогировать и продолжить ждать.

```python
def escalate_notify(task, stuck_info):
    """Log warning and continue monitoring"""
    logger.warning(
        f"Task {task['id']} appears stuck for {stuck_info['stuck_duration']:.0f}s"
    )
    logger.debug(f"Progress indicators: {stuck_info['indicators']}")

    # Could send notification (email, Slack, etc.)
    # send_notification(...)
```

**Когда использовать**: Для долгих задач (> 2 часа), где 5 мин застоя нормально.

---

### Strategy 2: Interrupt (прервать)

Попытаться "разбудить" агента через signal или API.

```python
def escalate_interrupt(task, stuck_info):
    """Send interrupt signal to agent process"""
    logger.warning(f"Interrupting stuck task {task['id']}")

    # Send SIGUSR1 (custom signal agents can handle)
    os.kill(task["pid"], signal.SIGUSR1)

    # Or if agent has HTTP API:
    # requests.post(f"http://localhost:{task['port']}/interrupt")
```

**Когда использовать**: Если агент поддерживает graceful interrupts.

---

### Strategy 3: Kill and Retry (убить и перезапустить)

Жёстко убить процесс и запустить задачу заново.

```python
def escalate_kill_retry(task, stuck_info):
    """Kill stuck task and retry from beginning"""
    logger.warning(f"Killing and retrying task {task['id']}")

    # Kill process
    os.kill(task["pid"], signal.SIGKILL)

    # Clean up worktree
    subprocess.run(["git", "worktree", "remove", "--force", task["worktree_path"]])

    # Retry task (increment attempt counter)
    task["attempt"] = task.get("attempt", 0) + 1

    if task["attempt"] <= 3:
        logger.info(f"Retrying task {task['id']} (attempt {task['attempt']})")
        orchestrator.run_task(task)
    else:
        logger.error(f"Task {task['id']} failed after 3 attempts")
        mark_task_failed(task)
```

**Когда использовать**: Для коротких задач (< 1 час), когда перезапуск дешевле ожидания.

---

### Strategy 4: Escalate to Different Agent (переключить агента)

Самая интересная стратегия — передать задачу другому агенту.

```python
def escalate_switch_agent(task, stuck_info):
    """Switch to different agent (e.g., Claude → Codex)"""
    current_agent = task["runner"]
    logger.warning(f"Task {task['id']} stuck with {current_agent}, escalating to Codex")

    # Kill current process
    os.kill(task["pid"], signal.SIGKILL)

    # Prepare handoff context
    handoff = ContextHandoff()
    context_file = handoff.prepare(
        from_agent=current_agent,
        to_agent="codex",
        task=task,
        reason=f"Stuck for {stuck_info['stuck_duration']:.0f}s"
    )

    # Update task to use Codex
    task["runner"] = "codex"
    task["context_file"] = context_file
    task["escalated_from"] = current_agent

    # Restart with Codex
    logger.info(f"Restarting task {task['id']} with Codex")
    orchestrator.run_task(task)
```

**Когда использовать**: Идеально для autonomous mode — Claude застрял, Codex додавит.

---

### Strategy 5: Simplify Scope (упростить задачу)

Если задача слишком сложная — упростить её.

```python
def escalate_simplify(task, stuck_info):
    """Reduce task scope and retry"""
    logger.warning(f"Task {task['id']} stuck, simplifying scope")

    # Parse task definition
    task_md = Path(task["file"]).read_text()

    # Generate simplified version with LLM
    simplified = simplify_task_with_llm(task_md, reason=stuck_info)

    # Write simplified task
    simplified_path = task["file"].replace(".md", "_simplified.md")
    Path(simplified_path).write_text(simplified)

    # Kill and restart with simplified task
    os.kill(task["pid"], signal.SIGKILL)
    task["file"] = simplified_path
    task["simplified"] = True
    orchestrator.run_task(task)
```

**Когда использовать**: Когда задача слишком амбициозна для autonomous mode.

---

## Интеграция в Orchestrator

### Конфигурация

```json
{
  "tasks": [
    {
      "id": "complex-feature",
      "watchdog": {
        "enabled": true,
        "check_interval_seconds": 30,
        "stuck_threshold_seconds": 300,
        "indicators": [
          "files",
          "commits",
          "log",
          "tools"
        ],
        "escalation": {
          "strategy": "escalate_to_codex",
          "max_retries": 2,
          "fallback_strategy": "notify"
        }
      }
    }
  ]
}
```

### Реализация

```python
class Orchestrator:
    def run_task(self, task):
        """Run task with optional watchdog monitoring"""
        # Start task process
        process = self._start_task_process(task)
        task["pid"] = process.pid

        # Start watchdog if enabled
        if task.get("watchdog", {}).get("enabled"):
            watchdog = ProgressWatchdog(task)
            watchdog_thread = threading.Thread(
                target=self._monitor_with_watchdog,
                args=(task, watchdog),
                daemon=True
            )
            watchdog_thread.start()

        # Wait for completion or escalation
        while process.poll() is None:
            time.sleep(1)

        return self._finalize_task(task)

    def _monitor_with_watchdog(self, task, watchdog):
        """Background thread monitoring task progress"""
        config = task["watchdog"]
        check_interval = config["check_interval_seconds"]

        while True:
            time.sleep(check_interval)

            # Check if task still running
            if not psutil.pid_exists(task["pid"]):
                logger.debug(f"Task {task['id']} completed, stopping watchdog")
                break

            # Check progress
            has_progress, info = watchdog.check_progress()

            if has_progress is False:  # Stuck detected
                logger.warning(f"Watchdog detected stuck task {task['id']}")
                self._handle_escalation(task, info)
                break

    def _handle_escalation(self, task, stuck_info):
        """Handle stuck task according to escalation strategy"""
        strategy_name = task["watchdog"]["escalation"]["strategy"]
        strategies = {
            "notify": escalate_notify,
            "interrupt": escalate_interrupt,
            "kill_retry": escalate_kill_retry,
            "escalate_to_codex": escalate_switch_agent,
            "simplify": escalate_simplify
        }

        strategy_fn = strategies.get(strategy_name, escalate_notify)
        strategy_fn(task, stuck_info)
```

---

## Метрики для настройки

После внедрения watchdog, собирать статистику:

```jsonl
{"task_id": "db-schema", "stuck": false, "duration": 42, "indicators": {"files": true, "commits": true}}
{"task_id": "ui-complex", "stuck": true, "duration": 312, "stuck_at": 305, "escalation": "codex", "after_escalation_duration": 95}
{"task_id": "api-impl", "stuck": false, "duration": 67, "indicators": {"log": true, "tools": true}}
```

Анализировать:
- **False positive rate** — сколько задач ошибочно помечены как stuck
- **Detection latency** — как быстро детектируется застревание
- **Escalation effectiveness** — помогает ли эскалация завершить задачу

Настраивать:
- `stuck_threshold_seconds` — когда считать застрявшим
- `check_interval_seconds` — как часто проверять
- Набор индикаторов — какие комбинации работают лучше

---

## Визуализация прогресса

Опционально: real-time dashboard для мониторинга:

```
┌─────────────────────────────────────────────────────┐
│ Task: db-schema                       [⚠ Watching]  │
├─────────────────────────────────────────────────────┤
│ Runner: claude-code     Mode: autonomous            │
│ Duration: 8m 42s / 45m budget                       │
│                                                     │
│ Progress Indicators:                                │
│   Files changed:  ✓ (2m ago)    [=============>   ] │
│   Git commits:    ✓ (5m ago)    [========>        ] │
│   Log growth:     ✓ (12s ago)   [===============> ] │
│   CPU usage:      ✓ (42% avg)   [===========>     ] │
│   Tool patterns:  ✓ (healthy)   [===============>] │
│                                                     │
│ Recent Activity:                                    │
│   08:42 → Read: framework/tasks/db-schema.md        │
│   08:43 → Grep: "CREATE TABLE" in db/               │
│   08:44 → Write: db/migrations/001_initial.sql      │
│   08:45 → Bash: psql -f db/migrations/001_initial...│
│                                                     │
│ Status: 🟢 Making progress                          │
└─────────────────────────────────────────────────────┘
```

Реализация через curses, blessed, или rich (Python libraries для TUI).

---

**Статус**: Готов к реализации
**Приоритет**: High (критичен для autonomous mode)
**Зависимости**: Требует модификации orchestrator.py
**Следующий шаг**: Начать с простого LogGrowthMonitor, постепенно добавлять индикаторы
