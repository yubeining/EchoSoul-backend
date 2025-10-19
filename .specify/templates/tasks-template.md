# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 3.1: Setup
- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize [language] project with [framework] dependencies
- [ ] T003 [P] Configure linting and formatting tools

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
**CONSTITUTION COMPLIANCE: TDD is NON-NEGOTIABLE per EchoSoul AI Platform Constitution**
- [ ] T004 [P] Contract test POST /api/users in tests/contract/test_users_post.py
- [ ] T005 [P] Contract test GET /api/users/{id} in tests/contract/test_users_get.py
- [ ] T006 [P] Integration test user registration in tests/integration/test_registration.py
- [ ] T007 [P] Integration test auth flow in tests/integration/test_auth.py
- [ ] T008 [P] Security test authentication in tests/security/test_auth_security.py
- [ ] T009 [P] Performance test API response time in tests/performance/test_api_performance.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T010 [P] User model in src/models/user.py
- [ ] T011 [P] UserService CRUD in src/services/user_service.py
- [ ] T012 [P] CLI --create-user in src/cli/user_commands.py
- [ ] T013 POST /api/users endpoint
- [ ] T014 GET /api/users/{id} endpoint
- [ ] T015 Input validation and sanitization
- [ ] T016 Error handling and structured logging
- [ ] T017 JWT authentication implementation
- [ ] T018 Password encryption with bcrypt

## Phase 3.4: Integration
- [ ] T019 Connect UserService to MySQL database
- [ ] T020 Redis caching implementation
- [ ] T021 Auth middleware with JWT validation
- [ ] T022 Request/response structured logging
- [ ] T023 CORS and security headers
- [ ] T024 Health check endpoints
- [ ] T025 Database connection pooling

## Phase 3.5: Polish
- [ ] T026 [P] Unit tests for validation in tests/unit/test_validation.py
- [ ] T027 Performance tests (<200ms P95)
- [ ] T028 [P] Update OpenAPI documentation
- [ ] T029 Remove code duplication
- [ ] T030 Run manual testing scenarios
- [ ] T031 Security audit and vulnerability scan
- [ ] T032 Monitoring and observability setup

## Dependencies
- Tests (T004-T009) before implementation (T010-T018)
- T010 blocks T011, T019
- T017 blocks T021
- Implementation before integration (T019-T025)
- Integration before polish (T026-T032)

## Parallel Example
```
# Launch T004-T009 together (TDD tests):
Task: "Contract test POST /api/users in tests/contract/test_users_post.py"
Task: "Contract test GET /api/users/{id} in tests/contract/test_users_get.py"
Task: "Integration test registration in tests/integration/test_registration.py"
Task: "Integration test auth in tests/integration/test_auth.py"
Task: "Security test authentication in tests/security/test_auth_security.py"
Task: "Performance test API response time in tests/performance/test_api_performance.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts
- **CONSTITUTION COMPLIANCE**: All tasks must follow EchoSoul AI Platform Constitution principles
- **SECURITY**: All authentication and authorization tasks are mandatory
- **PERFORMANCE**: All API endpoints must meet <200ms P95 response time requirement

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - Each contract file → contract test task [P]
   - Each endpoint → implementation task
   
2. **From Data Model**:
   - Each entity → model creation task [P]
   - Relationships → service layer tasks
   
3. **From User Stories**:
   - Each story → integration test [P]
   - Quickstart scenarios → validation tasks

4. **Ordering**:
   - Setup → Tests → Models → Services → Endpoints → Polish
   - Dependencies block parallel execution

## Validation Checklist
*GATE: Checked by main() before returning*

- [ ] All contracts have corresponding tests
- [ ] All entities have model tasks
- [ ] All tests come before implementation
- [ ] Parallel tasks truly independent
- [ ] Each task specifies exact file path
- [ ] No task modifies same file as another [P] task