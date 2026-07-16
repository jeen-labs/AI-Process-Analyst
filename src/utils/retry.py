"""
===============================================================================
AI Process Analyst
===============================================================================

Module:
    retry.py

Purpose:
    Provide a reusable retry utility with optional exponential backoff.

Responsibilities:
    - Retry failed operations
    - Support exponential backoff
    - Limit maximum retry delay
    - Produce consistent retry logging
    - Centralise retry behaviour for every LLM provider

Author:
    Jeen Labs

Version:
    0.1.0

Status:
    Development
===============================================================================
"""

# =============================================================================
# Standard Library Imports
# =============================================================================

import time
from collections.abc import Callable
from typing import Any
from typing import TypeVar


# =============================================================================
# Type Variables
# =============================================================================

T = TypeVar("T")


# =============================================================================
# Retry Function
# =============================================================================

def retry(
    operation: Callable[[], T],
    retry_attempts: int = 3,
    retry_delay_seconds: int = 2,
    exponential_backoff: bool = True,
    max_retry_delay_seconds: int = 30,
    retry_on: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """
    Execute an operation with retry support.

    Parameters
    ----------
    operation : Callable
        Function to execute.

    retry_attempts : int
        Maximum number of attempts.

    retry_delay_seconds : int
        Initial delay before retry.

    exponential_backoff : bool
        Double the delay after every retry.

    max_retry_delay_seconds : int
        Maximum retry delay.

    retry_on : tuple[type[Exception], ...]
        Exception types that should trigger a retry.

    Returns
    -------
    T
        Result returned by the operation.

    Raises
    ------
    Exception
        Re-raises the final exception after all retries fail.
    """

    delay = retry_delay_seconds

    last_exception: Exception | None = None

    for attempt in range(1, retry_attempts + 1):

        print(f"Attempt {attempt}/{retry_attempts}...")

        try:

            result = operation()

            if attempt > 1:

                print("Retry successful.")

            return result

        except retry_on as error:

            last_exception = error

            if attempt == retry_attempts:

                break

            print(f"Attempt {attempt} failed.")

            print(str(error))

            print(f"Retrying in {delay} second(s)...")

            time.sleep(delay)

            if exponential_backoff:

                delay = min(
                    delay * 2,
                    max_retry_delay_seconds
                )

    raise RuntimeError(
        f"Operation failed after {retry_attempts} attempt(s)."
    ) from last_exception


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    counter = {"value": 0}

    def unstable_operation() -> str:

        counter["value"] += 1

        if counter["value"] < 3:

            raise RuntimeError("Temporary failure.")

        return "Success"

    result = retry(
        operation=unstable_operation,
        retry_attempts=5,
        retry_delay_seconds=1,
        exponential_backoff=True,
        max_retry_delay_seconds=8
    )

    print()
    print("=" * 70)
    print(result)