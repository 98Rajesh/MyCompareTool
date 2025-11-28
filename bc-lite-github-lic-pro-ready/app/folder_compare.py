import os, hashlib
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class FileEntry:
    path: str
    rel: str
    size: int
    mtime: float
    hash: Optional[str] = None

def walk(dirpath: str) -> List[FileEntry]:
    out = []
    dirpath = os.path.abspath(dirpath)
    for root, _, files in os.walk(dirpath):
        for f in files:
            p = os.path.join(root, f)
            try:
                st = os.stat(p)
            except FileNotFoundError:
                continue
            rel = os.path.relpath(p, dirpath)
            out.append(FileEntry(p, rel, st.st_size, st.st_mtime))
    return out

def hash_file(path: str, blocksize: int = 65536) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        for chunk in iter(lambda: fp.read(blocksize), b""):
            h.update(chunk)
    return h.hexdigest()

def compare_dirs(left: str, right: str, mode: str = "size_time", do_hash: bool = False):
    """
    mode: 'size_time' or 'content'
    """
    la = {e.rel: e for e in walk(left)}
    rb = {e.rel: e for e in walk(right)}
    all_keys = sorted(set(la) | set(rb))
    rows = []
    for k in all_keys:
        le = la.get(k)
        re = rb.get(k)
        status = ""
        if le and not re:
            status = "Left only"
        elif re and not le:
            status = "Right only"
        else:
            if mode == "size_time":
                status = "Equal" if (le.size == re.size and int(le.mtime) == int(re.mtime)) else "Different"
            else:
                if do_hash:
                    le.hash = hash_file(le.path)
                    re.hash = hash_file(re.path)
                    status = "Equal" if le.hash == re.hash else "Different"
                else:
                    status = "Different/Unknown (enable hashing)"
        rows.append({
            "relpath": k,
            "left_size": le.size if le else "",
            "right_size": re.size if re else "",
            "status": status,
            "left_path": le.path if le else "",
            "right_path": re.path if re else ""
        })
    return rows
