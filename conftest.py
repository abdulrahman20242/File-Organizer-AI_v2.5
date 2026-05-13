"""
conftest.py — يغير مسار pytest temp من C:/AppData إلى مجلد المشروع
لتجنب مشكلة "No space left on device" على C:
"""
import pytest
import tempfile
from pathlib import Path


def pytest_configure(config):
    """يغير مجلد الـ temp ليكون بجانب ملف conftest.py (على نفس القرص)."""
    project_dir = Path(__file__).parent
    tmp_dir = project_dir / ".pytest_tmp"
    tmp_dir.mkdir(exist_ok=True)
    tempfile.tempdir = str(tmp_dir)


@pytest.fixture(scope="session", autouse=True)
def cleanup_pytest_tmp():
    """ينظف مجلد temp بعد انتهاء جلسة الاختبارات."""
    yield
    import shutil
    tmp_dir = Path(__file__).parent / ".pytest_tmp"
    if tmp_dir.exists():
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass
