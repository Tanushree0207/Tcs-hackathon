from pydantic import BaseModel, Field, field_validator


class BugReportRequest(BaseModel):
    """Schema for validating incoming bug report submissions."""

    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Brief summary of the issue (3-200 characters).",
    )
    description: str = Field(
        ...,
        min_length=5,
        max_length=5000,
        description="Detailed description of the bug (5-5000 characters).",
    )
    severity: str = Field(
        ...,
        description="Reported severity: 'Critical', 'High', 'Medium', or 'Low'.",
    )

    @field_validator("title", "description", mode="before")
    @classmethod
    def strip_text(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("Field cannot be blank or contain only whitespace.")
        return value

    @field_validator("severity", mode="before")
    @classmethod
    def validate_severity(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Severity must be a string.")

        normalized = value.strip().capitalize()
        valid_severities = ("Critical", "High", "Medium", "Low")
        if normalized not in valid_severities:
            raise ValueError(
                f"Invalid severity '{value}'. Allowed values are: {', '.join(valid_severities)}."
            )
        return normalized
