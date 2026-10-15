from enum import Enum
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

# TODO: Add the missing fields to LogAnalysis with clear Field(description="...") hints:
# - severity: SeverityLevel
# - error_code: int
# - is_compromised: bool
# - recommended_fix: list[str]

class LogAnalysis(BaseModel):
    severity: SeverityLevel = Field(
        description="The severity level of the event: LOW, MEDIUM, HIGH, or CRITICAL."
    )
    error_code: int = Field(
        description="The integer HTTP or system error code extracted from the log. Return -1 if none exists."
    )
    is_compromised: bool = Field(
        description="True if active unauthorized access succeeded, false otherwise."
    )
    summary: str = Field(
        description="One-sentence technical summary of the event."
    )
    recommended_fix: list[str] = Field(
        description="List of concrete, actionable remediation steps to address the vulnerability or event."
    )

# TODO: Improve this system prompt so the model accurately classifies SIEM logs
SYSTEM_PROMPT = """
ROLE: You are an expert SIEM Log Analyzer and Security Architect.
CONTEXT: Your task is to analyze raw server logs and extract structured incident records.
INSTRUCTIONS:
- Carefully analyze the provided log for unauthorized access, vulnerabilities, and system errors.
- Evaluate the severity based on the potential impact (e.g., root access bypass is CRITICAL).
- Accurately extract any mentioned error codes, defaulting to -1 if absent.
- Clearly identify if a breach occurred (`is_compromised`).
- Provide concrete, technical remediation steps to secure the system.
"""

def parse_server_log(raw_log: str) -> LogAnalysis:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=f"Analyze the following raw server log:\n<log>{raw_log}</log>",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=LogAnalysis,
        ),
    )
    # Validate and deserialize JSON string directly into the Pydantic object
    return LogAnalysis.model_validate_json(response.text)

if __name__ == "__main__":
    sample = (
        "2026-10-15 02:11:44 [ALERT] sshd[9012]: Accepted password for root "
        "from 198.51.100.77 port 44122 ssh2 (ErrorCode=401 bypassed via PAM bug)"
    )
    print(parse_server_log(sample).model_dump_json(indent=2))

# --- Automated Unit Test (Run with: pytest test_module2_structured.py) ---
def test_ssh_breach_log_parsing():
    sample_log = (
        "2026-10-15 02:11:44 [ALERT] sshd[9012]: Accepted password for root "
        "from 198.51.100.77 port 44122 ssh2 (ErrorCode=401 bypassed via PAM bug)"
    )
    result = parse_server_log(sample_log)

    assert result.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]
    assert result.error_code == 401
    assert result.is_compromised is True
    assert len(result.recommended_fix) >= 1