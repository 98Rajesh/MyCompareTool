# Release Checklist

✔ Update version in `app/__version__.py`  
✔ Update `CHANGELOG.md`  
✔ Run full test suite  
✔ Build installers: pyinstaller --onefile --windowed app/main.py


✔ Smoke test:
- Folder compare
- Text diff
- Hex diff
- Git merge/diff

✔ Tag release:
git tag -a vX.Y -m "Release notes"
git push --tags


✔ Upload builds to GitHub Releases  
✔ Announce (optional)
