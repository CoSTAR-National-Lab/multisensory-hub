# Report issues log – scientific-accuracy audit

Audit of `report/Multisensory Hub_Aug.docx`, run 2026-08-24. Full findings with
suggested wordings: https://claude.ai/code/artifact/922ba8a6-c789-446d-a901-4587e73e8e46

Status: reference/bibliography integrity has been fixed in the doc (duplicate
Mendeley entries removed, citations re-pointed, bibliography regenerated). The
items below are the remaining **content** issues. Search strings (in
backticks) locate each one in Word via Ctrl+F. Tick items off as fixed.

## Wrong numbers and facts

Ticked items were edited directly in `report/Multisensory Hub_Aug.docx` on 2026-09-14 (python-docx, run-level edits, citations untouched) – the SharePoint copy still needs the same edits.

- [x] `within 200ms` (Smell → Adaptation) – smell adaptation takes tens of seconds to minutes; 200 ms is a neural ERP latency, not perceptual adaptation
- [x] `1.2 -- 2.1 m` (Interpersonal space) – Hall's proxemic bands are social 1.2–3.7 m, public >3.7 m; 2.1 m is an internal phase boundary
- [ ] `100-metre mansion` (Spatial illusions) – 56% room overlap roughly doubles usable floor area; it cannot compress a mansion into 9 m × 9 m
- [x] `1.4% in the general population` (Impaired smell) – compares objective testing (24.5%, ages 53–97) with self-report; objective adult prevalence is ~19% – compare like with like or label the 1.4% self-reported
- [ ] `worldwide` (Colour blindness) – 1-in-12 men applies to Northern-European-descent populations; global male red-green deficiency is ~3–5%
- [x] `2023--24` (Matrix / Cosm case study) – both Cosm venues opened in 2024; also `16:9` → the film's original frame is 2.39:1 widescreen
- [ ] `real-time brainwave data` (Brainstorms) – general audiences saw visualisations of pre-recorded EEG (125 study listeners); live capture was a bookable add-on; producer was Pollen Music Group with Richard Wright Music Ltd
- [x] `291 surround speakers` (ABBA Voyage) – the L-ISA system has 291 speakers in total, not 291 surround speakers
- [x] `first ever` (Steady State) – EEG-driven stage performance precedents exist (Lucier 1965; Rosenboom 1970s); narrow to the SSVEP-specific claim or attribute it as the production's own claim
- [x] `upside down` (Anti-gravity illusion) – a sloped-floor room cannot make people appear upside down; that is the rotated-set photo trick (as in the doc's own Illuseum figure) – split the two mechanisms – fixed 2026-09-14
- [ ] `vestibular system` (Touch → Localisation) – not involved in locating touch on the skin (that is somatosensory + proprioception); it maps touch into external space
- [ ] `2 cm in your visual field` (Arena-scale) – visual field extent is angular (~1° at 1 m); also `29 milliseconds later` holds only versus someone at the source, not the front row

## Latency chart rework (one job, several rows)

- [ ] TV rows: 45/125 ms are ITU *detection* thresholds but the chart labels them "Acceptable" (ITU acceptability ≈ 90/185 ms) – relabel or swap values
- [ ] Speech 2 m / 10 m rows are computed sound-propagation delays, not measured perceptual tolerances – move to their own visually distinct group or annotate
- [ ] `Own speech` 1 ms and `Pro drummers` 1 ms – implausible precision; check sources and report ranges
- [ ] Present 20 ms motion-to-photon as an engineering target, not a biological threshold (chart row and the `20ms or above` motion-sickness paragraph)
- [ ] If chart data changes, update `report/latency_data.json` / the CHART-DATA table so the interactive chart matches the text

## Overstated – soften the wording

- [ ] `80% of people` (rubber hand) → "roughly two-thirds to 80%, depending on method"
- [ ] `more than a trillion` (smell) → contested estimate (Meister 2015; Gerkin & Castro 2015); true number unknown
- [ ] `30° separation` (ventriloquism) → fusion strongest within ~10–15°; weak but measurable at 30°
- [ ] `feel relatively heavier` (size–weight illusion) → expectation account is debated; the illusion persists after expectations correct (Flanagan & Beltzner 2000)
- [ ] `Fechner` (experimental aesthetics) → his programme was largely unimodal; drop the multisensory attribution
- [ ] `amplifying effects such as the ventriloquist effect` (attention) → spatial ventriloquism is largely automatic; describe attention–integration interplay as bidirectional
- [ ] `eight possible combinations` (green-space study) → inconsistent with 4–5 senses; check the study's actual design
- [ ] `the two brain centres are strongly linked` (smell–memory) → name the pathway (olfactory input reaches amygdala/hippocampal regions without a thalamic relay); the advantage is emotionality/vividness, not accuracy; drop the "Therefore" into multisensory learning
- [ ] `East Asian norms tolerate closer proximity` → not supported by Sorokowska et al. 2017 (likely reversed); use the climate finding or drop
- [ ] `almost double the self-reported fear` (VR horror) → "substantially higher, in one small study" (ratios of rating-scale scores aren't meaningful)
- [ ] `High humidity slows evaporation` (smell context) → often the opposite for perceived intensity; reword to odorant-dependent effects
- [ ] `increases sales by 10%` (sensory marketing) → single in-store trial; frame as "one retail trial found ~10% uplift"
- [ ] `similar to cinema-going audiences` → 50% vs ~40% is a gap; "skew younger than theatre audiences, though less markedly than immersive"
- [ ] `±2 cm` tracker drift → "centimetre-scale errors" (varies by tracking system)
- [ ] `drier or rougher` (parchment-skin) → "drier, more parchment-like" (the classic result is dryness/smoothness, not roughness)
- [ ] `+5 dB increase in sound level or about 150%` (lip-reading/attention) → the established effect is a detection/intelligibility benefit (~2–6 dB SNR equivalent), not loudness; and +5 dB ≈ 140% anyway
- [ ] `50-90 Hz` flicker sentence – fix leftover garble: "bright, large or stimuli seen in peripherally viewed objects" → "bright, large or peripherally viewed stimuli"

## Verify against the original source (numbers we could not confirm)

- [ ] VML `goosebumps` 65/64/53 generational split – check the Age of Re-enchantment PDF; credit "Wunderman Thompson Intelligence (now VML)"
- [ ] Gaming leisure-time shares (`22%` / 19% / 18%) – looks like Deloitte Digital Media Trends, not the VML report – verify which report contains it
- [ ] AC/DC quote (`felt the time`) – verify against Fink, *The Youngs* (2013); also uses em-dashes (house style is en-dashes)
- [ ] Cinema `37% cinemagoers` / 42% – BFI tracker gives 31% → 41% for all adults, a different metric – re-derive from the BFI report
- [ ] Hollow-face `1.3m` viewing distance – plausible but unconfirmed; hedge to "roughly 1–1.5 m under binocular viewing" if the source doesn't state it

## Typos

- [x] `45 and over represented` – fixed 2026-08-24
- [ ] `Ware of the Worlds` → "War of the Worlds"

---

# Instructions for another LLM: how this audit was done

Method used on 2026-08-24; repeat for future report revisions (this is also
logged as a standing step in Claude's project memory).

1. **Extract the text.** The Word doc is the single source of truth. Convert
   with `pandoc "report/Multisensory Hub_Aug.docx" -t markdown --wrap=none -o <scratch>/report.md`.
   Work from the extraction; cite locations by section name (line numbers
   change every save).

2. **Check reference integrity FIRST, mechanically.** Count bibliography
   entries vs the highest in-text superscript; grep the list for duplicate
   entries. A single duplicated entry shifts every later in-text number off by
   one and makes dozens of citations look wrong when only the list is broken.
   (Exactly this was found: two duplicated Mendeley records.) Only after the
   list is sound should individual citation targets be judged.

3. **Fan out parallel fact-checkers with web access.** Split the report into
   ~3 chunks, one agent per chunk. Each agent: inventory every checkable claim
   (percentages, market values, milliseconds, degrees, named studies, priority
   claims like "first ever"), verify against primary sources via web search,
   and return only issues in a fixed schema: LOCATION / CLAIM / PROBLEM /
   CORRECTION / CONFIDENCE, plus a separate "unverifiable but load-bearing"
   list and a "checked and correct" list (the last one prevents re-litigating
   sound claims later).

4. **Add knowledge-only second opinions from DIFFERENT model families.** Run
   the full report past models with no web access, prompted as sceptical
   domain reviewers. This session used Claude Opus and Claude Sonnet
   (subagents) plus two non-Claude models available as CLIs on this machine
   (see `~/.claude/CLAUDE.md`, section "Other (non-Claude) LLMs"):
   - OpenAI Codex: `codex exec -s read-only --skip-git-repo-check - < brief.txt`
     (brief = reviewer instructions + full report text via stdin)
   - Gemini via Antigravity: `agy -p "<prompt with ABSOLUTE file path>" --model gemini-3.1-pro-high --mode plan`
     (check `agy models` first; agy ignores the shell cwd and often writes its
     full answer to a file under `~/.gemini/antigravity-cli/brain/<id>/`, with
     only a summary on stdout)
   Both are slow (1–2+ min) – run in background. Different model families
   catch different things: Codex added the parchment-skin descriptor and
   cone-of-confusion issues; Gemini added the anti-gravity-room mechanism
   conflation and the vestibular/touch error.

5. **Adjudicate conflicts by evidence, not vote.** Where a knowledge-only
   reviewer contradicted a web-verified check, the source-verified finding
   won. Example: two model reviewers "corrected" the ADHD temporal-binding
   direction, but the cited paper (Panagiotidi 2017) actually supports the
   report's wording – the fix was to keep the claim and strengthen its hedge.
   Never accept a reviewer's confident memory over a checked source.

6. **Classify findings by action**: (a) structural/citation, (b) factual
   corrections (wrong number/date/attribution), (c) overstated – hedge or
   re-source, (d) unverifiable – check the original PDF, (e) typos. Lead with
   the structural fix – it collapses many apparent errors at once.

7. **Verify fixes against the artifact of record, not claims.** After each
   round of author edits, re-run pandoc on the fresh docx and grep the exact
   trouble spots. Gotchas learned here: the repo docx is a manual snapshot
   (browser downloads land in `~/Downloads` as "name (N).docx" and must be
   copied over – it never syncs itself); the Mendeley bibliography only
   regenerates on "Update bibliography", so in-text numbers vs list length
   can legitimately disagree between refresh and save; and in
   number-by-appearance styles every insertion renumbers the list, so
   identify references by title, never by number.
