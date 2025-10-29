## User Story 005 – Pre-Award Director Needs Richer Matching

**Role**: Director, Department of Pediatrics Pre-Award Office  
**Need**: Deliver meaningful foundation matches using our actual faculty and foundation spreadsheets without manual keyword surgery.  
**Benefit**: Confidently provide faculty with actionable opportunities and avoid wasting staff time on empty digests.

### Narrative
As the Pre-Award director, I want the matching engine to recognize close keyword relationships (e.g., “pulmonary hypertension” vs. “neonatal and pediatric pulmonary hypertension”) so I can trust that the digest surfaces real opportunities using the inputs we already maintain.

### Problem Today
- Exact-match logic misses obvious overlaps between faculty focus areas and foundation descriptions.  
- Manual inspection shows numerous valid pairings that the tool currently ignores.  
- Staff cannot deliver results until the matching feels credible.

### Success Signals
- Digest lists non-zero matches for representative faculty (e.g., Matthew Douglass) using our current Excel files.  
- Scores rank tighter matches above broader ones, giving staff triage guidance.  
- Spot checks confirm substring, pluralization, and closely-related phrases match as expected.  
- Director can share initial results without rewriting foundation keywords.

### Acceptance Criteria
1. Matching accounts for partial phrase overlaps and basic stemming (e.g., “inflammation” ↔ “inflammatory”).  
2. Faculties receiving zero matches are traceable to a clear reason (e.g., truly no overlap) rather than simplistic exact matching.  
3. Output includes match scores so staff can prioritize and vet borderline cases.  
4. Engine operates on the existing faculty and foundation spreadsheets without requiring manual keyword rewrites.  
5. Provide a quick verification script or guidance to reproduce a known match (Matthew Douglass ↔ pediatric pulmonary hypertension foundation).

### Open Questions
- Do we need to support adjustable similarity thresholds per run? ✅ Yes—per-run tuning is preferred; per-faculty sliders are not required.  
- What level of stemming/lemmatization is sufficient without pulling in heavy NLP dependencies? ✅ Decision: adopt robust NLP tooling (e.g., an established lemmatization library) to reliably connect variants like “inflammation” and “inflammatory.”
