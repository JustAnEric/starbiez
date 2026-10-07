def is_jerryscript_available() -> bool:
    # its just an import check, nothing special
    try:
        import jerryscript
        return True
    except ImportError:
        return False

def run_jscript_file(entry: str):
    if not is_jerryscript_available():
        return False
    import jerryscript
    ... # stub for now

__all__ = ['run_jscript_file', 'is_jerryscript_available']