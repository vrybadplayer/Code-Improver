## Context
See proposal.md - Why for motivation. The application currently does not have a dark mode toggle. The UI layer and theme provider need to be updated to support theme switching.

## Goals / Non-Goals
**Goals:**
- Provide a user-accessible toggle to switch between light and dark themes.
- Persist the user's theme preference across sessions.
- Respect the system's theme preference when no user preference is set.

**Non-Goals:**
- Changing the overall visual design beyond the color scheme.
- Supporting multiple themes beyond light and dark.
- Implementing automatic theme switching based on time of day.

## Decisions
### Theme Storage
**Decision:** Use browser localStorage to persist theme preference.
**Rationale:** Simple, client-side, no server dependency. Alternatives considered: cookies (sent with every request), server-side database (requires backend). LocalStorage is sufficient for this use case.

### Theme Application
**Decision:** Use a CSS class on the root element (e.g., `data-theme="dark"` or `data-theme="light"`).
**Rationale:** Allows easy scoping of theme-specific styles. Alternatives: inline styles (harder to maintain), multiple stylesheets (more network requests).

### Toggle Component
**Decision:** Create a reusable toggle switch component in the settings menu.
**Rationale:** Promotes reusability and consistency. Alternative: a simple checkbox, but a toggle provides better affordance for on/off states.

## Risks / Trade-offs
[Risk of flash of incorrect theme] → Mitigation: Read theme preference early in application load and apply before first paint.
[Risk of accessibility issues] → Mitigation: Ensure toggle has proper ARIA labels and keyboard support.
[Risk of increased bundle size] → Mitigation: Keep toggle component lightweight and lazy-load if necessary.