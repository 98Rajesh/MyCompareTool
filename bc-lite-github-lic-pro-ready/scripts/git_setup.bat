@echo off
set WRAPPER_PATH=%cd%\app\git_wrapper.py

git config --global diff.tool bc-lite
git config --global difftool.bc-lite.cmd "python \"%WRAPPER_PATH%\" %LOCAL% %REMOTE%"

git config --global merge.tool bc-lite
git config --global mergetool.bc-lite.cmd "python \"%WRAPPER_PATH%\""

git config --global mergetool.bc-lite.trustExitCode true

echo Configured git to use BC-Lite as difftool & mergetool.
