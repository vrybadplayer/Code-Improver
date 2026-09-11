## 1. Setup

- [ ] 1.1 Create theme utility file and verify file exists
- [ ] 1.2 Add theme constants (light, dark) and verify they are exported correctly

## 2. Theme Storage Implementation

- [ ] 2.1 Implement function to get theme preference from localStorage and verify it returns null when not set
- [ ] 2.2 Implement function to save theme preference to localStorage and verify it persists after page reload
- [ ] 2.3 Implement function to apply theme based on preference and verify it sets the correct data-theme attribute

## 3. Theme Application Implementation

- [ ] 3.1 Create theme provider component that reads preference and applies theme and verify it applies correct theme on render
- [ ] 3.2 Ensure theme provider respects system preference when no user preference is set and verify it matches OS theme
- [ ] 3.3 Add early theme application to prevent flash of incorrect theme and verify no flash occurs on initial load

## 4. Toggle Component Implementation

- [ ] 4.1 Create reusable toggle switch component with proper ARIA labels and keyboard support and verify it is accessible
- [ ] 4.2 Connect toggle to theme provider so that toggling updates the theme and verify theme changes when toggle is used
- [ ] 4.3 Ensure toggle reflects current theme state and verify toggle position matches applied theme

## 5. Integration and Testing

- [ ] 5.1 Add toggle to settings menu and verify it appears in the correct location
- [ ] 5.2 Test theme persistence across sessions by toggling, refreshing, and verifying theme persists
- [ ] 5.3 Test system preference fallback by clearing user preference and changing OS theme (simulate) and verify application follows OS theme