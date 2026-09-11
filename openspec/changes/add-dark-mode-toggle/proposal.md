## Why

Users want a dark mode toggle to reduce eye strain in low-light conditions and to follow system preferences. Providing a toggle allows users to switch between light and dark themes based on their preference or system settings.

## What Changes

- Add a toggle switch in the settings menu to enable/disable dark mode.
- Implement a theme provider that applies the selected theme (light or dark) to the application.
- Persist the user's theme preference (e.g., in local storage or a settings database).

## Capabilities

### New Capabilities
- `ui/dark-mode`: Manages the dark mode state and applies the appropriate styles.

### Modified Capabilities
*(No existing capabilities are being modified; this change introduces a new capability.)*

## Impact

- The UI layer, specifically the settings component and the theme provider.
- Any component that uses the theme provider for styling.
- Persistence layer for storing user preferences.