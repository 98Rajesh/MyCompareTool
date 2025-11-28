from typing import List, Tuple

def myers_diff(a: List[str], b: List[str]) -> List[Tuple[str, str]]:
    """
    Return a list of tuples (tag, text) where tag in (' ', '-', '+')
    ' ' = equal, '-' = deletion from a, '+' = insertion from b
    Based on the O(ND) Myers algorithm (simplified, line-based).
    """
    N, M = len(a), len(b)
    maxd = N + M
    v = {1: 0}
    trace = []

    for d in range(0, maxd + 1):
        v_snapshot = v.copy()
        trace.append(v_snapshot)
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
                x = v.get(k + 1, 0)
            else:
                x = v.get(k - 1, 0) + 1
            y = x - k
            while x < N and y < M and a[x] == b[y]:
                x += 1
                y += 1
            v[k] = x
            if x >= N and y >= M:
                break
        else:
            continue
        break

    # backtrack
    res = []
    x, y = N, M
    for d in range(len(trace) - 1, -1, -1):
        v = trace[d]
        k = x - y
        if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
            pk = k + 1
        else:
            pk = k - 1
        px = v.get(pk, 0)
        py = px - pk
        while x > px and y > py:
            res.append((' ', a[x - 1]))
            x -= 1
            y -= 1
        if d == 0:
            break
        if x == px:
            res.append(('+', b[y - 1]))
            y -= 1
        else:
            res.append(('-', a[x - 1]))
            x -= 1

    res.reverse()
    return res

def diff_as_html(a_text: str, b_text: str) -> str:
    a = a_text.splitlines()
    b = b_text.splitlines()
    hunks = myers_diff(a, b)
    rows = []
    for tag, line in hunks:
        if tag == ' ':
            cls = "equal"
        elif tag == '-':
            cls = "del"
        else:
            cls = "ins"
        rows.append(f"<tr class='{cls}'><td class='tag'>{tag}</td><td class='txt'>{line}</td></tr>")
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; }}
table {{ border-collapse: collapse; width: 100%; }}
td {{ padding: 2px 6px; vertical-align: top; }}
tr.equal {{ background: #f5f5f5; }}
tr.del {{ background: #ffecec; }}
tr.ins {{ background: #eaffea; }}
td.tag {{ width: 24px; color: #888; }}
td.txt {{ white-space: pre; }}
</style></head><body>
<h3>BC-Lite Diff</h3>
<table>{''.join(rows)}</table>
</body></html>"""
    return html
