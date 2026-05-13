"""
AI Content Organizer Module
Provides AI-powered file organization using Ollama (local/cloud models).
"""

# ═══════════════════════════════════════════════════════════════
# Section 1: Imports — only stdlib here so tests work without PySide6
# ═══════════════════════════════════════════════════════════════

import json
import logging
import re
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger("file_organizer.ai")


# ═══════════════════════════════════════════════════════════════
# Section 2: Constants
# ═══════════════════════════════════════════════════════════════

TEXT_EXTENSIONS = {
    ".txt", ".md", ".rst", ".log", ".csv", ".tsv",
    ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".htm",
    ".css", ".scss", ".sass", ".less",
    ".java", ".kt", ".swift", ".go", ".rs", ".cpp", ".c",
    ".h", ".hpp", ".cs", ".php", ".rb", ".sh", ".bash",
    ".ps1", ".bat", ".cmd",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".xml", ".env", ".properties",
    ".tex", ".bib", ".sql", ".graphql", ".rtf",
}

PROJECT_INDICATORS = {
    "package.json", "package-lock.json", "yarn.lock",
    "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg", "pipfile",
    "pom.xml", "build.gradle", "cargo.toml",
    "cmakelists.txt", "makefile",
    "pubspec.yaml",
    "composer.json",
    ".git", ".gitignore",
    "index.html", "index.htm",
    "readme.md", "readme.txt",
}

CLOUD_MODELS = ["gemma4:31b-cloud", "gemma3:27b-cloud"]
CONTENT_PREVIEW_CHARS = 1500


# ═══════════════════════════════════════════════════════════════
# Section 3: OllamaClient
# ═══════════════════════════════════════════════════════════════

class OllamaClient:
    """Handles communication with Ollama API."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")

    def fetch_models(self) -> List[str]:
        """GET /api/tags → returns list of model names. Returns [] on failure."""
        try:
            url = f"{self.base_url}/api/tags"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                return [m["name"] for m in data.get("models", [])]
        except Exception as e:
            logger.warning(f"Could not fetch Ollama models: {e}")
            return []

    def get_all_models(self) -> List[str]:
        """Returns CLOUD_MODELS + local models (no duplicates)."""
        local_models = self.fetch_models()
        combined = list(CLOUD_MODELS)
        for m in local_models:
            if m not in combined:
                combined.append(m)
        return combined

    def generate(self, prompt: str, model: str) -> str:
        """POST /api/generate → returns response text. timeout=60."""
        try:
            url = f"{self.base_url}/api/generate"
            payload = json.dumps({
                "model": model,
                "prompt": prompt,
                "stream": False
            }).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("response", "").strip()
        except urllib.error.URLError as e:
            raise ConnectionError(f"Cannot connect to Ollama: {e}")
        except Exception as e:
            raise RuntimeError(f"Ollama generate failed: {e}")

    def is_connected(self) -> bool:
        """Tries to connect and returns True/False."""
        try:
            url = f"{self.base_url}/api/tags"
            with urllib.request.urlopen(url, timeout=5):
                return True
        except Exception:
            return False


# ═══════════════════════════════════════════════════════════════
# Section 4: ContentAnalyzer
# ═══════════════════════════════════════════════════════════════

class ContentAnalyzer:
    """Reads files and analyzes projects for categorization."""

    def __init__(self, client: Optional[OllamaClient], model: Optional[str]):
        self.client = client
        self.model = model

    def is_project_folder(self, folder: Path) -> bool:
        """Checks if folder contains any PROJECT_INDICATORS at top-level."""
        try:
            names = {item.name.lower() for item in folder.iterdir()}
            return bool(names & PROJECT_INDICATORS)
        except (OSError, PermissionError):
            return False

    def get_folder_structure(self, folder: Path) -> str:
        """Builds a text representation of folder structure (top-level only, max 30 items)."""
        try:
            items = list(folder.iterdir())[:30]
            return "\n".join(item.name for item in items)
        except (OSError, PermissionError):
            return folder.name

    def read_file_preview(self, file: Path) -> Optional[str]:
        """Reads first CONTENT_PREVIEW_CHARS from a text file."""
        if file.suffix.lower() == ".pdf":
            return self._read_pdf_preview(file)
        for encoding in ("utf-8", "latin-1"):
            try:
                with open(file, "r", encoding=encoding, errors="replace") as f:
                    return f.read(CONTENT_PREVIEW_CHARS)
            except Exception:
                continue
        return None

    def _read_pdf_preview(self, file: Path) -> Optional[str]:
        """Attempts to extract text from PDF using pypdf or pdfplumber."""
        try:
            import pypdf
            reader = pypdf.PdfReader(str(file))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
                if len(text) >= CONTENT_PREVIEW_CHARS:
                    break
            return text[:CONTENT_PREVIEW_CHARS] if text.strip() else None
        except ImportError:
            pass
        except Exception:
            pass

        try:
            import pdfplumber
            with pdfplumber.open(str(file)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                    if len(text) >= CONTENT_PREVIEW_CHARS:
                        break
                return text[:CONTENT_PREVIEW_CHARS] if text.strip() else None
        except ImportError:
            pass
        except Exception:
            pass

        return None

    @staticmethod
    def _sanitize_folder_name(name: str) -> str:
        """Removes invalid characters from folder name."""
        sanitized = re.sub(r'[/\\:*?"<>|]', "", name).strip()
        sanitized = re.sub(r'\s+', ' ', sanitized)
        return sanitized if sanitized else "Uncategorized"

    def analyze_file(self, file: Path) -> str:
        """Analyzes a single file and returns suggested folder name."""
        filename = file.name
        content_preview = None
        if file.suffix.lower() in TEXT_EXTENSIONS or file.suffix.lower() == ".pdf":
            content_preview = self.read_file_preview(file)

        if content_preview:
            prompt = (
                "You are a file organizer. Based on the filename and content preview below,\n"
                "suggest a single folder name to categorize this file.\n"
                "Rules:\n"
                "- Return ONLY the folder name, nothing else.\n"
                "- Use Title Case (e.g. \"Python Scripts\", \"Finance Reports\", \"Personal Notes\").\n"
                "- Be specific but not too narrow (2-4 words max).\n"
                "- No slashes, no special characters.\n\n"
                f"Filename: {filename}\n"
                f"Content preview:\n{content_preview}\n\n"
                "Folder name:"
            )
        else:
            prompt = (
                "You are a file organizer. Based ONLY on the filename below,\n"
                "suggest a single folder name to categorize this file.\n"
                "Rules:\n"
                "- Return ONLY the folder name, nothing else.\n"
                "- Use Title Case (e.g. \"Videos\", \"Photos\", \"Music\").\n"
                "- No slashes, no special characters.\n\n"
                f"Filename: {filename}\n\n"
                "Folder name:"
            )

        try:
            response = self.client.generate(prompt, self.model)
            folder_name = response.split("\n")[0].strip()
            folder_name = self._sanitize_folder_name(folder_name)
            return folder_name if folder_name else "Uncategorized"
        except Exception as e:
            logger.warning(f"AI analysis failed for {filename}: {e}")
            return "Uncategorized"

    def analyze_project(self, folder: Path) -> str:
        """Analyzes a project folder and returns suggested category name."""
        folder_name = folder.name
        file_structure = self.get_folder_structure(folder)

        prompt = (
            "You are a developer tool. Based on the project folder name and file structure below,\n"
            "suggest a single category folder name for this project.\n"
            "Rules:\n"
            "- Return ONLY the folder name, nothing else.\n"
            "- Use Title Case (e.g. \"Python Projects\", \"React Projects\", \"Flutter Apps\").\n"
            "- Group by technology/type, not by specific project name.\n"
            "- No slashes, no special characters.\n\n"
            f"Project folder name: {folder_name}\n"
            f"File structure (top-level):\n{file_structure}\n\n"
            "Category folder name:"
        )

        try:
            response = self.client.generate(prompt, self.model)
            category = response.split("\n")[0].strip()
            category = self._sanitize_folder_name(category)
            return category if category else "Uncategorized Projects"
        except Exception as e:
            logger.warning(f"AI project analysis failed for {folder_name}: {e}")
            return "Uncategorized Projects"


# ═══════════════════════════════════════════════════════════════
# Sections 5-7: Qt classes — imported lazily to keep tests working
# ═══════════════════════════════════════════════════════════════

def _get_qt_classes():
    """Lazy-load Qt classes only when needed (not during unit tests)."""
    from PySide6.QtCore import QThread, Signal
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
    )
    from PySide6.QtGui import QColor
    return QThread, Signal, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
           QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QColor


class ModelRefreshWorker:
    """Fetches available models from Ollama in background (QThread)."""
    def __new__(cls, ollama_url: str):
        QThread, Signal, *_ = _get_qt_classes()

        class _ModelRefreshWorker(QThread):
            models_ready = Signal(list)
            error = Signal(str)

            def __init__(self, url):
                super().__init__()
                self.ollama_url = url

            def run(self):
                try:
                    client = OllamaClient(self.ollama_url)
                    models = client.get_all_models()
                    self.models_ready.emit(models)
                except Exception as e:
                    self.error.emit(str(e))

        return _ModelRefreshWorker(ollama_url)


class AIContentWorker:
    """Analyzes files and projects using AI in background (QThread)."""
    def __new__(cls, source: Path, dest: Path, model: str,
                ollama_url: str, cancel_event, recursive: bool = False):
        QThread, Signal, *_ = _get_qt_classes()

        class _AIContentWorker(QThread):
            progress_updated = Signal(int, int)
            item_analyzed = Signal(str, str, str)
            analysis_complete = Signal(list)
            log_message = Signal(str)
            error_occurred = Signal(str)

            def __init__(self, src, dst, mdl, url, evt, rec):
                super().__init__()
                self.source = src
                self.dest = dst
                self.model = mdl
                self.ollama_url = url
                self._cancel_event = evt
                self.recursive = rec

            def cancel(self):
                self._cancel_event.set()

            def run(self):
                try:
                    client = OllamaClient(self.ollama_url)
                    analyzer = ContentAnalyzer(client, self.model)
                    plan = []
                    items_to_analyze = []

                    try:
                        for item in self.source.iterdir():
                            if item == self.dest:
                                continue
                            if item.is_dir():
                                items_to_analyze.append(("folder", item))
                    except (OSError, PermissionError) as e:
                        self.log_message.emit(f"⚠️ Could not list source folder: {e}")

                    try:
                        for item in self.source.iterdir():
                            if item.is_file():
                                items_to_analyze.append(("file", item))
                    except (OSError, PermissionError) as e:
                        self.log_message.emit(f"⚠️ Could not list source files: {e}")

                    total = len(items_to_analyze)
                    self.progress_updated.emit(0, total)

                    for idx, (item_kind, item_path) in enumerate(items_to_analyze, 1):
                        if self._cancel_event.is_set():
                            self.log_message.emit("🛑 AI analysis cancelled.")
                            break

                        if item_kind == "folder":
                            if analyzer.is_project_folder(item_path):
                                self.log_message.emit(f"🔍 Analyzing project: {item_path.name}")
                                category = analyzer.analyze_project(item_path)
                                plan.append({"name": item_path.name, "path": item_path,
                                             "type": "project", "dest": category})
                                self.item_analyzed.emit(item_path.name, "project", category)
                                self.log_message.emit(f"  → {category}/{item_path.name}")
                            else:
                                sub_files = list(item_path.rglob("*") if self.recursive
                                                 else item_path.glob("*"))
                                for sub_file in sub_files:
                                    if self._cancel_event.is_set():
                                        break
                                    if sub_file.is_file():
                                        self.log_message.emit(f"🔍 Analyzing: {sub_file.name}")
                                        folder_name = analyzer.analyze_file(sub_file)
                                        plan.append({"name": sub_file.name, "path": sub_file,
                                                     "type": "file", "dest": folder_name})
                                        self.item_analyzed.emit(sub_file.name, "file", folder_name)
                                        self.log_message.emit(f"  → {folder_name}/{sub_file.name}")
                        else:
                            self.log_message.emit(f"🔍 Analyzing: {item_path.name}")
                            folder_name = analyzer.analyze_file(item_path)
                            plan.append({"name": item_path.name, "path": item_path,
                                         "type": "file", "dest": folder_name})
                            self.item_analyzed.emit(item_path.name, "file", folder_name)
                            self.log_message.emit(f"  → {folder_name}/{item_path.name}")

                        self.progress_updated.emit(idx, total)

                    self.analysis_complete.emit(plan)

                except Exception as e:
                    logger.error(f"AIContentWorker error: {e}", exc_info=True)
                    self.error_occurred.emit(str(e))

        return _AIContentWorker(source, dest, model, ollama_url, cancel_event, recursive)


class AIPreviewDialog:
    """Shows AI organization plan for user review (QDialog)."""
    def __new__(cls, plan: list, dest_root: Path, parent=None):
        QThread, Signal, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
            QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QColor = _get_qt_classes()

        try:
            import qtawesome as qta
            QTA_AVAILABLE = True
        except ImportError:
            QTA_AVAILABLE = False

        class _AIPreviewDialog(QDialog):
            def __init__(self, p, dest, par):
                super().__init__(par)
                self._plan = p
                self.dest_root = dest
                self.setWindowTitle("AI Organization Preview")
                self.setMinimumSize(750, 500)
                self._setup_ui()

            def _setup_ui(self):
                layout = QVBoxLayout(self)

                files_count = sum(1 for item in self._plan if item["type"] == "file")
                projects_count = sum(1 for item in self._plan if item["type"] == "project")
                summary_label = QLabel(
                    f"Found {files_count} files and {projects_count} projects to organize."
                )
                summary_label.setStyleSheet("font-weight: bold; padding: 8px; font-size: 13px;")
                layout.addWidget(summary_label)

                hint_label = QLabel(
                    "💡 Double-click the Destination Folder column to edit before proceeding."
                )
                hint_label.setStyleSheet("color: #666; padding: 4px;")
                layout.addWidget(hint_label)

                self.table = QTableWidget(len(self._plan), 3)
                self.table.setHorizontalHeaderLabels(["Item", "Type", "Destination Folder"])
                self.table.horizontalHeader().setSectionResizeMode(
                    0, QHeaderView.ResizeMode.Stretch)
                self.table.horizontalHeader().setSectionResizeMode(
                    1, QHeaderView.ResizeMode.ResizeToContents)
                self.table.horizontalHeader().setSectionResizeMode(
                    2, QHeaderView.ResizeMode.Stretch)
                self.table.setAlternatingRowColors(True)
                self.table.setSelectionBehavior(
                    QAbstractItemView.SelectionBehavior.SelectRows)

                from PySide6.QtCore import Qt as _Qt
                _no_edit = _Qt.ItemFlag.ItemIsEditable

                for row, item in enumerate(self._plan):
                    name_item = QTableWidgetItem(item["name"])
                    name_item.setFlags(name_item.flags() & ~_no_edit)
                    self.table.setItem(row, 0, name_item)

                    type_item = QTableWidgetItem(item["type"].capitalize())
                    type_item.setFlags(type_item.flags() & ~_no_edit)
                    if item["type"] == "project":
                        type_item.setBackground(QColor("#BBDEFB"))
                    self.table.setItem(row, 1, type_item)

                    dest_item = QTableWidgetItem(item["dest"])
                    if item["type"] == "project":
                        dest_item.setBackground(QColor("#E3F2FD"))
                    self.table.setItem(row, 2, dest_item)

                layout.addWidget(self.table)

                btn_layout = QHBoxLayout()
                cancel_btn = QPushButton("Cancel")
                if QTA_AVAILABLE:
                    cancel_btn.setIcon(qta.icon('fa5s.times'))
                cancel_btn.clicked.connect(self.reject)
                btn_layout.addWidget(cancel_btn)
                btn_layout.addStretch()

                proceed_btn = QPushButton("Proceed")
                if QTA_AVAILABLE:
                    proceed_btn.setIcon(qta.icon('fa5s.check'))
                proceed_btn.setDefault(True)
                proceed_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        padding: 8px 20px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #43A047; }
                """)
                proceed_btn.clicked.connect(self.accept)
                btn_layout.addWidget(proceed_btn)
                layout.addLayout(btn_layout)

            def get_final_plan(self) -> list:
                result = []
                for row in range(self.table.rowCount()):
                    result.append({
                        "name": self.table.item(row, 0).text(),
                        "path": self._plan[row]["path"],
                        "type": self.table.item(row, 1).text().lower(),
                        "dest": self.table.item(row, 2).text(),
                    })
                return result

        return _AIPreviewDialog(plan, dest_root, parent)
