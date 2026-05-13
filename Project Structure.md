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
