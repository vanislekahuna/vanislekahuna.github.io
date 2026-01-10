# vanislekahuna.github.io

Personal portfolio and blog exploring the intersection of Machine Learning and Climate Action to ensure that the future is Solarpunk!


## Bridging Cyberpunk inevitability into Solarpunk possibility

My vision of the future transforms the cyberpunk trajectory we're on, where technology increasingly dominates nature, into a solarpunk reality where AI becomes nature's ally. A future where safe and responsible AI augments our fight against climate change. By enhancing human intelligence with machine learning for climate applications like wildfire prediction, ecosystem restoration, or effective energy policy, we can redirect our technological momentum from extraction to symbiosis. By changing our trajectory, a golden age of humanity can be actualized with the technological advancements of today so that the next generation not only inherits a habitable planet, but a thriving one.


## Technology Stack

- **Jekyll** - Static site generator
- **GitHub Pages** - Hosting platform
- **Kramdown** - Markdown processor
- **Rouge** - Syntax highlighting
- **SCSS** - Styling

## Site Structure
```
vanislekahuna.github.io/
├── _config.yml              # Site configuration
├── _layouts/                # Page templates
│   ├── default.html         # Base layout with navigation
│   ├── post.html           # Blog post layout
│   └── page.html           # Static page layout
├── _posts/                 # Blog posts (YYYY-MM-DD-title.md)
├── _sass/                  # SCSS partials
├── images/                 # Image assets
├── js/                     # JavaScript files
├── projects/              # Custom project files
├── about.md               # About page
├── climate-ai.html        # Climate Change/AI page
├── index.html             # Homepage (blog listing)
└── style.scss             # Main stylesheet
```

## How to Add Content

### Adding a New Blog Post

1. **Create a new file** in the `_posts/` directory with the format:
```
   YYYY-MM-DD-your-post-title.md
```
   Example: `2024-11-21-climate-ai-trends.md`

2. **Add YAML front matter** at the top of the file:
```yaml
   ---
   layout: post
   title: "Your Post Title: Subtitle Goes Here"
   categories: [climate-ai]
   ---
```
   
   **Important notes:**
   - Always wrap titles containing colons (`:`) in quotes
   - Use `categories: [climate-ai]` to show posts on the Climate_Change/AI page
   - Omit categories or use different ones for general blog posts

3. **Write your content** using Markdown below the front matter

4. **Commit and push** to GitHub - changes appear in 1-2 minutes

### Adding Images to Posts

1. **Upload images** to the `/images/` directory (organize in subfolders as needed):
```
   images/
   └── your-project-name/
       └── your-image.jpg
```

2. **Reference images** in your posts:
```html
   <img src="{{ site.baseurl }}/images/your-project-name/your-image.jpg" alt="Description">
```
   
   Or with full HTML:
```html
   <figure>
       <img src="{{ site.baseurl }}/images/your-project-name/your-image.jpg" style="width:100%">
       <figcaption>Your caption here</figcaption>
   </figure>
```

### Embedding Jupyter Notebooks

**Option 1: Direct link to nbviewer**
```markdown
[View Interactive Notebook](https://nbviewer.org/github/vanislekahuna/repo-name/blob/main/notebooks/your-notebook.ipynb)
```

**Option 2: Embed using iframe**
```html
<iframe src="https://nbviewer.org/github/vanislekahuna/repo-name/blob/main/notebooks/your-notebook.ipynb" 
        width="100%" 
        height="800px" 
        frameborder="0">
</iframe>
```

## How to Create a New Page

### Creating a Category Page (like Climate_Change/AI)

1. **Create a new HTML file** in the root directory (e.g., `new-category.html`):
```html
   ---
   layout: default
   title: Your Category Name
   ---

   <div class="posts">
     {% for post in site.categories.your-category %}
       <article class="post">
         <h1><a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a></h1>
         <div class="entry">
           {{ post.excerpt }}
         </div>
         <a href="{{ site.baseurl }}{{ post.url }}" class="read-more">Read More</a>
       </article>
     {% endfor %}
   </div>
```

2. **Add to navigation** in `_layouts/default.html` (around line 33):
```html
   <nav>
     <a href="{{ site.baseurl }}/about">About</a>
     <a href="https://vanislekahuna.github.io/Statistical-Rethinking-PyMC/">Bayesian_ML</a>
     <a href="{{ site.baseurl }}/climate-ai">Climate_Change/AI</a>
     <a href="{{ site.baseurl }}/new-category">New Category</a>
   </nav>
```

### Creating a Static Page (like About)

1. **Create a markdown file** in the root directory (e.g., `contact.md`):
```markdown
   ---
   layout: page
   title: Contact
   permalink: /contact/
   ---

   Your page content here...
```

2. **Add to navigation** in `_layouts/default.html`

## How to Add/Reorder Navigation Tabs

Edit `_layouts/default.html` (lines 32-37):
```html
<nav>
  <a href="{{ site.baseurl }}/about">About</a>
  <a href="https://vanislekahuna.github.io/Statistical-Rethinking-PyMC/">Bayesian_ML</a>
  <a href="{{ site.baseurl }}/climate-ai">Climate_Change/AI</a>
  <!-- Add new tabs here -->
</nav>
```

**Order matters** - tabs appear left-to-right in the order listed.

## Design Customization

### Changing Colors/Theme

Edit `_sass/_variables.scss` to modify:
- Light mode colors: `$light-bg`, `$light-text`, etc.
- Dark mode colors: `$dark-bg`, `$dark-text`, etc.
- Accent colors: `$blue`, `$green`, `$darkgreen`

### Changing Fonts

Edit `_sass/_variables.scss`:
```scss
$helvetica: Helvetica, Arial, sans-serif;
$monospace: 'Courier New', Courier, monospace;
```

Then update `style.scss` to apply fonts to different elements.

### Adding Custom CSS

Add custom styles to `style.scss` after the imports:
```scss
// Your custom CSS here
.your-custom-class {
  property: value;
}
```

### Centering Post Titles

In `style.scss`, add to the `.post` section (around line 280):
```scss
.post {
  > h1 {
    text-align: center;
  }
  // ... rest of styles
}
```

## Site Configuration

Edit `_config.yml` to update:
- Site name and description
- Social media links (footer icons)
- Avatar image
- Base URL
- Navigation links

Example:
```yaml
name: vanisle_kahuna
description: Building the BioCyberse future.
avatar: https://raw.githubusercontent.com/vanislekahuna/jekyll-now/master/images/your-avatar.png
```

## Troubleshooting

### Post Not Appearing

**Issue**: New post doesn't show up on the site

**Solutions**:
- ✅ Check filename format: `YYYY-MM-DD-title.md`
- ✅ Ensure YAML front matter is valid (no unquoted colons in title)
- ✅ For category pages, verify the `categories:` field matches
- ✅ Wait 1-2 minutes for GitHub Pages to rebuild
- ✅ Hard refresh browser (Ctrl+Shift+F5 or Cmd+Shift+R)

### Images Not Loading

**Issue**: Images appear blank or broken

**Solutions**:
- ✅ Move images to `/images/` directory (not `/_posts/`)
- ✅ Use correct path: `{{ site.baseurl }}/images/your-image.jpg`
- ✅ Check image file actually exists in repository
- ✅ Verify image filename matches exactly (case-sensitive)

### YAML Parsing Errors

**Issue**: "Error in user YAML" or page won't render

**Solutions**:
- ✅ Wrap titles containing colons in quotes: `title: "Title: Subtitle"`
- ✅ Check for proper indentation (use spaces, not tabs)
- ✅ Ensure all YAML values are valid
- ✅ Use [YAML validator](https://www.yamllint.com/) to check syntax

### CSS Changes Not Appearing

**Issue**: Style changes don't show up

**Solutions**:
- ✅ Clear browser cache / hard refresh
- ✅ Check for SCSS syntax errors
- ✅ Verify selectors are specific enough
- ✅ Wait for GitHub Pages rebuild (1-2 minutes)

### Category Page Empty

**Issue**: Category page shows no posts

**Solutions**:
- ✅ Verify posts have correct category in front matter
- ✅ Check category name matches exactly (case-sensitive)
- ✅ Ensure category page queries the right category:
```
  {% for post in site.categories.climate-ai %}
```

## Contributing

This is primarily a personal portfolio, but suggestions and corrections are welcome:

1. **Fork** the repository
2. **Create a branch** for your changes
3. **Make your edits** following the guidelines above
4. **Submit a pull request** with a clear description of changes

For major changes, please open an issue first to discuss proposed modifications.

## License

This project uses the [Jekyll Now](https://github.com/barryclark/jekyll-now) template. Content is © Ruiz Rivera. Feel free to reference or learn from the code structure, but please don't reproduce the content without permission.

---

**Live Site**: [https://vanislekahuna.github.io](https://vanislekahuna.github.io)  
**Statistical Rethinking Project**: [https://vanislekahuna.github.io/Statistical-Rethinking-PyMC/](https://vanislekahuna.github.io/Statistical-Rethinking-PyMC/)