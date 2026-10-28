"""
ai_engine.errors

Defines standard exception types for ai_engine.
"""


class AIError(Exception):
    """
    Base exception raised by ai_engine when an AI model invocation, parsing,
    validation, or contract compliance check fails.
    Teammates (such as the FastAPI gateway in backend/) catch this exception.
    """
    pass
