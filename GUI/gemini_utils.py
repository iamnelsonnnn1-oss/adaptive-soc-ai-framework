"""Shared helpers for interacting with the Gemini engine."""


def classify_api_error(error: Exception) -> str:
    """Map a Gemini API exception to a human-readable reason phrase.

    The returned phrase is prefixed by the caller with the appropriate
    context (e.g. "Handshake Failed:" or "Neural Link Error:").
    """
    error_msg = str(error).lower()
    if "401" in error_msg or "api_key_invalid" in error_msg:
        return "Invalid credential baseline."
    if "429" in error_msg or "quota" in error_msg:
        return "API rate limit active."
    if "404" in error_msg or "not found" in error_msg:
        return "Model target unavailable."
    if "location" in error_msg:
        return "Restricted regional access."
    return "Secure engine disconnect."
