from pathlib import Path


def ensure_dir(dir: Path) -> Path:
    dir.mkdir(parents = True, exist_ok = True)
    if not dir.exists() or not dir.is_dir():
        raise RuntimeError(f"Dir {dir} withing config folder does not exist or not a directory")
    else:
        return dir
   