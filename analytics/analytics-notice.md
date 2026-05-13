# Analytics Notice

This document is the source of truth for the analytics notice shown to visitors of the Multisensory Hub.

## Notice text (as displayed in the site footer)

We collect anonymous, aggregate engagement data to understand which topics and sections of this report are useful to visitors. We do not collect names, emails, raw IP addresses, or use third-party advertising analytics. You can opt out of analytics at any time.

## What we collect

- Which pages and sections visitors reach
- Which topics and concepts attract engagement (page views, downloads, outbound link clicks)
- Approximate device type (mobile/tablet/desktop) and browser family
- Referrer domain (e.g. "google.com") — not the full referring URL
- An anonymous, tab-scoped session ID stored in sessionStorage — it is never sent to a third party and is lost when the tab closes

## What we do not collect

- Names, email addresses, or any directly identifying information
- Raw IP addresses (discarded immediately after the request is received)
- Cookies or persistent identifiers across sessions
- Mouse movements, keystrokes, or session recordings
- Individual user journeys linked across days or weeks
- Any data from third-party advertising or social networks

## Legal basis

UK GDPR legitimate interest. A Legitimate Interest Assessment has been completed and approved by RHUL/StoryFutures before the tracker was activated in production.

## Opt out

Visitors may opt out at any time using the button in the site footer. Opt-out preference is stored in the browser's localStorage under the key `concept_analytics_optout`. It persists across sessions in the same browser without requiring a cookie. Clearing browser storage will reset this preference.

The tracker also honours the Global Privacy Control (GPC) browser signal where present.

## Data retention and suppression

Raw events are retained for 90 days. Aggregate summaries are retained indefinitely. Public summaries exclude any block with fewer than 10 unique sessions (suppression threshold) to prevent identification of individual visits.

## Contact

For questions about this analytics setup, contact the StoryFutures team at Royal Holloway, University of London.
