# Report issues log – scientific-accuracy audit

Audit of `report/Multisensory Hub_Aug.docx`, run 2026-08-24. Full findings with
suggested wordings: https://claude.ai/code/artifact/922ba8a6-c789-446d-a901-4587e73e8e46

Status: reference/bibliography integrity has been fixed in the doc (duplicate
Mendeley entries removed, citations re-pointed, bibliography regenerated). The
items below are the remaining **content** issues. Search strings (in
backticks) locate each one in Word via Ctrl+F. Tick items off as fixed.

## Wrong numbers and facts

Ticked items were edited in the repo copy of `report/Multisensory Hub_Aug.docx` on 2026-09-14. Andy is editing a separate working doc that will later be copied over the repo copy, so ALL approved rewordings below (ticked or not) must be applied in that working doc – see "Approved rewordings" at the end of this section.

- [x] `within 200ms` (Smell → Adaptation) – smell adaptation takes tens of seconds to minutes; 200 ms is a neural ERP latency, not perceptual adaptation
- [x] `1.2 -- 2.1 m` (Interpersonal space) – Hall's proxemic bands are social 1.2–3.7 m, public >3.7 m; 2.1 m is an internal phase boundary
- [x] `100-metre mansion` (Spatial illusions) – 56% room overlap roughly doubles usable floor area; it cannot compress a mansion into 9 m × 9 m
- [x] `1.4% in the general population` (Impaired smell) – compares objective testing (24.5%, ages 53–97) with self-report; objective adult prevalence is ~19% – compare like with like or label the 1.4% self-reported
- [x] `worldwide` (Colour blindness) – 1-in-12 men applies to Northern-European-descent populations; global male red-green deficiency is ~3–5%
- [x] `2023--24` (Matrix / Cosm case study) – both Cosm venues opened in 2024; also `16:9` → the film's original frame is 2.39:1 widescreen
- [x] `real-time brainwave data` (Brainstorms) – general audiences saw visualisations of pre-recorded EEG (125 study listeners); live capture was a bookable add-on; producer was Pollen Music Group with Richard Wright Music Ltd
- [x] `291 surround speakers` (ABBA Voyage) – the L-ISA system has 291 speakers in total, not 291 surround speakers
- [x] `first ever` (Steady State) – EEG-driven stage performance precedents exist (Lucier 1965; Rosenboom 1970s); narrow to the SSVEP-specific claim or attribute it as the production's own claim
- [x] `upside down` (Anti-gravity illusion) – a sloped-floor room cannot make people appear upside down; that is the rotated-set photo trick (as in the doc's own Illuseum figure) – split the two mechanisms – fixed 2026-09-14
- [x] `vestibular system` (Touch → Localisation) – not involved in locating touch on the skin (that is somatosensory + proprioception); it maps touch into external space. CORRECTION 2026-09-14: Ferrè, Vagnoni & Haggard 2013 (Neuropsychologia) show vestibular stimulation does shift perceived touch location on the hand, so soften rather than delete
- [ ] `2 cm in your visual field` (Arena-scale) – visual field extent is angular (~1° at 1 m); also `29 milliseconds later` holds only versus someone at the source, not the front row

### Approved rewordings (2026-09-14) – apply in the working doc

Old → new. Citation superscripts stay where they are.

1. Smell → Adaptation: "sometimes within 200ms^104^, meaning that we might not notice a certain smell after it has been present for a certain amount of time" → "often within seconds to minutes (the brain's earliest responses to a repeated odour begin to weaken within a fraction of a second^104^), meaning that we might not notice a smell once it has been present for a while"
2. Interpersonal space: "social (1.2 – 2.1 m) and public (> 2.1 m)" → "social (1.2 – 3.7 m) and public (> 3.7 m)"
3. Impaired smell: "one study found that 24.5% of those older than 53 had an impaired sense of smell, compared to around 1.4% in the general population^111^" → "one study that tested people aged 53 to 97 found that 24.5% had an impaired sense of smell, rising to 62.5% among those aged 80 and over, yet only 9.5% of participants reported a problem themselves^111^" (all figures from Murphy 2002)
4. Cosm: "Los Angeles and Dallas in 2023–24" → "Los Angeles and Dallas in 2024"; "its original 16:9 frame" → "its original widescreen frame"
5. ABBA Voyage: "an L-ISA system with 291 surround speakers" → "an L-Acoustics L-ISA immersive system of 291 loudspeakers"
6. Steady State: ", facilitating the first ever use of brain sensors to consciously control sound and visuals on stage." → ", allowing him to consciously steer sound and visuals on stage through his brain signals."
7. Anti-gravity illusion bullet: "appear to lean at impossible angles, upside down, or pour liquids uphill." → "appear to lean at impossible angles or pour liquids uphill. A related trick rotates the entire set by 90° or 180°, fixing furniture to the walls or ceiling, so that photographs show visitors apparently standing on the ceiling (see the Reversed Room figure)."
8. Spatial illusions: "can be realigned to turn a small lab into a much larger building. Follow-up work on impossible spaces found that rooms can overlap by up to 56%, letting a 100-metre mansion fit inside a 9 m × 9 m tracking area without anyone noticing." → "can be realigned to explore a virtual building roughly ten times larger than the physical lab. Follow-up work on impossible spaces found that small virtual rooms can overlap by up to 56% (larger rooms filling a 9 m × 9 m tracking area, by up to 31%) before users begin to notice, allowing a considerably larger interior to be compressed into a small physical space."
9. Colour blindness: "experience some form of colour blindness^89^ worldwide." → "of Northern European descent experience some form of colour blindness^89^, with lower but still substantial rates in other populations." (optional new ref: Birch 2012, JOSA A 29:313–320)
10. Brainstorms: "produced by Pollen and curated at London's Frameless gallery. The experience visualises the audience's real-time brainwave data while listening to Pink Floyd through the use of EEG caps that measure their neural activity. This experience allowed people to view creative projections of their brain's real-time reactions to the music as" → "produced by Pollen Music Group with Richard Wright Music and staged at London's Frameless gallery. The experience visualises brainwave data recorded from 125 volunteers who listened to Pink Floyd while wearing EEG caps, with a separate bookable session in which visitors could have their own brain activity captured. Audiences viewed creative projections of the brain's reactions to the music as"
11. Touch → Localisation: "...and body map) and the vestibular system (which contributes cues relating to gravity and movement) to help us identify where on our bodies we're being touched." → "...and body map) to help us identify where on our bodies we're being touched, and with the vestibular system (which contributes cues relating to gravity and movement) to place that touch in the space around us. Vestibular signals can even subtly shift where on the skin a touch seems to fall."

Items 1–7 are already in the repo docx; items 8–11 are approved but not applied anywhere yet.

## Latency chart rework (one job, several rows)

Done 2026-09-14 – new CHART-DATA table, legend and three prose edits are in `latency_chart_update.md` (paste into the working doc). Pipeline + chart now support a third `Reference` threshold (grey "for comparison" panel); `report/latency_data.json` and `docusaurus-site/src/data/latency_data.json` already regenerated from the new table.

- [x] TV rows: 45/125 ms are ITU *detection* thresholds but the chart labels them "Acceptable" (ITU acceptability ≈ 90/185 ms) – relabel or swap values
- [x] Speech 2 m / 10 m rows are computed sound-propagation delays, not measured perceptual tolerances – move to their own visually distinct group or annotate
- [x] `Own speech` 1 ms and `Pro drummers` 1 ms – implausible precision; check sources and report ranges
- [x] Present 20 ms motion-to-photon as an engineering target, not a biological threshold (chart row and the `20ms or above` motion-sickness paragraph)
- [x] If chart data changes, update `report/latency_data.json` / the CHART-DATA table so the interactive chart matches the text

## Overstated – soften the wording

Andy reports these implemented in the working doc on 2026-09-14 ("most" of them – untick any that were skipped). Proposed wordings were given in chat; two citation fixes go with them: parchment-skin should cite Jousmäki & Hari (currently swapped with the whole-body-illusion citation), and the lip-reading sentence needs a new reference (Sumby & Pollack 1954 or MacLeod & Summerfield 1987) because Bronkhorst 2015 does not support it.

- [x] `80% of people` (rubber hand) → "roughly two-thirds to 80%, depending on method"
- [x] `more than a trillion` (smell) → contested estimate (Meister 2015; Gerkin & Castro 2015); true number unknown
- [x] `30° separation` (ventriloquism) → fusion strongest within ~10–15°; weak but measurable at 30°
- [x] `feel relatively heavier` (size–weight illusion) → expectation account is debated; the illusion persists after expectations correct (Flanagan & Beltzner 2000)
- [x] `Fechner` (experimental aesthetics) → his programme was largely unimodal; drop the multisensory attribution
- [x] `amplifying effects such as the ventriloquist effect` (attention) → spatial ventriloquism is largely automatic; describe attention–integration interplay as bidirectional
- [x] `eight possible combinations` (green-space study) → inconsistent with 4–5 senses; check the study's actual design
- [x] `the two brain centres are strongly linked` (smell–memory) → name the pathway (olfactory input reaches amygdala/hippocampal regions without a thalamic relay); the advantage is emotionality/vividness, not accuracy; drop the "Therefore" into multisensory learning
- [x] `East Asian norms tolerate closer proximity` → not supported by Sorokowska et al. 2017 (likely reversed); use the climate finding or drop
- [x] `almost double the self-reported fear` (VR horror) → "substantially higher, in one small study" (ratios of rating-scale scores aren't meaningful)
- [x] `High humidity slows evaporation` (smell context) → often the opposite for perceived intensity; reword to odorant-dependent effects – already gone from the Aug docx (checked 2026-09-14)
- [x] `increases sales by 10%` (sensory marketing) → single in-store trial; frame as "one retail trial found ~10% uplift"
- [x] `similar to cinema-going audiences` → 50% vs ~40% is a gap; "skew younger than theatre audiences, though less markedly than immersive"
- [x] `±2 cm` tracker drift → "centimetre-scale errors" (varies by tracking system)
- [x] `drier or rougher` (parchment-skin) → "drier, more parchment-like" (the classic result is dryness/smoothness, not roughness)
- [x] `+5 dB increase in sound level or about 150%` (lip-reading/attention) → the established effect is a detection/intelligibility benefit (~2–6 dB SNR equivalent), not loudness; and +5 dB ≈ 140% anyway
- [x] `50-90 Hz` flicker sentence – fix leftover garble: "bright, large or stimuli seen in peripherally viewed objects" → "bright, large or peripherally viewed stimuli" – already fixed in the Aug docx (checked 2026-09-14)

## Verify against the original source (numbers we could not confirm)

- [x] VML `goosebumps` 65/64/53 generational split – CONFIRMED 2026-09-15 against the PDF (~/Downloads/The-age-of-re-enchantment-2.06.23.pdf, "By the numbers" p.21): Gen Z 65%, Millennials 64%, Gen X 53%, Boomers+ 36%; generations defined as 18–29 / 30–44 / 45–59 / 60+. Only fix: credit the report as "Wunderman Thompson Intelligence (now VML)" – the PDF cover says "A report by Wunderman Thompson Intelligence"
- [x] Gaming leisure-time shares (`22%` / 19% / 18%) – NOT in the VML report (checked the PDF). Source is Newzoo (2023), *How different generations engage with video games today* (Gamer insight report): Gen Alpha 22%, Gen Z 19%, Millennials 18% of weekly *entertainment* time. Action: add a Newzoo reference and re-point the citation from ^1^; say "entertainment time" not "leisure time"
- [ ] AC/DC quote (`felt the time`) – could not verify online 2026-09-15 (not indexed by web search, Google Books or Open Library full-text). Check the physical/ebook copy of Fink; if the sentence isn't verbatim, drop the quotation marks and paraphrase. Either way change the em-dashes to en-dashes
- [x] Cinema `37% cinemagoers` / 42% – CONFIRMED 2026-09-15 in the BFI report (ref 6, *Watching films in the UK*, Feb 2023, chart "Age profile % of cinema-goers"): 16–34s were 37% of cinema-goers in Wave I and 42% in Wave III, vs 30% of the population. Two fixes: Wave I fieldwork was Aug–Sep 2019 (boost Feb 2020), so say "in 2019" not "2020"; and the sentence currently cites ^5^ (NRG) – re-point to ^6^ (BFI)
- [x] Hollow-face `1.3m` viewing distance – MISREAD 2026-09-15: in Koessler & Hill 2015 the 1.3 m is the mask's height above the floor, not a viewing distance. Their measured flipping distances were ~1.5 m with two eyes (1468–1523 mm) and ~1.1–1.2 m with one eye. Reword: "when viewed from roughly 1.5 m and beyond with both eyes (closer with one eye covered)^87^"

## Typos

- [x] `45 and over represented` – fixed 2026-08-24
- [x] `Ware of the Worlds` → "War of the Worlds"

---

# Instructions for another LLM: how this audit was done

Method used on 2026-08-24; repeat for future report revisions (this is also
logged as a standing step in Claude's project memory).

1. **Extract the text.** The Word doc is the single source of truth. Convert
   with `pandoc "report/<the one .docx in report/>" -t markdown --wrap=none -o <scratch>/report.md`
   (the file is renamed each revision: May, Aug, Sept...).
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
