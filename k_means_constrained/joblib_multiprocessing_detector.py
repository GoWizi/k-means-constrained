import os
import tempfile


def has_joblib_multiprocessing_error():
    """
    Check if joblib will have multiprocessing issues.

    Returns:
        bool: True if joblib will fallback to serial mode (error condition)
    """
    # Check environment variable first
    mp_env = int(os.environ.get("JOBLIB_MULTIPROCESSING", 1)) or None
    if not mp_env:
        return True  # Disabled by environment

    # Try to import multiprocessing modules
    try:
        import multiprocessing as mp

        import _multiprocessing  # noqa
    except ImportError:
        return True  # Can't import multiprocessing

    # Test semaphore creation (this is where the actual error usually occurs)
    try:
        from _multiprocessing import SemLock

        _rand = tempfile._RandomNameSequence()
        for i in range(100):
            try:
                name = "/joblib-{}-{}".format(os.getpid(), next(_rand))
                _sem = SemLock(0, 0, 1, name=name, unlink=True)
                del _sem  # cleanup
                break
            except FileExistsError as e:  # pragma: no cover
                if i >= 99:
                    raise FileExistsError("cannot find name for semaphore") from e

        return False  # Multiprocessing is working fine

    except (FileExistsError, AttributeError, ImportError, OSError):
        return True  # Will fallback to serial mode
