from typing import List

CONFLICT_START = "<<<<<<< LEFT\n"
CONFLICT_MID = "=======\n"
CONFLICT_END = ">>>>>>> RIGHT\n"

def _diff3(base: List[str], left: List[str], right: List[str]) -> List[str]:
    """
    Very small, naive diff3-like merge.
    """
    out = []
    i = j = 0
    while i < len(left) or j < len(right):
        l = left[i] if i < len(left) else None
        r = right[j] if j < len(right) else None
        if l == r:
            out.append(l if l is not None else "")
            i += (i < len(left))
            j += (j < len(right))
        elif l is None:
            out.append(r)
            j += 1
        elif r is None:
            out.append(l)
            i += 1
        else:
            out.append(CONFLICT_START)
            out.append(l)
            out.append(CONFLICT_MID)
            out.append(r)
            out.append(CONFLICT_END)
            i += 1
            j += 1
    return out

def merge_text(base_text: str, left_text: str, right_text: str) -> str:
    base = base_text.splitlines(keepends=True)
    left = left_text.splitlines(keepends=True)
    right = right_text.splitlines(keepends=True)
    merged = _diff3(base, left, right)
    return "".join(merged)
