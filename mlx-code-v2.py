#!/usr/bin/env python3
# mlx-code-pro: intelligent local coding assistant with context awareness
# Requires: pip install mlx-lm pillow

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
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Set
from pathlib import Path

try:
    from mlx_lm import load, generate
except ImportError:
    print("ERROR: mlx-lm not found. Install with: pip install mlx-lm")
    sys.exit(1)

try:
    from PIL import Image

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

# ROOT_DIR will be set dynamically to current working directory at startup
ROOT_DIR = None  # Set in main()
LOG_DIR = os.path.expanduser("~/.mlx-code")
BACKUP_DIR = os.path.join(LOG_DIR, "backups")
HISTORY_FILE = os.path.join(LOG_DIR, "history.log")
CONFIG_FILE = os.path.join(LOG_DIR, "config.json")

DEFAULT_MODEL = "mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit"  # 1.5B - lightweight demo model (upgrade recommended)

MODEL_ALIASES = {
    "q7b": "mlx-community/qwen2.5-coder-7b-instruct-4bit",
    "q3b": "mlx-community/qwen2.5-coder-3b-instruct-4bit",
    "q1.5b": "mlx-community/Qwen2.5-Coder-1.5B-Instruct-4bit",
    "q14b": "mlx-community/Qwen2.5-Coder-14B-Instruct-4bit",
    "mistral": "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
    "m7b": "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
    "deepseek": "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit",
    "ds": "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit",
    "deepseek-1.3b": "mlx-community/DeepSeek-Coder-1.3B-Instruct-4bit",
}

DEFAULT_MAX_TOKENS = 1024
DEFAULT_CTX_CHARS = 24000

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
        except:
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
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)  # First 5KB
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
    if "7b" in model_name.lower():
        return "~4.3GB"
    elif "3b" in model_name.lower():
        return "~1.9GB"
    elif "1.5b" in model_name.lower():
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
        return textwrap.dedent(
            f"""
            You are MLX-CODE-PRO, an advanced AI coding assistant with full project context awareness.

            CAPABILITIES:
            - You can read and analyze files automatically when users reference them
            - You understand project structure and dependencies
            - You provide context-aware suggestions based on the entire codebase
            - You can view and describe images in the project

            CORE RULES:
            - All operations are restricted to "{ROOT_DIR}"
            - Be proactive: if a user asks about a file, assume you have its content in context
            - Provide detailed, production-ready code with proper error handling
            - Always explain your reasoning and consider edge cases

            CONTEXT AWARENESS:
            - Files mentioned in conversation are automatically loaded into your context
            - You have access to project structure and key configuration files
            - Use this context to provide more accurate and relevant suggestions

            FILE EDITING PROTOCOL:
            CRITICAL: When user asks to create, modify, or edit files, you MUST use the file: format.

            For normal questions/discussions: use regular markdown.
            For file modifications: use the file: format below.

            CORRECT format for file modifications (note the "file:" prefix):

            ```file:path/to/file.py
            def hello():
                print("Hello World")
            ```

            WRONG - do NOT use language names for file modifications:
            ```python
            def hello():
                print("Hello World")
            ```

            Rules:
            - Use relative paths from current directory
            - Provide COMPLETE file content, not diffs
            - Multiple file blocks allowed
            - The syntax is ```file:filename NOT ```language
            - DO NOT use file blocks for answering questions

            CODE QUALITY STANDARDS:
            - Follow language-specific best practices and style guides
            - Include appropriate error handling and validation
            - Add meaningful comments for complex logic
            - Consider performance, security, and maintainability
            - Write testable code with clear separation of concerns

            SECURITY:
            - Never suggest code with obvious vulnerabilities
            - Warn about potential security issues in existing code
            - Be cautious with file operations, credentials, and user input
            - Recommend secure alternatives when applicable

            COMMUNICATION:
            - Be concise but thorough
            - Use markdown for formatting
            - Provide working examples when helpful
            - Ask for clarification when requirements are ambiguous
            - NEVER make up or hallucinate file names or content
            - If asked about files you don't have in context, say so clearly
            - For directory listings, tell users to use the /ls command
            """
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
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(10000)  # First 10KB
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
        except:
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

        # Opened files
        if self.opened_files:
            parts.append(f"\nFiles in context ({len(self.opened_files)}):")
            for filepath, content in list(self.opened_files.items())[:5]:  # Limit to 5
                rel_path = os.path.relpath(filepath, ROOT_DIR)
                parts.append(f"\n--- {rel_path} ---")
                if content.startswith("[Image:"):
                    parts.append(content)
                else:
                    preview = content[:800] + ("..." if len(content) > 800 else "")
                    parts.append(preview)

        return "\n".join(parts)

    def _build_prompt(self, user_message: str, cwd: str) -> str:
        """Build complete prompt with system + context + history using Qwen chat template."""
        context = self._build_context_section(cwd)
        user_with_ctx = f"{context}\n\n--- User Message ---\n{user_message}"

        # Use Qwen chat template format for better responses
        parts: List[str] = []

        # System message
        parts.append(f"<|im_start|>system\n{self.system_prompt}<|im_end|>")

        # Add relevant history (smart prioritization)
        for role, txt in self._get_prioritized_history():
            if role == "user":
                parts.append(f"<|im_start|>user\n{txt}<|im_end|>")
            else:
                parts.append(f"<|im_start|>assistant\n{txt}<|im_end|>")

        # Current user message
        parts.append(f"<|im_start|>user\n{user_with_ctx}<|im_end|>")
        parts.append("<|im_start|>assistant")

        return "\n".join(parts)

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
        """Send query with automatic context loading."""
        self.last_query = user_message
        self.stats["queries"] += 1

        # Auto-load referenced files
        self.auto_load_referenced_files(user_message, cwd)

        # Build and send prompt
        prompt = self._build_prompt(user_message, cwd)

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

        # Clean up Qwen chat template tokens from response
        response = response.split("<|im_end|>")[0].strip()
        response = response.split("<|im_start|>")[0].strip()

        # Update stats and history
        self.stats["tokens_generated"] += len(response.split())
        self.history.append(("user", user_message))
        self.history.append(("assistant", response))
        self._trim_history()

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


def print_colored_response(text: str):
    """Print response with markdown formatting."""
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
            if line.startswith("#"):
                print(BOLD + FG_CYAN + line + RESET)
            elif line.startswith("**") or line.startswith("*"):
                print(FG_CYAN + line + RESET)
            else:
                print(FG_CYAN + line + RESET)


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

        if session.project_context:
            print(f"\n  {FG_CYAN}Project context files:{RESET}")
            for name in session.project_context.keys():
                print(f"    • {name}")

        if session.opened_files:
            print(f"\n  {FG_CYAN}Opened files:{RESET}")
            for path in session.opened_files.keys():
                rel = os.path.relpath(path, ROOT_DIR)
                print(f"    • {rel}")

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
    print(f"  Tokens generated:       ~{session.stats['tokens_generated']}")
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
    print(f"  {FG_GREEN}/q7b, /q3b, /q1.5b{RESET}     Quick model switch")
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
    print(f"  {FG_GREEN}/grep <pattern>{RESET}        Search in files")
    print(f"  {FG_GREEN}/diff <f1> <f2>{RESET}        Compare files")
    print()
    print("TEMPLATES:")
    print(f"  {FG_GREEN}/template{RESET}              List templates")
    print(f"  {FG_GREEN}/template <name> <file>{RESET} Apply template")
    print(f"    Available: test, doc, refactor, review, optimize, explain, debug, secure")
    print()
    print("BACKUP & HISTORY:")
    print(f"  {FG_GREEN}/backups [file]{RESET}        List backups")
    print(f"  {FG_GREEN}/restore <bk> <file>{RESET}   Restore from backup")
    print(f"  {FG_GREEN}/save [file]{RESET}           Export chat")
    print()
    print("UTILITIES:")
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
# MAIN LOOP
# ---------------------------------------------------------------------------

def main():
    global ROOT_DIR

    # Set ROOT_DIR dynamically to where the script is launched
    ROOT_DIR = os.getcwd()

    ensure_directories()

    # Initialize
    cwd = ROOT_DIR

    config = load_config()
    model_name = config.get("model", DEFAULT_MODEL)
    max_tokens = config.get("max_tokens", DEFAULT_MAX_TOKENS)
    ctx_chars = config.get("ctx_chars", DEFAULT_CTX_CHARS)

    print_banner()
    print_help()

    session = ChatSession(model_name, max_tokens, ctx_chars)

    # Load project context automatically
    project_type = detect_project_type(cwd)
    session.load_project_context(cwd)

    print_status(model_name, cwd, project_type, session)

    buffer: List[str] = []

    while True:
        try:
            line = input(f"{FG_GREEN}>{RESET} ")
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Goodbye!")
            break

        stripped = line.strip()

        # Empty line -> send
        if stripped == "":
            if buffer:
                user_message = "\n".join(buffer)
                buffer = []

                # Generate response
                print(f"\n{FG_CYAN}🤖 Assistant:{RESET}\n")
                response = session.ask(user_message, cwd)
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
                print("Configuration saved. 👋 Goodbye!")
                break

            # Help
            if cmd == "/help":
                print_help()
                print_status(model_name, cwd, project_type, session)
                continue

            # Clear
            if cmd == "/clear":
                session.history.clear()
                print(f"{FG_GREEN}✓ Chat history cleared{RESET}")
                continue

            # Model
            if cmd == "/model":
                if len(parts) < 2:
                    print(f"{FG_RED}Usage: /model <huggingface-model-id>{RESET}")
                    continue
                new_model = parts[1].strip()
                model_name = new_model
                session = ChatSession(model_name, max_tokens, ctx_chars)
                session.load_project_context(cwd)
                print_status(model_name, cwd, project_type, session)
                continue

            # Aliases
            if cmd in ("/q7b", "/q3b", "/q1.5b", "/mistral", "/m7b"):
                key = cmd[1:]
                new_model = MODEL_ALIASES.get(key)
                if not new_model:
                    print(f"{FG_RED}Alias {cmd} not configured{RESET}")
                    continue
                model_name = new_model
                session = ChatSession(model_name, max_tokens, ctx_chars)
                session.load_project_context(cwd)
                print_status(model_name, cwd, project_type, session)
                continue

            # Tokens
            if cmd == "/tokens":
                if len(parts) != 2 or not parts[1].isdigit():
                    print(f"{FG_RED}Usage: /tokens <number>{RESET}")
                    continue
                max_tokens = int(parts[1])
                session.max_tokens = max_tokens
                print(f"{FG_GREEN}✓ Max tokens: {max_tokens}{RESET}")
                continue

            # Context size
            if cmd == "/ctx":
                if len(parts) != 2 or not parts[1].isdigit():
                    print(f"{FG_RED}Usage: /ctx <number>{RESET}")
                    continue
                ctx_chars = int(parts[1])
                session.ctx_chars = ctx_chars
                print(f"{FG_GREEN}✓ Context size: {ctx_chars} chars{RESET}")
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
                session.clear_context()
                session.load_project_context(cwd)
                print_status(model_name, cwd, project_type, session)
                continue

            # LS
            if cmd == "/ls":
                target = resolve_path(" ".join(parts[1:]) if len(parts) > 1 else "", cwd)
                if not is_safe_path(target):
                    print(f"{FG_RED}Cannot list outside sandbox{RESET}")
                    continue
                if not os.path.isdir(target):
                    print(f"{FG_RED}No such directory{RESET}")
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
                    print(f"{FG_RED}No such file{RESET}")
                    continue

                try:
                    if is_image_file(target):
                        desc = describe_image(target)
                        session.opened_files[target] = desc
                        print(f"{FG_GREEN}✓ Loaded image: {desc}{RESET}")
                    else:
                        with open(target, "r", encoding="utf-8") as f:
                            content = f.read()
                        rel = os.path.relpath(target, ROOT_DIR)
                        session.opened_files[target] = content
                        print(f"{FG_GREEN}✓ Loaded {rel} into context ({len(content)} chars){RESET}")
                except Exception as e:
                    print(f"{FG_RED}Error: {e}{RESET}")
                continue

            # CONTEXT
            if cmd == "/context":
                handle_context(parts, session, cwd)
                continue

            # TEMPLATE
            if cmd == "/template":
                template_query = handle_template(parts, cwd, session)
                if template_query:
                    buffer = [template_query]
                    print(f"{FG_CYAN}Template ready. Press Enter to send.{RESET}")
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
                out_path_raw = " ".join(parts[1:]) if len(
                    parts) > 1 else f"mlx-session-{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                out_path = resolve_path(out_path_raw, cwd)
                if not is_safe_path(out_path):
                    print(f"{FG_RED}Cannot save outside sandbox{RESET}")
                    continue

                lines = [
                    f"# MLX-CODE-PRO Session\n",
                    f"**Model:** {model_name}\n",
                    f"**Date:** {datetime.now().isoformat()}\n",
                    f"**Project:** {project_type or 'Unknown'}\n",
                    "\n---\n\n",
                ]
                for role, txt in session.history:
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
                continue

            # LAST
            if cmd == "/last":
                if session.last_query:
                    buffer = [session.last_query]
                    print(f"{FG_CYAN}Repeating last query. Press Enter.{RESET}")
                else:
                    print(f"{FG_YELLOW}No previous query{RESET}")
                continue

            # EDIT
            if cmd == "/edit":
                if not session.last_modified_files:
                    print(f"{FG_YELLOW}No files modified yet{RESET}")
                    continue
                editor = os.environ.get("EDITOR", "nano")
                last_file = session.last_modified_files[-1]
                print(f"{FG_CYAN}Opening in {editor}...{RESET}")
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
                    print(f"{FG_GREEN}🔧 Detected: {detected}{RESET}")
                    print(f"\n{FG_CYAN}Project structure:{RESET}")
                    print(get_project_structure(cwd))
                else:
                    print(f"{FG_YELLOW}Could not detect project type{RESET}")
                continue

            # Unknown
            print(f"{FG_RED}Unknown command: {cmd}{RESET}")
            print(f"{FG_YELLOW}Type /help for commands{RESET}")
            continue

        # Normal text
        buffer.append(line)


if __name__ == "__main__":
    main()