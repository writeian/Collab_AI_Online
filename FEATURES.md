# AI Collab Online — Features

Full capability breakdown. For positioning and the short pitch, see [README.md](README.md).

---

## Mountain learning journey

- Visual learning progression (mountain / trail metaphor) as a default room experience  
- Step markers, progress tracking, deep links to stages  
- Social indicators: avatars, activity, team participation  
- Responsive, mobile-friendly layout  

---

## Intelligent learning progression

- **Automatic note generation** from discussion milestones (e.g. 5+ message thresholds)  
- **Cross-chat learning context** — new chats can use insights from earlier conversations in the same room  
- **AI-generated welcome messages** using room goals, objectives, and prior discussion context  
- **Progressive paths** that remember the broader journey (non-linear where the product allows)  

---

## Audiences

### Educators

- Learning environments from **templates** (study groups, academic essays, writing workshops, etc.)  
- Guided **multi-step** processes (e.g. 10-step essay flow)  
- Progress and analytics-oriented tooling  
- Customizable AI / mode prompts for stages and subjects  

### Writing teams & collaborators

- **Rooms** with real-time chat and AI  
- **Presence** in the sidebar; owners treated like members for presence where implemented  
- Templates (e.g. business, creative)  
- Collapsible goal categories  
- **Per-chat AI on/off**  

### Content creators

- **Google Docs** import / analysis where configured  
- Stage-aware AI responses  
- Room-based workspaces  
- Feedback on structure and drafting  

### Highlights

- Intelligent progression across chats  
- Automatic notes at milestones  
- Adaptive welcomes  
- Multiple **built-in templates**  
- Context-aware AI  
- Collaboration-first design  
- Mobile-responsive UI  

---

## Core product areas

### Learning progression

- Notes at **5, 10, 15…** message milestones (configurable behavior may evolve)  
- Cross-chat references for new conversations  
- Welcome generation from goals + objectives + prior work  
- **Pin-seeded chats** from shared pins (minimum pin count enforced in app); **9 synthesis options** (explore, study, essay, presentation, etc.)  
- **PinChatMetadata** snapshot so pin context stays stable  

### Document generation & export

- Chat → structured **notes**, **outlines**, or raw transcript  
- **`.txt` / `.docx`**  
- Progressive unlock by conversation depth  
- Sidebar / dropdown entry points  

### Templates & rooms

- Multiple **pre-built templates**  
- Custom rooms with goals and flexible progression  
- Create / edit flows: goals → proposal → refine → create  

### AI-powered collaboration

- **Archetype-aware** prompts (cognitive style) where enabled  
- **Anthropic Claude** as primary provider; failover and alternatives configurable  
- Mode-specific guidance along learning steps  
- **Tone & Length** (critique level + short / medium / long)  
- **Google Docs** integration where OAuth is set  
- Pin-aware system prompts in pin-seeded threads  
- **Multi-participant weaving** — when several people speak in the recent window, prompts can synthesize by name (see `AI_WEAVING_*` env vars in [DEVELOPMENT.md](DEVELOPMENT.md))  

### Analytics & administration

- Progression / note-generation oriented analytics  
- User analytics with export options  
- System instructions / custom modes  
- Members and roles  
- Achievements / gamification where enabled  

### Chat UX

- Focus mode  
- **Tone & Length** in sidebar; help via `?` tooltips (portaled above chat stack)  
- **Busy rooms:** when active participant count crosses a threshold, UI may default length to **Short** once per spike (user can override)  
- Rubric-style recommendations where implemented  
- Liquid-glass style UI patterns  
- Modular templates and external JS  
- Flash messages with dismiss  

### Architecture & performance *(summary)*

- Flask blueprints, SQLAlchemy 2.x, Alembic  
- Modular templates and cache-busted static assets  
- Railway / other production deployments supported  

---

## Optional / future

- **Trial mode** (guest trials): see `docs/trial_sessions_option_2.md`  
