# Contributing to BC-Lite

Thank you for your interest in contributing! 🎉

---

## 🔧 How to Build

```sh
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app/main.py

# Build the EXE and installer:
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --name "BC-Lite" --onefile --windowed app\main.py

# then create installer
cd installer
makensis bc-lite-installer.nsi

# Wire up Git (same as before):
bash scripts/git_setup.sh
# or
scripts\git_setup.bat


🧪 Testing
Tests are planned under tests/ using pytest.

# 🛠 Coding Standards

Use PEP8 style formatting.

Use type hints.

PRs must include:

Before/after screenshots (if UI change)

Test coverage (if logic)