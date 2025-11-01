# Phase 3 – Tool Header Alignment Plan

Date: 2025-10-31

Goal: Give the three tool blocks (Learning Progress, Tone & Critique, Generate Document) consistent headers while keeping their bodies implemented as-is for now.

---

## 1. Desired UX

* “Tools” accordion stays open by default and shows the tone/progress summary line.
* Inside the accordion, each tool starts with a compact header row:
  - Left: icon + title (`Inter`, 0.9rem, semibold).
  - Right: optional chevron button for sections that toggle.
* Bodies can remain unique (button grids, sliders, status cards), but they sit below a shared divider and use the existing card padding.

---

## 2. Implementation Overview

1. **HTML wrappers** – Add a `.tool-card` container for each tool within the existing `tool-stack` so the header markup matches.
2. **CSS styling** – Create `tool-card`, `tool-card__header`, `tool-card__title`, `tool-card__meta`, `tool-card__chevron`, `tool-card__body` classes in `components.css`.
3. **Document generator injection** – Update `restore-document-generation.js` to render its content inside the new header/body structure.
4. **Tone component** – Wrap the injected markup in the same classes; leave the slider logic untouched.
5. **Learning progress markup** – Move current title/button/status inside a `tool-card__body` and render the header with the shared layout.

---

## 3. Step-by-Step Instructions

### Step 1 – Update `templates/chat/view.html`

* Inside `<div class="tool-stack">`, wrap each tool in:
  ```html
  <section class="tool-card" id="progress-card">
    <div class="tool-card__header">
      <div class="tool-card__title">
        <i data-lucide="activity" class="w-4 h-4"></i>
        Learning Progress
      </div>
    </div>
    <div class="tool-card__body">
      <!-- Existing button + status markup -->
    </div>
  </section>
  ```
* Add placeholders for tone and document cards (`<section id="tone-card">`, `<section id="doc-card">`) so injected HTML can slot into `tool-card__body`.

### Step 2 – Style headers (`src/app/static/css/components.css`)

Add (after sidebar accordion styles):
```css
.tool-stack { display: flex; flex-direction: column; gap: 1rem; }
.tool-card {
    border: 1px solid hsl(var(--border));
    border-radius: 0.75rem;
    background: hsl(var(--card));
    padding: 1rem;
    box-shadow: 0 4px 12px rgb(15 23 42 / 0.08);
}
.tool-card__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
}
.tool-card__title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
    font-weight: 600;
    color: hsl(var(--foreground));
}
.tool-card__meta {
    font-size: 0.75rem;
    color: hsl(var(--muted-foreground));
}
.tool-card__chevron {
    border: none;
    background: transparent;
    color: hsl(var(--muted-foreground));
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.75rem;
    height: 1.75rem;
    border-radius: 0.5rem;
}
.tool-card__chevron[aria-expanded='true'] { transform: rotate(180deg); }
.tool-card__body { font-size: 0.85rem; color: hsl(var(--foreground)); }
```

### Step 3 – Modify document dropdown injection

* Update `restore-document-generation.js` to produce:
  ```javascript
  const docGenHTML = `
    <section class="tool-card">
      <div class="tool-card__header">
        <div class="tool-card__title">
          <i data-lucide="file-text" class="w-4 h-4"></i>
          Generate Document
        </div>
        <button type="button" class="tool-card__chevron" aria-expanded="false" onclick="toggleDocumentDropdown(this)">
          <i data-lucide="chevron-down" class="w-4 h-4"></i>
        </button>
      </div>
      <div class="tool-card__body" id="document-dropdown" hidden>
        ...existing content...
      </div>
    </section>
  `;
  ```
* Adjust `toggleDocumentDropdown` to accept the button reference, toggle `[hidden]`, and rotate the chevron by setting `aria-expanded`.

### Step 4 – Update tone injection

* In `templates/base.html`, after fetching `tone_critique_control.html`, wrap the markup manually:
  ```javascript
  const template = document.createElement('template');
  template.innerHTML = html.trim();
  const toneMarkup = template.content.firstElementChild; // existing <details>… block

  const toneCard = document.createElement('section');
  toneCard.className = 'tool-card';
  toneCard.id = 'tone-card';

  const toneHeader = document.createElement('div');
  toneHeader.className = 'tool-card__header';
  toneHeader.innerHTML = `
    <div class="tool-card__title">
      <i data-lucide="sliders" class="w-4 h-4"></i>
      Tone & Critique
    </div>
  `;

  const toneBody = document.createElement('div');
  toneBody.className = 'tool-card__body';
  toneBody.appendChild(toneMarkup);

  toneCard.appendChild(toneHeader);
  toneCard.appendChild(toneBody);

  mount.replaceChildren(toneCard);
  ```
* Remove the outer `<details>` wrapper (or keep it expanded) if you no longer want the native chevron; otherwise hide the default marker to avoid double toggles.
* Ensure `lucide.createIcons()` is re-run after insertion so the sliders icon renders.
* Inside `initToneCritiqueControl`, dispatch `tone:change` when the slider updates or saves, and store/read tone level with a single key (`chat_${chatId}_critique`) to stay in sync with the summary line.

### Step 5 – JS toggles (optional)

* For Learning Progress, the body is always visible; keep header without chevron.
* For Tone, consider leaving body open (no toggle) until we add collapse behavior.
* For Doc generator, reuse the chevron to toggle `[hidden]`.

---

## 4. Testing Checklist

1. **Desktop**: verify headers match, icons align, chevron rotates for doc card.
2. **Tone**: load page with saved tone → summary shows correct label; adjusting slider updates summary instantly.
3. **Progress**: run assessment → summary updates; header remains consistent.
4. **Document dropdown**: toggle open/closed; buttons still submit exports.
5. **Mobile drawer**: accordion + cards render without double padding; chevron tap target works.
6. **Focus mode**: sidebar hidden; no JS errors when cards aren’t mounted.

---

## 5. Rollout Notes

* Change touches multiple files—treat as Phase 3 sprint.
* Implement in small commits:
  1. HTML wrappers.
  2. CSS styling.
  3. Doc injection update.
  4. Tone injection + events.
  5. Final polish/test fixes.
* Keep existing IDs (`#assess-progress-btn`, etc.) so current JS keeps working.

---

## Key Questions Before Implementation

### Tone Component Integration (Critical)
1. **Injection path** – Confirm the injection routine in `templates/base.html`: timing, target element, and failure handling.
2. **Storage contract** – Document the sessionStorage key(s) and formats currently used to persist tone level.
3. **Event dispatch** – Decide where to trigger a `tone:change` event (slider `input`, save button, wrapper JS) without destabilising the component.  
   **Decisions captured:** tone card should sit immediately after the Learning Progress card once injected; persistence of expanded state is desired (per-chat). _Open_: confirm whether core component markup can be rewritten versus wrapped post-injection.

### Toggle Behaviour (Critical)
1. **Toggle coverage** – Determine which tools should collapse (e.g., keep Learning Progress open, allow Tone/Docs to toggle).  
   **Decision:** Progress and Tone remain open; Document Generation collapsible.
2. **Mechanism** – Choose between native `<details>`, `hidden` attribute, or custom animation.  
   **Decision:** follow standard disclosure pattern (button with `aria-expanded` / `aria-controls` plus `hidden` body).
3. **Persistence** – Decide whether expanded state persists per chat (localStorage) or resets each load.  
   **Decision:** persist collapsed state per chat.

### Accessibility (Important)
1. **ARIA usage** – Define aria-expanded/aria-controls patterns for custom toggles.  
   **Decision:** adopt the standard disclosure ARIA pattern.
2. **Keyboard support** – Ensure toggles respond to Enter/Space and retain focus outlines.
3. **Announcements** – Decide if state changes need live-region announcements or descriptive labels.

### Mobile Responsiveness (Important)
1. **Summary meta** – Choose how the tone/progress line behaves on narrow screens (hide, abbreviate, or stack).  
   **Decision:** follow best mobile practice (team to determine exact treatment during implementation).
2. **Tap targets** – Guarantee chevrons meet the 44×44px guideline or make entire headers tappable.  
   **Decision:** follow mobile best practice (likely full-header tap target).
3. **Spacing** – Confirm tool-stack gaps and padding scale appropriately on mobile.

### Error Handling (Nice to Have)
1. **Doc dropdown failures** – Define fallback behaviour if injection fails.
2. **Tone load issues** – Provide graceful feedback when the tone component errors.
3. **Assessment failures** – Decide how the summary reflects API errors versus last successful assessment.

### CSS Cascade (Nice to Have)
1. **Scoping** – Decide whether `.tool-card` styles stay scoped to the sidebar.
2. **Interaction with existing styles** – Verify buttons/inputs within cards retain expected styling.
3. **Layering** – Confirm chevron/toggle elements do not introduce z-index conflicts.

### Injection Timing (Important)
1. **Order of operations** – Verify the sequence of tone/doc injections relative to the template markup.
2. **Loading states** – Decide if placeholders or skeletons are needed while cards populate.
3. **Ordering guarantees** – Ensure final DOM order remains Progress → Tone → Documents regardless of load timing.

### Summary Updates (Important)
1. **Update cadence** – Determine whether tone summary updates on slider input, on save, or both.
2. **Early calls** – Guard against summary updates firing before the DOM elements exist.
3. **Unsaved state** – Consider signalling when tone changes are not yet saved.

### Backwards Compatibility (Nice to Have)
1. **Cached pages** – Plan for users loading cached assets (force refresh vs. dual support).
2. **Legacy storage keys** – Handle existing sessionStorage values gracefully.
3. **Selector compatibility** – Ensure dependent JS is updated alongside markup changes.

### Performance (Nice to Have)
1. **Deferred rendering** – Decide whether any tool card can render lazily.
2. **Animations** – Evaluate whether toggle animations are worth the complexity.
3. **Large payloads** – Consider future scalability if document options grow significantly.

---

Ready for implementation when we decide to start the card-alignment work. Until then, this doc captures the plan and testing requirements.***

---

## Top Questions Snapshot (Priority Order)

### 🔴 Critical – Must Answer Before Starting
1. **Tone Injection – WHERE exactly?**
2. **Tone Component – CAN we wrap after injection?**
3. **Tone Event – WHERE to dispatch it?**

### 🟡 Important – Address During Planning
4. **Summary Meta on Mobile – Hide or show?**
5. **Chevron Tap Targets – Adequate size?**
6. **ARIA Controls – Complete specification?**

### 🟢 Nice to Have – Decide During Implementation
7. **Injection Failures – Graceful degradation?**
8. **Summary Update Timing – Real-time or on-save?**
9. **Toggle State Persistence – Yes or no?**

---

## Follow-Up Improvements (Tone & Docs Visual Polish)

1. **Tone Heading Cleanup**
   - Goal: Remove the duplicate “Tone & Critique” line inside the injected markup so the card header is the only title.
   - Implementation:
     * Update the fetched component (`tone_critique_control.html`) to demote or hide its `<summary>` text (e.g., replace with `sr-only` span or move wording into the card header).
     * Alternatively, after wrapping the component, locate the first heading within `.tool-card__body` and hide it via JS/CSS (`.tool-card__body > details > summary { display:none; }`).
   - Difficulty: Low – mostly markup/CSS adjustment. Watch for accessibility if hiding the native summary.

2. **Generate Document Visual Alignment**
   - Goal: Replace emoji file indicators with Lucide icons or badge chips so the doc card matches the rest of the design system.
   - Implementation:
     * In `restore-document-generation.js` (HTML string) swap emoji with `<i data-lucide="file-text">`, `<i data-lucide="sticky-note">`, etc.
     * Add small badge styles (`.tool-chip`) for `.txt` / `.docx` to keep alignment tight.
     * Re-run `lucide.createIcons()` (already happening) after injection.
   - Difficulty: Low – string updates plus minor CSS.

3. **Tone Slider Body Spacing**
   - Goal: Improve readability inside the Tone card by balancing padding and alignment.
   - Implementation:
     * Add class hooks (`.tone-card__slider`, `.tone-card__actions`) and apply consistent spacing in `components.css` (e.g., extra padding above the slider, align “Save” and tip text).
     * Optionally center-align slider labels or left-align everything for clarity.
   - Difficulty: Low/Medium – CSS tweaks, ensure layout remains responsive.
