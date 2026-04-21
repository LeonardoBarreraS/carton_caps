from __future__ import annotations

import dataclasses
import logging
from pathlib import Path

from conversation_management.application.ports.i_event_publisher import (
    IEventPublisher as BC1IEventPublisher,
)
from decision_intelligence.application.ports.i_event_publisher import (
    IEventPublisher as BC2IEventPublisher,
)

_logger = logging.getLogger("carton_caps.domain_events")


class LoggingEventPublisher(BC1IEventPublisher, BC2IEventPublisher):
    """
    Shell-layer implementation of both BC-1 and BC-2 IEventPublisher ports.

    Emits each domain event as a structured INFO-level log line using Python's
    standard logging module.  A single instance is wired to all use cases in
    the composition root.

    Log format:
        [DomainEvent] <EventType> <field>=<value> ...

    Never raises — log failures are silently swallowed so they can never
    interrupt the main turn pipeline.
    """

    def __init__(self, log_path: str) -> None:
        self._configure_file_handler(log_path)

    def publish(self, events: list) -> None:
        for event in events:
            try:
                event_type = type(event).__name__
                fields = " ".join(
                    f"{k}={v}"
                    for k, v in dataclasses.asdict(event).items()
                )
                _logger.info("[DomainEvent] %s %s", event_type, fields)
            except Exception:  # noqa: BLE001
                pass

    def _configure_file_handler(self, log_path: str) -> None:
        try:
            target_path = Path(log_path).resolve()
            target_path.parent.mkdir(parents=True, exist_ok=True)

            for handler in _logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler_path = Path(handler.baseFilename).resolve()
                    if handler_path == target_path:
                        return

            file_handler = logging.FileHandler(target_path, encoding="utf-8")
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
            )
            _logger.setLevel(logging.INFO)
            _logger.addHandler(file_handler)
            _logger.propagate = False
        except Exception:  # noqa: BLE001
            pass
