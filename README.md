# UMU Curriculum Designer

**A faculty-facing curriculum revision and lecture-planning application for Usha Martin University, Ranchi.**

UMU Curriculum Designer helps faculty prepare a review copy of an existing course syllabus, consider carefully selected curriculum-enrichment activities, and generate a structured teaching plan. It is a drafting and review aid, **not** a system that automatically approves curriculum changes.

## What the application does

1. **Capture course information:** programme, faculty name, faculty/department, semester, course title and code, credits, teaching weeks and weekly lecture hours.
2. **Preserve the original syllabus:** enter approved Course Outcomes (COs), unit titles, original topic descriptions and unit-wise lecture hours. The original topic text is retained in the revised Word document.
3. **Review optional AI, IKS and SDG additions:** faculty may enter proposed activities and supporting references, select a target unit, and decide whether to include each proposal. Included additions are shown in **bold, highlighted text** beside the corresponding original unit content.
4. **Check unit placement:** if a proposed activity says, for example, "Unit II" but its selected destination is "Unit I", the application displays a conflict warning and prevents Word export until the discrepancy is corrected. An unassigned or conflicting addition is not silently inserted into the wrong unit.
5. **Prepare a week-wise lecture plan:** distribute unit topics over the entered teaching weeks and lecture hours, with provisional CO mapping. Compact unit labels improve the readability of the teaching-plan table.
6. **Review workload calculations:** compare the sum of unit hours with scheduled contact hours. The application also shows an *illustrative* 30-notional-hours-per-credit calculation; this is **not asserted to be an approved UMU rule**.
7. **Export editable documents:** download a revised syllabus in Microsoft Word, a week-wise lecture and learning plan in Microsoft Word, or the entered course data as JSON. Saved JSON can be uploaded later to continue editing.

## Typical workflow

Open the application and follow the five guided steps:

**Course information → Course outcomes and units → AI/IKS/SDG additions → Lecture plan → Review and downloads.**

Use **Previous** and **Next** to navigate. Confirm all source references, unit allocations, CO mapping and teaching hours before sharing the exported documents for academic consideration.

## Run locally

Requires Python 3.10 or newer.

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

For Streamlit Community Cloud, select repository `Arithmetic-Power-Geometry/UMU-Curriculum-Designer`, branch `main`, and entry point `app.py`.

## Scope and limitations

- Suggested additions are **faculty-entered and reviewed**; this public edition does not claim to perform automatic, verified curriculum research.
- The week-wise CO mapping is provisional and requires academic verification.
- The 30-hours-per-credit notional calculation is illustrative and conditional on competent University authorization.
- The application does not constitute an academic approval workflow or replace University bodies, applicable statutes, or professional-council requirements.
- No authentication or secure multi-user storage is provided by this application. Do not enter confidential personal data or unpublished restricted institutional records into a public deployment.

## License

Copyright © 2026 **Mohammad Amir Khusru Akhtar**.

Licensed under the **Apache License, Version 2.0**. See [LICENSE](LICENSE), [NOTICE](NOTICE), and the [full Apache 2.0 license terms](https://www.apache.org/licenses/LICENSE-2.0).
