# BC-Lite

> A lightweight, cross-platform file & folder comparison tool inspired by Beyond Compare.

[![CI](https://img.shields.io/github/actions/workflow/status/ORG/REPO/ci.yml?branch=main)](https://github.com/ORG/REPO/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-brightgreen.svg)](https://www.python.org/)

> ⚠️ Replace `ORG/REPO` above with your actual GitHub org/user and repo name.

---

## ✨ Features

- 📁 **Folder compare** (size / timestamp / SHA-256)
- 🧾 **Text diff** using Myers algorithm
- 🧬 **Hex diff viewer** for binaries
- 🧩 **Git integration** as `difftool` & `mergetool`
- 📄 **HTML diff reports** (CLI)

---

## 🖼 Screenshots (placeholders)

> Add real screenshots taken from Windows/Linux/macOS builds.

| Folder Compare | Text Diff | Hex Diff |
| -------------- | --------- | -------- |
| _screenshot_1_ | _screenshot_2_ | _screenshot_3_ |

Create a `screenshots/` folder and store PNGs like:

- `screenshots/folder-compare.png`
- `screenshots/text-diff.png`
- `screenshots/hex-diff.png`

Then update the table:

```markdown
| Folder Compare | Text Diff | Hex Diff |
| -------------- | --------- | -------- |
| ![](screenshots/folder-compare.png) | ![](screenshots/text-diff.png) | ![](screenshots/hex-diff.png) |
```

---

## 🚀 Getting Started

```bash
git clone https://github.com/ORG/REPO.git
cd REPO

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python app/main.py
```

---

## 🧪 HTML Diff (CLI)

```bash
python scripts/report_cli.py --left a.txt --right b.txt --out diff.html
```

Open `diff.html` in your browser.

---

## 🔗 Git Integration

Configure BC-Lite as your Git difftool & mergetool:

### Linux / macOS

```bash
bash scripts/git_setup.sh
```

### Windows

```bat
scripts\git_setup.bat
```

Usage:

```bash
git difftool --tool=bc-lite HEAD~1 HEAD
git mergetool --tool=bc-lite
```

---

## 📦 Building Binaries (PyInstaller)

### Windows

```bat
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --name "BC-Lite" --onefile --windowed app/main.py
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --name "bc-lite" --onefile --windowed app/main.py
```

Artifacts will be under `dist/`.

---

## 📚 Docs

See:

- [`SPEC.md`](SPEC.md) – product & technical spec
- [`REQUIREMENTS.md`](REQUIREMENTS.md) – detailed requirements
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md)
- [`docs/ROADMAP.md`](docs/ROADMAP.md)
- [`docs/RELEASE_PROCESS.md`](docs/RELEASE_PROCESS.md)
- [`docs/CHANGELOG.md`](docs/CHANGELOG.md)

---

## 🤝 Contributing

Contributions are welcome! Please read [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) before opening a PR.

---

## 📜 License

BC-Lite is released under the [MIT License](LICENSE).
