"""Confirmation logic removed.

This module previously contained an interactive Textual modal and a
fallback prompt to confirm starting a job. The confirmation step was removed
— calling code should start the job immediately. The module is retained as a
no-op stub to avoid import errors in older code paths.
"""


def confirm_start_job() -> bool:
    """Stub implementation kept for backwards compatibility.

    Always returns True so callers that still import this function will see
    the job proceed without interactive confirmation.
    """
    return True


