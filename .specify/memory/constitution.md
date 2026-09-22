<!--
Sync Impact Report
- Version change: 1.1.0 -> 2.0.0
- Modified principles: III. End-to-End Traceability (scope redefined by data used in processing)
- Added sections: none
- Removed sections: none
- Follow-up TODOs: none
-->
# Repository Miner Constitution

## Core Principles

### I. Architectural Simplicity
The system MUST use the simplest architecture that satisfies current, evidenced requirements.
Microservices, queues, distributed processing, and additional infrastructure MUST NOT be
introduced without a documented concrete need and an explicit review of their operational cost.
This keeps delivery and operation proportional to the problem being solved.

### II. Credential Security and Incident Response
GitLab tokens, AI-provider API keys, and other secrets MUST NOT appear in source code, logs,
reports, fixtures, error messages, or generated artifacts. Secrets MUST be supplied through an
approved external configuration mechanism, and diagnostic output MUST redact sensitive values.

When exposure of a credential is suspected, the system MUST mark the credential as compromised,
MUST prevent its use in new operations, and MUST create an auditable incident record without
recording the secret value. The operator MUST be informed that the credential needs to be
invalidated or rotated at its external provider. The system MUST allow the compromised credential
to be replaced and MUST record that replacement in an auditable form without retaining or
revealing plaintext values.

Automatic invalidation or rotation at an external provider is NOT REQUIRED because provider
capabilities vary. This limitation MUST NOT permit continued use of a credential marked as
compromised inside Repository Miner.

### III. End-to-End Traceability
Every mining result MUST be traceable through every level of information that participated in the
process that produced it. Traceability requirements MUST be proportional to the data actually used
and MUST NOT cause collection of additional data solely to satisfy provenance.

For results produced exclusively from commit metadata, including identification of commits made by
unauthorized users, the result MUST identify the configuration, execution, repository, branch,
commit hash, author, author e-mail, and commit date. This metadata MUST allow a reviewer to locate
the originating commit and reproduce the rule evaluation.

Related-file information MUST be retained when, and only when, the responsible functionality
analyzes or otherwise uses files, diffs, or source content to produce the result. Any transformation
or analysis MUST preserve identifiers for all input levels it actually consumed. A result missing
required provenance from its own processing inputs is incomplete and MUST NOT be presented as
actionable.

### IV. Incremental Mining
Recurring runs MUST persist and consult processing state so that commits already analyzed under
the same relevant analysis configuration are not processed again. Reprocessing MUST occur only
when explicitly requested or when a documented change invalidates the prior result. State
updates MUST happen only after the corresponding unit of work reaches a known terminal state.

### V. Integration Isolation
GitLab access and AI-provider access MUST remain behind explicit interfaces or adapters and MUST
NOT be embedded in domain rules. The mining and analysis domain MUST depend on abstractions that
express required capabilities rather than vendor-specific clients. Provider replacement or
testing with a fake implementation MUST NOT require changes to business rules.

### VI. Probabilistic AI Findings
Semantic analysis output MUST be represented and communicated as a possible risk, never as
definitive proof of a bug or vulnerability. Reports MUST distinguish model-generated assessment
from source evidence and MUST preserve enough context for human review. Automated decisions with
material impact MUST NOT rely solely on an AI finding.

### VII. Testability Without External Services
Mining and analysis rules MUST be testable without live connections to GitLab or AI providers.
External interactions MUST be replaceable by fakes, stubs, or contract-controlled test doubles.
Tests MUST cover success, malformed responses, rate limits, timeouts, and partial failures where
those cases affect domain behavior.

### VIII. Failure Isolation
A failure while processing one repository or commit MUST be contained whenever continued
processing is safe. The execution MUST record the failed unit and reason, continue with
independent units, and produce a final status that reflects partial failure. Global termination
is permitted only when a shared prerequisite makes further work invalid or unsafe.

### IX. Code Privacy and Data Minimization
Only information necessary for the requested analysis MUST be sent to an AI provider. The system
MUST minimize code excerpts and metadata, exclude secrets and unrelated content, and make the
outbound payload auditable without logging sensitive code. New AI use cases MUST document the
data sent, its purpose, and the applicable retention assumptions.

### X. Execution Observability
Every execution MUST record its start, end, final state, repositories processed, commits
analyzed, failures, and findings. Events MUST use stable correlation identifiers and sufficient
structure for operational diagnosis while complying with credential security and code privacy.
Counts and terminal status MUST remain consistent even when work completes partially.

## Engineering Constraints

- Architectural additions beyond the current simple design MUST include the concrete requirement,
  rejected simpler option, operational impact, and removal or migration implications.
- Integration boundaries MUST expose provider-neutral contracts and translate vendor-specific
  failures into application-level outcomes.
- Persistent incremental state MUST be scoped at least by repository and commit and MUST preserve
  enough configuration identity to determine whether a prior analysis remains reusable.
- Logs and reports MUST apply data minimization: operational metadata is recorded, while secrets
  and unnecessary source content are excluded or redacted.
- AI prompts and payload builders MUST be reviewable as privacy-sensitive integration code.

## Delivery and Review Gates

- Every specification and implementation plan MUST identify affected principles and explain any
  necessary complexity.
- Code review MUST verify traceability fields, incremental-processing behavior, failure isolation,
  secret redaction, and AI data minimization when those concerns are affected.
- Automated tests MUST exercise domain rules through integration abstractions without requiring
  external credentials or network access.
- Integration contract tests MAY use controlled provider environments, but MUST remain separate
  from the deterministic domain test suite.
- Before release, an execution-level verification MUST confirm observable lifecycle events and
  accurate summary counts for successful, failed, and partially successful runs.
- Any exception to a principle MUST be documented with scope, owner, rationale, mitigation, and an
  expiration or review date before the exception is accepted.

## Governance

This constitution is the highest-priority engineering policy for Repository Miner. Specifications,
plans, tasks, reviews, and implementation decisions MUST comply with it. When another project
document conflicts with this constitution, this constitution governs until it is amended.

Amendments MUST be proposed as an explicit documentation change that states the rationale,
affected principles, compatibility impact, and required migration work. Approval requires project
maintainer review and confirmation that dependent specifications, plans, and operational guidance
remain consistent. The amendment date and version MUST be updated when approved.

Versions follow semantic versioning for governance: MAJOR for removal or incompatible redefinition
of a principle; MINOR for a new principle or materially expanded obligation; PATCH for clarification
that does not change obligations. The Sync Impact Report accompanying an amendment MUST explain the
selected increment.

Constitution compliance MUST be reviewed during specification, planning, and code review. Reviewers
MUST reject unexplained violations. Approved exceptions MUST satisfy the documentation and expiry
requirements in Delivery and Review Gates, and recurring exceptions MUST trigger consideration of a
formal amendment.

**Version**: 2.0.0 | **Ratified**: 2026-09-18 | **Last Amended**: 2026-09-19
