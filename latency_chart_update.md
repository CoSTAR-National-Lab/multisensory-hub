# Latency chart – updated CHART-DATA table and related text

Prepared 2026-09-14, updated 2026-09-15 from the sources cited in the table.

**How to put it in Word.** Two ways work:

1. *Paste as text (what was done on 2026-09-15).* Paste the table block below
   straight into the doc. The pipeline now accepts this form even though Word
   turns it into escaped text – but keep the line `[CHART-DATA: latency-tolerance]`
   on its own paragraph immediately above the table and `[/CHART-DATA]` below it.
   (The 15 Sept paste dropped the opening line; the parser now assumes
   `latency-tolerance` and warns, but put it back.)
2. *Real Word table.* Select the pasted lines, Insert → Table → Convert Text to
   Table, separator "Other: |", then delete the `|---|` row. Cleaner, optional.

**Citations in the table are keys, not numbers.** Each Label cell ends with a
key in braces, e.g. `{Shay 2024}` or `{Shay 2024; Lester Boley 2007}`. At build
time the pipeline resolves each key against the Mendeley bibliography (every
word in the key must appear in the entry, plus the year) and writes the current
reference number into the chart, so Mendeley renumbering never breaks it.
The keys themselves are invisible on the site.

For a source to be in the bibliography it still needs one real Mendeley
citation somewhere in the document. Put a single citation group on the
sentence that introduces the chart, covering all seven sources: Shay 2024;
Stauffert 2020; Carmack 2013; Attig 2017; ITU-R BT.1359-1 (1998); CCITT G.114
(1988); Lester & Boley 2007.

The `Threshold` column takes three values: `Acceptable`, `Not noticeable`, and
`Reference` (physical delays drawn in a separate grey "for comparison" panel).

## CHART-DATA table

Paste everything from the `[CHART-DATA: ...]` line to the `[/CHART-DATA]` line, markers included:

[CHART-DATA: latency-tolerance]

| Group | Label | Value (ms) | Error (ms) | Threshold |
|---|---|---|---|---|
| Collaborative music | Rhythm-section groups playing by ear (jazz, rock) {Shay 2024} | 7.5 | 2.5 | Acceptable |
| Collaborative music | Orchestra following a conductor {Shay 2024} | 40 | 0 | Acceptable |
| Live sound monitoring | Own voice via in-ear monitors {Shay 2024; Lester Boley 2007} | 8 | 2 | Acceptable |
| Live sound monitoring | Stage wedge monitors (varies by instrument) {Lester Boley 2007} | 22 | 20 | Acceptable |
| XR | Motion to photon (industry design target) {Stauffert 2020; Carmack 2013} | 20 | 0 | Acceptable |
| XR | Tactile to visual {Attig 2017} | 55 | 0 | Acceptable |
| XR | Tactile to audio {Attig 2017} | 25 | 0 | Acceptable |
| TV | Audio ahead of video {Telecommunication Union 1998} | 90 | 0 | Acceptable |
| TV | Video ahead of audio {Telecommunication Union 1998} | 185 | 0 | Acceptable |
| Speech | Speech over mobile phone {CCITT 1988} | 150 | 50 | Acceptable |
| Live sound monitoring | Own voice via in-ear monitors {Shay 2024; Lester Boley 2007} | 1.5 | 0.5 | Not noticeable |
| XR | Head-tracking lag in XR (detection threshold varies 3–17 ms) {Stauffert 2020} | 10 | 7 | Not noticeable |
| TV | Broadcast sync, audio ahead of video {Telecommunication Union 1998} | 45 | 0 | Not noticeable |
| TV | Broadcast sync, video ahead of audio {Telecommunication Union 1998} | 125 | 0 | Not noticeable |
| Sound travel | Sound travelling 2 m through air | 6 | 0 | Reference |
| Sound travel | Sound travelling 10 m through air | 29 | 0 | Reference |
| Sound travel | Front to back of a 12 m orchestra stage {Shay 2024} | 35 | 0 | Reference |
| [LEGEND] | Key latency tolerances for multisensory experiences. "Acceptable" bars show delays that studies or standards report as acceptable for a given activity; "Not noticeable" bars show delays reported as below detection; "For comparison" bars show how long sound takes to travel everyday distances through air – these are physics, not perceptual limits. Error bars show the range reported across studies, instruments or participants. The 20 ms motion-to-photon figure is an industry design target rather than a measured threshold. XR stands for eXtended Reality. | | | |

[/CHART-DATA]

## What changed and why

| Row | Change | Source basis |
|---|---|---|
| Pro drummers 1 ms | Removed. Shay 2024 only says "it is reported that a good professional drummer can subtly shift the timing of the beat by single milliseconds" – hearsay, not a measured tolerance. | Shay 2024 p.2 |
| Play by ear 7.5 ± 2.5 | Kept; relabelled. Shay puts the limit for rhythm groups "on the order of 5 ms to 10 ms". | Shay 2024 p.2 |
| Orchestra 40 ms | New. Shay back-derives ~40 ms from a 40-ft seating spread for conductor-led orchestras. | Shay 2024 p.2 |
| Own speech 1 ms | Split into two rows. Shay: mic-to-headphone latency of 1.0–1.5 ms "was found to be imperceptible"; 6–7 ms "can start to be noticed" but "still quite normal, acceptable"; ~10 ms "distracting and not acceptable". Lester & Boley's smallest tested latency was 1.4 ms. | Shay 2024 p.1–2; Lester & Boley 2007 |
| Wedge monitors 22 ± 20 | New. Lester & Boley: acceptable latency "can range from 42 ms to possibly less than 1.4 ms" depending on instrument; more latency is acceptable with wedges than in-ears. | Lester & Boley 2007 abstract |
| Motion to photon 20 ms | Kept; relabelled as an industry design target. Stauffert et al. cite Carmack's "recommends less than 20 ms" as a guideline and report detection thresholds below 17 ms, down to 3.2 ms in one participant. | Stauffert 2020 |
| Head-tracking lag 10 ± 7 | New "Not noticeable" row summarising the 3–17 ms detection range above. | Stauffert 2020 |
| TV 45 / 125 ms | Moved to "Not noticeable" – these are the ITU detectability thresholds. | ITU-R BT.1359-1 |
| TV 90 / 185 ms | New "Acceptable" rows – the ITU acceptability thresholds. | ITU-R BT.1359-1 |
| Speech 2 m / 10 m | Moved to the new "Reference" category; citation removed (they are computed from 343 m/s, not from Shay); 10 m corrected from 30 ± 5 to 29. | physics; matches the report's own 2.9 ms per metre |
| Orchestra stage 35 ms | New reference row so the 40 ms orchestra tolerance has its physical counterpart (40 ft ≈ 12 m ≈ 35 ms). | Shay 2024 p.2 |
| Legend | Rewritten to explain the three categories and the error bars. | – |

## Text edits in the surrounding prose

**Intro sentence before the chart** (section "Latency tolerances")

Old: The graph below illustrates the lags that can be tolerated for different tasks and information type.

New: The graph below illustrates the lags reported as acceptable, or as not noticeable, for different tasks and types of information, alongside everyday sound-travel times for comparison.

**Live Music Streaming bullet**

Old: For broadcast-style audiovisual sync, viewers begin to detect mismatch at roughly 45 ms when audio leads video, and 125 ms when video leads audio.

New: For broadcast-style audiovisual sync, viewers begin to detect mismatch at roughly 45 ms when audio leads video and 125 ms when video leads audio, and judge it unacceptable beyond roughly 90 ms and 185 ms respectively {Telecommunication Union 1998}.

**Motion sickness and comfort paragraph**

Old: even minor delays between head movement and visual can create sensory discrepancies that the brain interprets as disorienting (delays of 20ms or above^120^).

New: even minor delays between head movement and visual update can create sensory discrepancies that the brain interprets as disorienting (the widely quoted 20 ms motion-to-photon figure is an industry design target rather than a perceptual threshold; sensitive users can detect head-tracking lags well below this^120^).
