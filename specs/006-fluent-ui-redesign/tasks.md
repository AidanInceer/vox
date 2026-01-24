# Tasks: Fluent UI Redesign for Windows 11

**Branch**: `006-fluent-ui-redesign`
**Generated**: January 24, 2026
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Phase 1: Setup

**Purpose**: Initialize project structure and create component file skeletons

- [x] T001 Create component file skeleton src/ui/components/card.py with FluentCard class stub
- [x] T002 [P] Create component file skeleton src/ui/components/model_slider.py with ModelSlider class stub
- [x] T003 [P] Create component file skeleton src/ui/components/theme_toggle.py with ThemeToggle class stub
- [x] T004 [P] Create component file skeleton src/ui/components/speed_slider.py with SpeedSlider class stub
- [x] T005 [P] Create component file skeleton src/ui/components/keycap.py with KeyCapLabel class stub
- [x] T006 [P] Create component file skeleton src/ui/components/history_item.py with HistoryItemCard class stub
- [x] T007 [P] Create component file skeleton src/ui/components/empty_state.py with EmptyState class stub
- [x] T008 Update src/ui/components/**init**.py to export new components

**Checkpoint**: All component files exist with class stubs, imports work

---

## Phase 2: Foundational - Styles and Theme Infrastructure

**Purpose**: Core styling infrastructure that all user stories depend on (BLOCKS all user stories)

- [x] T009 Add SPACING dict with 8px grid values (xs:4, sm:8, md:16, lg:24, xl:32, xxl:48) to src/ui/styles.py
- [x] T010 [P] Add FONTS dict with Fluent type scale (display, title, subtitle, body, caption, mono) to src/ui/styles.py
- [x] T011 [P] Add ICONS dict with Unicode symbols (status, settings, history, record, etc.) to src/ui/styles.py
- [x] T012 [P] Add COLORS_LIGHT and COLORS_DARK dicts with Fluent color tokens to src/ui/styles.py
- [x] T013 Add THEMES dict mapping "light" to "cosmo" and "dark" to "darkly" in src/ui/styles.py
- [x] T014 Implement switch_theme(root, theme) function to change theme at runtime in src/ui/styles.py
- [x] T015 Implement configure_fluent_overrides(style, theme) for custom tab and button styling in src/ui/styles.py
- [x] T016 Replace current PADDING usages with SPACING throughout src/ui/styles.py

**Checkpoint**: Theme switching works, style constants are defined, tests pass

---

## Phase 3: User Story 1 - Modern First Impression (Priority: P1)

**Goal**: Deliver a native Windows 11 look with immediate visual impact on launch

**Independent Test**: Launch app, visually compare against Windows 11 Settings app for consistent feel

### Implementation for User Story 1

- [x] T017 [US1] Implement FluentCard with Canvas shadow simulation in src/ui/components/card.py
- [x] T018 [P] [US1] Add FluentCard tests for shadow offset and theme-aware styling in tests/unit/test_ui_components.py
- [x] T019 [US1] Update Status tab to use FluentCard containers instead of LabelFrame in src/ui/main_window.py
- [x] T020 [US1] Update Settings tab to use FluentCard containers in src/ui/main_window.py
- [x] T021 [US1] Update History tab to use FluentCard containers in src/ui/main_window.py
- [x] T022 [US1] Add tab icons (🏠 Status, ⚙️ Settings, 📋 History) to Notebook tabs in src/ui/main_window.py
- [x] T023 [US1] Configure Fluent-style tab styling (rounded pill selection indicator) in src/ui/styles.py
- [x] T024 [US1] Apply FONTS type scale to all text elements across tabs in src/ui/main_window.py
- [x] T025 [US1] Add theme initialization on app startup (load from database) in src/ui/main_window.py

**Checkpoint**: App launches with elevated cards, styled tabs with icons, consistent typography

---

## Phase 4: User Story 2 - Clear Visual Hierarchy (Priority: P1)

**Goal**: Primary actions (Record button) are immediately identifiable, secondary elements subordinated

**Independent Test**: Show app to new user, time how long to identify Record action (target: <2 seconds)

### Implementation for User Story 2

- [x] T026 [US2] Style Record button as focal point with primary accent color and larger size in src/ui/main_window.py
- [x] T027 [P] [US2] Implement KeyCapLabel component with visual key cap styling in src/ui/components/keycap.py
- [x] T028 [US2] Replace plain hotkey text with KeyCapLabel in Status tab in src/ui/main_window.py
- [x] T029 [US2] Implement pill-style status indicator (Recording/Ready) with icon in src/ui/main_window.py
- [x] T030 [US2] Add visual grouping with clear section boundaries using FluentCard titles in src/ui/main_window.py
- [x] T031 [US2] Apply subtitle font styling to card headers, caption styling to helper text in src/ui/main_window.py

**Checkpoint**: Record button stands out, hotkey displays as key caps, status is prominent pill badge

---

## Phase 5: User Story 3 - Centered and Balanced Layout (Priority: P2)

**Goal**: Content is properly centered, elements aligned on consistent grid

**Independent Test**: Take screenshots, apply grid overlay to verify 8px alignment

### Implementation for User Story 3

- [x] T032 [US3] Center Status tab content horizontally within content area in src/ui/main_window.py
- [x] T033 [US3] Apply SPACING constants to all padding and margins in Status tab in src/ui/main_window.py
- [x] T034 [P] [US3] Apply SPACING constants to Settings tab layout in src/ui/main_window.py
- [x] T035 [P] [US3] Apply SPACING constants to History tab layout in src/ui/main_window.py
- [x] T036 [US3] Align form controls (labels + inputs) on consistent vertical grid in Settings tab in src/ui/main_window.py
- [x] T037 [US3] Ensure consistent button sizing and spacing across all tabs in src/ui/main_window.py

**Checkpoint**: All content centered, elements aligned to 8px grid, balanced visual weight

---

## Phase 6: User Story 4 - Fluent Navigation Experience (Priority: P2)

**Goal**: Tab navigation feels native to Windows 11 with proper hover/selection feedback

**Independent Test**: Navigate between tabs using mouse and keyboard, verify visual feedback

### Implementation for User Story 4

- [x] T038 [US4] Add hover state styling for tab items (rounded highlight) in src/ui/styles.py
- [x] T039 [US4] Add pressed state styling for tab items in src/ui/styles.py
- [x] T040 [US4] Add focus indicator styling for keyboard navigation on tabs in src/ui/styles.py
- [x] T041 [US4] Test tab keyboard navigation (Tab/Arrow keys) works correctly in src/ui/main_window.py
- [x] T042 [US4] Add smooth transition effect for tab selection indicator in src/ui/styles.py

**Checkpoint**: Tabs have hover, pressed, selected, and focus states all visually distinct

---

## Phase 7: User Story 5 - Accessible Color and Contrast (Priority: P2)

**Goal**: WCAG AA compliance, status indicators use icon+text (not color alone)

**Independent Test**: Run contrast checker on all text/background combinations (target: 4.5:1 minimum)

### Implementation for User Story 5

- [x] T043 [US5] Verify all text/background combinations meet 4.5:1 contrast ratio in src/ui/styles.py
- [x] T044 [P] [US5] Update status indicators to use both icon AND text (not color alone) in src/ui/main_window.py
- [x] T045 [P] [US5] Add focus ring styling for all interactive elements (buttons, sliders) in src/ui/styles.py
- [x] T046 [US5] Test keyboard-only navigation through all interactive elements in src/ui/main_window.py
- [x] T047 [US5] Verify disabled states are visually distinguishable in src/ui/styles.py

**Checkpoint**: Contrast passes WCAG AA, all states distinguishable, keyboard navigation complete

---

## Phase 8: User Story 6 - Consistent Typography (Priority: P3)

**Goal**: Only defined type scale used, clear heading/body hierarchy throughout

**Independent Test**: Catalog all font usages, verify against FONTS dict (no arbitrary sizes)

### Implementation for User Story 6

- [x] T048 [US6] Audit all text elements for FONTS dict compliance in src/ui/main_window.py
- [x] T049 [P] [US6] Replace any arbitrary font sizes with FONTS constants in src/ui/main_window.py
- [x] T050 [US6] Verify monospace font (Cascadia Code) used for hotkey displays in src/ui/main_window.py
- [x] T051 [US6] Add unit tests for typography consistency in tests/unit/test_ui_styles.py

**Checkpoint**: All text uses defined type scale, no arbitrary font sizes, tests pass

---

## Phase 9: Model & Voice Settings Feature

**Goal**: Add STT model slider and TTS speed controls to Settings tab

**Independent Test**: Change model/speed, restart app, verify settings persisted

### Implementation for Model & Voice Settings

- [x] T052 Implement ModelSlider component with 7-position discrete scale in src/ui/components/model_slider.py
- [x] T053 [P] Add ModelSlider unit tests for value mapping (slider position to model name) in tests/unit/test_ui_components.py
- [x] T054 Implement SpeedSlider component with 0.5-2.0 range in src/ui/components/speed_slider.py
- [x] T055 [P] Add SpeedSlider unit tests for value range and step validation in tests/unit/test_ui_components.py
- [x] T056 Implement ThemeToggle component (light/dark switch) in src/ui/components/theme_toggle.py
- [x] T057 [P] Add ThemeToggle unit tests in tests/unit/test_ui_components.py
- [x] T058 Add "Model & Voice" FluentCard to Settings tab in src/ui/main_window.py
- [x] T059 Integrate ModelSlider with config.set_stt_default_model() in src/ui/main_window.py
- [x] T060 Integrate SpeedSlider with config save (TTS speed setting) in src/ui/main_window.py
- [x] T061 Add "Appearance" FluentCard with ThemeToggle to Settings tab in src/ui/main_window.py
- [x] T062 Implement debounced auto-save (500ms delay) for slider changes in src/ui/main_window.py
- [x] T063 Add visual save confirmation (brief toast/flash) on settings change in src/ui/main_window.py
- [x] T064 Remove explicit Save button from Settings tab in src/ui/main_window.py

**Checkpoint**: Model & Voice card works, theme toggle works, settings auto-save with visual feedback

---

## Phase 10: History Tab Enhancements

**Goal**: Modern history item cards with hover-reveal actions

**Independent Test**: Hover over history items, verify Copy/Delete buttons appear

### Implementation for History Tab

- [x] T065 Implement EmptyState component with icon, message, and description in src/ui/components/empty_state.py
- [x] T066 [P] Add EmptyState unit tests in tests/unit/test_ui_components.py
- [x] T067 Implement HistoryItemCard with hover-reveal actions in src/ui/components/history_item.py
- [x] T068 [P] Add HistoryItemCard unit tests for hover state and callbacks in tests/unit/test_ui_components.py
- [x] T069 Replace current history list with HistoryItemCard components in src/ui/main_window.py
- [x] T070 Add EmptyState to History tab when no items exist in src/ui/main_window.py
- [x] T071 Ensure consistent item height in history list in src/ui/main_window.py

**Checkpoint**: History items have hover-reveal actions, empty state displays when no history

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, cleanup, and documentation updates

- [x] T072 [P] Update src/ui/**init**.py to export all new components
- [x] T073 [P] Add theme persistence integration test in tests/integration/test_app_lifecycle.py
- [x] T074 Run full test suite and verify >80% coverage
- [x] T075 [P] Update src/ui/indicator.py colors to use COLORS dict for theme consistency
- [x] T076 Test window resize behavior (400px to 1920px) for no element overlap
- [x] T077 Test high DPI scaling (100% to 200%) for no layout breakage
- [x] T078 Run quickstart.md validation to verify all test scenarios pass
- [x] T079 [P] Update CHANGELOG.md with feature summary

**Checkpoint**: All tests pass, coverage maintained, resize/DPI scenarios validated

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 - implement first
  - US3, US4, US5 are P2 - implement after P1 stories
  - US6 is P3 - implement last
- **Model & Voice (Phase 9)**: Depends on Foundational - can run in parallel with P2 stories
- **History Tab (Phase 10)**: Depends on Foundational and FluentCard from US1
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Foundation for all card usage
- **User Story 2 (P1)**: Can start after Foundational - May use FluentCard from US1 but core work is independent
- **User Story 3 (P2)**: Can start after Foundational - Independent layout work
- **User Story 4 (P2)**: Can start after Foundational - Tab styling independent of content
- **User Story 5 (P2)**: Can start after Foundational - Accessibility can be verified in parallel
- **User Story 6 (P3)**: Can start after Foundational - Typography audit independent of other stories

### Within Each User Story

- Core component implementation before integration
- Style changes before main_window integration
- Tests should pass after each story completion

### Parallel Opportunities

- All Setup tasks T002-T007 marked [P] can run in parallel
- Foundational tasks T010-T012 marked [P] can run in parallel
- Model & Voice components (T052-T057) can run in parallel with P2 stories
- History components (T065-T068) can run in parallel with other Phase 10 tasks
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: Setup Phase

```text
# Launch all component skeleton tasks together:
Task: T001 - FluentCard skeleton (base for others)
Task: T002 [P] - ModelSlider skeleton
Task: T003 [P] - ThemeToggle skeleton
Task: T004 [P] - SpeedSlider skeleton
Task: T005 [P] - KeyCapLabel skeleton
Task: T006 [P] - HistoryItemCard skeleton
Task: T007 [P] - EmptyState skeleton
```

## Parallel Example: Model & Voice Phase

```text
# Launch component implementations in parallel:
Task: T052 - ModelSlider implementation
Task: T053 [P] - ModelSlider tests
Task: T054 - SpeedSlider implementation
Task: T055 [P] - SpeedSlider tests
Task: T056 - ThemeToggle implementation
Task: T057 [P] - ThemeToggle tests
```

---

## Implementation Strategy

### MVP First (User Stories 1-2 Only)

1. Complete Phase 1: Setup (component skeletons)
2. Complete Phase 2: Foundational (styles, theme switching)
3. Complete Phase 3: User Story 1 (FluentCard, styled tabs, typography)
4. Complete Phase 4: User Story 2 (Record button focal point, KeyCapLabel)
5. **STOP and VALIDATE**: App looks modern, primary actions are clear
6. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 + 2 → Modern look achieved → Deploy/Demo (MVP!)
3. Add User Story 3-5 → Polished layout and accessibility → Deploy/Demo
4. Add User Story 6 → Typography consistency → Deploy/Demo
5. Add Model & Voice + History → Full feature set → Final Release

### Recommended Sequence

For a single developer:

1. Phase 1 → Phase 2 (Foundation)
2. Phase 3 → Phase 4 (P1 MVP)
3. Phase 9 (Model & Voice - user's specific request)
4. Phase 5 → Phase 6 → Phase 7 (P2 polish)
5. Phase 10 (History enhancements)
6. Phase 8 (P3 typography)
7. Phase 11 (Final polish)

---

## Notes

- [P] tasks = different files, no dependencies
- [US#] label maps task to specific user story for traceability
- FluentCard (T017) is foundational for many tabs - complete early
- Theme switching (T014) is foundational - complete before UI work
- Auto-save debounce (T062) prevents excessive writes during slider drag
- Verify tests fail before implementing (if TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
