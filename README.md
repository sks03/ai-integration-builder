# AI-Generated Integration Builder

An AI-powered prototype that generates SaaS API connectors from API documentation, validates them against safety rules, and tests them through a sandbox-first workflow.

## 1. Overview

Building and maintaining SaaS integrations often requires engineering effort for every application. Differences in API structures, authentication methods, pagination, permissions, and rate limits make it difficult to support a long tail of SaaS applications.

The AI-Generated Integration Builder explores how AI can simplify this process by allowing an IT administrator to provide API documentation and generate a connector without manually writing integration code.

**The goal:** Make SaaS integration creation faster and more accessible while maintaining control over permissions, data access, and execution.

## 2. Prototype Scope

The current prototype demonstrates a read-only Calendly integration.

| Area | Scope |
|---|---|
| Initial application | Calendly |
| Authentication | Calendly Personal Access Token |
| User data | Organization memberships |
| Activity data | Scheduled events |
| API operations | Read-only GET requests |
| Connector generation | OpenAI API |
| Validation | Static safeguards and AI-assisted review |
| Execution | Sandbox / dry-run workflow |

**Out of scope:** Write operations, provisioning, meeting content, invitee data, billing data, and multi-application production support.

## 3. How It Works

The prototype follows this workflow:

1. **Documentation input:** The user provides API documentation.
2. **AI connector generation:** The OpenAI model analyzes the documentation and generates Python connector code.
3. **Safety review:** The generated code is checked against safety requirements and reviewed for potential risks.
4. **Sandbox execution:** The connector is executed to validate authentication and retrieve data from Calendly.
5. **Data preview:** Retrieved data is presented with sensitive user information masked.

## 4. Architecture

```text
API Documentation
       |
       v
Documentation Input
       |
       v
OpenAI Connector Generator
       |
       v
Generated Python Connector
       |
       v
Safety Review
  (Static + AI-assisted)
       |
       v
Sandbox / Dry Run
       |
       v
Calendly API
       |
       v
Masked Data Preview
```

### Key components

| Component | Responsibility |
|---|---|
| `app.py` | Streamlit user interface and workflow orchestration |
| `generator.py` | AI-powered connector generation |
| `reviewer.py` | AI-assisted review of generated code |
| `safeguards.py` | Static safety checks |
| `runner.py` | Sandbox / dry-run execution |
| `generated/` | Generated connector implementation |
| `prompts/` | Instructions for connector generation and review |

## 5. Safety and Governance

The prototype incorporates a safety-first approach to generated integrations.

- **Read-only access:** Connector operations are restricted to GET requests.
- **Documentation grounding:** Connector generation is guided by the supplied API documentation.
- **Credential handling:** API keys and access tokens are supplied through environment variables, not embedded in generated code.
- **PII protection:** Sensitive user information is masked in the displayed preview.
- **Safer logging:** Logs focus on execution status and record counts rather than exposing raw user data.
- **Execution controls:** The generated connector is reviewed before sandbox execution.

The sandbox-first approach is intended to validate the connector before any future production activation. A production implementation would require additional isolation, access controls, monitoring, approval, and rollback mechanisms.

## 6. Calendly Sandbox Results

The prototype was successfully executed against Calendly.

| Validation | Result |
|---|---|
| Authentication | Successful |
| Organization users retrieved | 1 |
| Scheduled events retrieved | 0 |
| Usage window | Last 30 days |
| User preview | Sensitive fields masked |
| Execution | Successful |

The zero scheduled events result indicates that no events were returned for the selected 30-day period. The API request itself completed successfully.

**Note:** Scheduled events are treated as an activity signal, not as a comprehensive measure of application usage or user logins.

## 7. Technology Stack

- Python
- Streamlit
- OpenAI API
- Calendly REST API
- Requests
- Git and GitHub

## 8. Run Locally

### Prerequisites

- Python 3.10 or later
- OpenAI API key
- Calendly Personal Access Token with the required read-only permissions

### Installation

Clone the repository:

```bash
git clone https://github.com/sks03/ai-integration-builder.git
cd ai-integration-builder
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### Configure environment variables

In PowerShell:

```powershell
$env:OPENAI_API_KEY = Read-Host "Enter OpenAI API key"
$env:CALENDLY_TOKEN = Read-Host "Enter Calendly token"
$env:LLM_MODEL = "gpt-4o"
```

Use your own credentials. Never commit API keys or tokens to the repository.

### Launch the application

```bash
python -m streamlit run app.py
```

## 9. Limitations and Future Considerations

This is an MVP prototype demonstrating the connector-generation and validation workflow. It is not a production-ready integration platform.

Potential next steps include:

- Support additional SaaS applications.
- Define and enforce a standardized CloudEagle data schema.
- Improve connector validation and automated test coverage.
- Introduce stronger runtime isolation and production approval controls.
- Handle API plan limitations, rate limits, and schema changes.
- Add connector versioning, monitoring, and rollback.

---

**Built as a product prototype exploring AI-assisted SaaS integration generation, with a focus on usability, safety, and controlled execution.**
