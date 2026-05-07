# QA Protocol

Universal quality assurance protocol for all tasks. No task is complete until the relevant checks below have been performed and documented.

## Functional Testing

### Buttons and Interactive Elements
- Every button on affected pages must be clicked and must produce the expected result.
- Disabled buttons must show a clear reason or be visually distinct.
- Submit buttons must handle double-click, rapid-click, and click-while-loading.

### Forms
- Required fields must be enforced with clear validation messages.
- Optional fields must not block submission.
- Form state must survive input errors without clearing valid fields.
- Email, number, and date inputs must reject obviously invalid values.

### Routes
- Every route affected by the task must be visitable without errors.
- Dynamic routes must handle missing or invalid parameters gracefully.
- Navigation between pages must not produce console errors or blank screens.

### Responsive Testing
- Mobile (375px): layout must not overflow, text must be readable, buttons must be tappable.
- Tablet (768px): layout must adapt, not just shrink.
- Desktop (1280px+): layout must use available space, not just center a narrow column.

## Technical Testing

### Console and Network
- Browser console must show zero errors on every affected page.
- Network tab must show no failed requests during normal flow.
- CORS errors are blockers.

### API Routes
- Every API route affected by the task must return correct status codes.
- Invalid input must return 400, not 500.
- Missing resources must return 404, not crash.
- Successful operations must return the expected payload.

### Database Persistence
- Inserts must produce verifiable rows in the correct table.
- Updates must modify only the intended fields.
- Storage uploads must produce verifiable files in the correct bucket.
- Foreign key relationships must be correct.

### Auth and Sessions
- When auth is implemented: protected routes must redirect unauthenticated users.
- Session state must survive page refresh.
- When auth is not implemented: document which routes will need protection later.

## State Testing

### Empty States
- Pages must render correctly with zero data.
- Lists with no items must show a designed empty state, not a blank area.

### Error States
- Failed API calls must show user-facing error messages.
- Network failures must not produce white screens.
- Invalid URLs must show 404 pages, not crashes.

### Loading States
- Async operations must show loading indicators.
- Loading must not flash for instant operations.
- Polling must show progress, not just a spinner.

## Regression Testing

- Existing pages not modified by the task must still work.
- Build, typecheck, and lint must pass after every task.
- Previously working flows must not break.

## Evidence Requirements

Every completed task must include:
- List of pages visited and verified.
- Screenshot or description of key states tested.
- Build/typecheck/lint command output.
- Any console errors observed (even if not caused by this task).
- Explicit confirmation of each acceptance criterion.

## QA Verdicts

- **PASS**: All checks passed, all acceptance criteria met.
- **FAIL_FIX_REQUIRED**: One or more checks failed. Specific fixes are listed.
- **RESEARCH_REQUIRED**: A question cannot be answered without research. Scope and time estimate must be provided.
- **HUMAN_DECISION_REQUIRED**: A product, design, or business decision is needed.
- **BLOCKED**: An external dependency, missing credential, or unresolved blocker prevents progress.

## Risk Levels

- **low**: Cosmetic or minor behavioral issue. Does not affect core functionality.
- **medium**: Functional issue that affects a secondary flow or edge case.
- **high**: Functional issue that affects a primary flow or data integrity.
- **critical**: Data loss, security exposure, crash on primary flow, or regression in shipped functionality.
