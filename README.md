# NBA 2K27 Cap Breaker & Pro Build Architect

An offline-first PWA for mobile. Open `index.html` over http, or open `2k27-lab-portable.html` directly as a single file.

- **Cap Breaker Simulator:** +1 per click, max +5 per attribute, 28 total from REP 11, Season 9, Crew 4, Lifetime 2 and Specialization 2. It shows the badge, animation and Takeover unlocks and the builder cost saved.
- **Badge & Animation Gate Matrix:** 53 badges, 1643 LockerCodes gates, Takeovers and legacy aliases.
- **Synergy Fuse & Token Loadout Planner:** Rec / 3s modes, Fuse +1/+2 with Reaction pairs, and the 1/3/4/5 · 2/4/5/6 · 3/5/6/7 token costs.
- **Builds:** The owner's 6 builds and 5 illustrative meta templates.
- **Passing:** preset Direction 85 / Distance 10 / Openness 5. The no-look pass is Hold R1/RB + Right Stick.

Build with `python3 build_pwa.py`. The data comes from a local research file through `gen_data.py` (pre-built into `src/data.json`).
Fan tool, not affiliated with 2K.
