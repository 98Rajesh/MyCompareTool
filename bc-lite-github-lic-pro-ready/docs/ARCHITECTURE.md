# BC-Lite Architecture Overview

## 1. Introduction

This document explains how BC-Lite is structured internally, how major components communicate, and the reasoning behind key technical decisions.

---

## 2. High-Level Architecture

+-------------+ +------------------+ +------------------------+
| UI Layer | --> | Command Routing | -->| Comparison Engines |
+-------------+ +------------------+ +------------------------+
| | |
| | |
↓ ↓ ↓
PySide6 Widgets CLI argument handlers Folder, Text, Binary diff


---

## 3. Core Modules

| Module | Purpose |
|--------|---------|
| `app/main.py` | Entry point, window manager, git integration launch modes |
| `folder_compare.py` | Recursively compares directory structures |
| `diff.py` | Myers diff implementation for text files |
| `three_way_merge.py` | 3-way line-merge used for conflict resolution |
| `hex_viewer.py` | Binary hex+ASCII visualization widget |
| `git_wrapper.py` | CLI tool interface used by Git difftool/mergetool |

---

## 4. GUI Flow (PySide6)

MainWindow
┣── FolderCompareWidget
┣── FileDiffWidget
┗── HexViewerDialog (future detachable)


UI is event-driven. Long-running tasks (hashing, folder scanning) will later migrate to `QThreadPool`.

---

## 5. Data Flow (Git Mode)

Git → git_wrapper.py → main.py (parse args) → UI mode (diff/merge) → Exit code → Git


Exit codes ensure correct Git workflow behavior.

---

## 6. Packaging Flow


---

## 7. Planned Extensions

- Multithreaded folder hashing
- Plugin system
- Configurable ignore/filter rules
- Themes (dark/light/custom)
