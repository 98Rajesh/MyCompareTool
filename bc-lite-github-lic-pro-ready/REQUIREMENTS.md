# BC-Lite — Requirements Specification

This document captures detailed requirements for the BC-Lite project.

## 1. Functional Requirements

### 1.1 Application Startup

- **FR-1.1**: The application SHALL start with a main window containing tabbed views.
- **FR-1.2**: The default tabs SHALL include at least:
  - `Folder Compare`
  - `File Diff`
- **FR-1.3**: When launched without arguments, the application SHALL open in normal interactive GUI mode.

### 1.2 Folder Comparison

- **FR-2.1**: The user SHALL be able to select a left and right directory via folder dialogs.
- **FR-2.2**: The application SHALL recursively scan both folders and build a list of relative file paths.
- **FR-2.3**: For each file path, the application SHALL display:
  - Relative path from the root of the comparison
  - File size on left and right (if present)
  - Status label (`Left only`, `Right only`, `Equal`, `Different`)
- **FR-2.4**: The application SHALL support comparison modes:
  - `size_time`: compare using file size and integer seconds of modification time.
  - `content`: compare via SHA-256 hash of full file content (optional).
- **FR-2.5**: When `content` mode with hashing is enabled, identical hashes SHALL be treated as `Equal`.
- **FR-2.6**: The user interface SHALL allow sorting by any column.

### 1.3 File Diff (Text)

- **FR-3.1**: The user SHALL be able to select a left and right file via open file dialogs.
- **FR-3.2**: The application SHALL detect binary files using a simple heuristic (presence of NUL bytes in the first block).
- **FR-3.3**: If either file appears binary, the application SHALL display an informational message and NOT attempt a text diff.
- **FR-3.4**: If both files are treated as text, the application SHALL decode bytes to text using:
  - chardet detection where available
  - fall back to UTF-8 with replacement.
- **FR-3.5**: The application SHALL compute a line-based diff using the Myers algorithm.
- **FR-3.6**: Diff results SHALL be rendered in a read-only text view with per-line markers:
  - Unchanged: `"    <line>"`
  - Deletion: `"-   <line>"`
  - Insertion: `"+   <line>"`

### 1.4 Hex Diff Viewer

- **FR-4.1**: The user SHALL be able to select two files for hex comparison.
- **FR-4.2**: The application SHALL display both files in parallel hex+ASCII views.
- **FR-4.3**: Each view row SHALL contain:
  - Offset address (hex)
  - Hex representation of up to 16 bytes
  - ASCII representation where bytes in [0x20, 0x7E] are rendered as characters; others as `.`  
- **FR-4.4**: The application SHALL compare each corresponding byte position and visually emphasize differences (e.g., using brackets `[XX]` around differing bytes).
- **FR-4.5**: If one file is longer than the other, missing bytes in the shorter file SHALL be rendered as placeholders.

### 1.5 Git Integration — Diff Tool

- **FR-5.1**: A command-line wrapper (`git_wrapper.py`) SHALL support a mode where it is called with two positional arguments: `<left> <right>`.
- **FR-5.2**: In this mode, the wrapper SHALL launch BC-Lite with a `--git-diff left right` argument set.
- **FR-5.3**: The application, when invoked with `--git-diff`, SHALL:
  - Open the GUI.
  - Load the given files into the File Diff tab.
  - Automatically run the diff.
- **FR-5.4**: The process SHALL block until the user closes the window.
- **FR-5.5**: On normal closure, the process SHALL exit with code `0`. On error launching the GUI or bad parameters, SHALL exit non-zero.

### 1.6 Git Integration — Merge Tool

- **FR-6.1**: The wrapper SHALL be able to read Git-provided environment variables `LOCAL`, `REMOTE`, `BASE`, `MERGED`.
- **FR-6.2**: When `LOCAL` and `REMOTE` and `MERGED` are available, the wrapper SHALL invoke BC-Lite with:
  - `--git-merge --local LOCAL --remote REMOTE [--base BASE] --merged MERGED`
- **FR-6.3**: When invoked in `--git-merge` mode, BC-Lite SHALL open a modal merge dialog instead of the main comparison tabs.
- **FR-6.4**: The merge dialog SHALL display:
  - Paths for local, remote, base (if any), and merged output.
- **FR-6.5**: The merge dialog SHALL load local, remote, and base content (if present) as UTF-8 with replacement.
- **FR-6.6**: The dialog SHALL compute a best-effort 3-way merge using `merge_text(base, local, remote)`.
- **FR-6.7**: The merged result SHALL be displayed in an editable text area.
- **FR-6.8**: The dialog SHALL provide at least two actions:
  - **Save**: write edited merged content to the `MERGED` file path.
  - **Cancel**: close without modifying `MERGED`.
- **FR-6.9**: On successful Save, the application SHALL exit with code `0`. On Cancel or write failure, it SHALL exit with code `1` or another non-zero code.

### 1.7 HTML Diff Report (CLI)

- **FR-7.1**: A script `scripts/report_cli.py` SHALL provide a command-line interface for generating HTML diff reports.
- **FR-7.2**: The script SHALL accept `--left`, `--right`, `--out` arguments.
- **FR-7.3**: The script SHALL compute a line-based diff using the same Myers implementation as the GUI.
- **FR-7.4**: The script SHALL write an HTML file with inline CSS and rows classified as equal, inserted, or deleted.

## 2. Non-Functional Requirements

### 2.1 Performance

- **NFR-1.1**: Folder comparison for up to ~50k files per side SHALL complete in reasonable time on modern hardware (exact benchmark TBD).
- **NFR-1.2**: Hash-based content comparison SHALL be optional and disabled by default to avoid unnecessary overhead.
- **NFR-1.3**: Hex diff viewer SHOULD remain responsive for files up to several MB; for larger files, future versions MAY introduce paging.

### 2.2 Portability

- **NFR-2.1**: Source code SHALL be portable across Windows, Linux, and macOS as long as Python and PySide6 are supported on the platform.
- **NFR-2.2**: No platform-specific filesystem operations SHALL be included in core logic beyond standard Python libraries.

### 2.3 Usability

- **NFR-3.1**: The GUI SHALL be usable on common desktop resolutions (1366×768 and above).
- **NFR-3.2**: Text contrast, fonts, and spacing SHALL be readable under default Qt themes (light and dark).

### 2.4 Reliability

- **NFR-4.1**: All file I/O operations SHALL handle exceptions gracefully and display useful error messages.
- **NFR-4.2**: Git integration SHALL fail-safe; if the GUI cannot start, the wrapper SHALL return a non-zero exit code and print a message to stderr.

## 3. External Interfaces

- **Python Runtime**: CPython 3.9+ recommended.
- **GUI Toolkit**: PySide6 (Qt 6).
- **Git**: Used externally by end-users; BC-Lite exposes a command-line interface compatible with Git difftool/mergetool expectations.
- **OS Filesystem**: Read-only for comparisons; read/write when saving merge outputs.

## 4. Constraints

- Implemented fully in Python (no compiled C extensions) for ease of distribution.
- Reliance on PyInstaller for single-file packaging.
- No built-in network access in the core application (future plug-ins may add remote connectivity).

## 5. Acceptance Criteria

- AC-1: User can compare two directories and see correct status labels for added, removed, and modified files.
- AC-2: User can compare two text files and see a readable line-based diff.
- AC-3: User can inspect two binary files in hex view and locate differing bytes.
- AC-4: Git difftool configured with BC-Lite successfully opens GUIs and returns control to Git after window close.
- AC-5: Git mergetool configured with BC-Lite allows user to resolve conflicts, saves to MERGED, and Git recognizes completion (exit code 0).
