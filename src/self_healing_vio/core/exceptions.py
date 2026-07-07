"""Domain-specific exceptions for SHIELD-VIO."""

from __future__ import annotations


class ShieldVioError(Exception):
    """Base exception for SHIELD-VIO errors."""


class ConfigurationError(ShieldVioError):
    """Raised when a configuration is missing, inconsistent, or invalid."""


class DetectorError(ShieldVioError):
    """Raised when a detector cannot evaluate its input."""


class DiagnosisError(ShieldVioError):
    """Raised when diagnosis inference fails or produces invalid probabilities."""


class RecoveryPolicyError(ShieldVioError):
    """Raised when a recovery policy cannot select a valid action."""


class BackendUnavailableError(ShieldVioError):
    """Raised when a requested VIO backend is not available."""
