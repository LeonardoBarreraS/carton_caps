from __future__ import annotations

from abc import ABC, abstractmethod


class IEventPublisher(ABC):
    """
    Application-layer port for publishing domain events raised by BC-2 aggregates.

    Called by use cases after draining domain events from DecisionContext.
    Implemented in the shell layer by LoggingEventPublisher.

    Consumed events:
      - ContextUpdated  (emitted when a PreferenceSignal is added)
      - GapDetected     (emitted when gap evaluation finds context insufficient)
      - ContextReady    (emitted when context reaches ready state for first time)
    """

    @abstractmethod
    def publish(self, events: list) -> None:
        """Publish all domain events from a single aggregate drain."""
        ...
