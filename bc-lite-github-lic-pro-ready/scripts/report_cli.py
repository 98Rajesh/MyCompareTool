import argparse
from pathlib import Path
from app.diff import diff_as_html

def main():
    ap = argparse.ArgumentParser(description="BC-Lite HTML diff report generator")
    ap.add_argument("--left", required=True, help="Left text file")
    ap.add_argument("--right", required=True, help="Right text file")
    ap.add_argument("--out", required=True, help="Output HTML file")
    args = ap.parse_args()

    lt = Path(args.left).read_text(encoding="utf-8", errors="ignore")
    rt = Path(args.right).read_text(encoding="utf-8", errors="ignore")
    html = diff_as_html(lt, rt)
    Path(args.out).write_text(html, encoding="utf-8")
    print(f"Wrote {args.out}")

if __name__ == "__main__":
    main()
