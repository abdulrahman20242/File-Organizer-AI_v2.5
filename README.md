# 📂 File Organizer Pro

A powerful and user-friendly desktop application built with Python and PySide6 to intelligently sort your files into clean, organized folders.

Tired of cluttered "Downloads" or "Desktop" folders? File Organizer Pro automates the cleaning process with a rich set of features, a multi-language interface, and robust safety mechanisms like Undo and Dry-run mode.

![Sortify Screenshot](https://raw.githubusercontent.com/abdulrahman20242/File-Organizer_v2.4/main/Capture.PNG)

---

## ✨ What's New in v2.5

*   **🤖 AI Content Organizer:** Brand new "By Content (AI)" mode powered by Ollama. Analyzes file contents and project structures to intelligently suggest destination folders — not just by extension, but by actual meaning.
*   **🗂️ Smart Project Detection:** Automatically detects programming projects (Python, React, Flutter, Rust, Java...) and moves them as a single unit to the right category folder.
*   **☁️ Local & Cloud Models:** Supports local Ollama models alongside cloud models (`gemma4:31b-cloud`, `gemma3:27b-cloud`) — all selectable from within the app.
*   **👁️ AI Preview Dialog:** Review and edit the AI's suggested destinations before any files are moved.
*   **🐛 Bug Fixes & Stability:** Various improvements including a PySide6 compatibility fix for newer versions.

---

## 🚀 Features

### Core Functionality
*   **Multiple Organization Modes:**
    *   **By Type:** Groups files into folders like `Images`, `Videos`, `Documents`.
    *   **By Name:** Creates a folder for each file, named after the file itself.
    *   **By Date (Month):** Sorts files into `Year/Month` folders (e.g., `2024/10-October`).
    *   **By Date (Day):** Sorts files into `Year/Month/Day` folders (e.g., `2024/10/16`).
    *   **By Size:** Categorizes files as `Small`, `Medium`, or `Large`.
    *   **By First Letter:** Groups files into alphabetical folders (`A`, `B`, `C`...).
    *   **🆕 By Content (AI):** Uses Ollama AI to read file contents and suggest meaningful folder names.
*   **Flexible Actions:** Choose to **Move** original files or create a **Copy**.
*   **Smart Conflict Resolution:** Automatically `Rename`, `Overwrite`, or `Skip` files if they already exist in the destination.
*   **Recursive Processing:** Option to include all files from subdirectories.
*   **Skip Uncategorized:** Option to skip files with unknown extensions instead of moving to "Others".

### 🤖 AI Content Organizer (New in v2.5)
*   **Content-Aware Classification:** Reads the first 1500 characters of text files to understand their purpose before categorizing.
*   **40+ Supported Text Formats:** `.py`, `.js`, `.md`, `.txt`, `.json`, `.yaml`, `.sql`, `.html`, `.css`, and many more.
*   **PDF Support:** Extracts text from PDFs via `pypdf` or `pdfplumber` (optional install).
*   **Filename Fallback:** Files that can't be read (images, videos, audio) are classified by filename alone — the process never stops.
*   **Project Detection:** Scans sub-folders for indicator files (`package.json`, `requirements.txt`, `Cargo.toml`, `.git`, etc.) and treats them as projects, moving the entire folder as one unit.
*   **Editable Preview:** Before any file is moved, a preview dialog shows the full plan. Double-click any row to change the destination.
*   **Model Flexibility:** Refresh the model list at any time to pick from available local or cloud Ollama models.

### User Experience & Interface
*   **✨ Enhanced Category Editor:** A powerful interface to manage categories:
    *   **Auto-Detect:** Scan any folder to discover new file extensions automatically.
    *   **Quick Add:** Add extensions instantly by typing and pressing Enter.
    *   **Bulk Add:** Add multiple extensions at once (comma or line separated).
    *   **Move Extensions:** Transfer extensions between categories easily.
    *   **Import/Export:** Backup and restore your category configurations.
    *   **Search & Filter:** Quickly find categories and extensions.
    *   **Color Coding:** Visual identification for each category.
    *   **Keyboard Shortcuts:** `Ctrl+N`, `Ctrl+F`, `Ctrl+S`, `Ctrl+E`, `Ctrl+I`, `F1`, `Delete`.
*   **Modern GUI:** Clean and responsive interface built with PySide6.
*   **Real-time Progress:** A progress bar and live log ensure the app never freezes during long operations.
*   **Detailed Results Table:** See the status of each file (Success, Skipped, Failed) in a clear, color-coded table.
*   **Multi-language Support:** Switch between **English** and **Arabic** on the fly.
*   **Themes:** Instantly switch between **Light** and **Dark** modes.
*   **Drag & Drop:** Easily drop your source folder into the path input field.

### Safety & Customization
*   **↩️ Undo Last Operation:** Revert the entire last organization process with a single click — works with AI mode too.
*   **🛡️ Dry-run Mode:** A simulation mode that shows you what will happen **without touching your files**.
*   **💾 Profiles:** Save and load your favorite settings for quick reuse.
*   **🚫 Skip Unknown Files:** Choose to skip files that don't match any category instead of moving them to "Others".
*   **Easy Windows Launch:** Includes a `Sortify.bat` script for double-click execution.

---

## 🛠️ Installation

**Prerequisites:** Python 3.9+

1.  Clone the repository and navigate into the project directory:
    ```bash
    git clone https://github.com/abdulrahman20242/File-Organizer-AI_v2.5.git
    cd File-Organizer-AI_v2.5
    ```

2.  **Create and activate a virtual environment (Recommended):**
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

4.  **(Optional) For AI PDF support:**
    ```bash
    pip install pypdf
    # or
    pip install pdfplumber
    ```

5.  **(Required for AI mode) Install Ollama:**
    Download from [https://ollama.com](https://ollama.com), then pull a model:
    ```bash
    ollama pull gemma2:2b
    ```

---

## 🖥️ Usage

### Standard Mode
```bash
python file_organizer_gui.py
```
Or on Windows, double-click **`Sortify.bat`**.

1.  **Select Source & Destination:** Use "Browse" or drag-and-drop. If destination is empty, `Organized_Files` is created inside the source.
2.  **Choose Options:** Mode, action (move/copy), conflict policy.
3.  **Run** → monitor progress → **Undo** if needed.

### AI Mode
1.  Start Ollama: `ollama serve`
2.  In the app, select **"By Content (AI)"** from the Mode dropdown.
3.  The **AI Settings Panel** appears — set your Ollama URL and click **Refresh** to load models.
4.  Select source & destination, then click **Run**.
5.  The AI analyzes each file/project in the background (progress shown live in log).
6.  A **Preview Dialog** appears — review suggestions, edit any destination, then click **Proceed**.
7.  Files are moved/copied. Use **Undo** to revert if needed.

---

## ⚙️ Customization

### Using the Category Editor
Access from `Edit → Manage Categories` or the toolbar.

*   **Auto-Detect:** Scan a folder to discover all file extensions in it.
*   **Bulk Add:** Add multiple extensions at once.
*   **Import/Export:** Save/load your category setup as JSON.
*   **Search:** `Ctrl+F` to find any category or extension.
*   **Colors:** Right-click a category to change its color.

### Manual Configuration

Edit **`categories.json`** directly:
```json
{
  "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".heic", ".eps"],
  "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
  "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx"],
  "Others": []
}
```

Edit **`category_colors.json`** for colors:
```json
{
  "Images": "#4CAF50",
  "Videos": "#2196F3",
  "Documents": "#FF9800",
  "Others": "#9E9E9E"
}
```

---

## 🧪 Running Tests

The project includes **95 tests** covering all core logic and the new AI module.

1.  Install test dependencies:
    ```bash
    pip install pytest
    ```

2.  Run from the project root:
    ```bash
    # Run all tests
    pytest test_organizer.py -v

    # Quick summary
    pytest test_organizer.py -q

    # AI module tests only
    pytest test_organizer.py::TestAIContentOrganizer -v

    # With coverage report
    pytest test_organizer.py --cov=file_organizer --cov-report=html
    ```

> **Note for Windows users:** If your C: drive is low on space, tests use `conftest.py` to redirect temp files to the project folder automatically.

---

## 📒 Project Structure

```
File-Organizer-AI_v2.5/
├── file_organizer_gui.py      Main PySide6 GUI
├── file_organizer.py          Core file operation logic (move, copy, undo, etc.)
├── ai_content_organizer.py    🆕 AI engine: Ollama client, content analyzer, workers, preview dialog
├── category_editor.py         Enhanced category editor dialog
├── test_organizer.py          pytest suite (95 tests)
├── conftest.py                🆕 pytest temp dir fix for Windows
├── translations.json          EN + AR strings (includes new AI keys)
├── Sortify.bat                Windows double-click launcher
├── categories.json            File type categories (auto-generated)
├── category_colors.json       Category colors (auto-generated)
├── settings.json              User settings including AI URL & model (auto-generated)
├── profiles.json              Saved profiles (auto-generated)
├── requirements.txt           Runtime dependencies
└── requirements-dev.txt       Dev/test dependencies
```

---

## 🔧 Troubleshooting

*   **App doesn't start:** Make sure Python 3.9+ is installed and run `pip install -r requirements.txt`.
*   **Theme not working:** `pip install pyqtdarktheme`
*   **Icons not showing:** `pip install qtawesome`
*   **AI mode — "Cannot connect to Ollama":** Make sure Ollama is running (`ollama serve`) and the URL in AI Settings is correct.
*   **AI mode — no models in dropdown:** Click **Refresh** after Ollama is running. Make sure you've pulled at least one model (`ollama pull gemma2:2b`).
*   **Tests failing with "No space left on device":** Your C: drive is full. The included `conftest.py` redirects pytest temp files to the project folder (F: or wherever the project lives).
*   **Reset to defaults:** Delete `settings.json`, `categories.json`, and `profiles.json`.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the repository
2.  Create your feature branch: `git checkout -b feature/AmazingFeature`
3.  Commit your changes: `git commit -m 'Add some AmazingFeature'`
4.  Push to the branch: `git push origin feature/AmazingFeature`
5.  Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Abdulrahman** — [GitHub Profile](https://github.com/abdulrahman20242)

---

## 🙏 Acknowledgments

*   [PySide6](https://doc.qt.io/qtforpython/) — Qt for Python
*   [QtAwesome](https://github.com/spyder-ide/qtawesome) — Iconic fonts for PyQt/PySide
*   [pyqtdarktheme](https://github.com/5yutan5/PyQtDarkTheme) — Dark theme support
*   [Ollama](https://ollama.com) — Local AI model runtime
