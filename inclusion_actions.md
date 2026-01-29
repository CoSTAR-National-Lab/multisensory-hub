# Inclusion Actions

Sequential tasks to improve accessibility across the Multisensory Hub site. Each action is self-contained. Run them in order — later tasks may depend on patterns established by earlier ones.

---

## Action 1: Add skip-to-content link [COMPLETED]

**File:** `docusaurus-site/src/css/custom.css` and `docusaurus-site/src/theme/Root.js` (create if missing, or use the Docusaurus swizzle pattern for `Root`).

Add a visually hidden skip link as the first focusable element on every page. It should:

- Be positioned offscreen by default using a `.sr-only` utility class
- Become visible on `:focus` (positioned at top-left, high z-index, solid background)
- Link to `#__docusaurus_skipToContent_fallback` (the ID Docusaurus places on its main content wrapper)
- Have text "Skip to main content"

Also add a reusable `.sr-only` utility class to `custom.css` for use in later actions:

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

---

## Action 2: Add prefers-reduced-motion support [COMPLETED]

**File:** `docusaurus-site/src/css/custom.css`

Add a media query at the end of the file that disables all non-essential animation and transition for users who request reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

This covers `fadeInUp`, `bounce`, `spin`, `float`, and any future animations without needing per-component changes.

---

## Action 3: Make RefPopup keyboard-accessible [COMPLETED]

**File:** `docusaurus-site/src/components/RefPopup.tsx`

Currently the popup only appears on `onMouseEnter`/`onMouseLeave`. Change it so that:

- The trigger element also responds to `onFocus` (show popup) and `onBlur` (hide popup). Use a short `setTimeout` on blur (~150ms) to allow focus to move into the popup itself without it closing.
- Add `tabIndex={0}` if the trigger is not already a focusable element.
- Add `role="button"` and `aria-describedby={popupId}` on the trigger, where `popupId` is a unique ID placed on the popup container.
- Add `role="tooltip"` and the matching `id={popupId}` on the popup container.
- Generate `popupId` from the ref number, e.g. `ref-popup-{refNum}`.
- Ensure the popup does not trap focus — it should close on Escape keypress (`onKeyDown` handler on the trigger).
- Do not remove the existing mouse handlers.

---

## Action 4: Make RefTooltip keyboard-accessible [COMPLETED]

**File:** `docusaurus-site/src/components/RefTooltip.tsx`

Apply the same pattern as Action 3:

- Add `onFocus`/`onBlur` with delayed blur to the trigger element.
- Add `role="tooltip"`, a unique `id`, and `aria-describedby` linking trigger to tooltip.
- Add Escape key handler to close.
- Preserve existing mouse behaviour.

---

## Action 5: Fix CollapsibleSection keyboard support [COMPLETED]

**File:** `docusaurus-site/src/components/interactive/CollapsibleSection.tsx`

The component already uses a `<button>` with `aria-expanded`. Add:

- `aria-controls={panelId}` on the button, where `panelId` is a unique ID.
- `id={panelId}` and `role="region"` on the collapsible content container.
- Generate `panelId` from the section title slug or a counter, e.g. `collapsible-panel-{index}`.
- Verify the `<button>` natively handles Enter/Space (it should if it's a real `<button>` element — if it's a `<div>` with `onClick`, change it to `<button>`).
- Add `aria-label` on the button if the button text alone is not descriptive (e.g. if it only shows a chevron icon).

---

## Action 6: Make Chart component accessible [CANCELLED - REPLACED BY ACTION 12 WARNING]

**File:** `docusaurus-site/src/components/interactive/Chart.tsx`

This action has been cancelled as per user feedback. Instead of just making the component accessible with fallback tables, the pipeline now flags all images (including charts) that have missing or generic alt-text in the source Word document (Action 12).

---

## Action 7: Make DataTable sort headers accessible [COMPLETED]

**File:** `docusaurus-site/src/components/interactive/DataTable.tsx`

- On each sortable `<th>`, add `aria-sort` with value `"ascending"`, `"descending"`, or `"none"` reflecting the current sort state.
- Wrap the sort trigger in a `<button>` inside the `<th>` (not a click handler on the `<th>` itself). This makes it natively keyboard-focusable and pressable with Enter/Space.
- Add `aria-label` on the search input: `aria-label="Filter table rows"`.
- Wrap the results count text (e.g. "Showing X of Y rows") in a container with `aria-live="polite"` and `role="status"` so screen readers announce changes when the user types in the filter.

---

## Action 8: Make Callout icons accessible [COMPLETED]

**File:** `docusaurus-site/src/components/interactive/Callout.tsx`

The component uses emoji as icons. For each callout type:

- Wrap the emoji in a `<span role="img" aria-label="...">` with a descriptive label matching the callout type (e.g. `aria-label="Information"` for info, `aria-label="Warning"` for warning, `aria-label="Tip"` for tip, `aria-label="Note"` for note).
- Alternatively, if the callout type is already conveyed by a visible label/title next to the icon, mark the emoji as `aria-hidden="true"` to avoid redundancy.
- Add `role="note"` on the callout container for info/tip/note types. Use `role="alert"` only for the warning type if it conveys urgent information; otherwise use `role="note"` for all.

---

## Action 9: Label icon-only buttons [COMPLETED]

**Files:** `docusaurus-site/src/components/RefPopup.tsx`, `docusaurus-site/src/components/interactive/ReferenceCard.tsx`, and any other component with icon-only buttons (copy, navigate, external link).

For every `<button>` or `<a>` that contains only an SVG icon or symbol with no visible text:

- Add `aria-label` describing the action (e.g. `aria-label="Copy reference"`, `aria-label="Open DOI link"`, `aria-label="Navigate to reference"`).
- Remove any `title` attributes that duplicate the `aria-label` (they cause double announcements in some screen readers). If you want hover text for sighted users, keep `title` but ensure `aria-label` takes precedence.
- Add `aria-hidden="true"` on the SVG/icon element itself so it's not announced separately.

---

## Action 10: Add focus-visible styles

**File:** `docusaurus-site/src/css/custom.css`

Add a global `:focus-visible` rule that applies a consistent, visible focus ring to all interactive elements. This should only appear for keyboard navigation, not mouse clicks:

```css
:focus-visible {
  outline: 2px solid var(--ifm-color-primary);
  outline-offset: 2px;
}

:focus:not(:focus-visible) {
  outline: none;
}
```

Apply this globally. Then check that no component CSS module overrides `outline: none` without providing an alternative focus indicator. If any do, remove that override or replace it with a box-shadow or border-based focus ring.

---

## Action 11: Add aria-live region for search results

**File:** `docusaurus-site/src/css/custom.css` (or the search component if swizzled)

If the search plugin renders a results dropdown, ensure the results container has `aria-live="polite"` so screen readers announce when results appear. If the search component is not swizzled and you can't modify its markup directly, add this CSS to at least ensure focus is visible:

```css
.searchResultsColumn_Z9K0 [role="listbox"] {
  /* ensure this container is announced */
}
```

If the search component is already accessible (check `@cmfcmf/docusaurus-search-local` docs), skip this action.

---

## Action 12: Flag missing or generic alt text during conversion [COMPLETED]

**File:** `docx_to_mdx.py`

In the `fix_mdx_syntax()` function or as a new post-processing step, add a check that scans for images with empty or likely auto-generated alt text. Print a warning if issues are found:

- Flag images where alt text is empty: `![](path)`
- Flag images where alt text matches common auto-generated patterns: starts with "A picture", "A screenshot", "A close up", "A group of", "image", "Image", "graphic", "Graphic", "figure", "Figure", or is shorter than 5 characters.
- Print warnings like: `WARNING: Image /media/image5.svg has generic alt text: "A picture containing text". Consider adding a descriptive alt.`
- Collect these warnings and print a summary at the end of the pipeline run with the count.

This does not fix the alt text — it alerts a human to address it in the Word source document.

---

## Action 13: Add prefers-contrast support

**File:** `docusaurus-site/src/css/custom.css`

Add a media query for users who request higher contrast:

```css
@media (prefers-contrast: more) {
  :root {
    --ifm-color-primary: #4338ca;
    --custom-shadow: none;
    --custom-border-radius: 4px;
  }
  [data-theme='dark'] {
    --ifm-color-primary: #a5b4fc;
  }
  * {
    border-color: currentColor !important;
    text-shadow: none !important;
  }
}
```

Adjust the specific colour values to ensure all text meets WCAG AAA contrast ratios (7:1) against their backgrounds. The key changes: stronger primary colour, removed decorative shadows, sharper borders, reduced border-radius.

---

## Verification

After completing all actions, run:

```bash
cd docusaurus-site && npm run build
```

The build should succeed with no new errors. Then manually test:

1. Tab through the homepage with keyboard only — skip link should appear, all interactive elements should be reachable and operable.
2. Open a page with citations — focus a RefPopup with Tab, verify the tooltip appears, press Escape to dismiss.
3. Toggle a CollapsibleSection with Enter/Space.
4. Enable "Reduce motion" in OS settings — verify no animations play.
5. Use a screen reader (NVDA or VoiceOver) on a page with a Chart and DataTable — verify data is announced.
