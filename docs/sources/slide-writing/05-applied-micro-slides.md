# Applied Micro Slides PDF

- Source: Jesse M. Shapiro, "How to Give an Applied Micro Talk: Unauthoritative Notes," [assigned Harvard PDF](https://shapiro.scholars.harvard.edu/sites/g/files/omnuum7731/files/shapiro/files/applied_micro_slides.pdf)
- Access status: Accessible by direct download from the assigned Harvard PDF URL on 2026-05-25; the browser fetch returned 403, but `curl -L -A 'Mozilla/5.0'` downloaded a valid 43-page Beamer PDF. The older Brown URL found in secondary references now returned a Brown 404 HTML page, so the report uses the assigned Harvard PDF only.
- Report date: 2026-05-25

## Core Slide-Writing Principles

1. Early slides must make the audience care.
   - Direct source claim: Shapiro argues that the audience does not initially care about the topic and that the speaker has only the first one or two slides to change that; he recommends using anecdotes, facts, or policy questions as motivation ([Shapiro PDF](https://shapiro.scholars.harvard.edu/sites/g/files/omnuum7731/files/shapiro/files/applied_micro_slides.pdf)).
   - Interpretation: The first slides should not be housekeeping, literature positioning, or a table of contents unless those directly create stakes for the research question.

2. State a real applied research question, not a literature-internal exercise.
   - Direct source claim: Shapiro says to state a research question, preferably a policy/counterfactual question, an estimate of an important deep parameter, a test of an important theoretical prediction, or all three. He contrasts this with questions motivated mainly by applying a model to a new industry, changing an assumption, or re-estimating prior work on different data ([Shapiro PDF](https://shapiro.scholars.harvard.edu/sites/g/files/omnuum7731/files/shapiro/files/applied_micro_slides.pdf)).
   - Interpretation: The talk's question slide should be understandable before the audience knows the literature niche.

3. Preview findings early, with enough method to make the result credible.
   - Direct source claim: Shapiro says to assume the audience is about to leave and make sure they leave with something. The preview should be tangible and terse, giving just enough methodology so results do not feel like magic, without crowding out the findings ([Shapiro PDF](https://shapiro.scholars.harvard.edu/sites/g/files/omnuum7731/files/shapiro/files/applied_micro_slides.pdf)).
   - Interpretation: A research talk should not hide results until the end. The early preview should combine magnitudes, comparison groups, and bottom-line implication, not just "we estimate X."

4. Explain data sources and measurement, but hide processing detail.
   - Direct source claim: Shapiro says the data section should clearly state the source of each variable, prevent later confusion about where variables come from or what level they are measured at, and anticipate pure measurement concerns. He also says the speaker should take credit for novel data, measurement, and variation, but not describe tedious data-processing steps ([Shapiro PDF](https://shapiro.scholars.harvard.edu/sites/g/files/omnuum7731/files/shapiro/files/applied_micro_slides.pdf)).
   - Interpretation: Data slides should answer "what is measured, from where, at what level, and why credible," while moving cleaning recipes and construction minutiae to notes, appendix, or paper.

5. Be explicit about model, variables, identification, and the bottom-line estimand.
   - Direct source claim: Shapiro escalates from a vague "panel data model" statement to an equation with variable definitions, then to an explicit identifying condition. He also recommends defining the bottom-line quantity of interest, such as a ratio that translates an estimate into an incidence result ([Shapiro PDF](https://shapiro.scholars.harvard.edu/sites/g/files/omnuum7731/files/shapiro/files/applied_micro_slides.pdf)).
   - Interpretation: A model slide should not merely display an equation; it should define symbols, state the identifying variation, and connect the coefficient to the substantive or welfare question.

6. Discuss key vulnerabilities, not every possible criticism.
   - Direct source claim: Shapiro recommends pausing to discuss the most important vulnerabilities of the modeling approach, why the model is a good approximation, and how plausibility or sensitivity will be assessed. He advises against trying to anticipate every criticism or listing all other models tried ([Shapiro PDF](https://shapiro.scholars.harvard.edu/sites/g/files/omnuum7731/files/shapiro/files/applied_micro_slides.pdf)).
   - Interpretation: Identification threats should be prioritized and tied to planned evidence, not treated as a defensive laundry list.

7. Slides are not documentation.
   - Direct source claim: Shapiro says that unlike readers of a paper, the audience cannot skip or browse, so every word is precious. Slides should be clear and sparse, with no extraneous detail. The paper is the complete description; the talk tells the story ([Shapiro PDF](https://shapiro.scholars.harvard.edu/sites/g/files/omnuum7731/files/shapiro/files/applied_micro_slides.pdf)).
   - Interpretation: The deck should be a guided argument, not a compressed paper replica.

8. Pacing and scale must match the talk slot.
   - Direct source claim: Shapiro's pacing rule is "no pauses" except when the speaker truly wants to stress something. He also says a 30-minute talk is not a 90-minute talk delivered three times faster; emphasis and detail must be chosen for the available time ([Shapiro PDF](https://shapiro.scholars.harvard.edu/sites/g/files/omnuum7731/files/shapiro/files/applied_micro_slides.pdf)).
   - Interpretation: Short talks require fewer claims, fewer tables, and fewer setup slides, not faster delivery.

9. Results should be visual where possible and summarized by a bottom line.
   - Direct source claim: Shapiro recommends figures wherever possible to tell the story in the data because they are more honest, complete, interesting, and persuasive. Tables should summarize key magnitudes, not every control coefficient or robustness check. The talk should have a single qualitative or, ideally, quantitative takeaway ([Shapiro PDF](https://shapiro.scholars.harvard.edu/sites/g/files/omnuum7731/files/shapiro/files/applied_micro_slides.pdf)).
   - Interpretation: Results sections should lead with data patterns and magnitudes, while full regression machinery belongs in backup or the paper.

10. Practice is part of the slide-writing standard.
    - Direct source claim: Shapiro closes by urging the speaker to practice a lot and give talks whenever possible ([Shapiro PDF](https://shapiro.scholars.harvard.edu/sites/g/files/omnuum7731/files/shapiro/files/applied_micro_slides.pdf)).
    - Interpretation: Slide design should support delivery: fewer moving parts, clearer transitions, and a sequence that can be rehearsed cleanly.

## Beamer-Specific Implications

- Start the Beamer deck with a stakes-first sequence: motivation, research question, what this paper adds, and preview of findings. Avoid opening with a generic outline unless the outline itself reduces confusion.
- Use an early "Preview of findings" frame with 2-3 concrete bullets: main magnitude, essential comparison or identification source, and substantive implication.
- Build data frames around variable-source-level triples: variable, source, unit of observation or aggregation. Keep data-cleaning details out of main frames unless they directly affect interpretation.
- For model frames, prefer a staged sequence: verbal model, displayed equation with definitions, identifying assumption, then bottom-line estimand. In Beamer this can be separate frames or controlled overlays, but the final static version should still read coherently.
- Add a dedicated "Main threat" or "Identification vulnerability" frame that names the highest-stakes concern and previews the diagnostic or sensitivity evidence. Avoid multi-threat lists unless each threat matters for the audience's evaluation.
- Treat figures as the default Beamer results object. Use tables only for key magnitudes, with controls, robustness checks, and specification detail placed in backup.
- Make each results frame end with or visually foreground the bottom-line takeaway. The takeaway can be a title, annotation, or short text line, but it should be quantitative when the research supports it.
- Use overlays sparingly. Shapiro's "no pauses unless stressing something" is consistent with using `\pause`, `\only`, or adjacent build frames only for intentional emphasis, not routine bullet reveal.
- Scale the deck by talk length. A 15- or 30-minute version should remove sections and details, not compress the 90-minute deck.
- Use speaker notes and the paper for documentation. Main Beamer frames should contain only material the speaker intends to discuss.

## What This Would Change In Our Current Framework

- Add an explicit early-deck structure recommendation to `.claude/rules/slide-writing-principles.md`: motivation, research question, contribution, and preview of findings before data/model/detail.
- Add a data-slide rule: show each important variable's source and level of measurement; omit processing recipes unless they affect credibility or interpretation.
- Add a model-slide rule: define variables and identifying assumptions directly on the slide, and connect the estimand to the bottom-line policy, welfare, or economic quantity.
- Add a talk-length rule: make shorter talks by choosing fewer claims and less detail, not by shrinking fonts, accelerating delivery, or retaining every section.
- Current framework already covers sparse slides, one point per slide, figure-forward results, backup slides for dense material, and restrained overlays. Shapiro supports those rules, but does not require major changes there.

## Tensions Or Caveats

- Shapiro's advice is tuned to applied micro seminars. It transfers well to empirical economics talks, but less directly to theory lectures, methods tutorials, or classes where documentation and derivation may be part of the teaching objective.
- The advice is intentionally forceful and stylized. For example, "no pauses" is best read as a warning against casual bullet-by-bullet reveal, not as a ban on all controlled Beamer builds.
- The recommendation to lead with tangible findings assumes findings are stable enough to preview. For early-stage research, a preview may need to state preliminary patterns and what remains unresolved.
- "Applied questions are motivated by economics, not the literature" is valuable discipline, but literature positioning still matters for job talks, conference framing, and contribution claims. It should be subordinated to the economic question, not eliminated.
- Figures are encouraged wherever possible, but some identification or mechanism arguments may require equations, diagrams, or compact tables. The relevant principle is story clarity, not figure maximalism.

## Source Notes

- The PDF text identifies the talk as "How to Give an Applied Micro Talk: Unauthoritative Notes" by Jesse M. Shapiro, Chicago Booth and NBER ([Shapiro PDF](https://shapiro.scholars.harvard.edu/sites/g/files/omnuum7731/files/shapiro/files/applied_micro_slides.pdf)).
- Local PDF metadata from `pdfinfo` reports a 43-page PDF made with LaTeX Beamer, with creation and modification date April 6, 2013. This is metadata, not a publication citation.
- Access reconstruction: the assigned Harvard URL was valid by direct download on 2026-05-25. The legacy Brown URL, `https://www.brown.edu/Research/Shapiro/pdfs/applied_micro_slides.pdf`, returned a Brown "Page Not Found" HTML document during this check.
- No bibliography entry was added because the task requested a source report only, and the available source is an online slide PDF without fuller bibliographic publication details beyond the author/title/affiliation in the PDF itself.
