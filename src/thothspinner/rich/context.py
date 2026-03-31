"""Context manager support for ThothSpinner.track()."""

from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING, Any

from rich.live import Live

if TYPE_CHECKING:
    from thothspinner.rich.thothspinner import ThothSpinner


class _TrackContext:
    """Context manager returned by ThothSpinner.track().

    Wraps a ThothSpinner and a Rich Live instance so callers don't need to
    manage either manually.  All ThothSpinner attributes and methods are
    accessible directly on this object via __getattr__.
    """

    def __init__(self, spinner: ThothSpinner, live: Live) -> None:
        # Use object.__setattr__ to avoid triggering __getattr__ recursion
        object.__setattr__(self, "_spinner", spinner)
        object.__setattr__(self, "_live", live)

    # ------------------------------------------------------------------
    # Convenience shorthand
    # ------------------------------------------------------------------

    def update(self, current: int, total: int | None = None) -> None:
        """Shorthand for spinner.update_progress(current=..., total=...)."""
        kwargs: dict[str, Any] = {"current": current}
        if total is not None:
            kwargs["total"] = total
        self._spinner.update_progress(**kwargs)

    # ------------------------------------------------------------------
    # Attribute forwarding to the underlying ThothSpinner
    # ------------------------------------------------------------------

    def __getattr__(self, name: str) -> Any:
        return getattr(object.__getattribute__(self, "_spinner"), name)

    # ------------------------------------------------------------------
    # Context manager protocol
    # ------------------------------------------------------------------

    def __enter__(self) -> _TrackContext:
        self._live.__enter__()
        self._spinner.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        if exc_type is None:
            self._spinner.success()
        else:
            self._spinner.error(str(exc_val) or None)
        self._live.__exit__(exc_type, exc_val, exc_tb)
        return False  # never suppress exceptions
