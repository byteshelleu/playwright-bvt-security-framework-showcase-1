"""Names of the registration form."""

from __future__ import annotations

REGISTER_EMAIL_NAME: str = "Email address field"
REGISTER_PASSWORD_NAME: str = "Field for the password"
REGISTER_REPEAT_NAME: str = "Field to confirm the password"
SECURITY_QUESTION_NAME: str = "Selection list for the security question"
SECURITY_QUESTION: str = "Your eldest siblings middle name?"
SECURITY_ANSWER_NAME: str = "Field for the answer to the security question"
REGISTER_BUTTON_NAME: str = "Button to complete the registration"
SECURITY_QUESTIONS_API: str = "**/api/SecurityQuestions/**"
"""The request whose answer fills the question list; it stays closed until then."""
