import contextlib


@contextlib.contextmanager
def open_iga_file(filepath, version):
    """Context manager for IGA file operations"""
    from ..iga import iga_file

    iga = None
    try:
        iga = iga_file.IGA_File(filepath, version)
        yield iga
    except Exception as e:
        print(f"Error opening IGA file: {e}")
    finally:
        if iga:
            iga.close()
