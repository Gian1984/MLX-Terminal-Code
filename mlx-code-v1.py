#!/usr/bin/env python3
# mlx-code: enhanced local coding assistant for ~/Projects
# Requires: pip install mlx-lm

import os
import sys
import re
import textwrap
import difflib
import json
import shutil
import threading
import time
import glob
from datetime import datetime
from typing import List, Tuple, Optional, Dict
from pathlib import Path

try:
    from mlx_lm import load, generate
except ImportError:
    print("ERROR: mlx-lm not found. Install with: pip install mlx-lm")
    sys.exit(1)

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

ROOT_DIR = os.path.expanduser("~/Projects")
LOG_DIR = os.path.expanduser("~/.mlx-code")
BACKUP_DIR = os.path.join(LOG_DIR, "backups")
HISTORY_FILE = os.path.join(LOG_DIR, "history.log")
CONFIG_FILE = os.path.join(LOG_DIR, "config.json")

DEFAULT_MODEL = "mlx-community/qwen2.5-coder-7b-instruct-4bit"

MODEL_ALIASES = {
    "q7b": "mlx-community/qwen2.5-coder-7b-instruct-4bit",
    "q3b": "mlx-community/qwen2.5-coder-3b-instruct-4bit",
    "q1.5b": "mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit",
}

DEFAULT_MAX_TOKENS = 1024
DEFAULT_CTX_CHARS = 20000

ALLOWED_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
    '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.r',
    '.html', '.css', '.scss', '.sass', '.less', '.vue', '.svelte',
    '.json', '.yaml', '.yml', '.toml', '.xml', '.md', '.txt', '.sh', '.bash',
    '.sql', '.graphql', '.proto', '.dockerfile', '.makefile', '.cmake'
}

TEMPLATES = {
    "test": "Create comprehensive unit tests for the following code. Use appropriate testing framework and include edge cases:\n\n",
    "doc": "Add detailed documentation and docstrings to the following code. Include parameter descriptions, return values, and examples:\n\n",
    "refactor": "Refactor the following code to improve readability, maintainability, and performance. Follow clean code principles:\n\n",
    "review": "Perform a thorough code review of the following code. Point out potential bugs, security issues, and suggest improvements:\n\n",
    "optimize": "Optimize the following code for better performance. Identify bottlenecks and suggest algorithmic improvements:\n\n",
    "explain": "Explain the following code in detail. Break down what each part does and why:\n\n",
}

BACKTICKS = "```"

# ---------------------------------------------------------------------------
# COLORS
# ---------------------------------------------------------------------------

RESET = "\033[0m"
BOLD = "\033[1m"

FG_RED = "\033[31m"
FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_BLUE = "\033[34m"
FG_MAGENTA = "\033[35m"
FG_CYAN = "\033[36m"
FG_WHITE = "\033[37m"

DIM = "\033[2m"
BG_RED = "\033[41m"


# ---------------------------------------------------------------------------
# LOADING SPINNER
# ---------------------------------------------------------------------------

class Spinner:
    """Simple loading spinner for long operations."""

    def __init__(self, message="Working"):
        self.message = message
        self.running = False
        self.thread = None

    def _spin(self):
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        idx = 0
        while self.running:
            sys.stdout.write(f"\r{FG_CYAN}{chars[idx]} {self.message}...{RESET}")
            sys.stdout.flush()
            idx = (idx + 1) % len(chars)
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()


# ---------------------------------------------------------------------------
# LOGGING & CONFIG
# ---------------------------------------------------------------------------

def ensure_directories():
    """Create necessary directories."""
    os.makedirs(ROOT_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)


def log_operation(operation: str, details: str):
    """Log operations to history file."""
    try:
        timestamp = datetime.now().isoformat()
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {operation}: {details}\n")
    except Exception as e:
        print(f"{FG_YELLOW}Warning: Could not write to log: {e}{RESET}")


def load_config() -> Dict:
    """Load user configuration."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config(config: Dict):
    """Save user configuration."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"{FG_YELLOW}Warning: Could not save config: {e}{RESET}")


# ---------------------------------------------------------------------------
# UTILS: SAFE PATHS
# ---------------------------------------------------------------------------

def is_safe_path(path: str) -> bool:
    """True if path is inside ROOT_DIR."""
    root = os.path.realpath(ROOT_DIR)
    target = os.path.realpath(path)
    return target == root or target.startswith(root + os.sep)


def resolve_path(user_path: str, current_dir: str) -> str:
    """Resolve a user path (relative or absolute) within ROOT_DIR."""
    if not user_path:
        return os.path.realpath(current_dir)
    if os.path.isabs(user_path):
        candidate = user_path
    else:
        candidate = os.path.join(current_dir, user_path)
    real = os.path.realpath(candidate)
    return real


def is_allowed_file(path: str) -> bool:
    """Check if file extension is allowed for modification."""
    ext = os.path.splitext(path)[1].lower()
    return ext in ALLOWED_EXTENSIONS or ext == ''


# ---------------------------------------------------------------------------
# PROJECT DETECTION
# ---------------------------------------------------------------------------

def detect_project_type(cwd: str) -> Optional[str]:
    """Detect project type based on files present."""
    markers = {
        "python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
        "nodejs": ["package.json", "yarn.lock", "pnpm-lock.yaml"],
        "rust": ["Cargo.toml"],
        "go": ["go.mod"],
        "java": ["pom.xml", "build.gradle"],
        "ruby": ["Gemfile"],
        "php": ["composer.json"],
    }

    for project_type, files in markers.items():
        for marker in files:
            if os.path.exists(os.path.join(cwd, marker)):
                return project_type
    return None


# ---------------------------------------------------------------------------
# BACKUP SYSTEM
# ---------------------------------------------------------------------------

def create_backup(file_path: str) -> Optional[str]:
    """Create a timestamped backup of a file before modification."""
    if not os.path.exists(file_path):
        return None

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rel_path = os.path.relpath(file_path, ROOT_DIR)
        backup_name = f"{rel_path.replace(os.sep, '_')}_{timestamp}"
        backup_path = os.path.join(BACKUP_DIR, backup_name)

        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"{FG_YELLOW}Warning: Could not create backup: {e}{RESET}")
        return None


def list_backups(file_path: str = None) -> List[str]:
    """List available backups for a file or all backups."""
    try:
        backups = sorted(os.listdir(BACKUP_DIR), reverse=True)
        if file_path:
            rel_path = os.path.relpath(file_path, ROOT_DIR)
            prefix = rel_path.replace(os.sep, '_')
            backups = [b for b in backups if b.startswith(prefix)]
        return backups
    except Exception:
        return []


def restore_backup(backup_name: str, target_path: str) -> bool:
    """Restore a file from backup."""
    try:
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        if not os.path.exists(backup_path):
            return False
        shutil.copy2(backup_path, target_path)
        return True
    except Exception as e:
        print(f"{FG_RED}Error restoring backup: {e}{RESET}")
        return False


# ---------------------------------------------------------------------------
# FILE TREE
# ---------------------------------------------------------------------------

def print_tree(directory: str, prefix: str = "", max_depth: int = 3, current_depth: int = 0):
    """Print directory tree structure."""
    if current_depth >= max_depth:
        return

    try:
        entries = sorted(os.listdir(directory))
        entries = [e for e in entries if not e.startswith('.')]

        for i, entry in enumerate(entries):
            path = os.path.join(directory, entry)
            is_last = i == len(entries) - 1

            connector = "└── " if is_last else "├── "
            if os.path.isdir(path):
                print(f"{prefix}{connector}{FG_BLUE}{entry}/{RESET}")
                extension = "    " if is_last else "│   "
                print_tree(path, prefix + extension, max_depth, current_depth + 1)
            else:
                print(f"{prefix}{connector}{entry}")
    except PermissionError:
        print(f"{prefix}{FG_RED}[Permission Denied]{RESET}")


# ---------------------------------------------------------------------------
# GREP FUNCTIONALITY
# ---------------------------------------------------------------------------

def grep_files(pattern: str, directory: str, extensions: set = None) -> List[Tuple[str, int, str]]:
    """Search for pattern in files. Returns list of (file, line_num, line_content)."""
    results = []
    try:
        regex = re.compile(pattern, re.IGNORECASE)
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1]

                if extensions and ext not in extensions:
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                results.append((file_path, line_num, line.rstrip()))
                except Exception:
                    continue
    except Exception as e:
        print(f"{FG_RED}Error during search: {e}{RESET}")

    return results


# ---------------------------------------------------------------------------
# PROMPT / CHAT SESSION
# ---------------------------------------------------------------------------

class ChatSession:
    def __init__(self, model_name: str, max_tokens: int, ctx_chars: int):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.ctx_chars = ctx_chars
        self.history: List[Tuple[str, str]] = []
        self.opened_files: List[str] = []
        self.last_query: str = ""
        self.last_modified_files: List[str] = []
        self.stats = {
            "queries": 0,
            "files_modified": 0,
            "tokens_generated": 0,
        }

        spinner = Spinner("Loading model")
        spinner.start()
        try:
            self.model, self.tokenizer = load(model_name)
            spinner.stop()
            print(f"{FG_GREEN}✓ Model loaded successfully{RESET}")
        except Exception as e:
            spinner.stop()
            print(f"{FG_RED}✗ Failed to load model: {e}{RESET}")
            sys.exit(1)

        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        return textwrap.dedent(
            f"""
            You are MLX-CODE, an advanced local coding assistant running in the macOS terminal.

            RULES:
            - You ONLY have access to files under the directory "{ROOT_DIR}".
            - Be concise but thorough. Focus on code quality and best practices.
            - Always return well-formatted, production-ready code with proper indentation.
            - When suggesting changes, explain WHY, not just WHAT.

            CONTEXT AWARENESS:
            - The current working directory is provided in each message.
            - Files opened with /open are in your context - reference them naturally.
            - Consider the project type when making suggestions.

            FILE EDITING PROTOCOL (CRITICAL):
            When creating or modifying files, use this EXACT format:

            ```file:relative/or/absolute/path.ext
            <complete file content here>
            ```

            - Paths should be relative to the current working directory when possible.
            - The content MUST be the complete desired file content, not a diff or patch.
            - You can output multiple file blocks in one response.
            - Outside file blocks, briefly explain your changes and reasoning.

            CODE QUALITY:
            - Follow language-specific best practices and conventions.
            - Include appropriate error handling.
            - Add comments for complex logic.
            - Consider edge cases and potential bugs.

            SECURITY:
            - Never suggest code with obvious security vulnerabilities.
            - Warn about potential security issues in existing code.
            - Be cautious with file operations, API keys, and user input.

            OUTPUT FORMAT:
            - Use markdown for formatting.
            - Use code blocks with language hints (```python, ```javascript, etc).
            - Keep responses focused and actionable.
            """
        ).strip()

    def _build_prompt(self, user_message: str, current_dir: str, project_type: Optional[str]) -> str:
        """Build full prompt including system + history + context."""
        context_parts = [f"Current working directory: {current_dir}"]

        if project_type:
            context_parts.append(f"Detected project type: {project_type}")

        if self.opened_files:
            context_parts.append(f"Files in context: {', '.join(self.opened_files)}")

        context = "\n".join(context_parts)
        user_with_ctx = f"{context}\n\n{user_message}"

        parts: List[str] = [self.system_prompt, ""]

        # Add prioritized history
        for role, txt in self._get_prioritized_history():
            parts.append(f"{role.capitalize()}: {txt}")

        parts.append(f"User: {user_with_ctx}")
        parts.append("Assistant:")
        return "\n\n".join(parts)

    def _get_prioritized_history(self) -> List[Tuple[str, str]]:
        """Get history with intelligent prioritization."""
        if not self.history:
            return []

        # Always keep last 3 exchanges
        recent = self.history[-6:] if len(self.history) >= 6 else self.history

        # Add file context messages
        file_messages = [
            (r, t) for r, t in self.history[:-6]
            if "Opened file" in t or "```file:" in t
        ]

        # Combine and ensure uniqueness
        combined = file_messages + recent
        seen = set()
        result = []
        for r, t in combined:
            if t not in seen:
                result.append((r, t))
                seen.add(t)

        return result

    def _trim_history(self):
        """Smart context control by character budget."""
        total = sum(len(t) for _, t in self.history)
        if total <= self.ctx_chars:
            return

        # Keep recent messages, trim older ones
        while self.history and total > self.ctx_chars:
            # Don't remove file context if possible
            removed = False
            for i in range(len(self.history)):
                role, txt = self.history[i]
                if "Opened file" not in txt and "```file:" not in txt:
                    self.history.pop(i)
                    total -= len(txt)
                    removed = True
                    break

            if not removed and self.history:
                role, txt = self.history.pop(0)
                total -= len(txt)

    def ask(self, user_message: str, current_dir: str, project_type: Optional[str] = None) -> str:
        """Send a query to the model."""
        self.last_query = user_message
        self.stats["queries"] += 1

        prompt = self._build_prompt(user_message, current_dir, project_type)

        spinner = Spinner("Generating response")
        spinner.start()

        try:
            response = generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=self.max_tokens,
                verbose=False,
            )
            spinner.stop()
        except Exception as e:
            spinner.stop()
            return f"Error generating response: {e}"

        if not isinstance(response, str):
            response = str(response)

        # Update statistics
        self.stats["tokens_generated"] += len(response.split())

        # Update history
        self.history.append(("user", user_message))
        self.history.append(("assistant", response))
        self._trim_history()

        return response


# ---------------------------------------------------------------------------
# PARSING ASSISTANT OUTPUT
# ---------------------------------------------------------------------------

FILE_BLOCK_RE = re.compile(
    r"```file:(?P<path>[^\n\r]+)\n(?P<content>.*?)(?:```|\Z)",
    re.DOTALL,
)

CODE_BLOCK_RE = re.compile(
    r"```(?P<lang>[^\n\r]*)\n(?P<content>.*?)(?:```|\Z)",
    re.DOTALL,
)


def extract_file_blocks(text: str):
    """Return list of dicts with path/content from ```file:...``` blocks."""
    blocks = []
    for m in FILE_BLOCK_RE.finditer(text):
        path = m.group("path").strip()
        content = m.group("content")
        blocks.append({"path": path, "content": content})
    return blocks


def extract_code_blocks(text: str):
    """Return list of generic fenced code blocks (not file: blocks)."""
    blocks = []
    for m in CODE_BLOCK_RE.finditer(text):
        if m.group("lang").strip().startswith("file:"):
            continue
        lang = m.group("lang").strip()
        content = m.group("content")
        blocks.append({"lang": lang, "content": content})
    return blocks


def print_colored_response(text: str):
    """Markdown-aware coloring for assistant output."""
    lines = text.splitlines()
    in_code = False
    for line in lines:
        if line.strip().startswith("```"):
            print(FG_YELLOW + line + RESET)
            in_code = not in_code
            continue

        if in_code:
            print(FG_MAGENTA + line + RESET)
        else:
            # Bold for headers
            if line.startswith("#"):
                print(BOLD + FG_CYAN + line + RESET)
            else:
                print(FG_CYAN + line + RESET)


def print_diff(old: str, new: str, path_display: str):
    """Print colored unified diff."""
    print(f"\n{FG_WHITE}{BOLD}{'─' * 60}{RESET}")
    print(f"{FG_WHITE}{BOLD}Changes for: {path_display}{RESET}")
    print(f"{FG_WHITE}{BOLD}{'─' * 60}{RESET}")

    diff = difflib.unified_diff(
        old.splitlines(),
        new.splitlines(),
        fromfile="original",
        tofile="modified",
        lineterm="",
    )

    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            print(FG_GREEN + line + RESET)
        elif line.startswith("-") and not line.startswith("---"):
            print(FG_RED + line + RESET)
        elif line.startswith("@@"):
            print(FG_YELLOW + line + RESET)
        else:
            print(DIM + line + RESET)
    print(f"{FG_WHITE}{BOLD}{'─' * 60}{RESET}\n")


def apply_file_changes(blocks, current_dir: str, session: ChatSession):
    """Process and apply file changes with safety checks."""
    if not blocks:
        return

    print(f"\n{FG_YELLOW}Found {len(blocks)} file(s) to modify{RESET}\n")

    changes_to_apply = []

    for block in blocks:
        rel_path = block["path"].strip()
        abs_path = resolve_path(rel_path, current_dir)

        # Safety checks
        if not is_safe_path(abs_path):
            print(f"{BG_RED}{FG_WHITE} BLOCKED {RESET} {FG_RED}Path outside sandbox: {abs_path}{RESET}")
            log_operation("BLOCKED_WRITE", abs_path)
            continue

        if not is_allowed_file(abs_path):
            print(f"{FG_YELLOW}⚠ Warning: {abs_path} has unusual extension{RESET}")
            confirm = input(f"{FG_YELLOW}Continue anyway? [y/N] {RESET}").strip().lower()
            if confirm != 'y':
                continue

        new_content = block["content"].rstrip("\n") + "\n"

        # Read existing content
        old_content = ""
        if os.path.exists(abs_path):
            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    old_content = f.read()
            except Exception as e:
                print(f"{FG_RED}Cannot read existing file {abs_path}: {e}{RESET}")
                continue

        rel_display = os.path.relpath(abs_path, ROOT_DIR)

        # Show diff
        if old_content:
            print_diff(old_content, new_content, rel_display)
        else:
            print(f"\n{FG_WHITE}{BOLD}{'─' * 60}{RESET}")
            print(f"{FG_GREEN}+ NEW FILE: {rel_display}{RESET}")
            print(f"{FG_WHITE}{BOLD}{'─' * 60}{RESET}")
            print(FG_MAGENTA + new_content[:500] + ("..." if len(new_content) > 500 else "") + RESET)
            print(f"{FG_WHITE}{BOLD}{'─' * 60}{RESET}\n")

        changes_to_apply.append({
            "path": abs_path,
            "display": rel_display,
            "old": old_content,
            "new": new_content,
        })

    if not changes_to_apply:
        return

    # Batch confirmation
    print(f"\n{FG_YELLOW}{'═' * 60}{RESET}")
    print(f"{FG_YELLOW}Ready to apply changes to {len(changes_to_apply)} file(s){RESET}")
    print(f"{FG_YELLOW}{'═' * 60}{RESET}")

    for change in changes_to_apply:
        print(f"  • {change['display']}")

    print(f"\n{FG_YELLOW}Options:{RESET}")
    print(f"  {FG_GREEN}[a]{RESET} Apply all")
    print(f"  {FG_CYAN}[i]{RESET} Apply individually")
    print(f"  {FG_RED}[n]{RESET} Cancel")

    choice = input(f"\n{FG_YELLOW}Your choice: {RESET}").strip().lower()

    if choice == 'a':
        for change in changes_to_apply:
            _write_file(change, session)
    elif choice == 'i':
        for change in changes_to_apply:
            ans = input(f"{FG_YELLOW}Apply changes to {change['display']}? [y/N] {RESET}").strip().lower()
            if ans == 'y':
                _write_file(change, session)
    else:
        print(f"{FG_CYAN}Cancelled. No files were modified.{RESET}")


def _write_file(change: Dict, session: ChatSession):
    """Write a single file with backup."""
    try:
        # Create backup if file exists
        if change["old"]:
            backup_path = create_backup(change["path"])
            if backup_path:
                print(f"{FG_BLUE}  ✓ Backup created{RESET}")

        # Write new content
        os.makedirs(os.path.dirname(change["path"]), exist_ok=True)
        with open(change["path"], "w", encoding="utf-8") as f:
            f.write(change["new"])

        print(f"{FG_GREEN}  ✓ Wrote {change['display']}{RESET}")

        # Update statistics and tracking
        session.stats["files_modified"] += 1
        session.last_modified_files.append(change["path"])
        log_operation("FILE_WRITE", change["display"])

    except Exception as e:
        print(f"{FG_RED}  ✗ Error writing {change['path']}: {e}{RESET}")
        log_operation("FILE_WRITE_ERROR", f"{change['path']}: {e}")


def maybe_save_code_block(text: str, current_dir: str, session: ChatSession):
    """Offer to save code blocks that aren't in file: format."""
    blocks = extract_code_blocks(text)
    if not blocks:
        return

    first = blocks[0]
    lang = first["lang"] or "txt"
    content = first["content"].rstrip("\n") + "\n"

    print(f"\n{FG_YELLOW}Detected a code block (language: {lang or 'plain text'}).{RESET}")
    ans = input(
        f"{FG_YELLOW}Save this code to a file? (enter filename or leave blank to skip): {RESET}"
    ).strip()

    if not ans:
        return

    # Suggest extension based on language
    if '.' not in ans and lang:
        ext_map = {
            'python': '.py', 'javascript': '.js', 'typescript': '.ts',
            'java': '.java', 'cpp': '.cpp', 'c': '.c', 'go': '.go',
            'rust': '.rs', 'ruby': '.rb', 'php': '.php', 'html': '.html',
            'css': '.css', 'json': '.json', 'yaml': '.yaml', 'sql': '.sql',
        }
        ext = ext_map.get(lang.lower(), '.txt')
        ans += ext
        print(f"{FG_CYAN}Using filename: {ans}{RESET}")

    abs_path = resolve_path(ans, current_dir)
    if not is_safe_path(abs_path):
        print(f"{FG_RED}Cannot save outside sandbox {ROOT_DIR}{RESET}")
        return

    old_content = ""
    if os.path.exists(abs_path):
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                old_content = f.read()
        except Exception as e:
            print(f"{FG_RED}Error reading existing file: {e}{RESET}")

    rel_display = os.path.relpath(abs_path, ROOT_DIR)

    if old_content:
        print_diff(old_content, content, rel_display)
    else:
        print(f"\n{FG_GREEN}+ NEW FILE: {rel_display}{RESET}")
        print(FG_MAGENTA + content[:500] + ("..." if len(content) > 500 else "") + RESET)

    confirm = input(f"{FG_YELLOW}Write code to {rel_display}? [y/N] {RESET}").strip().lower()
    if confirm == 'y':
        change = {
            "path": abs_path,
            "display": rel_display,
            "old": old_content,
            "new": content,
        }
        _write_file(change, session)


# ---------------------------------------------------------------------------
# COMMAND HANDLERS
# ---------------------------------------------------------------------------

def handle_tree(parts: List[str], cwd: str):
    """Handle /tree command."""
    if len(parts) > 1:
        target = resolve_path(" ".join(parts[1:]), cwd)
    else:
        target = cwd

    if not is_safe_path(target):
        print(f"{FG_RED}Cannot access outside sandbox{RESET}")
        return

    if not os.path.isdir(target):
        print(f"{FG_RED}Not a directory: {target}{RESET}")
        return

    print(f"\n{FG_CYAN}Directory structure:{RESET}")
    print(f"{FG_BLUE}{target}/{RESET}")
    print_tree(target)
    print()


def handle_grep(parts: List[str], cwd: str):
    """Handle /grep command."""
    if len(parts) < 2:
        print(f"{FG_RED}Usage: /grep <pattern> [path]{RESET}")
        return

    pattern = parts[1]
    if len(parts) > 2:
        target = resolve_path(" ".join(parts[2:]), cwd)
    else:
        target = cwd

    if not is_safe_path(target):
        print(f"{FG_RED}Cannot search outside sandbox{RESET}")
        return

    print(f"{FG_CYAN}Searching for '{pattern}'...{RESET}")
    results = grep_files(pattern, target, ALLOWED_EXTENSIONS)

    if not results:
        print(f"{FG_YELLOW}No matches found.{RESET}")
        return

    print(f"\n{FG_GREEN}Found {len(results)} match(es):{RESET}\n")
    for file_path, line_num, line_content in results[:50]:  # Limit to 50 results
        rel_path = os.path.relpath(file_path, ROOT_DIR)
        print(f"{FG_BLUE}{rel_path}{RESET}:{FG_YELLOW}{line_num}{RESET}: {line_content}")

    if len(results) > 50:
        print(f"\n{FG_YELLOW}... and {len(results) - 50} more matches{RESET}")


def handle_diff(parts: List[str], cwd: str):
    """Handle /diff command."""
    if len(parts) < 3:
        print(f"{FG_RED}Usage: /diff <file1> <file2>{RESET}")
        return

    file1 = resolve_path(parts[1], cwd)
    file2 = resolve_path(parts[2], cwd)

    if not is_safe_path(file1) or not is_safe_path(file2):
        print(f"{FG_RED}Cannot access files outside sandbox{RESET}")
        return

    try:
        with open(file1, 'r', encoding='utf-8') as f:
            content1 = f.read()
        with open(file2, 'r', encoding='utf-8') as f:
            content2 = f.read()

        rel1 = os.path.relpath(file1, ROOT_DIR)
        rel2 = os.path.relpath(file2, ROOT_DIR)

        print_diff(content1, content2, f"{rel1} vs {rel2}")
    except Exception as e:
        print(f"{FG_RED}Error reading files: {e}{RESET}")


def handle_template(parts: List[str], cwd: str, session: ChatSession) -> Optional[str]:
    """Handle /template command."""
    if len(parts) < 2:
        print(f"{FG_YELLOW}Available templates:{RESET}")
        for name, desc in TEMPLATES.items():
            print(f"  {FG_CYAN}{name}{RESET}: {desc[:60]}...")
        return None

    template_name = parts[1].lower()
    if template_name not in TEMPLATES:
        print(f"{FG_RED}Unknown template: {template_name}{RESET}")
        return None

    if len(parts) < 3:
        print(f"{FG_RED}Usage: /template {template_name} <file>{RESET}")
        return None

    file_path = resolve_path(parts[2], cwd)
    if not is_safe_path(file_path) or not os.path.isfile(file_path):
        print(f"{FG_RED}Invalid file: {file_path}{RESET}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return TEMPLATES[template_name] + f"```\n{content}\n```"
    except Exception as e:
        print(f"{FG_RED}Error reading file: {e}{RESET}")
        return None


def handle_backups(parts: List[str], cwd: str):
    """Handle /backups command."""
    if len(parts) > 1:
        file_path = resolve_path(" ".join(parts[1:]), cwd)
        backups = list_backups(file_path)
    else:
        backups = list_backups()

    if not backups:
        print(f"{FG_YELLOW}No backups found.{RESET}")
        return

    print(f"\n{FG_CYAN}Available backups ({len(backups)}):{RESET}\n")
    for backup in backups[:20]:  # Show last 20
        print(f"  {backup}")

    if len(backups) > 20:
        print(f"\n{FG_YELLOW}... and {len(backups) - 20} more{RESET}")


def handle_restore(parts: List[str], cwd: str):
    """Handle /restore command."""
    if len(parts) < 3:
        print(f"{FG_RED}Usage: /restore <backup_name> <target_file>{RESET}")
        return

    backup_name = parts[1]
    target_path = resolve_path(parts[2], cwd)

    if not is_safe_path(target_path):
        print(f"{FG_RED}Cannot restore outside sandbox{RESET}")
        return

    confirm = input(f"{FG_YELLOW}Restore {backup_name} to {target_path}? [y/N] {RESET}").strip().lower()
    if confirm == 'y':
        if restore_backup(backup_name, target_path):
            print(f"{FG_GREEN}✓ Restored successfully{RESET}")
            log_operation("RESTORE", f"{backup_name} -> {target_path}")
        else:
            print(f"{FG_RED}✗ Restore failed{RESET}")


def handle_stats(session: ChatSession):
    """Handle /stats command."""
    print(f"\n{FG_CYAN}{'═' * 50}{RESET}")
    print(f"{FG_CYAN}{BOLD}Session Statistics{RESET}")
    print(f"{FG_CYAN}{'═' * 50}{RESET}")
    print(f"  Queries sent:        {session.stats['queries']}")
    print(f"  Files modified:      {session.stats['files_modified']}")
    print(f"  Tokens generated:    ~{session.stats['tokens_generated']}")
    print(f"  Files in context:    {len(session.opened_files)}")
    print(f"  History entries:     {len(session.history)}")
    print(f"{FG_CYAN}{'═' * 50}{RESET}\n")


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

def print_banner():
    logo = r"""
███╗   ███╗██╗     ██╗  ██╗      ██████╗  ██████╗ ██████╗ ███████╗
████╗ ████║██║     ██║ ██╔╝     ██╔════╝ ██╔═══██╗██╔══██╗██╔════╝
██╔████╔██║██║     █████╔╝   ███╗██║  ███╗██║   ██║██████╔╝█████╗
██║╚██╔╝██║██║     ██╔═██╗   ╚══╝██║   ██║██║   ██║██╔══██╗██╔══╝
██║ ╚═╝ ██║███████╗██║  ██╗      ╚██████╔╝╚██████╔╝██║  ██║███████╗
╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝       ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝

          🚀 Enhanced Local Coding Assistant 🚀
"""
    print(FG_MAGENTA + logo + RESET)


def print_help(model_name: str, cwd: str, max_tokens: int, ctx_chars: int):
    print("=" * 80)
    print(" MLX-CODE — Enhanced Local Coding Assistant")
    print("=" * 80)
    print(f"Model:  {FG_CYAN}{model_name}{RESET}")
    print(f"Sandbox: {FG_CYAN}{ROOT_DIR}{RESET}")
    print(f"Logs:   {FG_CYAN}{LOG_DIR}{RESET}")
    print()
    print("CORE COMMANDS:")
    print(f"  {FG_GREEN}/help{RESET}              Show this help")
    print(f"  {FG_GREEN}/exit{RESET}              Quit the assistant")
    print(f"  {FG_GREEN}/clear{RESET}             Clear chat history")
    print()
    print("MODEL CONFIGURATION:")
    print(f"  {FG_GREEN}/model <id>{RESET}         Switch model (HuggingFace ID)")
    print(f"  {FG_GREEN}/q7b{RESET}               Quick: Qwen2.5 Coder 7B 4bit")
    print(f"  {FG_GREEN}/q3b{RESET}               Quick: Qwen2.5 Coder 3B 4bit")
    print(f"  {FG_GREEN}/tokens <n>{RESET}         Set max tokens per response")
    print(f"  {FG_GREEN}/ctx <n>{RESET}            Set context size (chars)")
    print()
    print("NAVIGATION & FILES:")
    print(f"  {FG_GREEN}/pwd{RESET}                Show current directory")
    print(f"  {FG_GREEN}/cd <path>{RESET}          Change directory")
    print(f"  {FG_GREEN}/ls [path]{RESET}          List directory contents")
    print(f"  {FG_GREEN}/tree [path]{RESET}        Show directory tree")
    print(f"  {FG_GREEN}/open <file>{RESET}        Load file into context")
    print(f"  {FG_GREEN}/grep <pattern>{RESET}     Search in files")
    print(f"  {FG_GREEN}/diff <f1> <f2>{RESET}     Compare two files")
    print()
    print("TEMPLATES & WORKFLOWS:")
    print(f"  {FG_GREEN}/template{RESET}           List available templates")
    print(f"  {FG_GREEN}/template <name> <file>{RESET}  Apply template to file")
    print(f"    Available: {', '.join(TEMPLATES.keys())}")
    print()
    print("BACKUP & HISTORY:")
    print(f"  {FG_GREEN}/backups [file]{RESET}     List backups")
    print(f"  {FG_GREEN}/restore <bk> <file>{RESET} Restore from backup")
    print(f"  {FG_GREEN}/save [file]{RESET}        Export chat to markdown")
    print(f"  {FG_GREEN}/last{RESET}               Repeat last query")
    print(f"  {FG_GREEN}/edit{RESET}               Open last modified file in $EDITOR")
    print()
    print("INFORMATION:")
    print(f"  {FG_GREEN}/stats{RESET}              Show session statistics")
    print(f"  {FG_GREEN}/project{RESET}            Detect project type")
    print()
    print("TIPS:")
    print("  • Multi-line input: finish with an empty line")
    print("  • Files are automatically backed up before modification")
    print("  • Use /tree to understand project structure")
    print("  • Templates speed up common tasks")
    print("=" * 80)
    print(f"CWD: {FG_CYAN}{cwd}{RESET} | "
          f"Tokens: {FG_CYAN}{max_tokens}{RESET} | "
          f"Context: {FG_CYAN}{ctx_chars}{RESET}")
    print("=" * 80)


def print_status(model_name: str, cwd: str, max_tokens: int, ctx_chars: int, project_type: Optional[str]):
    print("=" * 80)
    model_short = model_name.split('/')[-1][:30]
    cwd_short = cwd.replace(ROOT_DIR, "~")

    status_line = f" {model_short} | {cwd_short}"
    if project_type:
        status_line += f" | {FG_YELLOW}{project_type}{RESET}"

    print(status_line)
    print("=" * 80)


# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------

def main():
    ensure_directories()

    # Initialize
    cwd = os.getcwd()
    if not is_safe_path(cwd):
        cwd = ROOT_DIR
        os.chdir(cwd)

    config = load_config()
    model_name = config.get("model", DEFAULT_MODEL)
    max_tokens = config.get("max_tokens", DEFAULT_MAX_TOKENS)
    ctx_chars = config.get("ctx_chars", DEFAULT_CTX_CHARS)

    print_banner()
    print_help(model_name, cwd, max_tokens, ctx_chars)

    session = ChatSession(model_name, max_tokens, ctx_chars)
    project_type = detect_project_type(cwd)

    print_status(model_name, cwd, max_tokens, ctx_chars, project_type)

    buffer: List[str] = []

    while True:
        try:
            line = input(f"{FG_GREEN}>{RESET} ")
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! 👋")
            break

        stripped = line.strip()

        # Empty line -> send buffer
        if stripped == "":
            if buffer:
                user_message = "\n".join(buffer)
                buffer = []

                # Generate response
                print(f"\n{FG_CYAN}Assistant:{RESET}\n")
                response = session.ask(user_message, cwd, project_type)
                print_colored_response(response)

                # Handle file changes
                blocks = extract_file_blocks(response)
                if blocks:
                    apply_file_changes(blocks, cwd, session)
                else:
                    maybe_save_code_block(response, cwd, session)

                print()
                continue
            else:
                continue

        # Commands
        if stripped.startswith("/"):
            parts = stripped.split()
            cmd = parts[0].lower()

            # Exit
            if cmd == "/exit":
                config = {
                    "model": model_name,
                    "max_tokens": max_tokens,
                    "ctx_chars": ctx_chars,
                }
                save_config(config)
                print("Configuration saved. Goodbye! 👋")
                break

            # Help
            if cmd == "/help":
                print_help(model_name, cwd, max_tokens, ctx_chars)
                print_status(model_name, cwd, max_tokens, ctx_chars, project_type)
                continue

            # Clear
            if cmd == "/clear":
                session.history.clear()
                session.opened_files.clear()
                print(f"{FG_GREEN}✓ Chat history cleared{RESET}")
                continue

            # Model change
            if cmd == "/model":
                if len(parts) < 2:
                    print(f"{FG_RED}Usage: /model <huggingface-model-id>{RESET}")
                    continue
                new_model = parts[1].strip()
                model_name = new_model
                session = ChatSession(model_name, max_tokens, ctx_chars)
                print_status(model_name, cwd, max_tokens, ctx_chars, project_type)
                continue

            # Model aliases
            if cmd in ("/q7b", "/q3b", "/q1.5b"):
                key = cmd[1:]
                new_model = MODEL_ALIASES.get(key)
                if not new_model:
                    print(f"{FG_RED}Alias {cmd} not configured{RESET}")
                    continue
                model_name = new_model
                session = ChatSession(model_name, max_tokens, ctx_chars)
                print_status(model_name, cwd, max_tokens, ctx_chars, project_type)
                continue

            # Tokens
            if cmd == "/tokens":
                if len(parts) != 2 or not parts[1].isdigit():
                    print(f"{FG_RED}Usage: /tokens <number>{RESET}")
                    continue
                max_tokens = int(parts[1])
                session.max_tokens = max_tokens
                print(f"{FG_GREEN}✓ Max tokens set to {max_tokens}{RESET}")
                continue

            # Context
            if cmd == "/ctx":
                if len(parts) != 2 or not parts[1].isdigit():
                    print(f"{FG_RED}Usage: /ctx <number>{RESET}")
                    continue
                ctx_chars = int(parts[1])
                session.ctx_chars = ctx_chars
                print(f"{FG_GREEN}✓ Context size set to {ctx_chars} chars{RESET}")
                continue

            # PWD
            if cmd == "/pwd":
                rel = cwd.replace(ROOT_DIR, "~")
                print(f"{FG_CYAN}{rel}{RESET}")
                continue

            # CD
            if cmd == "/cd":
                if len(parts) < 2:
                    print(f"{FG_RED}Usage: /cd <path>{RESET}")
                    continue
                target = resolve_path(" ".join(parts[1:]), cwd)
                if not is_safe_path(target):
                    print(f"{FG_RED}Cannot cd outside sandbox{RESET}")
                    continue
                if not os.path.isdir(target):
                    print(f"{FG_RED}No such directory: {target}{RESET}")
                    continue
                cwd = target
                os.chdir(cwd)
                project_type = detect_project_type(cwd)
                print_status(model_name, cwd, max_tokens, ctx_chars, project_type)
                continue

            # LS
            if cmd == "/ls":
                if len(parts) > 1:
                    target = resolve_path(" ".join(parts[1:]), cwd)
                else:
                    target = cwd
                if not is_safe_path(target):
                    print(f"{FG_RED}Cannot list outside sandbox{RESET}")
                    continue
                if not os.path.isdir(target):
                    print(f"{FG_RED}No such directory: {target}{RESET}")
                    continue
                entries = sorted(os.listdir(target))
                for name in entries:
                    full = os.path.join(target, name)
                    if os.path.isdir(full):
                        print(FG_BLUE + name + "/" + RESET)
                    else:
                        print(name)
                continue

            # TREE
            if cmd == "/tree":
                handle_tree(parts, cwd)
                continue

            # GREP
            if cmd == "/grep":
                handle_grep(parts, cwd)
                continue

            # DIFF
            if cmd == "/diff":
                handle_diff(parts, cwd)
                continue

            # OPEN
            if cmd == "/open":
                if len(parts) < 2:
                    print(f"{FG_RED}Usage: /open <file>{RESET}")
                    continue
                target = resolve_path(" ".join(parts[1:]), cwd)
                if not is_safe_path(target):
                    print(f"{FG_RED}Cannot open outside sandbox{RESET}")
                    continue
                if not os.path.isfile(target):
                    print(f"{FG_RED}No such file: {target}{RESET}")
                    continue
                try:
                    with open(target, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    print(f"{FG_RED}Error reading file: {e}{RESET}")
                    continue

                rel = os.path.relpath(target, ROOT_DIR)
                pseudo_message = f"Opened file {rel}:\n\n{BACKTICKS}\n{content}\n{BACKTICKS}"
                session.history.append(("user", pseudo_message))
                session.opened_files.append(rel)
                print(f"{FG_GREEN}✓ Loaded {rel} into context{RESET}")
                continue

            # TEMPLATE
            if cmd == "/template":
                template_query = handle_template(parts, cwd, session)
                if template_query:
                    buffer = [template_query]
                    print(f"{FG_CYAN}Template prepared. Press Enter to send.{RESET}")
                continue

            # BACKUPS
            if cmd == "/backups":
                handle_backups(parts, cwd)
                continue

            # RESTORE
            if cmd == "/restore":
                handle_restore(parts, cwd)
                continue

            # SAVE
            if cmd == "/save":
                if len(parts) > 1:
                    out_path_raw = " ".join(parts[1:])
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    out_path_raw = f"mlx-session-{timestamp}.md"
                out_path = resolve_path(out_path_raw, cwd)
                if not is_safe_path(out_path):
                    print(f"{FG_RED}Cannot save outside sandbox{RESET}")
                    continue

                lines = [
                    f"# MLX-CODE Session Export\n",
                    f"**Model:** {model_name}\n",
                    f"**Date:** {datetime.now().isoformat()}\n",
                    f"**Project:** {project_type or 'Unknown'}\n",
                    "\n---\n\n",
                ]
                for role, txt in session.history:
                    if role == "user":
                        lines.append("## 👤 User\n\n")
                    else:
                        lines.append("## 🤖 Assistant\n\n")
                    lines.append(txt)
                    lines.append("\n\n---\n\n")
                try:
                    os.makedirs(os.path.dirname(out_path), exist_ok=True)
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write("".join(lines))
                    rel = os.path.relpath(out_path, ROOT_DIR)
                    print(f"{FG_GREEN}✓ Saved session to {rel}{RESET}")
                except Exception as e:
                    print(f"{FG_RED}Error saving session: {e}{RESET}")
                continue

            # LAST
            if cmd == "/last":
                if session.last_query:
                    buffer = [session.last_query]
                    print(f"{FG_CYAN}Repeating last query. Press Enter to send.{RESET}")
                else:
                    print(f"{FG_YELLOW}No previous query to repeat{RESET}")
                continue

            # EDIT
            if cmd == "/edit":
                if not session.last_modified_files:
                    print(f"{FG_YELLOW}No files have been modified yet{RESET}")
                    continue
                editor = os.environ.get("EDITOR", "nano")
                last_file = session.last_modified_files[-1]
                print(f"{FG_CYAN}Opening {last_file} in {editor}...{RESET}")
                os.system(f"{editor} {last_file}")
                continue

            # STATS
            if cmd == "/stats":
                handle_stats(session)
                continue

            # PROJECT
            if cmd == "/project":
                detected = detect_project_type(cwd)
                if detected:
                    print(f"{FG_GREEN}Detected project type: {detected}{RESET}")
                else:
                    print(f"{FG_YELLOW}Could not detect project type{RESET}")
                continue

            # Unknown command
            print(f"{FG_RED}Unknown command: {cmd}{RESET}")
            print(f"{FG_YELLOW}Type /help for available commands{RESET}")
            continue

        # Normal text -> add to buffer
        buffer.append(line)


if __name__ == "__main__":
    main()