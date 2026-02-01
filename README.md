# Alex Baldwin's Personal Website

A personal website with an animated wave background, featuring Finds (curated links), Writing, Publications, and Projects. All content appears on the homepage in a filterable masonry grid with light semi-transparent cards.

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

## Editing Page Text

### Homepage (Hero Section)

Edit `index.html` directly. Look for the hero section near the top:

```html
<section class="hero container">
  <p class="hero__greeting">Biomedical Engineer & Researcher</p>
  <h1 class="hero__title">Hi, I'm Alex Baldwin</h1>
  <p class="hero__description">
    Building the future of bioelectronic medicine...
  </p>
</section>
```

### About Page

Edit `about.html` directly. The main content is in the `<div class="about__content prose">` section:

```html
<div class="about__content prose">
  <p>
    I'm a biomedical engineer and researcher...
  </p>
  <!-- Add more paragraphs, headings, etc. -->
</div>
```

### Footer & Social Links

The footer appears in all HTML files. To update social links, edit the `<footer>` section and the social links in the hero section of `index.html`.

---

## Content Management

All dynamic content is stored in the `_data/` folder. After editing, run the build script to update the HTML.

### Writing (Essays & Stories)

**Option 1: Add .docx files (easiest)**

1. Place your `.docx` file in `writing/Original Files/`
2. Run `python3 scripts/build.py`
3. The script will automatically:
   - Extract the title from the filename
   - Get the creation date from the file
   - Guess the category (fiction/nonfiction) based on keywords
   - Convert it to Markdown and generate the HTML page

**Option 2: Create Markdown directly**

1. Create a new `.md` file in `_data/writings/` (e.g., `my-story.md`)
2. Use this format:
   ```markdown
   # Your Title Here

   # January 29, 2026

   # fiction

   Your content starts here. You can use **bold**, *italic*,
   [links](https://example.com), and other Markdown formatting.

   ## Subheadings work too

   Separate paragraphs with blank lines.
   ```
3. Run `python3 scripts/build.py`

**Markdown format:**
- First `#` header = Title
- Second `#` header = Date (format: "Month Day, Year")
- Third `#` header = Category (`fiction` or `nonfiction`)
- Everything after = Content

**To edit a writing after conversion:**
- Edit the `.md` file in `_data/writings/` (not the .docx)
- The build script won't overwrite your edits as long as the .md file is newer than the .docx

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

Publications are automatically sorted by year (newest first).

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

---

## Build Script

The build script (`scripts/build.py`) does the following:

1. Converts `.docx` files from `writing/Original Files/` to Markdown
2. Reads JSON files from `_data/`
3. Reads Markdown files from `_data/writings/`
4. For URLs, attempts to fetch Open Graph metadata (title, description, image)
5. Generates HTML cards for each content type
6. Inserts content between `<!-- BEGIN:section -->` and `<!-- END:section -->` markers
7. Generates individual HTML pages for each writing

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
│   ├── Original Files/   # Source .docx files (gitignored)
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

## Visual Design

The site features:
- **Animated wave background** - Blue/cyan/green SVG waves
- **Light semi-transparent cards** - White 90% opacity for readability
- **Single color scheme** - No dark/light mode toggle

### Customizing Colors

Edit the CSS custom properties in `css/style.css`:

```css
:root {
  --color-accent: #22d3ee;        /* Cyan accent for links/hover */
  --color-text: #f0f9ff;          /* Light text on dark background */
  /* ... */
}
```

Card colors are hardcoded for the light backgrounds:
- Titles: `#0c4a6e` (dark blue)
- Body text: `#334155` (slate)
- Meta text: `#64748b` (gray)
- Links: `#0891b2` (cyan)

### Customizing the Wave Background

The animated SVG is embedded in each HTML file after the `<body>` tag. To change colors, edit the `<linearGradient>` definitions in the SVG.

### Fonts

The site uses [Inter](https://fonts.google.com/specimen/Inter). To change it, update the Google Fonts link in the HTML `<head>` and the `--font-sans` CSS variable.

---

## Homepage Filter Buttons

The homepage displays all content in a filterable grid:
- **All** - Show everything
- **My Writing** - Your essays and stories
- **My Publications** - Academic publications
- **My Projects** - Projects you've built
- **Links** - Curated web links
- **Books** - Book recommendations
- **Papers** - Academic papers you've found
- **Surprise me** - Opens a random item

---

## Deployment

The site is designed for GitHub Pages. Push to the `main` branch and it will automatically deploy.

```bash
git add -A
git commit -m "Update content"
git push
```
