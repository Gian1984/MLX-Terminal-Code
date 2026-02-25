#!/Users/gianlucatiengo/.mlx-env/bin/python3
# mlx-code-pro: intelligent local coding assistant with context awareness
# Requires: pip install mlx-lm pillow prompt-toolkit

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
import base64
import subprocess
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Set
from pathlib import Path

try:
    from mlx_lm import load, stream_generate
except ImportError:
    print("ERROR: mlx-lm not found. Install with: pip install mlx-lm")
    sys.exit(1)

try:
    from PIL import Image

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.styles import Style
    from prompt_toolkit.formatted_text import HTML
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False
    print("WARNING: prompt-toolkit not found. Install for better experience: pip install prompt-toolkit")

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

# ROOT_DIR will be set dynamically to current working directory at startup
ROOT_DIR = None  # Set in main()
LOG_DIR = os.path.expanduser("~/.mlx-code")
BACKUP_DIR = os.path.join(LOG_DIR, "backups")
HISTORY_FILE = os.path.join(LOG_DIR, "history.log")
CONFIG_FILE = os.path.join(LOG_DIR, "config.json")
AUTOSAVE_FILE = os.path.join(LOG_DIR, "autosave.json")

DEFAULT_MODEL = "mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit"  # 1.5B - lightweight demo model (upgrade recommended)

MODEL_ALIASES = {
    # Qwen Coder Models (Recommended for coding)
    "q1.5b": "mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit",      # ~1.0GB RAM - Fast, basic
    "q3b": "mlx-community/qwen2.5-coder-3b-instruct-4bit",          # ~1.9GB RAM - Good balance
    "q7b": "mlx-community/qwen2.5-coder-7b-instruct-4bit",          # ~4.3GB RAM - Recommended
    "q14b": "mlx-community/Qwen2.5-Coder-14B-Instruct-4bit",        # ~8.5GB RAM - Advanced
    "q32b": "mlx-community/Qwen2.5-Coder-32B-Instruct-4bit",        # ~17GB RAM - Best (M4 Pro 24GB!)

    # DeepSeek Coder Models (Excellent for code)
    "ds1.3b": "mlx-community/DeepSeek-Coder-1.3B-Instruct-4bit",    # ~1.0GB RAM - Fast
    "ds6.7b": "mlx-community/DeepSeek-Coder-6.7B-Instruct-4bit",    # ~4.0GB RAM - Very good
    "ds": "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit",     # ~9.0GB RAM - Excellent
    "deepseek": "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit",

    # Mistral Models (Versatile)
    "mistral": "mlx-community/Mistral-7B-Instruct-v0.3-4bit",       # ~4.3GB RAM - Good general
    "m7b": "mlx-community/Mistral-7B-Instruct-v0.3-4bit",

    # Llama 3 Models (Strong reasoning)
    "llama3-8b": "mlx-community/Meta-Llama-3-8B-Instruct-4bit",     # ~4.5GB RAM - Good reasoning
    "l3-8b": "mlx-community/Meta-Llama-3-8B-Instruct-4bit",

    # Phi Models (Efficient, small)
    "phi3": "mlx-community/Phi-3-mini-4k-instruct-4bit",            # ~2.3GB RAM - Efficient
    "phi": "mlx-community/Phi-3-mini-4k-instruct-4bit",

    # CodeLlama (Specialized for code)
    "codellama": "mlx-community/CodeLlama-13b-Instruct-hf-4bit",    # ~7.0GB RAM - Code specialist
    "cl13b": "mlx-community/CodeLlama-13b-Instruct-hf-4bit",
}

DEFAULT_MAX_TOKENS = 1024
DEFAULT_CTX_CHARS = 24000
MAX_FILE_CONTEXT_CHARS = 15000  # Max chars for all loaded files combined in prompt

# File extensions for different purposes
CODE_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
    '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.r',
    '.sh', '.bash', '.sql', '.graphql', '.proto'
}

CONFIG_EXTENSIONS = {
    '.json', '.yaml', '.yml', '.toml', '.xml', '.ini', '.conf', '.cfg'
}

WEB_EXTENSIONS = {
    '.html', '.css', '.scss', '.sass', '.less', '.vue', '.svelte'
}

DOC_EXTENSIONS = {
    '.md', '.txt', '.rst', '.adoc'
}

IMAGE_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'
}

ALLOWED_EXTENSIONS = CODE_EXTENSIONS | CONFIG_EXTENSIONS | WEB_EXTENSIONS | DOC_EXTENSIONS

# Project structure files to auto-load for context
PROJECT_CONTEXT_FILES = [
    'README.md', 'README.txt', 'CONTRIBUTING.md',
    'package.json', 'requirements.txt', 'Cargo.toml', 'go.mod',
    'pyproject.toml', 'setup.py', 'Makefile', 'CMakeLists.txt',
    '.gitignore', 'Dockerfile', 'docker-compose.yml'
]

TEMPLATES = {
    "test": "Create comprehensive unit tests for the following code. Use appropriate testing framework and include edge cases:\n\n",
    "doc": "Add detailed documentation and docstrings to the following code. Include parameter descriptions, return values, and examples:\n\n",
    "refactor": "Refactor the following code to improve readability, maintainability, and performance. Follow clean code principles:\n\n",
    "review": "Perform a thorough code review of the following code. Point out potential bugs, security issues, and suggest improvements:\n\n",
    "optimize": "Optimize the following code for better performance. Identify bottlenecks and suggest algorithmic improvements:\n\n",
    "explain": "Explain the following code in detail. Break down what each part does and why:\n\n",
    "debug": "Help debug this code. Identify potential issues and suggest fixes:\n\n",
    "secure": "Analyze this code for security vulnerabilities and suggest improvements:\n\n",
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
    """Load user configuration (global)."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def load_project_config(cwd: str) -> Dict:
    """Load per-project config from .mlx-code.json if present.

    Supported fields: model, max_tokens, ctx_chars, auto_context.
    Project config overrides global config.
    """
    project_config_path = os.path.join(cwd, ".mlx-code.json")
    if os.path.exists(project_config_path):
        try:
            with open(project_config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Only allow known keys
            allowed = {"model", "max_tokens", "ctx_chars", "auto_context"}
            return {k: v for k, v in data.items() if k in allowed}
        except Exception as e:
            print(f"{FG_YELLOW}Warning: Could not read .mlx-code.json: {e}{RESET}")
    return {}


def save_config(config: Dict):
    """Save user configuration."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"{FG_YELLOW}Warning: Could not save config: {e}{RESET}")


def autosave_conversation(session_history: List[Tuple[str, str]], model_name: str, cwd: str):
    """Auto-save conversation to disk after each exchange."""
    try:
        data = {
            "model": model_name,
            "cwd": cwd,
            "timestamp": datetime.now().isoformat(),
            "history": [{"role": role, "content": content} for role, content in session_history],
        }
        with open(AUTOSAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass  # Silent - don't interrupt user flow


def load_autosave() -> Optional[Dict]:
    """Load autosaved conversation if it exists."""
    if not os.path.exists(AUTOSAVE_FILE):
        return None
    try:
        with open(AUTOSAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("history"):
            return data
    except Exception:
        pass
    return None


def clear_autosave():
    """Remove autosave file (on clean exit)."""
    try:
        if os.path.exists(AUTOSAVE_FILE):
            os.remove(AUTOSAVE_FILE)
    except Exception:
        pass


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


def is_image_file(path: str) -> bool:
    """Check if file is an image."""
    ext = os.path.splitext(path)[1].lower()
    return ext in IMAGE_EXTENSIONS


# ---------------------------------------------------------------------------
# INTELLIGENT FILE DETECTION
# ---------------------------------------------------------------------------

def extract_file_references(text: str, cwd: str) -> List[str]:
    """Extract file paths mentioned in user message."""
    references = []

    # Pattern 1: Explicit file mentions
    patterns = [
        r'(?:file|script|code|document)?\s*["\']([^"\']+\.[a-zA-Z0-9]+)["\']',
        r'(?:in|at|see|check|read|open|look at|modify|edit|update)\s+([a-zA-Z0-9_\-./]+\.[a-zA-Z0-9]+)',
        r'`([^`]+\.[a-zA-Z0-9]+)`',
        r'\b([a-zA-Z0-9_\-]+\.(py|js|jsx|ts|tsx|java|cpp|c|h|go|rs|rb|php|html|css|json|yaml|yml|md|txt))\b',
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            file_path = match.group(1)
            # Try to resolve the path
            if os.path.sep in file_path or file_path.startswith('.'):
                abs_path = resolve_path(file_path, cwd)
            else:
                # Try as relative to cwd first
                abs_path = resolve_path(file_path, cwd)
                # If not found, search in current directory
                if not os.path.exists(abs_path):
                    found = find_file_in_tree(file_path, cwd)
                    if found:
                        abs_path = found

            if os.path.exists(abs_path) and is_safe_path(abs_path):
                references.append(abs_path)

    return list(set(references))  # Remove duplicates


def find_file_in_tree(filename: str, start_dir: str, max_depth: int = 3) -> Optional[str]:
    """Search for a file in directory tree."""
    for root, dirs, files in os.walk(start_dir):
        # Limit depth
        depth = root[len(start_dir):].count(os.sep)
        if depth > max_depth:
            continue

        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        if filename in files:
            return os.path.join(root, filename)

    return None


def should_auto_load_file(filepath: str) -> bool:
    """Determine if file should be auto-loaded."""
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filepath)[1].lower()

    # Always load project context files
    if filename in PROJECT_CONTEXT_FILES:
        return True

    # Load code files that are reasonably sized
    if ext in CODE_EXTENSIONS or ext in CONFIG_EXTENSIONS:
        try:
            size = os.path.getsize(filepath)
            return size < 50000  # 50KB limit for auto-load
        except Exception:
            return False

    return False


# ---------------------------------------------------------------------------
# PROJECT DETECTION & CONTEXT
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
        "dotnet": ["*.csproj", "*.sln"],
    }

    for project_type, files in markers.items():
        for marker in files:
            if '*' in marker:
                if glob.glob(os.path.join(cwd, marker)):
                    return project_type
            else:
                if os.path.exists(os.path.join(cwd, marker)):
                    return project_type
    return None


def get_project_structure(cwd: str, max_files: int = 20) -> str:
    """Get a concise overview of project structure."""
    structure = []
    file_count = 0

    for root, dirs, files in os.walk(cwd):
        if file_count >= max_files:
            break

        # Skip hidden and common ignore directories
        dirs[:] = [d for d in dirs if
                   not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env', 'dist', 'build']]

        level = root.replace(cwd, '').count(os.sep)
        indent = ' ' * 2 * level
        folder_name = os.path.basename(root) or os.path.basename(cwd)
        structure.append(f'{indent}{folder_name}/')

        subindent = ' ' * 2 * (level + 1)
        for file in sorted(files)[:5]:  # Limit files per directory
            if file.startswith('.'):
                continue
            structure.append(f'{subindent}{file}')
            file_count += 1
            if file_count >= max_files:
                break

    if file_count >= max_files:
        structure.append("  ...")

    return '\n'.join(structure)


def load_project_context(cwd: str) -> Dict[str, str]:
    """Load important project files for context."""
    context = {}

    for filename in PROJECT_CONTEXT_FILES:
        filepath = os.path.join(cwd, filename)
        if os.path.exists(filepath) and is_safe_path(filepath):
            try:
                file_size = os.path.getsize(filepath)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)  # First 5KB
                    if file_size > 5000:
                        content += f"\n\n[... TRUNCATED — showing 5KB of {file_size / 1024:.1f}KB total ...]"
                    context[filename] = content
            except Exception:
                continue

    return context


# ---------------------------------------------------------------------------
# IMAGE HANDLING
# ---------------------------------------------------------------------------

def encode_image_to_base64(image_path: str) -> Optional[str]:
    """Encode image to base64 for context."""
    if not HAS_PIL:
        return None

    try:
        with Image.open(image_path) as img:
            # Resize if too large
            max_size = (800, 800)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convert to RGB if necessary
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')

            # Save to base64
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return img_str
    except Exception as e:
        print(f"{FG_YELLOW}Warning: Could not process image: {e}{RESET}")
        return None


def describe_image(image_path: str) -> str:
    """Create a textual description of image for context."""
    if not HAS_PIL:
        return f"[Image: {os.path.basename(image_path)}]"

    try:
        with Image.open(image_path) as img:
            width, height = img.size
            mode = img.mode
            format_name = img.format or "Unknown"

            return f"[Image: {os.path.basename(image_path)} - {width}x{height}px, {mode} mode, {format_name} format]"
    except Exception:
        return f"[Image: {os.path.basename(image_path)}]"


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
# FILE TREE & SEARCH
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


def grep_files(pattern: str, directory: str, extensions: set = None) -> List[Tuple[str, int, str]]:
    """Search for pattern in files. Returns list of (file, line_num, line_content)."""
    results = []
    try:
        regex = re.compile(pattern, re.IGNORECASE)
        for root, dirs, files in os.walk(directory):
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
# MODEL HELPERS
# ---------------------------------------------------------------------------

def is_model_cached(model_name: str) -> bool:
    """Check if model is already downloaded in cache."""
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    if not os.path.exists(cache_dir):
        return False

    # HuggingFace converts model names like: mlx-community/model -> models--mlx-community--model
    model_dir_name = f"models--{model_name.replace('/', '--')}"
    model_path = os.path.join(cache_dir, model_dir_name)

    return os.path.exists(model_path) and os.path.isdir(model_path)


def get_model_size_estimate(model_name: str) -> str:
    """Get estimated download size for model."""
    name_lower = model_name.lower()
    if "32b" in name_lower:
        return "~17GB"
    elif "14b" in name_lower or "13b" in name_lower:
        return "~8.5GB"
    elif "8b" in name_lower or "9b" in name_lower:
        return "~4.5GB"
    elif "7b" in name_lower or "6.7b" in name_lower:
        return "~4.0GB"
    elif "3b" in name_lower:
        return "~1.9GB"
    elif "1.5b" in name_lower or "1.3b" in name_lower:
        return "~1.0GB"
    else:
        return "~2-5GB"


def download_model_with_git_lfs(model_name: str) -> bool:
    """
    Download model using git-lfs (3-5x faster than HuggingFace Hub).
    Returns True if successful, False otherwise.
    """
    import tempfile
    import shutil

    # Check if git-lfs is installed
    result = subprocess.run(["which", "git-lfs"], capture_output=True)
    if result.returncode != 0:
        print(f"{FG_YELLOW}ℹ️  git-lfs not found. Install with: brew install git-lfs{RESET}")
        print(f"{FG_YELLOW}   (Using standard download method instead){RESET}\n")
        return False

    print(f"{FG_CYAN}🚀 Using git-lfs for faster download (3-5x faster!){RESET}")
    print(f"{FG_CYAN}{'─' * 70}{RESET}")

    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    repo_url = f"https://huggingface.co/{model_name}"
    repo_name = model_name.split('/')[-1]
    temp_repo_path = os.path.join(temp_dir, repo_name)

    try:
        # Clone with git-lfs
        print(f"{FG_CYAN}📥 Cloning from HuggingFace...{RESET}")
        result = subprocess.run(
            ["git", "clone", repo_url, temp_repo_path],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"{FG_RED}❌ Git clone failed: {result.stderr}{RESET}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False

        # Move to HuggingFace cache location
        cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        os.makedirs(cache_dir, exist_ok=True)

        model_dir_name = f"models--{model_name.replace('/', '--')}"
        final_path = os.path.join(cache_dir, model_dir_name)

        # Remove old incomplete downloads if any
        if os.path.exists(final_path):
            shutil.rmtree(final_path)

        # Move cloned repo to cache
        shutil.move(temp_repo_path, final_path)
        shutil.rmtree(temp_dir, ignore_errors=True)

        print(f"{FG_GREEN}✅ Model downloaded successfully with git-lfs!{RESET}")
        print(f"{FG_CYAN}{'─' * 70}{RESET}\n")
        return True

    except Exception as e:
        print(f"{FG_RED}❌ Error during git-lfs download: {e}{RESET}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False


def list_installed_models() -> List[Tuple[str, str, str]]:
    """
    List all installed models in the HuggingFace cache.
    Returns list of (model_name, directory_name, size)
    """
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    if not os.path.exists(cache_dir):
        return []

    installed = []
    try:
        for entry in os.listdir(cache_dir):
            if entry.startswith("models--"):
                model_path = os.path.join(cache_dir, entry)
                if os.path.isdir(model_path):
                    # Convert directory name back to model name
                    model_name = entry.replace("models--", "").replace("--", "/")

                    # Calculate size
                    total_size = 0
                    for dirpath, dirnames, filenames in os.walk(model_path):
                        for filename in filenames:
                            filepath = os.path.join(dirpath, filename)
                            try:
                                total_size += os.path.getsize(filepath)
                            except Exception:
                                pass

                    # Format size
                    size_gb = total_size / (1024**3)
                    size_str = f"{size_gb:.2f}GB"

                    installed.append((model_name, entry, size_str))
    except Exception as e:
        print(f"{FG_YELLOW}Warning: Could not list models: {e}{RESET}")

    return sorted(installed)


def delete_model(model_name: str) -> bool:
    """Delete a model from the cache."""
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    model_dir_name = f"models--{model_name.replace('/', '--')}"
    model_path = os.path.join(cache_dir, model_dir_name)

    if not os.path.exists(model_path):
        return False

    try:
        shutil.rmtree(model_path)
        return True
    except Exception as e:
        print(f"{FG_RED}Error deleting model: {e}{RESET}")
        return False


def get_model_ram_requirement(model_name: str) -> str:
    """Get estimated RAM requirement for model."""
    name_lower = model_name.lower()
    if "32b" in name_lower:
        return "~20-22GB"
    elif "14b" in name_lower or "13b" in name_lower:
        return "~10-12GB"
    elif "8b" in name_lower or "9b" in name_lower:
        return "~6-8GB"
    elif "7b" in name_lower or "6.7b" in name_lower:
        return "~5-7GB"
    elif "3b" in name_lower:
        return "~3-4GB"
    elif "1.5b" in name_lower or "1.3b" in name_lower:
        return "~2-3GB"
    else:
        return "~4-8GB"


def list_available_models() -> Dict[str, Dict]:
    """List all available models with metadata."""
    models = {}

    for alias, full_name in MODEL_ALIASES.items():
        models[alias] = {
            "name": full_name,
            "size": get_model_size_estimate(full_name),
            "ram": get_model_ram_requirement(full_name),
            "cached": is_model_cached(full_name)
        }

    return models


# ---------------------------------------------------------------------------
# INTELLIGENT CHAT SESSION
# ---------------------------------------------------------------------------

class ChatSession:
    def __init__(self, model_name: str, max_tokens: int, ctx_chars: int):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.ctx_chars = ctx_chars
        self.history: List[Tuple[str, str]] = []
        self.opened_files: Dict[str, str] = {}  # path -> content
        self.project_context: Dict[str, str] = {}
        self.last_query: str = ""
        self.last_modified_files: List[str] = []
        self.auto_context_enabled = True
        self.stats = {
            "queries": 0,
            "files_modified": 0,
            "files_auto_loaded": 0,
            "tokens_generated": 0,
            "prompt_tokens": 0,
        }

        # Model loading with better feedback
        model_cached = is_model_cached(model_name)
        model_size = get_model_size_estimate(model_name)

        print(f"\n{FG_CYAN}{'─' * 70}{RESET}")
        print(f"{FG_CYAN}📥 Loading model: {model_name.split('/')[-1]}{RESET}")

        if model_cached:
            print(f"{FG_GREEN}✓ Model found in cache - loading from disk{RESET}")
            print(f"{FG_CYAN}{'─' * 70}{RESET}\n")
        else:
            print(f"{FG_YELLOW}⚠️  Model not cached - will download {model_size}{RESET}")
            print(f"{FG_YELLOW}⏱️  Estimated time: 5-30 min (depends on your internet speed){RESET}")
            print(f"\n{FG_YELLOW}💡 If download is too slow (< 500 KB/s), press Ctrl+C and:{RESET}")
            print(f"   • Try smaller model: /q1.5b (only 1GB)")
            print(f"   • Check your internet connection (try ethernet cable)")
            print(f"   • Try again later (servers might be busy)")
            print(f"   • Download manually: huggingface-cli download {model_name}")
            print(f"{FG_CYAN}{'─' * 70}{RESET}\n")
            print(f"{FG_CYAN}Download progress:{RESET}")

        try:
            # Don't use spinner - let HuggingFace progress bars show
            self.model, self.tokenizer = load(model_name)
            print(f"\n{FG_GREEN}✅ Model loaded successfully!{RESET}\n")

        except KeyboardInterrupt:
            print(f"\n\n{FG_YELLOW}⚠️  Download interrupted by user{RESET}")
            print(f"{FG_CYAN}💡 Next time you run, download will resume from where it stopped{RESET}")
            print(f"{FG_CYAN}💡 Or try a smaller model - edit ~/mlx-code line 43{RESET}")
            sys.exit(0)

        except Exception as e:
            print(f"\n{FG_RED}{'═' * 70}{RESET}")
            print(f"{FG_RED}❌ Failed to load model{RESET}")
            print(f"{FG_RED}{'═' * 70}{RESET}")

            error_msg = str(e).lower()

            # Provide specific help based on error type
            if "connection" in error_msg or "timeout" in error_msg or "network" in error_msg:
                print(f"\n{FG_YELLOW}🌐 Network Connection Problem:{RESET}")
                print(f"   • Check your internet connection")
                print(f"   • Try using ethernet instead of WiFi")
                print(f"   • Disable VPN if you're using one")
                print(f"   • Try again in a few minutes")

            elif "disk" in error_msg or "space" in error_msg:
                print(f"\n{FG_YELLOW}💾 Disk Space Problem:{RESET}")
                print(f"   • Free up disk space (need ~2-5GB)")
                print(f"   • Check: df -h ~")

            elif "permission" in error_msg:
                print(f"\n{FG_YELLOW}🔒 Permission Problem:{RESET}")
                print(f"   • Check ~/.cache/huggingface/ permissions")
                print(f"   • Try: chmod -R u+w ~/.cache/huggingface/")

            else:
                print(f"\n{FG_YELLOW}❓ Unknown Error:{RESET}")
                print(f"   Error details: {e}")

            print(f"\n{FG_CYAN}💡 Quick Fixes:{RESET}")
            print(f"   1. Try smaller model: edit ~/mlx-code line 43")
            print(f"      Change to: Qwen2.5-Coder-1.5B-Instruct-4bit")
            print(f"   2. Manual download: huggingface-cli download {model_name}")
            print(f"   3. Check logs: ls -la ~/.cache/huggingface/")
            print(f"{FG_RED}{'═' * 70}{RESET}\n")
            sys.exit(1)

        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        today = time.strftime("%Y-%m-%d")
        return textwrap.dedent(
            f"""You are MLX-CODE-PRO, an AI coding assistant. Today is {today}.
You have access to the user's project files. Answer questions and help with code.

When editing files, use this format:
```file:path/to/file.py
complete file content here
```
Use relative paths. Provide COMPLETE file content, not diffs.
Do NOT use ```python or ```js for file edits — only ```file:filename.

Be concise. Use markdown. Never hallucinate file names."""
        ).strip()

    def load_project_context(self, cwd: str):
        """Load project context files."""
        if not self.auto_context_enabled:
            return

        self.project_context = load_project_context(cwd)
        if self.project_context:
            print(f"{FG_CYAN}📁 Loaded project context: {', '.join(self.project_context.keys())}{RESET}")

    def auto_load_referenced_files(self, user_message: str, cwd: str) -> List[str]:
        """Automatically load files referenced in user message."""
        if not self.auto_context_enabled:
            return []

        referenced = extract_file_references(user_message, cwd)
        loaded = []

        for filepath in referenced:
            if filepath in self.opened_files:
                continue  # Already loaded

            if is_image_file(filepath):
                # Handle images
                desc = describe_image(filepath)
                self.opened_files[filepath] = desc
                loaded.append(filepath)
                continue

            if should_auto_load_file(filepath):
                try:
                    file_size = os.path.getsize(filepath)
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(10000)  # First 10KB
                        if file_size > 10000:
                            content += f"\n\n[... TRUNCATED — showing 10KB of {file_size / 1024:.1f}KB total ...]"
                            print(f"{FG_YELLOW}  ⚠ {os.path.basename(filepath)} truncated ({file_size / 1024:.1f}KB > 10KB limit){RESET}")
                        self.opened_files[filepath] = content
                        loaded.append(filepath)
                        self.stats["files_auto_loaded"] += 1
                except Exception:
                    continue

        if loaded:
            files_str = ', '.join([os.path.basename(f) for f in loaded])
            print(f"{FG_GREEN}📖 Auto-loaded: {files_str}{RESET}")

        return loaded

    def _build_context_section(self, cwd: str) -> str:
        """Build context section with project info and loaded files."""
        parts = []

        # Current directory and project type - VERY EXPLICIT
        project_type = detect_project_type(cwd)
        parts.append("=" * 70)
        parts.append(f"YOU ARE CURRENTLY IN THIS DIRECTORY: {cwd}")
        if cwd != ROOT_DIR:
            parts.append(f"Project root (where mlx-code was launched): {ROOT_DIR}")

        # List files in current directory for better context
        try:
            files_in_dir = os.listdir(cwd)[:10]  # First 10 files
            if files_in_dir:
                parts.append(f"Files in current directory: {', '.join(files_in_dir)}")
        except Exception:
            pass

        if project_type:
            parts.append(f"Project type: {project_type}")
        parts.append("=" * 70)

        # Project context files
        if self.project_context:
            parts.append("\nProject Configuration:")
            for filename, content in list(self.project_context.items())[:3]:  # Limit to 3
                parts.append(f"\n--- {filename} ---")
                parts.append(content[:500] + ("..." if len(content) > 500 else ""))

        # Opened files — with total budget enforcement
        if self.opened_files:
            budget_remaining = MAX_FILE_CONTEXT_CHARS
            files_included = 0
            # Iterate in reverse order (most recently added first = most relevant)
            file_items = list(self.opened_files.items())
            file_items.reverse()

            parts.append(f"\nFiles in context ({len(self.opened_files)} loaded, budget {MAX_FILE_CONTEXT_CHARS} chars):")

            for filepath, content in file_items:
                if budget_remaining <= 0:
                    skipped = len(file_items) - files_included
                    parts.append(f"\n[... {skipped} more file(s) skipped — context budget exhausted ...]")
                    break

                rel_path = os.path.relpath(filepath, ROOT_DIR)
                parts.append(f"\n--- {rel_path} ---")

                if content.startswith("[Image:"):
                    parts.append(content)
                    files_included += 1
                    continue

                # Fit within remaining budget
                max_for_file = min(len(content), budget_remaining, 3000)
                if len(content) > max_for_file:
                    preview = content[:max_for_file] + f"\n[... TRUNCATED — {len(content)} chars total, showing {max_for_file} ...]"
                else:
                    preview = content
                parts.append(preview)
                budget_remaining -= len(preview)
                files_included += 1

        return "\n".join(parts)

    def _build_prompt(self, user_message: str, cwd: str) -> str:
        """Build complete prompt using the tokenizer's native chat template.

        This works correctly with any model (Qwen, Llama, Mistral, Phi, DeepSeek, etc.)
        by delegating template formatting to the tokenizer itself.
        """
        context = self._build_context_section(cwd)

        # Put context in the system prompt to avoid repeating it every turn
        system_with_ctx = f"{self.system_prompt}\n\n{context}"

        # Build messages list in OpenAI-compatible format
        messages: List[Dict[str, str]] = []
        messages.append({"role": "system", "content": system_with_ctx})

        # Add relevant history (smart prioritization)
        for role, txt in self._get_prioritized_history():
            messages.append({"role": role, "content": txt})

        # Current user message — clean, no context duplication
        messages.append({"role": "user", "content": user_message})

        # Use tokenizer's native chat template
        try:
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            # Fallback: manual Qwen-style template for older tokenizers
            parts: List[str] = []
            for msg in messages:
                parts.append(f"<|im_start|>{msg['role']}\n{msg['content']}<|im_end|>")
            parts.append("<|im_start|>assistant")
            prompt = "\n".join(parts)

        return prompt

    def _get_prioritized_history(self) -> List[Tuple[str, str]]:
        """Get history with intelligent prioritization."""
        if not self.history:
            return []

        # Keep last 4 exchanges (8 messages)
        recent = self.history[-8:] if len(self.history) >= 8 else self.history

        # Add important context messages (file operations, opens)
        important = [
            (r, t) for r, t in self.history[:-8]
            if any(keyword in t for keyword in ["Opened file", "```file:", "Auto-loaded", "Project context"])
        ]

        # Combine, remove duplicates
        combined = important[-3:] + recent  # Max 3 old important + recent
        seen = set()
        result = []
        for r, t in combined:
            content_hash = hash(t[:100])  # Hash first 100 chars
            if content_hash not in seen:
                result.append((r, t))
                seen.add(content_hash)

        return result

    def _trim_history(self):
        """Smart context trimming."""
        total = sum(len(t) for _, t in self.history)
        if total <= self.ctx_chars:
            return

        # Keep important messages, trim others
        while self.history and total > self.ctx_chars:
            removed = False
            for i in range(len(self.history) - 8):  # Don't touch last 8
                role, txt = self.history[i]
                if not any(keyword in txt for keyword in ["Opened", "```file:", "Auto-loaded", "Project"]):
                    self.history.pop(i)
                    total -= len(txt)
                    removed = True
                    break

            if not removed and len(self.history) > 8:
                role, txt = self.history.pop(0)
                total -= len(txt)
            else:
                break

    def ask(self, user_message: str, cwd: str) -> str:
        """Send query with automatic context loading and streaming output."""
        self.last_query = user_message
        self.stats["queries"] += 1

        # Auto-load referenced files
        self.auto_load_referenced_files(user_message, cwd)

        # Build and send prompt
        prompt = self._build_prompt(user_message, cwd)

        # Count prompt tokens for stats
        try:
            prompt_tokens = len(self.tokenizer.encode(prompt))
            self.stats["prompt_tokens"] += prompt_tokens
        except Exception:
            prompt_tokens = 0

        # Stream response token by token with markdown rendering
        response_parts: List[str] = []
        token_count = 0
        start_time = time.time()
        renderer = StreamRenderer()

        # Repetition detection: track recent output to detect stuck loops
        recent_window = ""
        repetition_detected = False

        # Show thinking indicator while prompt is processed
        print(f"{DIM}Thinking...{RESET}", end="", flush=True)

        try:
            first_token = True
            for chunk in stream_generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=self.max_tokens,
            ):
                if first_token:
                    # Clear "Thinking..." and start showing response
                    print(f"\r{' ' * 20}\r", end="", flush=True)
                    first_token = False
                text = chunk.text
                # Stop at end-of-turn tokens (model-agnostic cleanup)
                if any(stop in text for stop in ["<|im_end|>", "<|im_start|>", "<|eot_id|>", "</s>"]):
                    for stop in ["<|im_end|>", "<|im_start|>", "<|eot_id|>", "</s>"]:
                        text = text.split(stop)[0]
                    if text:
                        renderer.feed(text)
                        response_parts.append(text)
                    break
                renderer.feed(text)
                response_parts.append(text)
                token_count += 1

                # Repetition detection — check every 50 tokens
                if token_count % 50 == 0 and token_count >= 150:
                    full_text = "".join(response_parts)
                    tail = full_text[-300:]  # Last 300 chars
                    # Check if a pattern of 30+ chars repeats 3+ times
                    for pat_len in range(30, 80):
                        if pat_len > len(tail) // 3:
                            break
                        pattern = tail[-pat_len:]
                        if tail.count(pattern) >= 3:
                            repetition_detected = True
                            break
                    if repetition_detected:
                        print(f"\n{FG_YELLOW}(repetition detected — stopping generation){RESET}")
                        break
        except KeyboardInterrupt:
            print(f"\n{FG_YELLOW}(generation interrupted){RESET}")
        except Exception as e:
            print(f"\n{FG_RED}Error generating response: {e}{RESET}")
            return f"Error generating response: {e}"

        renderer.flush()
        elapsed = time.time() - start_time
        speed = token_count / elapsed if elapsed > 0 else 0
        print(f"\n{DIM}[{token_count} tokens, {speed:.1f} tok/s]{RESET}")

        response = "".join(response_parts).strip()

        # Update stats and history
        self.stats["tokens_generated"] += token_count
        self.history.append(("user", user_message))
        self.history.append(("assistant", response))
        self._trim_history()

        # Auto-save conversation to disk
        autosave_conversation(self.history, self.model_name, ROOT_DIR)

        return response

    def clear_context(self):
        """Clear loaded files context."""
        self.opened_files.clear()
        self.project_context.clear()
        print(f"{FG_GREEN}✓ Context cleared{RESET}")


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
    """Extract file blocks from response."""
    blocks = []
    for m in FILE_BLOCK_RE.finditer(text):
        path = m.group("path").strip()
        content = m.group("content")
        blocks.append({"path": path, "content": content})
    return blocks


def extract_code_blocks(text: str):
    """Extract code blocks from response."""
    blocks = []
    for m in CODE_BLOCK_RE.finditer(text):
        if m.group("lang").strip().startswith("file:"):
            continue
        lang = m.group("lang").strip()
        content = m.group("content")
        blocks.append({"lang": lang, "content": content})
    return blocks


def _render_inline_markdown(line: str) -> str:
    """Apply inline markdown formatting: **bold**, *italic*, `code`."""
    # Inline code: `text` -> magenta
    line = re.sub(r'`([^`]+)`', f'{FG_MAGENTA}\\1{RESET}', line)
    # Bold: **text** -> bold
    line = re.sub(r'\*\*([^*]+)\*\*', f'{BOLD}\\1{RESET}', line)
    # Italic: *text* -> dim (avoid matching bullet lists)
    line = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', f'{DIM}\\1{RESET}', line)
    return line


def print_colored_response(text: str):
    """Print response with proper markdown formatting."""
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
            # Headers
            if re.match(r'^#{1,6}\s', line):
                print(BOLD + FG_CYAN + line + RESET)
            # Bullet lists (-, *, +)
            elif re.match(r'^(\s*)([-*+])\s', line):
                m = re.match(r'^(\s*)([-*+])\s(.*)', line)
                indent, bullet, content = m.group(1), m.group(2), m.group(3)
                print(f"{indent}{FG_GREEN}{bullet}{RESET} {_render_inline_markdown(content)}")
            # Numbered lists
            elif re.match(r'^(\s*)\d+[.)]\s', line):
                m = re.match(r'^(\s*)(\d+[.)]\s)(.*)', line)
                indent, num, content = m.group(1), m.group(2), m.group(3)
                print(f"{indent}{FG_GREEN}{num}{RESET}{_render_inline_markdown(content)}")
            # Horizontal rules
            elif re.match(r'^---+$|^\*\*\*+$|^___+$', line.strip()):
                print(DIM + line + RESET)
            # Blockquotes
            elif line.startswith('>'):
                print(f"{FG_YELLOW}│{RESET} {DIM}{line[1:].strip()}{RESET}")
            # Normal text
            else:
                print(_render_inline_markdown(line))


class StreamRenderer:
    """Line-buffered markdown renderer for streaming output."""

    def __init__(self):
        self.line_buffer = ""
        self.in_code_block = False

    def feed(self, text: str):
        """Feed a chunk of text. Renders complete lines with markdown colors."""
        self.line_buffer += text

        while "\n" in self.line_buffer:
            line, self.line_buffer = self.line_buffer.split("\n", 1)
            self._render_line(line)
            print(flush=True)

        # Flush partial lines to show streaming in real-time
        sys.stdout.flush()

    def flush(self):
        """Flush any remaining text in the buffer."""
        if self.line_buffer:
            self._render_line(self.line_buffer)
            self.line_buffer = ""
            sys.stdout.flush()

    def _render_line(self, line: str):
        """Render a single line with markdown formatting."""
        stripped = line.strip()

        # Code block delimiters
        if stripped.startswith("```"):
            print(FG_YELLOW + line + RESET, end="")
            self.in_code_block = not self.in_code_block
            return

        # Inside code block
        if self.in_code_block:
            print(FG_MAGENTA + line + RESET, end="")
            return

        # Headers
        if re.match(r'^#{1,6}\s', line):
            print(BOLD + FG_CYAN + line + RESET, end="")
        # Bullet lists
        elif re.match(r'^(\s*)([-*+])\s', line):
            m = re.match(r'^(\s*)([-*+])\s(.*)', line)
            if m:
                print(f"{m.group(1)}{FG_GREEN}{m.group(2)}{RESET} {_render_inline_markdown(m.group(3))}", end="")
            else:
                print(line, end="")
        # Numbered lists
        elif re.match(r'^(\s*)\d+[.)]\s', line):
            m = re.match(r'^(\s*)(\d+[.)]\s)(.*)', line)
            if m:
                print(f"{m.group(1)}{FG_GREEN}{m.group(2)}{RESET}{_render_inline_markdown(m.group(3))}", end="")
            else:
                print(line, end="")
        # Blockquotes
        elif line.startswith('>'):
            print(f"{FG_YELLOW}│{RESET} {DIM}{line[1:].strip()}{RESET}", end="")
        # Horizontal rules
        elif re.match(r'^---+$|^\*\*\*+$|^___+$', stripped):
            print(DIM + line + RESET, end="")
        # Normal text with inline formatting
        else:
            print(_render_inline_markdown(line), end="")


def print_diff(old: str, new: str, path_display: str):
    """Print colored diff."""
    print(f"\n{FG_WHITE}{BOLD}{'─' * 70}{RESET}")
    print(f"{FG_WHITE}{BOLD}📝 Changes for: {path_display}{RESET}")
    print(f"{FG_WHITE}{BOLD}{'─' * 70}{RESET}")

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
    print(f"{FG_WHITE}{BOLD}{'─' * 70}{RESET}\n")


def apply_file_changes(blocks, current_dir: str, session: ChatSession):
    """Apply file changes with safety checks and backups."""
    if not blocks:
        return

    print(f"\n{FG_YELLOW}📝 Found {len(blocks)} file(s) to modify{RESET}\n")

    changes_to_apply = []

    for block in blocks:
        rel_path = block["path"].strip()
        abs_path = resolve_path(rel_path, current_dir)

        # Safety checks
        if not is_safe_path(abs_path):
            print(f"{BG_RED}{FG_WHITE} ⛔ BLOCKED {RESET} {FG_RED}Path outside sandbox: {abs_path}{RESET}")
            log_operation("BLOCKED_WRITE", abs_path)
            continue

        if not is_allowed_file(abs_path):
            print(f"{FG_YELLOW}⚠️  Warning: {abs_path} has unusual extension{RESET}")
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
            print(f"\n{FG_WHITE}{BOLD}{'─' * 70}{RESET}")
            print(f"{FG_GREEN}➕ NEW FILE: {rel_display}{RESET}")
            print(f"{FG_WHITE}{BOLD}{'─' * 70}{RESET}")
            print(FG_MAGENTA + new_content[:600] + ("..." if len(new_content) > 600 else "") + RESET)
            print(f"{FG_WHITE}{BOLD}{'─' * 70}{RESET}\n")

        changes_to_apply.append({
            "path": abs_path,
            "display": rel_display,
            "old": old_content,
            "new": new_content,
        })

    if not changes_to_apply:
        return

    # Batch confirmation
    print(f"\n{FG_YELLOW}{'═' * 70}{RESET}")
    print(f"{FG_YELLOW}✅ Ready to apply changes to {len(changes_to_apply)} file(s){RESET}")
    print(f"{FG_YELLOW}{'═' * 70}{RESET}")

    for change in changes_to_apply:
        print(f"  • {change['display']}")

    print(f"\n{FG_YELLOW}Options:{RESET}")
    print(f"  {FG_GREEN}[a]{RESET} Apply all changes")
    print(f"  {FG_CYAN}[i]{RESET} Apply individually")
    print(f"  {FG_RED}[n]{RESET} Cancel all")

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
        print(f"{FG_CYAN}❌ Cancelled. No files were modified.{RESET}")


def _write_file(change: Dict, session: ChatSession):
    """Write file with backup."""
    try:
        # Backup if exists
        if change["old"]:
            backup_path = create_backup(change["path"])
            if backup_path:
                print(f"{FG_BLUE}  💾 Backup created{RESET}")

        # Write
        os.makedirs(os.path.dirname(change["path"]), exist_ok=True)
        with open(change["path"], "w", encoding="utf-8") as f:
            f.write(change["new"])

        print(f"{FG_GREEN}  ✅ Wrote {change['display']}{RESET}")

        # Update tracking
        session.stats["files_modified"] += 1
        session.last_modified_files.append(change["path"])
        log_operation("FILE_WRITE", change["display"])

        # Add to opened files for context
        session.opened_files[change["path"]] = change["new"]

    except Exception as e:
        print(f"{FG_RED}  ❌ Error writing {change['path']}: {e}{RESET}")
        log_operation("FILE_WRITE_ERROR", f"{change['path']}: {e}")


def maybe_save_code_block(text: str, current_dir: str, session: ChatSession):
    """Offer to save code blocks."""
    blocks = extract_code_blocks(text)
    if not blocks:
        return

    first = blocks[0]
    lang = first["lang"] or "txt"
    content = first["content"].rstrip("\n") + "\n"

    # Skip markdown and text blocks (usually just for display)
    skip_langs = ['markdown', 'md', 'text', 'txt', '']
    if lang.lower() in skip_langs:
        return

    # Skip very short blocks (< 3 lines, probably just examples)
    if len(content.splitlines()) < 3:
        return

    print(f"\n{FG_YELLOW}💡 Detected a code block (language: {lang or 'plain text'}).{RESET}")
    ans = input(
        f"{FG_YELLOW}Save to file? (enter filename or leave blank): {RESET}"
    ).strip()

    if not ans:
        return

    # Auto-suggest extension
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
        print(f"{FG_RED}Cannot save outside sandbox{RESET}")
        return

    old_content = ""
    if os.path.exists(abs_path):
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                old_content = f.read()
        except Exception:
            pass

    rel_display = os.path.relpath(abs_path, ROOT_DIR)

    if old_content:
        print_diff(old_content, content, rel_display)
    else:
        print(f"\n{FG_GREEN}➕ NEW FILE: {rel_display}{RESET}")

    confirm = input(f"{FG_YELLOW}Write code? [y/N] {RESET}").strip().lower()
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
    target = resolve_path(" ".join(parts[1:]) if len(parts) > 1 else "", cwd)

    if not is_safe_path(target):
        print(f"{FG_RED}Cannot access outside sandbox{RESET}")
        return

    if not os.path.isdir(target):
        print(f"{FG_RED}Not a directory: {target}{RESET}")
        return

    print(f"\n{FG_CYAN}📁 Directory structure:{RESET}")
    print(f"{FG_BLUE}{target}/{RESET}")
    print_tree(target)
    print()


def handle_grep(parts: List[str], cwd: str):
    """Handle /grep command."""
    if len(parts) < 2:
        print(f"{FG_RED}Usage: /grep <pattern> [path]{RESET}")
        return

    pattern = parts[1]
    target = resolve_path(" ".join(parts[2:]) if len(parts) > 2 else "", cwd)

    if not is_safe_path(target):
        print(f"{FG_RED}Cannot search outside sandbox{RESET}")
        return

    print(f"{FG_CYAN}🔍 Searching for '{pattern}'...{RESET}")
    results = grep_files(pattern, target, ALLOWED_EXTENSIONS)

    if not results:
        print(f"{FG_YELLOW}No matches found.{RESET}")
        return

    print(f"\n{FG_GREEN}Found {len(results)} match(es):{RESET}\n")
    for file_path, line_num, line_content in results[:50]:
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

        print_diff(content1, content2, f"{rel1} ↔ {rel2}")
    except Exception as e:
        print(f"{FG_RED}Error reading files: {e}{RESET}")


def handle_template(parts: List[str], cwd: str, session: ChatSession) -> Optional[str]:
    """Handle /template command."""
    if len(parts) < 2:
        print(f"\n{FG_CYAN}📋 Available templates:{RESET}\n")
        for name, desc in TEMPLATES.items():
            print(f"  {FG_GREEN}{name:12}{RESET} - {desc[:50]}...")
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


def handle_context(parts: List[str], session: ChatSession, cwd: str):
    """Handle /context command."""
    if len(parts) < 2:
        # Show current context
        print(f"\n{FG_CYAN}📚 Current Context:{RESET}\n")
        print(
            f"  Auto-context: {FG_GREEN if session.auto_context_enabled else FG_RED}{'enabled' if session.auto_context_enabled else 'disabled'}{RESET}")
        print(f"  Project files: {len(session.project_context)}")
        print(f"  Loaded files: {len(session.opened_files)}")

        # Show context budget usage
        total_chars = sum(len(c) for c in session.opened_files.values())
        pct = (total_chars / MAX_FILE_CONTEXT_CHARS * 100) if MAX_FILE_CONTEXT_CHARS > 0 else 0
        bar_len = 20
        filled = int(bar_len * min(pct, 100) / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        color = FG_GREEN if pct < 70 else (FG_YELLOW if pct < 90 else FG_RED)
        print(f"  Context budget: {color}{bar} {total_chars}/{MAX_FILE_CONTEXT_CHARS} chars ({pct:.0f}%){RESET}")

        if session.project_context:
            print(f"\n  {FG_CYAN}Project context files:{RESET}")
            for name, content in session.project_context.items():
                print(f"    • {name} ({len(content)} chars)")

        if session.opened_files:
            print(f"\n  {FG_CYAN}Opened files:{RESET}")
            for path, content in session.opened_files.items():
                rel = os.path.relpath(path, ROOT_DIR)
                print(f"    • {rel} ({len(content)} chars)")

        print()
        return

    subcmd = parts[1].lower()

    if subcmd == "on":
        session.auto_context_enabled = True
        print(f"{FG_GREEN}✓ Auto-context enabled{RESET}")
    elif subcmd == "off":
        session.auto_context_enabled = False
        print(f"{FG_YELLOW}⚠ Auto-context disabled{RESET}")
    elif subcmd == "clear":
        session.clear_context()
    elif subcmd == "reload":
        session.clear_context()
        session.load_project_context(cwd)
    else:
        print(f"{FG_RED}Unknown subcommand. Use: on, off, clear, reload{RESET}")


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

    print(f"\n{FG_CYAN}💾 Available backups ({len(backups)}):{RESET}\n")
    for backup in backups[:20]:
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
            print(f"{FG_GREEN}✅ Restored successfully{RESET}")
            log_operation("RESTORE", f"{backup_name} -> {target_path}")
        else:
            print(f"{FG_RED}❌ Restore failed{RESET}")


def handle_stats(session: ChatSession):
    """Handle /stats command."""
    print(f"\n{FG_CYAN}{'═' * 60}{RESET}")
    print(f"{FG_CYAN}{BOLD}📊 Session Statistics{RESET}")
    print(f"{FG_CYAN}{'═' * 60}{RESET}")
    print(f"  Queries sent:           {session.stats['queries']}")
    print(f"  Files modified:         {session.stats['files_modified']}")
    print(f"  Files auto-loaded:      {session.stats['files_auto_loaded']}")
    print(f"  Prompt tokens (total):  {session.stats['prompt_tokens']}")
    print(f"  Generated tokens:       {session.stats['tokens_generated']}")
    print(f"  Files in context:       {len(session.opened_files)}")
    print(f"  Project context files:  {len(session.project_context)}")
    print(f"  History entries:        {len(session.history)}")
    print(
        f"  Auto-context:           {FG_GREEN if session.auto_context_enabled else FG_RED}{'enabled' if session.auto_context_enabled else 'disabled'}{RESET}")
    print(f"{FG_CYAN}{'═' * 60}{RESET}\n")


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

def print_banner():
    logo = r"""
███╗   ███╗██╗     ██╗  ██╗      ██████╗ ██████╗  ██████╗ 
████╗ ████║██║     ██║ ██╔╝      ██╔══██╗██╔══██╗██╔═══██╗
██╔████╔██║██║     █████╔╝ █████╗██████╔╝██████╔╝██║   ██║
██║╚██╔╝██║██║     ██╔═██╗ ╚════╝██╔═══╝ ██╔══██╗██║   ██║
██║ ╚═╝ ██║███████╗██║  ██╗      ██║     ██║  ██║╚██████╔╝
╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝      ╚═╝     ╚═╝  ╚═╝ ╚═════╝ 

    🚀 Intelligent Context-Aware Coding Assistant 🚀
"""
    print(FG_MAGENTA + logo + RESET)


def print_help():
    print("=" * 80)
    print(" MLX-CODE-PRO — Intelligent Context-Aware Coding Assistant")
    print("=" * 80)
    print(f"Working Directory: {FG_CYAN}{ROOT_DIR}{RESET}")
    print()
    print("🎯 KEY FEATURES:")
    print("  • Automatic file loading when you mention them")
    print("  • Full project context awareness")
    print("  • Image support (with PIL)")
    print("  • Smart code suggestions based on your codebase")
    print()
    print("CORE COMMANDS:")
    print(f"  {FG_GREEN}/help{RESET}                  Show this help")
    print(f"  {FG_GREEN}/exit{RESET}                  Quit")
    print(f"  {FG_GREEN}/clear{RESET}                 Clear chat history")
    print()
    print("CONTEXT MANAGEMENT:")
    print(f"  {FG_GREEN}/context{RESET}               Show current context")
    print(f"  {FG_GREEN}/context on|off{RESET}        Enable/disable auto-context")
    print(f"  {FG_GREEN}/context clear{RESET}         Clear loaded files")
    print(f"  {FG_GREEN}/context reload{RESET}        Reload project context")
    print(f"  {FG_GREEN}/open <file>{RESET}           Manually load file")
    print()
    print("MODEL & SETTINGS:")
    print(f"  {FG_GREEN}/model <id>{RESET}            Switch model")
    print(f"  {FG_GREEN}/models{RESET}                List available models")
    print(f"  {FG_GREEN}/installed{RESET}             Show installed models")
    print(f"  {FG_GREEN}/download <model>{RESET}      Download a model")
    print(f"  {FG_GREEN}/delete <model>{RESET}        Delete a model from cache")
    print()
    print(f"  {FG_CYAN}Quick model switches (M4 Pro 24GB optimized):{RESET}")
    print(f"    {FG_GREEN}/q1.5b{RESET} (1GB)   {FG_GREEN}/q3b{RESET} (2GB)    {FG_GREEN}/q7b{RESET} (4GB)    {FG_GREEN}/q14b{RESET} (9GB)   {FG_GREEN}/q32b{RESET} (17GB)")
    print(f"    {FG_GREEN}/ds1.3b{RESET} (1GB)  {FG_GREEN}/ds6.7b{RESET} (4GB)  {FG_GREEN}/ds{RESET} (9GB)     {FG_GREEN}/deepseek{RESET} (9GB)")
    print(f"    {FG_GREEN}/phi3{RESET} (2GB)    {FG_GREEN}/llama3-8b{RESET} (5GB)  {FG_GREEN}/mistral{RESET} (4GB)  {FG_GREEN}/codellama{RESET} (7GB)")
    print()
    print(f"  {FG_GREEN}/tokens <n>{RESET}            Set max tokens")
    print(f"  {FG_GREEN}/ctx <n>{RESET}               Set context size")
    print()
    print("NAVIGATION:")
    print(f"  {FG_GREEN}/pwd{RESET}                   Show directory")
    print(f"  {FG_GREEN}/cd <path>{RESET}             Change directory")
    print(f"  {FG_GREEN}/ls [path]{RESET}             List files")
    print(f"  {FG_GREEN}/tree [path]{RESET}           Show tree")
    print()
    print("SEARCH & COMPARE:")
    print(f"  {FG_GREEN}/find <pattern>{RESET}        Find files by name (glob)")
    print(f"  {FG_GREEN}/grep <pattern>{RESET}        Search in file contents")
    print(f"  {FG_GREEN}/diff <f1> <f2>{RESET}        Compare files")
    print(f"  {FG_GREEN}/replace <f> \"a\" \"b\"{RESET}  Find and replace in file")
    print()
    print("GIT:")
    print(f"  {FG_GREEN}/git{RESET}                   Show git subcommands")
    print(f"  {FG_GREEN}/git status{RESET}             Show changed files")
    print(f"  {FG_GREEN}/git diff{RESET}               Show changes")
    print(f"  {FG_GREEN}/git log{RESET}                Recent commits")
    print(f"  {FG_GREEN}/git add <file>{RESET}         Stage file")
    print(f"  {FG_GREEN}/git commit <msg>{RESET}       Commit changes")
    print()
    print("TEMPLATES:")
    print(f"  {FG_GREEN}/template{RESET}              List templates")
    print(f"  {FG_GREEN}/template <name> <file>{RESET} Apply template")
    print(f"    Available: test, doc, refactor, review, optimize, explain, debug, secure")
    print()
    print("BACKUP & HISTORY:")
    print(f"  {FG_GREEN}/undo{RESET}                  Undo last file modification")
    print(f"  {FG_GREEN}/backups [file]{RESET}        List backups")
    print(f"  {FG_GREEN}/restore <bk> <file>{RESET}   Restore from backup")
    print(f"  {FG_GREEN}/save [file]{RESET}           Export chat")
    print()
    print("EXECUTION:")
    print(f"  {FG_GREEN}/run <command>{RESET}         Execute a shell command")
    print(f"  {FG_GREEN}/run <cmd> --ai{RESET}        Run and send output to AI")
    print()
    print("UTILITIES:")
    print(f"  {FG_GREEN}/copy{RESET}                  Copy last code block to clipboard")
    print(f"  {FG_GREEN}/last{RESET}                  Repeat last query")
    print(f"  {FG_GREEN}/edit{RESET}                  Open last file in $EDITOR")
    print(f"  {FG_GREEN}/stats{RESET}                 Show statistics")
    print(f"  {FG_GREEN}/project{RESET}               Detect project type")
    print()
    print("💡 SMART FEATURES:")
    print("  • Just mention a file (e.g., 'check main.py') and it's auto-loaded!")
    print("  • The assistant reads and understands your project structure")
    print("  • Multi-line input: finish with empty line")
    print("  • All files backed up before modification")
    print()
    if HAS_PROMPT_TOOLKIT:
        print("⌨️  KEYBOARD SHORTCUTS:")
        print("  • ↑/↓ Arrow keys: Navigate command history")
        print("  • ←/→ Arrow keys: Move cursor for editing")
        print("  • Tab: Auto-complete commands")
        print("  • Ctrl+C: Clear current input (or use /exit to quit)")
        print("  • Ctrl+D: Exit")
        print("  • Ctrl+R: Search command history")
    else:
        print(f"{FG_YELLOW}💡 Install prompt-toolkit for better input: pip install prompt-toolkit{RESET}")
    print("=" * 80)


def print_status(model_name: str, cwd: str, project_type: Optional[str], session: ChatSession):
    model_short = model_name.split('/')[-1][:35]
    cwd_short = cwd.replace(ROOT_DIR, "~")

    status_parts = [f"📂 {cwd_short}"]
    if project_type:
        status_parts.append(f"🔧 {project_type}")
    status_parts.append(f"🤖 {model_short}")

    auto_ctx = "🟢" if session.auto_context_enabled else "🔴"
    status_parts.append(f"{auto_ctx} auto-context")

    print("=" * 80)
    print(" | ".join(status_parts))
    print("=" * 80)


# ---------------------------------------------------------------------------
# APP STATE (shared mutable state for command handlers)
# ---------------------------------------------------------------------------

class AppState:
    """Mutable application state shared across command handlers."""

    def __init__(self, model_name: str, max_tokens: int, ctx_chars: int, cwd: str, session: ChatSession):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.ctx_chars = ctx_chars
        self.cwd = cwd
        self.session = session
        self.project_type = detect_project_type(cwd)
        self.buffer: List[str] = []

    def reload_session(self):
        """Create a new ChatSession preserving history and context."""
        old_history = self.session.history[:]
        old_files = dict(self.session.opened_files)
        old_stats = dict(self.session.stats)
        old_auto_ctx = self.session.auto_context_enabled

        self.session = ChatSession(self.model_name, self.max_tokens, self.ctx_chars)
        self.session.history = old_history
        self.session.opened_files = old_files
        self.session.stats = old_stats
        self.session.auto_context_enabled = old_auto_ctx
        self.session.load_project_context(self.cwd)
        self.project_type = detect_project_type(self.cwd)


# ---------------------------------------------------------------------------
# COMMAND HANDLERS (each returns a signal: None=continue, "break"=exit)
# ---------------------------------------------------------------------------

def cmd_exit(parts: List[str], state: AppState) -> Optional[str]:
    config = {
        "model": state.model_name,
        "max_tokens": state.max_tokens,
        "ctx_chars": state.ctx_chars,
    }
    save_config(config)
    clear_autosave()
    print("Configuration saved. 👋 Goodbye!")
    return "break"


def cmd_help(parts: List[str], state: AppState) -> None:
    print_help()
    print_status(state.model_name, state.cwd, state.project_type, state.session)


def cmd_clear(parts: List[str], state: AppState) -> None:
    state.session.history.clear()
    print(f"{FG_GREEN}✓ Chat history cleared{RESET}")


def cmd_model(parts: List[str], state: AppState) -> None:
    if len(parts) < 2:
        print(f"{FG_RED}Usage: /model <huggingface-model-id>{RESET}")
        return
    state.model_name = parts[1].strip()
    state.reload_session()
    print_status(state.model_name, state.cwd, state.project_type, state.session)


def cmd_models(parts: List[str], state: AppState) -> None:
    print(f"\n{FG_CYAN}{'═' * 80}{RESET}")
    print(f"{FG_CYAN}{BOLD}📦 Available Models{RESET}")
    print(f"{FG_CYAN}{'═' * 80}{RESET}\n")

    models = list_available_models()
    categories = {
        "Qwen Coder (Recommended for Code)": ["q1.5b", "q3b", "q7b", "q14b", "q32b"],
        "DeepSeek Coder (Excellent)": ["ds1.3b", "ds6.7b", "ds", "deepseek"],
        "Mistral (Versatile)": ["mistral", "m7b"],
        "Llama 3 (Strong Reasoning)": ["llama3-8b", "l3-8b"],
        "Phi (Efficient)": ["phi3", "phi"],
        "CodeLlama (Code Specialist)": ["codellama", "cl13b"],
    }

    for category, aliases in categories.items():
        print(f"{FG_YELLOW}{BOLD}{category}{RESET}")
        for alias in aliases:
            if alias in models:
                model = models[alias]
                status = f"{FG_GREEN}✓ Installed{RESET}" if model["cached"] else f"{FG_RED}✗ Not installed{RESET}"
                print(f"  {FG_GREEN}/{alias:12}{RESET}  {model['size']:>7}  {model['ram']:>10} RAM  {status}")
        print()

    print(f"{FG_CYAN}💡 Usage:{RESET}")
    print(f"  • Switch model: {FG_GREEN}/<alias>{RESET} (e.g., /q32b)")
    print(f"  • Download: {FG_GREEN}/download <alias>{RESET} (e.g., /download q32b)")
    print(f"  • Delete: {FG_GREEN}/delete <alias>{RESET}")
    print(f"\n{FG_CYAN}{'═' * 80}{RESET}\n")


def cmd_installed(parts: List[str], state: AppState) -> None:
    installed = list_installed_models()
    if not installed:
        print(f"\n{FG_YELLOW}No models installed yet.{RESET}")
        print(f"{FG_CYAN}Use {FG_GREEN}/models{FG_CYAN} to see available models{RESET}\n")
        return

    print(f"\n{FG_CYAN}{'═' * 80}{RESET}")
    print(f"{FG_CYAN}{BOLD}💾 Installed Models{RESET}")
    print(f"{FG_CYAN}{'═' * 80}{RESET}\n")

    total_size = 0
    for m_name, dir_name, size_str in installed:
        size_gb = float(size_str.replace("GB", ""))
        total_size += size_gb

        alias = None
        for a, full_name in MODEL_ALIASES.items():
            if full_name == m_name:
                alias = f"/{a}"
                break

        alias_str = f"{FG_GREEN}{alias}{RESET}" if alias else ""
        print(f"  {FG_CYAN}{m_name:55}{RESET} {size_str:>8}  {alias_str}")

    print(f"\n{FG_YELLOW}Total disk usage: {total_size:.2f}GB{RESET}")
    print(f"{FG_CYAN}Cache location: ~/.cache/huggingface/hub/{RESET}")
    print(f"{FG_CYAN}{'═' * 80}{RESET}\n")


def cmd_download(parts: List[str], state: AppState) -> None:
    if len(parts) < 2:
        print(f"{FG_RED}Usage: /download <model-alias>{RESET}")
        print(f"{FG_CYAN}Example: /download q32b{RESET}")
        print(f"{FG_CYAN}Use {FG_GREEN}/models{FG_CYAN} to see available models{RESET}")
        return

    alias = parts[1].lower()
    if alias not in MODEL_ALIASES:
        print(f"{FG_RED}Unknown model alias: {alias}{RESET}")
        print(f"{FG_CYAN}Use {FG_GREEN}/models{FG_CYAN} to see available models{RESET}")
        return

    target_model = MODEL_ALIASES[alias]

    if is_model_cached(target_model):
        print(f"{FG_YELLOW}Model {alias} is already downloaded!{RESET}")
        ans = input(f"{FG_YELLOW}Re-download anyway? [y/N] {RESET}").strip().lower()
        if ans != 'y':
            return

    size = get_model_size_estimate(target_model)
    ram = get_model_ram_requirement(target_model)

    print(f"\n{FG_CYAN}{'═' * 70}{RESET}")
    print(f"{FG_CYAN}📥 Download Model: {FG_GREEN}/{alias}{RESET}")
    print(f"{FG_CYAN}{'═' * 70}{RESET}")
    print(f"  Model: {target_model}")
    print(f"  Size: {size}")
    print(f"  RAM needed: {ram}")
    print(f"{FG_CYAN}{'═' * 70}{RESET}\n")

    confirm = input(f"{FG_YELLOW}Download this model? [y/N] {RESET}").strip().lower()
    if confirm != 'y':
        print(f"{FG_CYAN}Download cancelled.{RESET}")
        return

    print(f"\n{FG_CYAN}Starting download...{RESET}\n")
    success = download_model_with_git_lfs(target_model)

    if not success:
        print(f"{FG_CYAN}Falling back to standard download...{RESET}\n")
        try:
            spinner = Spinner("Downloading model")
            spinner.start()
            _model, _tokenizer = load(target_model)
            spinner.stop()
            print(f"{FG_GREEN}✅ Model downloaded successfully!{RESET}\n")
            del _model, _tokenizer
        except Exception as e:
            spinner.stop()
            print(f"{FG_RED}❌ Download failed: {e}{RESET}\n")


def cmd_delete(parts: List[str], state: AppState) -> None:
    if len(parts) < 2:
        print(f"{FG_RED}Usage: /delete <model-alias>{RESET}")
        print(f"{FG_CYAN}Example: /delete q3b{RESET}")
        print(f"{FG_CYAN}Use {FG_GREEN}/installed{FG_CYAN} to see installed models{RESET}")
        return

    alias = parts[1].lower()
    if alias not in MODEL_ALIASES:
        print(f"{FG_RED}Unknown model alias: {alias}{RESET}")
        print(f"{FG_CYAN}Use {FG_GREEN}/models{FG_CYAN} to see available models{RESET}")
        return

    target_model = MODEL_ALIASES[alias]
    if not is_model_cached(target_model):
        print(f"{FG_YELLOW}Model {alias} is not installed.{RESET}")
        return

    print(f"\n{FG_YELLOW}⚠️  WARNING: This will delete the model from disk!{RESET}")
    print(f"  Model: {target_model}")
    print(f"  Alias: /{alias}\n")

    confirm = input(f"{FG_YELLOW}Are you sure? [y/N] {RESET}").strip().lower()
    if confirm != 'y':
        print(f"{FG_CYAN}Deletion cancelled.{RESET}")
        return

    if delete_model(target_model):
        print(f"{FG_GREEN}✅ Model deleted successfully!{RESET}")
        log_operation("MODEL_DELETE", target_model)
    else:
        print(f"{FG_RED}❌ Failed to delete model{RESET}")


def cmd_tokens(parts: List[str], state: AppState) -> None:
    if len(parts) != 2 or not parts[1].isdigit():
        print(f"{FG_RED}Usage: /tokens <number>{RESET}")
        return
    state.max_tokens = int(parts[1])
    state.session.max_tokens = state.max_tokens
    print(f"{FG_GREEN}✓ Max tokens: {state.max_tokens}{RESET}")


def cmd_ctx(parts: List[str], state: AppState) -> None:
    if len(parts) != 2 or not parts[1].isdigit():
        print(f"{FG_RED}Usage: /ctx <number>{RESET}")
        return
    state.ctx_chars = int(parts[1])
    state.session.ctx_chars = state.ctx_chars
    print(f"{FG_GREEN}✓ Context size: {state.ctx_chars} chars{RESET}")


def cmd_pwd(parts: List[str], state: AppState) -> None:
    rel = state.cwd.replace(ROOT_DIR, "~")
    print(f"{FG_CYAN}{rel}{RESET}")


def cmd_cd(parts: List[str], state: AppState) -> None:
    if len(parts) < 2:
        print(f"{FG_RED}Usage: /cd <path>{RESET}")
        return
    target = resolve_path(" ".join(parts[1:]), state.cwd)
    if not is_safe_path(target):
        print(f"{FG_RED}Cannot cd outside sandbox{RESET}")
        return
    if not os.path.isdir(target):
        print(f"{FG_RED}No such directory: {target}{RESET}")
        return
    state.cwd = target
    os.chdir(state.cwd)
    state.session.clear_context()
    state.session.load_project_context(state.cwd)
    state.project_type = detect_project_type(state.cwd)

    # Load per-project config if present
    project_cfg = load_project_config(state.cwd)
    if project_cfg:
        if "auto_context" in project_cfg:
            state.session.auto_context_enabled = bool(project_cfg["auto_context"])
        print(f"{FG_CYAN}📋 Loaded project config from .mlx-code.json{RESET}")

    print_status(state.model_name, state.cwd, state.project_type, state.session)


def cmd_ls(parts: List[str], state: AppState) -> None:
    target = resolve_path(" ".join(parts[1:]) if len(parts) > 1 else "", state.cwd)
    if not is_safe_path(target):
        print(f"{FG_RED}Cannot list outside sandbox{RESET}")
        return
    if not os.path.isdir(target):
        print(f"{FG_RED}No such directory{RESET}")
        return
    entries = sorted(os.listdir(target))
    for name in entries:
        full = os.path.join(target, name)
        if os.path.isdir(full):
            print(FG_BLUE + name + "/" + RESET)
        else:
            print(name)


def cmd_open(parts: List[str], state: AppState) -> None:
    """Open a file into context. Supports line ranges: /open file.py:10-50"""
    if len(parts) < 2:
        print(f"{FG_RED}Usage: /open <file>[:<start>-<end>]{RESET}")
        print(f"{FG_CYAN}Examples:{RESET}")
        print(f"  {FG_GREEN}/open main.py{RESET}           Load entire file")
        print(f"  {FG_GREEN}/open main.py:10-50{RESET}     Load lines 10-50")
        print(f"  {FG_GREEN}/open main.py:100{RESET}       Load from line 100 onward")
        return

    raw_arg = " ".join(parts[1:])
    line_start = None
    line_end = None

    # Parse line range (file.py:10-50 or file.py:100)
    if ":" in raw_arg:
        last_colon = raw_arg.rfind(":")
        range_part = raw_arg[last_colon + 1:]
        file_part = raw_arg[:last_colon]

        # Check if it looks like a line range (not a Windows path like C:\...)
        if re.match(r'^\d+(-\d+)?$', range_part):
            if "-" in range_part:
                try:
                    line_start, line_end = map(int, range_part.split("-", 1))
                except ValueError:
                    pass
            else:
                try:
                    line_start = int(range_part)
                except ValueError:
                    pass
            raw_arg = file_part

    target = resolve_path(raw_arg, state.cwd)
    if not is_safe_path(target):
        print(f"{FG_RED}Cannot open outside sandbox{RESET}")
        return
    if not os.path.isfile(target):
        print(f"{FG_RED}No such file: {raw_arg}{RESET}")
        return

    try:
        if is_image_file(target):
            desc = describe_image(target)
            state.session.opened_files[target] = desc
            print(f"{FG_GREEN}✓ Loaded image: {desc}{RESET}")
            return

        file_size = os.path.getsize(target)
        rel = os.path.relpath(target, ROOT_DIR)

        with open(target, "r", encoding="utf-8") as f:
            all_lines = f.readlines()

        total_lines = len(all_lines)

        # Apply line range
        if line_start is not None:
            start_idx = max(0, line_start - 1)  # Convert to 0-based
            end_idx = line_end if line_end else total_lines
            end_idx = min(end_idx, total_lines)

            selected = all_lines[start_idx:end_idx]
            # Add line numbers for context
            numbered = []
            for i, line in enumerate(selected, start=start_idx + 1):
                numbered.append(f"{i:4d} | {line.rstrip()}")
            content = f"[Lines {start_idx + 1}-{end_idx} of {total_lines} in {rel}]\n" + "\n".join(numbered)
            range_str = f" (lines {start_idx + 1}-{end_idx} of {total_lines})"
        else:
            content = "".join(all_lines)
            range_str = ""

        state.session.opened_files[target] = content
        print(f"{FG_GREEN}✓ Loaded {rel}{range_str} — {len(content)} chars, {total_lines} total lines, {file_size / 1024:.1f}KB{RESET}")

    except Exception as e:
        print(f"{FG_RED}Error: {e}{RESET}")


def cmd_template(parts: List[str], state: AppState) -> None:
    template_query = handle_template(parts, state.cwd, state.session)
    if template_query:
        state.buffer = [template_query]
        print(f"{FG_CYAN}Template ready. Press Enter to send.{RESET}")


def cmd_undo(parts: List[str], state: AppState) -> None:
    if not state.session.last_modified_files:
        print(f"{FG_YELLOW}Nothing to undo — no files modified yet.{RESET}")
        return

    last_file = state.session.last_modified_files[-1]
    rel_display = os.path.relpath(last_file, ROOT_DIR)
    backups = list_backups(last_file)

    if not backups:
        print(f"{FG_YELLOW}No backup found for {rel_display}{RESET}")
        return

    latest_backup = backups[0]
    print(f"{FG_CYAN}Undo last change to: {rel_display}{RESET}")
    print(f"{FG_CYAN}Restore from backup: {latest_backup}{RESET}")

    confirm = input(f"{FG_YELLOW}Restore? [y/N] {RESET}").strip().lower()
    if confirm == 'y':
        if restore_backup(latest_backup, last_file):
            print(f"{FG_GREEN}✅ Restored {rel_display} to previous version{RESET}")
            state.session.last_modified_files.pop()
            log_operation("UNDO", rel_display)
            try:
                with open(last_file, 'r', encoding='utf-8', errors='ignore') as f:
                    state.session.opened_files[last_file] = f.read(10000)
            except Exception:
                pass
        else:
            print(f"{FG_RED}❌ Restore failed{RESET}")
    else:
        print(f"{FG_CYAN}Undo cancelled.{RESET}")


def cmd_save(parts: List[str], state: AppState) -> None:
    out_path_raw = " ".join(parts[1:]) if len(parts) > 1 else f"mlx-session-{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    out_path = resolve_path(out_path_raw, state.cwd)
    if not is_safe_path(out_path):
        print(f"{FG_RED}Cannot save outside sandbox{RESET}")
        return

    lines = [
        f"# MLX-CODE-PRO Session\n",
        f"**Model:** {state.model_name}\n",
        f"**Date:** {datetime.now().isoformat()}\n",
        f"**Project:** {state.project_type or 'Unknown'}\n",
        "\n---\n\n",
    ]
    for role, txt in state.session.history:
        emoji = "👤" if role == "user" else "🤖"
        lines.append(f"## {emoji} {role.title()}\n\n")
        lines.append(txt)
        lines.append("\n\n---\n\n")
    try:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("".join(lines))
        rel = os.path.relpath(out_path, ROOT_DIR)
        print(f"{FG_GREEN}✓ Saved to {rel}{RESET}")
    except Exception as e:
        print(f"{FG_RED}Error: {e}{RESET}")


def cmd_last(parts: List[str], state: AppState) -> None:
    if state.session.last_query:
        state.buffer = [state.session.last_query]
        print(f"{FG_CYAN}Repeating last query. Press Enter.{RESET}")
    else:
        print(f"{FG_YELLOW}No previous query{RESET}")


def cmd_edit(parts: List[str], state: AppState) -> None:
    if not state.session.last_modified_files:
        print(f"{FG_YELLOW}No files modified yet{RESET}")
        return
    editor = os.environ.get("EDITOR", "nano")
    last_file = state.session.last_modified_files[-1]
    print(f"{FG_CYAN}Opening in {editor}...{RESET}")
    subprocess.run([editor, last_file])


def cmd_git(parts: List[str], state: AppState) -> None:
    """Handle /git command with subcommands: status, diff, log, add, commit."""
    subcmds = {
        "status": ["git", "status", "--short"],
        "diff": ["git", "diff"],
        "log": ["git", "log", "--oneline", "-20"],
        "branch": ["git", "branch", "-a"],
        "stash": ["git", "stash", "list"],
    }

    if len(parts) < 2:
        print(f"\n{FG_CYAN}Git Commands:{RESET}")
        print(f"  {FG_GREEN}/git status{RESET}              Show changed files")
        print(f"  {FG_GREEN}/git diff{RESET}                Show unstaged changes")
        print(f"  {FG_GREEN}/git diff --staged{RESET}       Show staged changes")
        print(f"  {FG_GREEN}/git log{RESET}                 Show recent commits")
        print(f"  {FG_GREEN}/git branch{RESET}              List branches")
        print(f"  {FG_GREEN}/git add <file>{RESET}          Stage a file")
        print(f"  {FG_GREEN}/git add .{RESET}               Stage all changes")
        print(f"  {FG_GREEN}/git commit <message>{RESET}    Commit staged changes")
        print(f"  {FG_GREEN}/git stash{RESET}               List stashes")
        print()
        return

    subcmd = parts[1].lower()

    # Predefined safe subcommands
    if subcmd in subcmds:
        git_cmd = subcmds[subcmd]
        # Handle extra flags like /git diff --staged
        if len(parts) > 2:
            git_cmd = git_cmd + parts[2:]
    elif subcmd == "add":
        if len(parts) < 3:
            print(f"{FG_RED}Usage: /git add <file|.>{RESET}")
            return
        git_cmd = ["git", "add"] + parts[2:]
    elif subcmd == "commit":
        if len(parts) < 3:
            print(f"{FG_RED}Usage: /git commit <message>{RESET}")
            return
        message = " ".join(parts[2:])
        git_cmd = ["git", "commit", "-m", message]
    else:
        print(f"{FG_RED}Unknown git subcommand: {subcmd}{RESET}")
        print(f"{FG_YELLOW}Use /git for available commands{RESET}")
        return

    try:
        result = subprocess.run(
            git_cmd,
            cwd=state.cwd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout.strip()
        errors = result.stderr.strip()

        if output:
            # Color git diff output
            if subcmd == "diff":
                for line in output.splitlines():
                    if line.startswith("+") and not line.startswith("+++"):
                        print(f"{FG_GREEN}{line}{RESET}")
                    elif line.startswith("-") and not line.startswith("---"):
                        print(f"{FG_RED}{line}{RESET}")
                    elif line.startswith("@@"):
                        print(f"{FG_YELLOW}{line}{RESET}")
                    else:
                        print(line)
            else:
                print(output)

        if errors:
            print(f"{FG_YELLOW}{errors}{RESET}")

        if result.returncode != 0 and not output and not errors:
            print(f"{FG_YELLOW}(no output){RESET}")

    except subprocess.TimeoutExpired:
        print(f"{FG_RED}Git command timed out{RESET}")
    except FileNotFoundError:
        print(f"{FG_RED}Git not found. Install with: brew install git{RESET}")
    except Exception as e:
        print(f"{FG_RED}Git error: {e}{RESET}")


def cmd_replace(parts: List[str], state: AppState) -> None:
    """Find and replace text in a file. Usage: /replace file "old" "new" [--all]"""
    if len(parts) < 4:
        print(f"{FG_RED}Usage: /replace <file> \"old text\" \"new text\" [--all]{RESET}")
        print(f"{FG_CYAN}Examples:{RESET}")
        print(f'  {FG_GREEN}/replace main.py "old_func" "new_func"{RESET}        First occurrence')
        print(f'  {FG_GREEN}/replace main.py "old_func" "new_func" --all{RESET}  All occurrences')
        return

    # Parse arguments — extract quoted strings
    raw = " ".join(parts[1:])
    # Extract the file path (first non-quoted token)
    file_arg = parts[1]
    remaining = " ".join(parts[2:])

    # Extract quoted strings
    quoted = re.findall(r'"([^"]*)"', remaining)
    if len(quoted) < 2:
        print(f"{FG_RED}Please quote both old and new text with double quotes.{RESET}")
        print(f'{FG_CYAN}Example: /replace file.py "old text" "new text"{RESET}')
        return

    old_text = quoted[0]
    new_text = quoted[1]
    replace_all = "--all" in parts

    target = resolve_path(file_arg, state.cwd)
    if not is_safe_path(target):
        print(f"{FG_RED}Cannot modify outside sandbox{RESET}")
        return
    if not os.path.isfile(target):
        print(f"{FG_RED}No such file: {file_arg}{RESET}")
        return

    try:
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"{FG_RED}Error reading file: {e}{RESET}")
        return

    count = content.count(old_text)
    if count == 0:
        print(f"{FG_YELLOW}Text not found in {file_arg}{RESET}")
        return

    rel = os.path.relpath(target, ROOT_DIR)
    if replace_all:
        new_content = content.replace(old_text, new_text)
        print(f"{FG_CYAN}Found {count} occurrence(s) in {rel}{RESET}")
    else:
        new_content = content.replace(old_text, new_text, 1)
        print(f"{FG_CYAN}Found {count} occurrence(s), replacing first in {rel}{RESET}")

    # Show diff
    print_diff(content, new_content, rel)

    confirm = input(f"{FG_YELLOW}Apply replacement? [y/N] {RESET}").strip().lower()
    if confirm == 'y':
        backup = create_backup(target)
        if backup:
            print(f"{FG_BLUE}  💾 Backup created{RESET}")
        with open(target, "w", encoding="utf-8") as f:
            f.write(new_content)
        replaced = count if replace_all else 1
        print(f"{FG_GREEN}✅ Replaced {replaced} occurrence(s) in {rel}{RESET}")
        state.session.last_modified_files.append(target)
        state.session.stats["files_modified"] += 1
        state.session.opened_files[target] = new_content
        log_operation("REPLACE", f"{rel}: '{old_text}' -> '{new_text}'")
    else:
        print(f"{FG_CYAN}Replacement cancelled.{RESET}")


def cmd_find(parts: List[str], state: AppState) -> None:
    """Search for files by name pattern (glob-style)."""
    if len(parts) < 2:
        print(f"{FG_RED}Usage: /find <pattern>{RESET}")
        print(f"{FG_CYAN}Examples:{RESET}")
        print(f"  {FG_GREEN}/find *.py{RESET}              All Python files")
        print(f"  {FG_GREEN}/find test_*{RESET}            Files starting with test_")
        print(f"  {FG_GREEN}/find **/*.json{RESET}         JSON files in any subdirectory")
        print(f"  {FG_GREEN}/find main{RESET}              Files containing 'main' in name")
        return

    pattern = " ".join(parts[1:])

    # If no glob chars, wrap as *pattern*
    if not any(c in pattern for c in ['*', '?', '[']):
        pattern = f"**/*{pattern}*"
    elif not pattern.startswith("**/") and os.sep not in pattern:
        pattern = f"**/{pattern}"

    results = []
    for match in Path(state.cwd).glob(pattern):
        # Skip hidden files/dirs
        if any(part.startswith('.') for part in match.parts):
            continue
        # Skip common junk dirs
        skip_dirs = {'node_modules', '__pycache__', 'venv', 'env', '.git', 'dist', 'build'}
        if skip_dirs.intersection(match.parts):
            continue
        if match.is_file():
            results.append(match)

    if not results:
        print(f"{FG_YELLOW}No files matching '{pattern}'{RESET}")
        return

    results.sort(key=lambda p: str(p))
    print(f"\n{FG_GREEN}Found {len(results)} file(s):{RESET}\n")

    for path in results[:50]:
        rel = path.relative_to(state.cwd)
        try:
            size = path.stat().st_size
            if size < 1024:
                size_str = f"{size}B"
            else:
                size_str = f"{size / 1024:.1f}KB"
        except Exception:
            size_str = "?"
        print(f"  {FG_CYAN}{rel}{RESET}  {DIM}{size_str}{RESET}")

    if len(results) > 50:
        print(f"\n{FG_YELLOW}... and {len(results) - 50} more{RESET}")
    print()


def cmd_run(parts: List[str], state: AppState) -> None:
    """Execute a shell command in the project directory."""
    if len(parts) < 2:
        print(f"{FG_RED}Usage: /run <command>{RESET}")
        print(f"{FG_CYAN}Examples:{RESET}")
        print(f"  {FG_GREEN}/run python main.py{RESET}")
        print(f"  {FG_GREEN}/run npm test{RESET}")
        print(f"  {FG_GREEN}/run cargo build{RESET}")
        print(f"  {FG_GREEN}/run python -m pytest{RESET}")
        print(f"\n{FG_CYAN}Add {FG_GREEN}--ai{FG_CYAN} to send output to the assistant:{RESET}")
        print(f"  {FG_GREEN}/run python main.py --ai{RESET}")
        return

    # Check for --ai flag (send output to assistant)
    send_to_ai = "--ai" in parts
    cmd_parts = [p for p in parts[1:] if p != "--ai"]
    command = " ".join(cmd_parts)

    print(f"{FG_CYAN}$ {command}{RESET}")
    print(f"{DIM}{'─' * 70}{RESET}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=state.cwd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        stdout = result.stdout
        stderr = result.stderr

        # Limit output to avoid flooding
        max_output = 5000
        if stdout:
            if len(stdout) > max_output:
                print(stdout[:max_output])
                print(f"\n{FG_YELLOW}... output truncated ({len(stdout)} chars total){RESET}")
            else:
                print(stdout, end="")

        if stderr:
            if len(stderr) > max_output:
                print(f"{FG_RED}{stderr[:max_output]}{RESET}")
                print(f"\n{FG_YELLOW}... stderr truncated ({len(stderr)} chars total){RESET}")
            else:
                print(f"{FG_RED}{stderr}{RESET}", end="")

        print(f"{DIM}{'─' * 70}{RESET}")

        exit_code = result.returncode
        if exit_code == 0:
            print(f"{FG_GREEN}✓ Exit code: {exit_code}{RESET}")
        else:
            print(f"{FG_RED}✗ Exit code: {exit_code}{RESET}")

        # Optionally send to AI for analysis
        if send_to_ai:
            output_text = ""
            if stdout:
                output_text += stdout[:max_output]
            if stderr:
                output_text += f"\n[STDERR]:\n{stderr[:max_output]}"
            context_msg = f"I ran `{command}` (exit code {exit_code}). Here's the output:\n```\n{output_text}\n```\nPlease analyze this output."
            state.buffer = [context_msg]
            print(f"\n{FG_CYAN}Output queued for AI analysis. Press Enter to send.{RESET}")

    except subprocess.TimeoutExpired:
        print(f"{DIM}{'─' * 70}{RESET}")
        print(f"{FG_RED}✗ Command timed out (60s limit){RESET}")
    except Exception as e:
        print(f"{DIM}{'─' * 70}{RESET}")
        print(f"{FG_RED}✗ Error: {e}{RESET}")


def cmd_copy(parts: List[str], state: AppState) -> None:
    """Copy last code block from assistant's response to clipboard."""
    # Find last assistant message
    last_response = None
    for role, content in reversed(state.session.history):
        if role == "assistant":
            last_response = content
            break

    if not last_response:
        print(f"{FG_YELLOW}No assistant response to copy from.{RESET}")
        return

    # Extract code blocks
    blocks = extract_code_blocks(last_response)
    file_blocks = extract_file_blocks(last_response)
    all_blocks = file_blocks + blocks

    if not all_blocks:
        print(f"{FG_YELLOW}No code blocks found in last response.{RESET}")
        return

    if len(all_blocks) == 1:
        content = all_blocks[0]["content"]
        idx = 0
    else:
        # Let user choose which block
        print(f"\n{FG_CYAN}Found {len(all_blocks)} code block(s):{RESET}\n")
        for i, block in enumerate(all_blocks):
            label = block.get("path", block.get("lang", "code"))
            preview = block["content"].splitlines()[0][:60] if block["content"].strip() else "(empty)"
            print(f"  {FG_GREEN}[{i + 1}]{RESET} {label}: {DIM}{preview}{RESET}")

        choice = input(f"\n{FG_YELLOW}Copy which block? [1-{len(all_blocks)}] {RESET}").strip()
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(all_blocks):
                print(f"{FG_RED}Invalid choice.{RESET}")
                return
        except ValueError:
            print(f"{FG_RED}Invalid choice.{RESET}")
            return
        content = all_blocks[idx]["content"]

    try:
        process = subprocess.run(
            ["pbcopy"],
            input=content,
            text=True,
            capture_output=True,
            timeout=5,
        )
        if process.returncode == 0:
            lines = len(content.splitlines())
            print(f"{FG_GREEN}✓ Copied to clipboard ({lines} lines, {len(content)} chars){RESET}")
        else:
            print(f"{FG_RED}Failed to copy: {process.stderr}{RESET}")
    except FileNotFoundError:
        # Fallback for non-macOS
        print(f"{FG_YELLOW}pbcopy not found (macOS only). Content:{RESET}")
        print(content)
    except Exception as e:
        print(f"{FG_RED}Error: {e}{RESET}")


def cmd_project(parts: List[str], state: AppState) -> None:
    detected = detect_project_type(state.cwd)
    if detected:
        print(f"{FG_GREEN}🔧 Detected: {detected}{RESET}")
        print(f"\n{FG_CYAN}Project structure:{RESET}")
        print(get_project_structure(state.cwd))
    else:
        print(f"{FG_YELLOW}Could not detect project type{RESET}")


# Command dispatcher table
COMMAND_DISPATCH = {
    "/exit": cmd_exit,
    "/help": cmd_help,
    "/clear": cmd_clear,
    "/model": cmd_model,
    "/models": cmd_models,
    "/installed": cmd_installed,
    "/download": cmd_download,
    "/delete": cmd_delete,
    "/tokens": cmd_tokens,
    "/ctx": cmd_ctx,
    "/pwd": cmd_pwd,
    "/cd": cmd_cd,
    "/ls": cmd_ls,
    "/tree": lambda parts, state: handle_tree(parts, state.cwd),
    "/grep": lambda parts, state: handle_grep(parts, state.cwd),
    "/diff": lambda parts, state: handle_diff(parts, state.cwd),
    "/open": cmd_open,
    "/context": lambda parts, state: handle_context(parts, state.session, state.cwd),
    "/template": cmd_template,
    "/undo": cmd_undo,
    "/backups": lambda parts, state: handle_backups(parts, state.cwd),
    "/restore": lambda parts, state: handle_restore(parts, state.cwd),
    "/save": cmd_save,
    "/last": cmd_last,
    "/edit": cmd_edit,
    "/stats": lambda parts, state: handle_stats(state.session),
    "/project": cmd_project,
    "/git": cmd_git,
    "/run": cmd_run,
    "/find": cmd_find,
    "/replace": cmd_replace,
    "/copy": cmd_copy,
}


# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------

def main():
    global ROOT_DIR

    # Set ROOT_DIR dynamically to where the script is launched
    ROOT_DIR = os.getcwd()

    ensure_directories()

    config = load_config()

    # Per-project config overrides global config
    project_cfg = load_project_config(ROOT_DIR)
    if project_cfg:
        config.update(project_cfg)
        print(f"{FG_CYAN}📋 Loaded project config from .mlx-code.json{RESET}")

    model_name = config.get("model", DEFAULT_MODEL)
    max_tokens = config.get("max_tokens", DEFAULT_MAX_TOKENS)
    ctx_chars = config.get("ctx_chars", DEFAULT_CTX_CHARS)

    print_banner()
    print_help()

    session = ChatSession(model_name, max_tokens, ctx_chars)
    if "auto_context" in config:
        session.auto_context_enabled = bool(config["auto_context"])
    state = AppState(model_name, max_tokens, ctx_chars, ROOT_DIR, session)
    session.load_project_context(state.cwd)

    # Offer to restore autosaved conversation
    autosave = load_autosave()
    if autosave and autosave.get("history"):
        n_msgs = len(autosave["history"])
        ts = autosave.get("timestamp", "unknown")
        print(f"\n{FG_YELLOW}💾 Found autosaved conversation ({n_msgs} messages, from {ts}){RESET}")
        restore = input(f"{FG_YELLOW}Restore previous conversation? [y/N] {RESET}").strip().lower()
        if restore == 'y':
            for msg in autosave["history"]:
                session.history.append((msg["role"], msg["content"]))
            print(f"{FG_GREEN}✓ Restored {n_msgs} messages{RESET}")
        else:
            clear_autosave()

    print_status(state.model_name, state.cwd, state.project_type, state.session)

    # Setup advanced input with prompt_toolkit (if available)
    if HAS_PROMPT_TOOLKIT:
        history_file = os.path.join(LOG_DIR, "command_history.txt")
        commands = sorted(set(
            list(COMMAND_DISPATCH.keys()) +
            [f"/{alias}" for alias in MODEL_ALIASES.keys()]
        ))
        completer = WordCompleter(commands, ignore_case=True, sentence=True)
        prompt_style = Style.from_dict({'prompt': 'ansigreen bold'})
        prompt_session = PromptSession(
            history=FileHistory(history_file),
            auto_suggest=AutoSuggestFromHistory(),
            completer=completer,
            complete_while_typing=False,
            style=prompt_style,
            enable_history_search=True,
            multiline=False,
        )
    else:
        prompt_session = None

    while True:
        try:
            if HAS_PROMPT_TOOLKIT and prompt_session:
                line = prompt_session.prompt(HTML(f'<ansigreen>></ansigreen> '))
            else:
                line = input(f"{FG_GREEN}>{RESET} ")
        except KeyboardInterrupt:
            if state.buffer:
                print(f"\n{FG_YELLOW}^C (buffer cleared){RESET}")
                state.buffer = []
            else:
                print(f"\n{FG_YELLOW}^C (use /exit to quit){RESET}")
            continue
        except EOFError:
            clear_autosave()
            print("\n\n👋 Goodbye!")
            break

        stripped = line.strip()

        # Empty line -> send buffered message
        if stripped == "":
            if state.buffer:
                user_message = "\n".join(state.buffer)
                state.buffer = []

                # Generate response (streamed to terminal in real-time)
                print(f"\n{FG_CYAN}🤖 Assistant:{RESET}\n")
                response = state.session.ask(user_message, state.cwd)

                # Handle file changes
                blocks = extract_file_blocks(response)
                if blocks:
                    apply_file_changes(blocks, state.cwd, state.session)
                else:
                    maybe_save_code_block(response, state.cwd, state.session)

                print()
            continue

        # Commands
        if stripped.startswith("/"):
            parts = stripped.split()
            cmd = parts[0].lower()

            # Check dispatcher first
            handler = COMMAND_DISPATCH.get(cmd)

            # Check model aliases (e.g., /q7b, /ds, /llama3-8b)
            if handler is None and cmd[1:] in MODEL_ALIASES:
                state.model_name = MODEL_ALIASES[cmd[1:]]
                state.reload_session()
                print_status(state.model_name, state.cwd, state.project_type, state.session)
                continue

            if handler is None:
                print(f"{FG_RED}Unknown command: {cmd}{RESET}")
                print(f"{FG_YELLOW}Type /help for commands{RESET}")
                continue

            result = handler(parts, state)
            if result == "break":
                break
            continue

        # Normal text — add to multi-line buffer
        state.buffer.append(line)
        if len(state.buffer) == 1:
            print(f"{DIM}(press Enter on empty line to send, or keep typing for multi-line){RESET}")


if __name__ == "__main__":
    main()