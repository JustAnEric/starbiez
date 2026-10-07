def exists(path: str) -> bool:
    try:
        with open(path, "r") as fp:
            return True
    except OSError:
        return False

__all__ = ['exists']