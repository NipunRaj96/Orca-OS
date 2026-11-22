# Orca OS
### An AI-Assisted Operating System Wrapper for Natural Language System Management

Orca OS explores a different way of interacting with a computer: instead of requiring users to translate every task into shell commands, it allows them to describe what they want to accomplish in natural language.

The project investigates how locally hosted large language models can interpret system-level requests, understand relevant system context, generate structured commands and interact with operating-system services through a controlled execution layer.

The broader research direction is an AI-native computing environment where intelligent agents are integrated more deeply into system management. The current prototype implements this idea as a modular user-space wrapper around a conventional operating system.

**Orca OS does not currently replace the Linux kernel or implement a modified operating-system kernel.**

---

## The idea

Traditional command-line interfaces require users to know which commands to execute, how to combine them and which system resources or files they need to inspect.

Orca OS explores whether a local AI layer can bridge that gap.

A user can express an instruction such as:

```bash
orca "show me which processes are consuming the most memory"
```

The system gathers relevant context, sends the request to a locally hosted language model, interprets its structured response, validates the suggested command against predefined policies and presents the result to the user.

The objective is not simply to generate shell commands. It is to design a controlled interaction layer between natural-language instructions, AI reasoning and operating-system operations.

---

## Architecture

Orca OS is designed around modular components with clearly defined responsibilities and interfaces.

### Current prototype architecture

```text
                   USER
                     |
                     v
          Natural Language Request
                     |
                     v
             CLI / UI Overlay
                     |
                     v
             Context Provider
          /        |         \
     Processes   Memory    Disk Usage
          \        |         /
                     |
                     v
                LLM Manager
              (Local Ollama)
                     |
                     v
            Structured Response
              CommandSuggestion
                     |
                     v
             Command Validator
              /      |      \
           Execute  Clarify  Block
              |
              v
       Human Confirmation
              |
              v
         Command Executor
              |
              v
       Operating System
              |
              v
        Execution Result
```

### Core components

| Component | Responsibility |
|---|---|
| CLI and UI | Accepts natural-language requests and presents suggestions |
| Context Provider | Collects selected system information for contextual reasoning |
| LLM Manager | Communicates with the local language model and produces structured command suggestions |
| Command Models | Defines typed objects for requests, context, commands, risks and execution results |
| Policy Engine | Applies policy rules and determines permitted actions |
| Command Validator | Detects dangerous command patterns and evaluates confidence and risk |
| Command Executor | Executes approved commands with time and output limits |
| Background Daemon | Exposes a local API for communication with the system |

The Python implementation is organised into separate modules under `orca/`, including `core/`, `llm/`, `security/`, `tools/`, `ui/` and `utils/`.

### System context

The Context Provider collects information that may help the language model interpret a request, including:

- Running processes and their resource utilisation.
- Disk and memory usage.
- Recent shell commands.
- Available desktop-window information where supported.

Context collection is intentionally separated from command generation so that system information can be supplied through a defined interface.

### Local language model integration

Orca uses Ollama as its default local model interface.

The LLM Manager builds prompts using the user's request and available system context, then requests a structured response.

A typed `CommandSuggestion` model represents the generated command, confidence, proposed action, risk level, explanation and relevant context.

The structured interface helps separate model-generated suggestions from the logic that decides whether an operation should proceed.

### Command validation and execution

A language model should not be treated as an unrestricted authority over an operating system.

Orca therefore separates command generation from validation and execution.

The current implementation includes:

- Pattern-based checks for potentially destructive commands.
- Policy rules for supported command categories.
- Confidence thresholds that can request clarification.
- Risk classification for suggested operations.
- Explicit confirmation in the interactive CLI before execution.
- Execution timeouts and output-size limits.

On Linux, the current executor can use a `systemd-run` scope with CPU and memory limits. This is a resource-control mechanism, not a complete security sandbox.

On macOS, the current executor falls back to direct execution. This path does not provide the same process isolation.

Orca is an experimental prototype. Generated commands must be reviewed, and the project should be tested in an isolated development environment rather than against important personal or production systems.

---

## Broader research architecture

The research paper explores a broader architecture for an AI-native operating environment.

It considers three conceptual layers:

1. **Application Layer:** User-facing applications, system tools and AI agents.
2. **Kernel Layer:** The conventional operating-system kernel alongside a proposed AI-specific management layer.
3. **Hardware Layer:** CPU, GPU, memory, storage and networking resources.

The proposed AI-specific layer explores responsibilities such as agent coordination, scheduling, context management, memory management and resource optimisation.

An important distinction is that these are broader architectural and research directions. The current repository does not implement a second kernel, kernel-level AI scheduler or system-call interception mechanism.

The implemented intelligence, command generation, validation and execution workflow operates in user space.

---

## Research directions

Orca OS explores several directions for future development:

**Agent coordination:** Designing how specialised agents could communicate, delegate tasks and share relevant context through well-defined interfaces.

**AI-aware scheduling:** Exploring whether system workloads and AI-agent execution could be coordinated using workload-aware scheduling policies.

**Context and memory management:** Investigating how short-term task context and persistent information could be managed across user interactions and agent workflows.

**System monitoring and resource optimisation:** Exploring how AI-assisted analysis could help users understand system health and identify resource-intensive operations.

**Security and isolation:** Strengthening the boundaries between model-generated instructions, agent capabilities and operating-system operations.

**Deeper operating-system integration:** Investigating possible integration with scheduling, system-call and resource-management subsystems while preserving the reliability of the underlying operating system.

These directions form the broader research vision rather than a claim that every feature is available in the current prototype.

---

## Technology stack

| Area | Technologies |
|---|---|
| Primary language | Python |
| Local model runtime | Ollama |
| Model integration | HTTPX |
| Structured data models | Pydantic |
| CLI | Click, Rich |
| Background API | FastAPI, Uvicorn |
| System monitoring | psutil |
| Configuration | YAML |
| Validation | Policy rules and command-pattern checks |
| Testing | Pytest |
| Desktop integration | GTK / Python UI components |

---

## Getting started

Orca is an experimental Python project. A Linux development environment with Python 3.9 or later, Ollama and a systemd user session is recommended.

### 1. Clone the repository

```bash
git clone https://github.com/NipunRaj96/Orca-OS.git
cd Orca-OS
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the project

```bash
pip install -e ".[dev]"
```

Some desktop and system-integration dependencies may require additional operating-system packages.

### 4. Configure Ollama

Start the Ollama service and download the model configured in `config/orca.yaml`.

```bash
ollama serve
ollama pull llama3.1:8b
```

The default configuration points to the local Ollama endpoint:

```yaml
llm:
  base_url: "http://localhost:11434"
  model: "llama3.1:8b"
  temperature: 0.1
  max_tokens: 512
```

### 5. Try a request

Start with dry-run mode so that the suggested command is displayed without being executed.

```bash
orca "show me disk usage" --dry-run
```

Additional examples:

```bash
orca "list the running processes" --dry-run
orca "check available memory" --dry-run
orca "find large files in my home directory" --dry-run
```

### 6. Start the background daemon

```bash
orca --daemon --host 127.0.0.1 --port 8080
```

The daemon exposes the following local endpoints:

| Endpoint | Purpose |
|---|---|
| `POST /query` | Generate and validate a command suggestion |
| `POST /execute` | Submit a command suggestion to the executor |
| `GET /status` | Return daemon status |
| `GET /health` | Health check |

The daemon is intended for local experimentation. Do not expose it to untrusted networks or treat its execution endpoint as a hardened remote command-execution interface.

### 7. Run the desktop overlay

```bash
orca --overlay
```

The overlay requires the relevant desktop and GTK dependencies to be installed.

---

## Testing

The repository includes initial unit tests for command validation.

Run them with:

```bash
pytest tests/unit/
```

The current tests cover safe command handling, dangerous-pattern blocking, confidence-based clarification, shell-piping restrictions and command sanitisation.

The test coverage is still limited and should not be interpreted as a complete security verification of the system.

---

## Research paper

**Orca-OS: An Artificial Intelligence Aided Operating System Wrapper for Natural Language System Management**

Authors:
- Nipun Kumar
- Divyansh Sharma

Faculty mentor:
- Dr. Fatima Ziya, Assistant Professor, School of Computing Science and Engineering, Galgotias University.

The accompanying research paper explores the proposed architecture, its security model, system-management use cases, performance evaluation and possible directions for deeper AI integration into operating systems.

The paper reports more than 94% successful task completion, median response latency below 500 ms and automation of over 60% of low-risk tasks in its described prototype evaluation. These figures belong to the paper's reported test setup and should not be interpreted as production-wide guarantees.

The paper and associated acceptance documentation are available in [`Research-Paper/`](Research-Paper/).

---

## Project status

Orca OS is an ongoing research and prototyping project.

The current implementation focuses on a user-space natural-language system-management workflow, local LLM integration, contextual information gathering, command validation and controlled execution.

The broader AI-native operating-system architecture remains a research direction. Kernel-level integration, a dedicated AI kernel, advanced multi-agent scheduling and adaptive resource management are not implemented capabilities of the current prototype.

The repository also contains experimental distribution and packaging material under `orca-os-distro/`. These materials are exploratory and should not be confused with a verified, production-ready standalone Linux distribution.

---

**Orca OS — Exploring a more natural interface between people, AI and operating systems.**
