# Claude's Project Memory

## Project Overview
Alex Baldwin's personal website - a static site with masonry grid layout displaying Finds, Writing, Publications, and Projects. Hosted on GitHub Pages.

## Key Commands
- **Preview locally:** `python3 -m http.server 8000`
- **Build site:** `python3 scripts/build.py`
- **Deploy:** `git push` (auto-deploys to GitHub Pages)

## Content Locations
- `_data/finds.json` - Curated links (categories: link, book, paper, video)
- `_data/writings/*.md` - Markdown files for essays/stories (title = 1st header, date = 2nd header)
- `_data/publications.json` - Academic publications
- `_data/projects.json` - Projects with local images in `/images/`

## Technical Notes
- Build script is Python (`scripts/build.py`), NOT Node.js
- Node.js is not in PATH on this machine
- Writings use simple Markdown-to-HTML conversion built into build.py
- All content types appear on homepage in filterable masonry grid
- Filter buttons: My Writing, My Publications, My Projects, Links, Books, Papers

## Current Content (as of Jan 2026)
- **Projects:** OpenNerve, OpenAVNS, Susuro Mood Tracker
- **Publications:** 8 papers (2016-2025) in IEEE, Springer, MDPI
- **Finds:** 4 curated links
- **Writing:** 1 sample story ("The Signal in the Static")

## Social Links
- GitHub: axbaldwin1
- LinkedIn: alexbbaldwin
- Instagram: axbaldwin
- Google Scholar: user=5WecH7IAAAAJ
