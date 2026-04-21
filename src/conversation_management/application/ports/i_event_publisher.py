from __future__ import annotations

from abc import ABC, abstractmethod


class IEventPublisher(ABC):
    """
    Application-layer port for publishing domain events raised by BC-1 aggregates.

    Called by use cases after draining domain events from ConversationSession.
    Implemented in the shell layer by LoggingEventPublisher.

    Consumed events:
      - SessionStarted  (emitted in StartSessionUseCase)
      - TurnProcessed   (emitted in ProcessTurnUseCase)
      - SessionClosed   (emitted in CloseSessionUseCase)
    """

    @abstractmethod
    def publish(self, events: list) -> None:
        """Publish all domain events from a single aggregate drain."""
        ...
