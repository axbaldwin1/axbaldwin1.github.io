# Alex Baldwin's Personal Website

A minimal personal website with sections for Finds (curated links), Writing, Publications, and Projects.

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

## Adding Content

All content is stored in JSON files in the `_data/` folder. After editing, run the build script to update the HTML.

### Finds (Homepage)

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
| `url` | Yes* | Link to the content |
| `title` | No | Title (auto-fetched if missing) |
| `category` | Yes | `link`, `book`, `tool`, `paper`, `video`, or `quote` |
| `notes` | Yes | Your thoughts/description |
| `size` | No | Card size: `small`, `medium`, or `large` |
| `image` | No | Image URL (auto-fetched if missing) |

**For quotes** (no URL needed):
```json
{
  "category": "quote",
  "quote": "The actual quote text",
  "author": "Person's Name",
  "notes": "Optional context"
}
```

---

### Writing (Essays & Stories)

Writing requires two steps:

#### Step 1: Create the post file

Copy `writing/_template.html` to a new file:

```bash
cp writing/_template.html writing/my-new-post.html
```

Edit the file:
- Replace `POST_TITLE` with your title
- Replace `POST_DATE` with the date (e.g., "January 15, 2026")
- Replace `POST_DESCRIPTION` with a brief summary
- Write your content in the `<article class="prose">` section

#### Step 2: Add to the index

Edit `_data/writing.json`:

```json
{
  "slug": "my-new-post",
  "title": "My New Post Title",
  "date": "2026-01-15",
  "description": "A brief description of the post"
}
```

**Fields:**
| Field | Required | Description |
|-------|----------|-------------|
| `slug` | Yes | Filename without `.html` (must match your file) |
| `title` | Yes | Post title |
| `date` | Yes | Date in `YYYY-MM-DD` format |
| `description` | No | Brief description |

Then run `python3 scripts/build.py` to update the writing index.

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
| `url` | No | Link to paper (DOI, arXiv, etc.) |
| `authors` | Yes | Array of author names |
| `venue` | Yes | Journal/conference name |
| `year` | Yes | Publication year |
| `type` | Yes | `journal`, `conference`, `thesis`, `preprint`, or `workshop` |
| `image` | No | Custom image (defaults provided by type) |

---

### Projects

Edit `_data/projects.json`:

```json
{
  "title": "Project Name",
  "url": "https://github.com/...",
  "description": "What it does",
  "status": "active",
  "tech": ["Python", "React"],
  "image": "https://..."
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
| `image` | No | Project image (default provided) |

---

## Build Script

The build script (`scripts/build.py`) does the following:

1. Reads JSON files from `_data/`
2. For URLs, attempts to fetch Open Graph metadata (title, description, image)
3. Generates HTML and inserts it between `<!-- BEGIN:section -->` and `<!-- END:section -->` markers
4. Writes the updated HTML files

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
│   └── writing.json      # Writing index
├── writing/
│   ├── _template.html    # Template for new posts
│   └── *.html            # Individual posts
├── css/
│   └── style.css         # All styles
├── scripts/
│   └── build.py          # Build script
├── index.html            # Homepage
├── about.html            # About page
├── writing.html          # Writing index
├── publications.html     # Publications page
└── projects.html         # Projects page
```

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

The site is designed for GitHub Pages. Push to the `main` branch and it will automatically deploy to `https://yourusername.github.io`.

```bash
git add -A
git commit -m "Update content"
git push
```
