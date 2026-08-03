Correct. I included admin sections again. That was wrong for the purpose you defined.

Below is the corrected template for an **LLM review context**, focused on bug detection, compliance checking, implementation alignment, and test coverage.

# LLM-Readable SRS Review Template

```text
SRS_REVIEW_CONTEXT
```

---

# 1. Purpose

## 1.1 System Purpose

```text
The system exists to:
[Describe the actual purpose of the software.]
```

## 1.2 Review Purpose

```text
This SRS context is intended to help an LLM review:
- Bugs
- Missing requirements
- Compliance failures
- Test coverage gaps
- Implementation mismatches
- Security violations
- Data handling errors
```

---

# 2. Scope

## 2.1 In Scope

| ID     | In-Scope Item |
| ------ | ------------- |
| SC-001 |               |
| SC-002 |               |
| SC-003 |               |

## 2.2 Out of Scope

| ID      | Out-of-Scope Item | Reason |
| ------- | ----------------- | ------ |
| OOS-001 |                   |        |
| OOS-002 |                   |        |

---

# 3. Glossary, Definitions, Acronyms, and Domain Terms

This section is mandatory for LLM review.

| Term | Type           | Definition | System Meaning |
| ---- | -------------- | ---------- | -------------- |
|      | Role           |            |                |
|      | State          |            |                |
|      | Domain term    |            |                |
|      | Technical term |            |                |
|      | Acronym        |            |                |

---

# 4. Requirement Language Rules

Include this because the LLM needs to understand requirement force.

| Word     | Meaning                              |
| -------- | ------------------------------------ |
| Shall    | Mandatory                            |
| Must     | Mandatory                            |
| Must not | Forbidden                            |
| Should   | Recommended but not mandatory        |
| May      | Optional / allowed                   |
| Can      | Capability, not necessarily required |

---

# 5. System Context

## 5.1 Product Overview

| Area                       | Description                                                                  |
| -------------------------- | ---------------------------------------------------------------------------- |
| Product name               |                                                                              |
| Product type               | Web app / API / desktop app / mobile app / service / LLM system / automation |
| Primary users              |                                                                              |
| Main goal                  |                                                                              |
| Deployment environment     |                                                                              |
| Main external dependencies |                                                                              |

## 5.2 Actors and External Systems

| Actor / System | Type            | Interaction With System |
| -------------- | --------------- | ----------------------- |
|                | Human user      |                         |
|                | Admin user      |                         |
|                | Database        |                         |
|                | External API    |                         |
|                | LLM provider    |                         |
|                | File storage    |                         |
|                | Vector database |                         |

---

# 6. User Classes and Permissions

| User Class      | Description | Allowed Actions | Forbidden Actions |
| --------------- | ----------- | --------------- | ----------------- |
| Guest           |             |                 |                   |
| User            |             |                 |                   |
| Admin           |             |                 |                   |
| System Operator |             |                 |                   |

---

# 7. Functional Requirements

## 7.1 Functional Requirement Format

| Field                  | Value               |
| ---------------------- | ------------------- |
| Requirement ID         | FR-001              |
| Requirement            | The system shall... |
| Actor                  |                     |
| Trigger                |                     |
| Input                  |                     |
| Processing Rule        |                     |
| Output                 |                     |
| Error Behavior         |                     |
| Acceptance Criteria    |                     |
| Related Business Rules |                     |
| Related Test Cases     |                     |

## 7.2 Functional Requirements

| ID     | Requirement      | Acceptance Criteria |
| ------ | ---------------- | ------------------- |
| FR-001 | The system shall |                     |
| FR-002 | The system shall |                     |
| FR-003 | The system shall |                     |

---

# 8. Use Cases / User Flows

## UC-001: Use Case Name

| Field                | Description |
| -------------------- | ----------- |
| Use Case ID          | UC-001      |
| Actor                |             |
| Goal                 |             |
| Preconditions        |             |
| Trigger              |             |
| Postconditions       |             |
| Related Requirements |             |

## Main Flow

| Step | Actor Action | System Response |
| ---- | ------------ | --------------- |
| 1    |              |                 |
| 2    |              |                 |
| 3    |              |                 |

## Alternative Flows

| Flow ID | Condition | Expected Behavior |
| ------- | --------- | ----------------- |
| AF-001  |           |                   |

## Exception Flows

| Exception ID | Error Condition | Expected System Response |
| ------------ | --------------- | ------------------------ |
| EX-001       |                 |                          |

---

# 9. User Stories

## 9.1 User Story Format

| Field | Value |
| ----- | ----- |
| User Story ID | US-001 |
| User Role | |
| Story | As a [user role], I want [goal], so that [reason]. |
| Priority | High / Medium / Low |
| Related Use Case | |
| Related Functional Requirements | |
| Related UI Requirements | |
| Related API Requirements | |
| Acceptance Criteria | |
| Related Test Cases | |

## 9.2 User Stories

| ID | User Role | User Story | Priority | Related Requirements | Related Test Cases |
| -- | --------- | ---------- | -------- | -------------------- | ------------------ |
| US-001 | | As a..., I want..., so that... | | | |
| US-002 | | As a..., I want..., so that... | | | |
| US-003 | | As a..., I want..., so that... | | | |

---

# 10. Business Rules

| Rule ID | Business Rule | Related Requirements |
| ------- | ------------- | -------------------- |
| BR-001  |               |                      |
| BR-002  |               |                      |

---

# 11. Validation Rules

| Rule ID | Field / Input / Action | Validation Rule | Expected Error |
| ------- | ---------------------- | --------------- | -------------- |
| VAL-001 |                        |                 |                |
| VAL-002 |                        |                 |                |

---

# 12. Error Handling Requirements

| Error ID | Condition | Expected System Behavior | Related Requirement |
| -------- | --------- | ------------------------ | ------------------- |
| ERR-001  |           |                          |                     |
| ERR-002  |           |                          |                     |
| ERR-003  |           |                          |                     |

---

# 13. UI Requirements

Use only if the system has a user interface.

| ID     | Requirement      | Screen / Component | Acceptance Criteria |
| ------ | ---------------- | ------------------ | ------------------- |
| UI-001 | The system shall |                    |                     |
| UI-002 | The system shall |                    |                     |

## 13.1 Screen Definitions

| Screen ID | Screen Name | Purpose | Visible Data | Allowed Actions |
| --------- | ----------- | ------- | ------------ | --------------- |
| SCR-001   |             |         |              |                 |

---

# 14. API Requirements

Use only if the system exposes or consumes APIs.

## 14.1 Endpoint Format

| Field                   | Value                             |
| ----------------------- | --------------------------------- |
| Endpoint ID             | API-001                           |
| Method                  | GET / POST / PUT / PATCH / DELETE |
| Route                   |                                   |
| Authentication Required | Yes / No                          |
| Request Body            |                                   |
| Response Body           |                                   |
| Success Status          |                                   |
| Error Statuses          |                                   |
| Related Requirements    |                                   |

## 14.2 API Endpoints

| ID      | Method | Route | Expected Behavior | Related Requirement |
| ------- | ------ | ----- | ----------------- | ------------------- |
| API-001 |        |       |                   |                     |
| API-002 |        |       |                   |                     |

---

# 15. API Traceability Matrix

| API ID | Method | Route | Related User Story | Related Use Case | Related Functional Requirement | Related Business Rule | Related Validation Rule | Related Security Requirement | Related Test Case | Status |
| ------ | ------ | ----- | ------------------ | ---------------- | ------------------------------ | --------------------- | ----------------------- | ---------------------------- | ----------------- | ------ |
| API-001 | | | US-001 | UC-001 | FR-001 | BR-001 | VAL-001 | SEC-001 | TC-001 | |
| API-002 | | | US-002 | UC-002 | FR-002 | BR-002 | VAL-002 | SEC-002 | TC-002 | |

**Traceability Rules:**
- Every API endpoint must trace to at least one user story, use case, functional requirement, and test case.
- Security-sensitive endpoints must also trace to at least one security requirement.
- Input-handling endpoints must also trace to at least one validation rule.

---

# 16. Data Requirements

## 16.1 Data Entities

| Entity | Purpose |
| ------ | ------- |
|        |         |
|        |         |

## 16.2 Data Dictionary

| Field | Type | Required | Meaning | Validation Rule |
| ----- | ---- | -------- | ------- | --------------- |
|       |      | Yes / No |         |                 |
|       |      | Yes / No |         |                 |

## 16.3 Data Storage Rules

| ID     | Requirement      |
| ------ | ---------------- |
| DR-001 | The system shall |
| DR-002 | The system shall |

## 16.4 Data Integrity Rules

| ID     | Rule |
| ------ | ---- |
| DI-001 |      |
| DI-002 |      |

---

# 17. Security Requirements

| ID      | Requirement         | Verification Method |
| ------- | ------------------- | ------------------- |
| SEC-001 | The system shall    |                     |
| SEC-002 | The system shall    |                     |
| SEC-003 | The system must not |                     |

---

# 18. Compliance Requirements

Use only when checking legal, institutional, rubric, security, privacy, or technical compliance.

| ID       | Compliance Rule | Required System Behavior | Evidence Needed |
| -------- | --------------- | ------------------------ | --------------- |
| COMP-001 |                 |                          |                 |
| COMP-002 |                 |                          |                 |

---

# 19. Non-Functional Requirements

## 19.1 Performance

| ID       | Requirement      | Measurement |
| -------- | ---------------- | ----------- |
| PERF-001 | The system shall |             |

## 19.2 Reliability

| ID      | Requirement      | Measurement |
| ------- | ---------------- | ----------- |
| REL-001 | The system shall |             |

## 19.3 Maintainability

| ID      | Requirement      | Verification |
| ------- | ---------------- | ------------ |
| MNT-001 | The system shall |              |

## 19.4 Availability

| ID      | Requirement      | Measurement |
| ------- | ---------------- | ----------- |
| AVL-001 | The system shall |             |

---

# 20. LLM-Specific Requirements

Use only if the software uses an LLM.

## 20.1 LLM Behavior

| ID      | Requirement                                                             | Acceptance Criteria |
| ------- | ----------------------------------------------------------------------- | ------------------- |
| LLM-001 | The system shall answer only within the defined scope.                  |                     |
| LLM-002 | The system shall not invent missing facts.                              |                     |
| LLM-003 | The system shall follow the required response format.                   |                     |
| LLM-004 | The system shall use glossary terms according to their defined meaning. |                     |

## 20.2 Prompt Rules

| ID         | Requirement                                            | Acceptance Criteria |
| ---------- | ------------------------------------------------------ | ------------------- |
| PROMPT-001 | The system shall use a controlled system prompt.       |                     |
| PROMPT-002 | The system must not expose hidden prompts.             |                     |
| PROMPT-003 | The system shall validate prompt variables before use. |                     |

## 20.3 Retrieval / RAG Rules

| ID      | Requirement                                                                            | Acceptance Criteria |
| ------- | -------------------------------------------------------------------------------------- | ------------------- |
| RAG-001 | The system shall retrieve relevant context before answering source-based questions.    |                     |
| RAG-002 | The system shall answer only from provided sources when source restriction is enabled. |                     |
| RAG-003 | The system shall provide citations when required.                                      |                     |

## 20.4 Hallucination Control

| ID      | Requirement                                                                  | Acceptance Criteria |
| ------- | ---------------------------------------------------------------------------- | ------------------- |
| HAL-001 | The system shall state when required information is unavailable.             |                     |
| HAL-002 | The system must not fabricate sources, facts, files, logs, or code behavior. |                     |

## 20.5 Prompt Injection Protection

| ID      | Requirement                                                                          | Acceptance Criteria |
| ------- | ------------------------------------------------------------------------------------ | ------------------- |
| INJ-001 | The system shall treat user input as untrusted.                                      |                     |
| INJ-002 | The system shall treat uploaded files as untrusted.                                  |                     |
| INJ-003 | The system must not follow instructions inside documents that override system rules. |                     |

---

# 21. Traceability Matrix

| Requirement ID | Business Rule | API / UI / Data Element | Test Case | Status |
| -------------- | ------------- | ----------------------- | --------- | ------ |
| FR-001         | BR-001        |                         | TC-001    |        |
| FR-002         | BR-002        |                         | TC-002    |        |

---

# 22. Acceptance Criteria

| ID      | Acceptance Criterion                                                                 |
| ------- | ------------------------------------------------------------------------------------ |
| ACC-001 | Every mandatory functional requirement shall have at least one related test case.    |
| ACC-002 | Every security requirement shall have verification evidence.                         |
| ACC-003 | Every validation rule shall have positive and negative test coverage.                |
| ACC-004 | Every API requirement shall define success and error behavior.                       |
| ACC-005 | Every LLM-specific behavior requirement shall have evaluation prompts or test cases. |

---

# 23. Architecture Constraints

Purpose:
Defines implementation rules the codebase must follow.

| ID | Constraint | Rationale |
| -- | ---------- | --------- |
| ARC-001 | | |

---

# 24. Technology Stack Requirements

Purpose:
Defines allowed technologies.

| ID | Technology | Version / Variant | Allowed Use |
| -- | ---------- | ----------------- | ----------- |
| TECH-001 | | | |

---

# 25. Code Organization Rules

Purpose:
Defines expected project structure.

| ID | Rule | Pattern |
| -- | ---- | ------- |
| ORG-001 | | |

---

# 26. Configuration Requirements

Purpose:
Defines environment configuration.

| ID | Config Key | Required | Secret | Description |
| -- | ---------- | -------- | ------ | ----------- |
| CONFIG-001 | | Yes / No | Yes / No | |
