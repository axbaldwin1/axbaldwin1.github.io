# Alex Baldwin's Personal Website

A minimal personal website with sections for Finds (curated links), Writing, Publications, and Projects. All content appears on the homepage in a filterable masonry grid.

## Quick Start

```bash
# Preview locally
python3 -m http.server 8000

# Build (after editing content)
python3 scripts/build.py

# Deploy
git add -A && git commit -m "Update content" && git push
```

---

## Content Management

All content is stored in the `_data/` folder. After editing, run the build script to update the HTML.

### Finds (Curated Links)

Edit `_data/finds.json`:

```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "category": "link",
  "notes": "Why I found this interesting",
  "size": "medium",
  "image": "https://..."
}
```

**Fields:**
| Field | Required | Description |
|-------|----------|-------------|
| `url` | Yes | Link to the content |
| `title` | No | Title (auto-fetched from URL if missing) |
| `category` | Yes | `link`, `book`, `paper`, or `video` |
| `notes` | Yes | Your thoughts/description |
| `size` | No | Card size: `small`, `medium`, or `large` |
| `image` | No | Image URL (auto-fetched from URL if missing) |

**To add a find:**
1. Add a new entry to `_data/finds.json`
2. Run `python3 scripts/build.py`

**To remove a find:**
1. Delete the entry from `_data/finds.json`
2. Run `python3 scripts/build.py`

---

### Writing (Essays & Stories)

Writings are Markdown files in `_data/writings/`. The build script converts them to HTML automatically.

**To add a new writing:**

1. Create a new `.md` file in `_data/writings/` (e.g., `my-story.md`)
2. Use this format:
   ```markdown
   # Your Title Here

   # January 29, 2026

   Your content starts here. You can use **bold**, *italic*,
   [links](https://example.com), and other Markdown formatting.

   ## Subheadings work too

   Separate paragraphs with blank lines.
   ```
3. Run `python3 scripts/build.py`

The build script will:
- Extract the title from the first `#` header
- Extract the date from the second `#` header
- Convert the rest to HTML
- Generate a page at `writing/your-title-here.html`
- Update `writing.html` with the new entry (sorted by date, newest first)
- Add it to the homepage grid

**To remove a writing:**
1. Delete the `.md` file from `_data/writings/`
2. Delete the corresponding `.html` file from `writing/`
3. Run `python3 scripts/build.py`

**Supported Markdown:**
- Headers (`#`, `##`, `###`)
- Bold (`**text**`) and italic (`*text*`)
- Links (`[text](url)`)
- Blockquotes (`> text`)
- Unordered lists (`- item`)
- Horizontal rules (`---`)
- Inline code (`` `code` ``)

---

### Publications

Edit `_data/publications.json`:

```json
{
  "title": "Paper Title",
  "url": "https://doi.org/...",
  "authors": ["A. Baldwin", "B. Coauthor"],
  "venue": "Journal Name",
  "year": 2024,
  "type": "journal"
}
```

**Fields:**
| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Paper title |
| `url` | No | Link to paper (DOI, publisher, etc.) |
| `authors` | Yes | Array of author names |
| `venue` | Yes | Journal/conference name |
| `year` | Yes | Publication year |
| `type` | Yes | `journal`, `conference`, `thesis`, `preprint`, or `workshop` |
| `image` | No | Custom image URL |

**To add a publication:**
1. Add a new entry to `_data/publications.json`
2. Run `python3 scripts/build.py`

**To remove a publication:**
1. Delete the entry from `_data/publications.json`
2. Run `python3 scripts/build.py`

---

### Projects

Edit `_data/projects.json`:

```json
{
  "title": "Project Name",
  "url": "https://github.com/...",
  "description": "What it does",
  "status": "active",
  "tech": ["Python", "Hardware"],
  "image": "/images/project-logo.png"
}
```

**Fields:**
| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Project name |
| `url` | No | Link to project |
| `description` | Yes | What the project does |
| `status` | Yes | `active` or `completed` |
| `tech` | No | Array of technologies used |
| `image` | No | Project image (local path or URL) |

**To add a project:**
1. Add a new entry to `_data/projects.json`
2. Optionally add a logo to `images/` folder
3. Run `python3 scripts/build.py`

**To remove a project:**
1. Delete the entry from `_data/projects.json`
2. Run `python3 scripts/build.py`

---

## Build Script

The build script (`scripts/build.py`) does the following:

1. Reads JSON files from `_data/`
2. Reads Markdown files from `_data/writings/`
3. For URLs, attempts to fetch Open Graph metadata (title, description, image)
4. Generates HTML cards for each content type
5. Inserts content between `<!-- BEGIN:section -->` and `<!-- END:section -->` markers
6. Generates individual HTML pages for each writing

Run it after any content changes:

```bash
python3 scripts/build.py
```

---

## File Structure

```
.
├── _data/
│   ├── finds.json        # Curated links for homepage
│   ├── publications.json # Scientific publications
│   ├── projects.json     # Projects
│   └── writings/         # Markdown files for writing
│       └── *.md
├── writing/
│   ├── _template.html    # Template for generated pages
│   └── *.html            # Generated writing pages
├── images/               # Local images (logos, etc.)
├── css/
│   └── style.css         # All styles
├── scripts/
│   └── build.py          # Build script
├── index.html            # Homepage with masonry grid
├── about.html            # About page
├── writing.html          # Writing index
├── publications.html     # Publications page
└── projects.html         # Projects page
```

---

## Homepage Filter Buttons

The homepage displays all content in a filterable grid. Filter buttons include:
- **All** - Show everything
- **My Writing** - Your essays and stories
- **My Publications** - Academic publications
- **My Projects** - Projects you've built
- **Links** - Curated web links
- **Books** - Book recommendations
- **Papers** - Academic papers you've found
- **Surprise me** - Opens a random item

---

## Customization

### Colors

Edit the CSS custom properties in `css/style.css`:

```css
:root {
  --color-accent: #0891b2;      /* Primary accent color */
  --color-bg: #f8fafc;          /* Background */
  --color-text: #0f172a;        /* Text */
  /* ... */
}
```

Dark mode colors are in `[data-theme="dark"]`.

### Fonts

The site uses [Inter](https://fonts.google.com/specimen/Inter). To change it, update the Google Fonts link in the HTML `<head>` and the `--font-sans` CSS variable.

---

## Deployment

The site is designed for GitHub Pages. Push to the `main` branch and it will automatically deploy.

```bash
git add -A
git commit -m "Update content"
git push
```
