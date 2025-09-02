"""Core state definitions for ThothSpinner components.

This module defines the lifecycle states that components can transition
through, with validation rules to ensure state machine integrity.
"""

from __future__ import annotations

from enum import Enum, auto


class ComponentState(Enum):
    """Component lifecycle states with transition validation.

    States:
        IN_PROGRESS: Active/animating state (default)
        SUCCESS: Successful completion (terminal state)
        ERROR: Error/failure state (terminal state)
    """

    IN_PROGRESS = auto()  # Active/animating state
    SUCCESS = auto()  # Successful completion
    ERROR = auto()  # Error/failure state

    def can_transition_to(self, new_state: ComponentState) -> bool:
        """Check if transition to new_state is valid.

        Transition rules:
        - Can always reset to IN_PROGRESS from any state
        - Can only go to terminal states (SUCCESS/ERROR) from IN_PROGRESS
        - Cannot transition directly between SUCCESS and ERROR

        Args:
            new_state: Target state to transition to

        Returns:
            True if transition is valid, False otherwise
        """
        # Can always reset to IN_PROGRESS
        if new_state == ComponentState.IN_PROGRESS:
            return True

        # Can only go to terminal states from IN_PROGRESS
        if self == ComponentState.IN_PROGRESS:
            return new_state in (ComponentState.SUCCESS, ComponentState.ERROR)

        # Cannot transition between SUCCESS and ERROR directly
        return False
