# README and Submission Screenshot Checklist

Use this checklist when you capture final screenshots for the public GitHub repo, PPT, and hackathon gallery.

## Recommended screenshot order

1. `PocketSignal overview`
- Show the hero section and the two main panels.
- Keep the screen clean with no partial loading states.

2. `Approve exact case`
- Run the saved `Approve` case.
- Show:
  - low risk result
  - decision board row
  - no flagged recovery conversation added

3. `Flag exact case in English`
- Use `Richer wording` or `Faster wording`, depending on the demo take you want to show.
- Show:
  - `Flag` status
  - risk score
  - recovery message
  - top reasons

4. `Flag exact case in Bahasa Melayu`
- Switch message language to `Bahasa Melayu`.
- Show the local recovery message clearly.

5. `Block exact case`
- Show:
  - `Block` status
  - high risk score
  - decision board row

6. `Architecture diagram`
- Export the draw.io diagram or slide version.
- Keep labels large and simple enough to read inside GitHub.

## Screenshot quality rules

- Use desktop resolution, not a tiny cropped window.
- Do not show terminal clutter unless the screenshot is specifically for `/health`.
- Do not capture half-rendered LLM messages.
- Use exact saved cases, not manual partial input, for all judge-facing screenshots.

## Where to store them

Recommended folder:

- `docs/assets/`

Recommended file names:

- `docs/assets/overview.png`
- `docs/assets/approve_case.png`
- `docs/assets/flag_case_en.png`
- `docs/assets/flag_case_bm.png`
- `docs/assets/block_case.png`
- `docs/assets/architecture.png`

## How to use them

- Add 1 to 2 images in the `README.md`
- Add 3 to 5 images across the slides
- Keep the rest ready in case judges open the repo during evaluation
