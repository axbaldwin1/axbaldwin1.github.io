# Claude's Project Memory

## Project Overview
Alex Baldwin's personal website - a static site with masonry grid layout displaying Finds, Writing, Publications, and Projects. Features an animated SVG wave background with blue/cyan/green color scheme. Hosted on GitHub Pages.

## Key Commands
- **Preview locally:** `python3 -m http.server 8000`
- **Build site:** `python3 scripts/build.py`
- **Deploy:** `git push` (auto-deploys to GitHub Pages)

## Content Locations
- `_data/finds.json` - Curated links (categories: link, book, paper, video)
- `_data/writings/*.md` - Markdown files for essays/stories (title = 1st header, date = 2nd header, category = 3rd header)
- `_data/publications.json` - Academic publications
- `_data/projects.json` - Projects with local images in `/images/`
- `writing/Original Files/` - Source .docx files (gitignored, auto-converted to markdown)

## Technical Notes
- Build script is Python (`scripts/build.py`), NOT Node.js
- Node.js is not in PATH on this machine
- Writings use simple Markdown-to-HTML conversion built into build.py
- All content types appear on homepage in filterable masonry grid
- Filter buttons: My Writing, My Publications, My Projects, Links, Books, Papers
- DOCX files in `writing/Original Files/` are auto-converted to markdown by build.py
  - Only converts if markdown doesn't exist or docx is newer (preserves manual edits)
  - Category (fiction/nonfiction) is guessed from keywords but can be edited in .md file

## Visual Design
- **Background:** Animated SVG waves with blue/cyan/green gradients (no purple)
- **Color scheme:** Single unified scheme (no dark/light mode toggle)
  - Dark animated wave background
  - Light semi-transparent cards (white 90% opacity) for readability
  - Dark text on cards (#0c4a6e titles, #334155 body, #64748b meta)
  - Cyan accents (#0891b2) for links and hover states
- **Cards:** All cards use `rgba(255, 255, 255, 0.9)` background with subtle cyan borders
- **Wave SVG** is embedded directly in each HTML page after `<body>` tag

## Current Content (as of Feb 2026)
- **Projects:** OpenNerve, OpenAVNS, Susuro Mood Tracker
- **Publications:** 8 papers (2016-2025) in IEEE, Springer, MDPI
- **Finds:** 4 curated links
- **Writing:** 15 pieces (fiction and nonfiction essays)

## Social Links
- GitHub: axbaldwin1
- LinkedIn: alexbbaldwin
- Instagram: axbaldwin
- Google Scholar: user=5WecH7IAAAAJ

## Recent Changes (Feb 2026)
- Added animated SVG wave background to all pages
- Single color scheme (removed dark/light mode toggle)
- Light semi-transparent card backgrounds for all content cards
- Readable text colors on light card backgrounds
- Added DOCX-to-Markdown auto-conversion for writings
- Added fiction/nonfiction categories for writing pieces
- Added copyright notices to writing pages
- Publications page: horizontal card layout with images on left, sorted by year
- Homepage masonry: publications show without images for cleaner look
