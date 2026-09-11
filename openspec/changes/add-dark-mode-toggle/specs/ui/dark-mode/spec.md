## Purpose
Allows users to switch between light and dark themes via a toggle, reducing eye strain and respecting system preferences.

## ADDED Requirements
### Requirement: Dark mode toggle
The system SHALL provide a toggle switch in the settings menu to enable or disable dark mode.

#### Scenario: User enables dark mode
- **WHEN** user toggles the dark mode switch to ON
- **THEN** the application applies the dark theme to all components

#### Scenario: User disables dark mode
- **WHEN** user toggles the dark mode switch to OFF
- **THEN** the application applies the light theme to all components

### Requirement: Theme persistence
The system SHALL persist the user's theme preference across sessions.

#### Scenario: Theme preference saved
- **WHEN** user sets dark mode preference
- **AND** user closes and reopens the application
- **THEN** the application restores the previously selected theme

### Requirement: System preference fallback
The system SHALL respect the operating system's theme preference when no user preference is set.

#### Scenario: System preference used
- **WHEN** user has not set a theme preference
- **AND** the operating system theme is dark
- **THEN** the application starts in dark mode
- **WHEN** user has not set a theme preference
- **AND** the operating system theme is light
- **THEN** the application starts in light mode