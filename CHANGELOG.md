# Changelog

Notable product and documentation updates. For install and env details, see [DEVELOPMENT.md](DEVELOPMENT.md).

---

## 2026 — Collaboration & chat polish

- **Participant presence** — heartbeats per room/chat; **room owners** included alongside `RoomMember` where applicable  
- **Presence + CSRF** — client uses correct chat id and cookie CSRF for ping endpoints  
- **Busy chat** — when active count crosses above five (same chat when presence includes `chat_id`), response length can default to **Short** once per spike (user can change in Tone & Length)  
- **Tone & Length UX** — `?` help tooltips **portaled to `document.body`** so sidebar `backdrop-filter` / overflow do not clip them  
- **Multi-participant AI weaving** — speaker-labeled history and collaboration prompts when multiple users appear in the recent window (see `AI_WEAVING_*` variables in [DEVELOPMENT.md](DEVELOPMENT.md))  

---

## Pin-seeded chats (v3.2) — ~December 2025

- Shared pins (≥ minimum count) seed new chats  
- **9 synthesis options** (explore, study, research essay, presentation, learning exercise, startup, artistic, social impact, analyze)  
- Pin-aware AI prompts with full pin context  
- **PinChatMetadata** stores pin snapshot at creation  
- Room / mountain UI: pin-based chat sections and badges  
- Sidebar grouping for pin-based chats  
- Option picker modal (glass styling, loading states)  
- Prompt size limits / truncation for large pin sets  

---

## Mountain learning journey (v3.0) — ~September 2025

- Mountain / trail as default room progression visualization  
- Curvy SVG trails, markers, progress  
- Social / avatar features, activity indicators  
- Mobile-friendly collapsible details, accessibility improvements  
- Deep links to steps, room stats  

---

## Tone & length (v3.1+) — ~September 2025 onward

- Five-level critique / feedback stance  
- Short / Medium / Long response length (session storage per chat)  
- Hidden fields / instructions sent with messages  
- Room81-style instruction keys for critique and length  

---

## Learning progression (v2.0)

- Automatic notes at milestones with iterative refinement  
- Cross-chat context and history  
- Welcomes combining goals + objectives + prior insights  
- Flexible, skippable / reversible paths where supported  

---

## Document generation & export

- Notes, outlines, raw export from chat  
- Progressive unlock by depth  
- `.txt` and `.docx`  
- Sidebar integration  

---

## UX (v3.1) — ~September 2025

- Continue / expand AI messages inline  
- Button contrast and accessibility  
- Password visibility toggle  
- Mobile focus behavior  

## UI / UX modernization

- Large template size reduction via JS extraction and components  
- Learning-green tokens and glass-style chat input  
- Auto-dismiss flash messages  

## Architecture

- Modular templates, external JS, improved error handling  
- Migration fallbacks for deploy reliability  

---

## 2025 — Sidebar & performance (Oct–Nov)

### Sidebar (phases 1–3)

- Collapsible sections: Tools, Participants, Other chats  
- Unified tool cards (progress, tone & length, document generation)  
- Dashboard summary of tone and progress  
- Lucide icons, spacing, ARIA patterns  
- Mobile drawer and tap targets  

### Performance & UX

- Adaptive polling (e.g. 5s active / 90s idle), wake on new messages  
- iPhone scroll fixes  
- Large reduction of inline JS  
- Console / a11y cleanup  

See also: `docs/SESSION-SUMMARY-2025-10-28.md`, `docs/PHASE3-tool-header-alignment.md`.

---

## Older README-era bullets (preserved)

The following appeared in the historical README and may overlap with sections above; kept for traceability.

- **Intelligent learning progression** — milestones, cross-chat context, welcomes, paths  
- **Document export** — progressive unlock, formats, sidebar  
- **Templates** — seven+ templates, custom goals  
- **AI** — Anthropic, modes, toggle, Docs, pin-aware  
- **Analytics** — progression, CSV export, system instructions, members, achievements  
- **Chat** — focus mode, tone & length, busy-room default, rubric-style help, modular JS  
