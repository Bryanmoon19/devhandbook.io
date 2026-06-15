#!/usr/bin/env python3
"""
Generate OG images for devhandbook.io blog posts.
Called by post-commit hook after Eleventy build.

Usage:
    python3 generate-og-image.py [post-slug]

If no slug provided, generates OG images for all blog posts missing them.
"""

import os
import re
import sys
import yaml
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# ── Paths ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.resolve()
BLOG_DIR = PROJECT_ROOT / "blog"
OG_IMAGE_DIR = PROJECT_ROOT / "_site" / "og-images"
OG_SOURCE_DIR = PROJECT_ROOT / "og-images"  # For passthrough

# ── Design Constants ───────────────────────────────────────────────
CARD_WIDTH = 1200
CARD_HEIGHT = 630
BG_COLOR = (251, 251, 253)       # #fbfbfd (Apple-style light bg)
BG_COLOR_DARK = (0, 0, 0)        # #000000 (dark mode reference)
ACCENT_BLUE = (0, 113, 227)      # #0071e3
TEXT_PRIMARY = (29, 29, 31)      # #1d1d1f
TEXT_SECONDARY = (110, 110, 115) # #6e6e73
TAG_BG = (0, 113, 227, 20)       # #0071e3 at low opacity

# ── Font Loading ───────────────────────────────────────────────────
def load_fonts():
    """Load fonts, falling back to defaults if not available."""
    fonts = {}
    
    # Try SF Pro fonts first (macOS)
    sf_pro_display = "/System/Library/Fonts/Helvetica.ttc"
    sf_pro_text = "/System/Library/Fonts/Helvetica.ttc"
    
    # Fallback font paths
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.dfont",
    ]
    
    def try_font(size, bold=False):
        for path in font_paths:
            try:
                if bold and ".ttc" in path:
                    return ImageFont.truetype(path, size, index=1)
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return ImageFont.load_default()
    
    fonts["title"] = try_font(52, bold=True)
    fonts["description"] = try_font(28)
    fonts["tag"] = try_font(20)
    fonts["meta"] = try_font(18)
    fonts["brand"] = try_font(24, bold=True)
    
    return fonts

# ── Color Utilities ────────────────────────────────────────────────
def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# ── Text Wrapping ──────────────────────────────────────────────────
def wrap_text(draw, text, font, max_width):
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # Word is too long, just add it
                lines.append(word)
                current_line = []
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

# ── Parse Blog Post Frontmatter ────────────────────────────────────
def parse_frontmatter(filepath):
    """Extract YAML frontmatter from a markdown blog post."""
    content = filepath.read_text()
    
    if not content.startswith('---'):
        return None
    
    # Find the end of frontmatter
    end_marker = content.find('\n---', 3)
    if end_marker == -1:
        return None
    
    try:
        frontmatter = yaml.safe_load(content[3:end_marker])
        return frontmatter
    except yaml.YAMLError:
        return None

# ── Generate Single OG Image ───────────────────────────────────────
def generate_og_image(post_file, output_path, fonts):
    """Generate an OG image for a single blog post."""
    fm = parse_frontmatter(post_file)
    if not fm:
        print(f"  ⚠️  Could not parse frontmatter for {post_file.name}")
        return False
    
    title = fm.get('title', 'Blog Post')
    description = fm.get('description', '')
    tags = fm.get('tags', [])
    date = fm.get('date')
    author = fm.get('author', 'Bryan Moon')
    
    # Create image
    img = Image.new('RGB', (CARD_WIDTH, CARD_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # ── Decorative elements ──────────────────────────────────────
    # Top accent bar
    draw.rectangle([0, 0, CARD_WIDTH, 4], fill=ACCENT_BLUE)
    
    # Subtle grid pattern (very light)
    grid_color = (240, 240, 242)
    for x in range(0, CARD_WIDTH, 60):
        draw.line([(x, 0), (x, CARD_HEIGHT)], fill=grid_color, width=1)
    for y in range(0, CARD_HEIGHT, 60):
        draw.line([(0, y), (CARD_WIDTH, y)], fill=grid_color, width=1)
    
    # ── Layout area ──────────────────────────────────────────────
    margin_left = 80
    margin_right = 80
    content_width = CARD_WIDTH - margin_left - margin_right
    
    # Brand / Logo area at top
    brand_y = 50
    draw.text((margin_left, brand_y), "devhandbook.io", font=fonts["brand"], fill=ACCENT_BLUE)
    
    # Author and date
    meta_parts = []
    if author:
        meta_parts.append(author)
    if date:
        if isinstance(date, datetime):
            meta_parts.append(date.strftime("%B %d, %Y"))
        else:
            meta_parts.append(str(date))
    
    meta_text = "  •  ".join(meta_parts) if meta_parts else ""
    if meta_text:
        draw.text((margin_left, brand_y + 35), meta_text, font=fonts["meta"], fill=TEXT_SECONDARY)
    
    # ── Title ──────────────────────────────────────────────────────
    title_y = 160
    title_lines = wrap_text(draw, title, fonts["title"], content_width)
    
    # Limit to 3 lines
    if len(title_lines) > 3:
        title_lines = title_lines[:3]
        title_lines[-1] = title_lines[-1][:50] + "..."
    
    for line in title_lines:
        draw.text((margin_left, title_y), line, font=fonts["title"], fill=TEXT_PRIMARY)
        # Get line height for next line
        bbox = draw.textbbox((0, 0), line, font=fonts["title"])
        line_height = bbox[3] - bbox[1]
        title_y += line_height + 12
    
    # ── Description ────────────────────────────────────────────────
    desc_y = title_y + 20
    if description:
        desc_lines = wrap_text(draw, description, fonts["description"], content_width)
        # Limit to 2 lines
        if len(desc_lines) > 2:
            desc_lines = desc_lines[:2]
            desc_lines[-1] = desc_lines[-1][:60] + "..."
        
        for line in desc_lines:
            draw.text((margin_left, desc_y), line, font=fonts["description"], fill=TEXT_SECONDARY)
            bbox = draw.textbbox((0, 0), line, font=fonts["description"])
            line_height = bbox[3] - bbox[1]
            desc_y += line_height + 8
    
    # ── Tags ─────────────────────────────────────────────────────
    if tags:
        tag_y = CARD_HEIGHT - 100
        tag_x = margin_left
        tag_spacing = 12
        
        for tag in tags[:4]:  # Max 4 tags
            tag_text = f"  {str(tag)}  "
            bbox = draw.textbbox((0, 0), tag_text, font=fonts["tag"])
            tag_width = bbox[2] - bbox[0]
            tag_height = bbox[3] - bbox[1] + 10
            
            # Tag background pill
            pill_radius = 6
            draw.rounded_rectangle(
                [tag_x, tag_y, tag_x + tag_width + 16, tag_y + tag_height + 6],
                radius=pill_radius,
                fill=(240, 248, 255),  # Very light blue
                outline=(0, 113, 227, 60),
                width=1
            )
            
            # Tag text
            draw.text((tag_x + 8, tag_y + 3), tag_text, font=fonts["tag"], fill=ACCENT_BLUE)
            
            tag_x += tag_width + 24 + tag_spacing
    
    # ── Footer decoration ────────────────────────────────────────
    # Small decorative dots
    dot_y = CARD_HEIGHT - 40
    for i in range(5):
        dot_x = CARD_WIDTH - 100 + (i * 14)
        draw.ellipse([dot_x, dot_y, dot_x + 6, dot_y + 6], fill=(0, 113, 227, 30))
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG", quality=95)
    
    return True

# ── Generate All Missing OG Images ─────────────────────────────────
def generate_all_missing():
    """Generate OG images for all blog posts missing them."""
    fonts = load_fonts()
    
    OG_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    
    blog_posts = sorted(BLOG_DIR.glob("*.md"))
    generated = 0
    skipped = 0
    
    print(f"🔍 Found {len(blog_posts)} blog posts")
    print(f"📁 OG images will be saved to: {OG_IMAGE_DIR}")
    print()
    
    for post_file in blog_posts:
        # Extract slug from filename
        slug = None
        # Try YYYY-MM-DD-slug.md format first
        match = re.match(r'\d{4}-\d{2}-\d{2}-(.+)\.md$', post_file.name)
        if match:
            slug = match.group(1)
        else:
            # Fallback: use the filename without extension as slug
            slug = post_file.stem
        
        if not slug:
            continue
        
        og_path = OG_IMAGE_DIR / f"{slug}.png"
        
        if og_path.exists():
            skipped += 1
            continue
        
        print(f"🎨 Generating OG image for: {slug}")
        success = generate_og_image(post_file, og_path, fonts)
        if success:
            generated += 1
            print(f"   ✅ Saved to {og_path}")
        else:
            print(f"   ❌ Failed")
    
    print()
    print(f"📊 Summary: {generated} generated, {skipped} already existed")
    return generated, skipped

# ── Generate for Specific Post ───────────────────────────────────
def generate_for_post(slug):
    """Generate OG image for a specific post slug."""
    fonts = load_fonts()
    
    # Find the post file
    post_file = None
    for f in BLOG_DIR.glob("*.md"):
        if slug in f.name:
            post_file = f
            break
    
    if not post_file.exists():
        print(f"❌ Post not found: {slug}")
        return False
    
    OG_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    og_path = OG_IMAGE_DIR / f"{slug}.png"
    
    print(f"🎨 Generating OG image for: {slug}")
    success = generate_og_image(post_file, og_path, fonts)
    if success:
        print(f"✅ Saved to {og_path}")
    return success

# ── Update Post Layout to Include OG Image ───────────────────────
def update_post_layout():
    """
    Modify the post.njk layout to include og:image meta tag.
    This should be run once during setup.
    """
    layout_path = PROJECT_ROOT / "_layouts" / "post.njk"
    
    if not layout_path.exists():
        print("❌ _layouts/post.njk not found")
        return False
    
    content = layout_path.read_text()
    
    # Check if og:image is already present
    if "og:image" in content:
        print("ℹ️  og:image already present in post.njk")
        return True
    
    # Find the Open Graph section and add og:image
    og_section = '<meta property="og:site_name" content="devhandbook.io">'
    if og_section in content:
        new_og = '''<meta property="og:site_name" content="devhandbook.io">
  <meta property="og:image" content="https://devhandbook.io/og-images/{{ page.fileSlug }}.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">'''
        content = content.replace(og_section, new_og)
        
        # Also add twitter:image
        twitter_section = '<meta name="twitter:card" content="summary">'
        if twitter_section in content:
            new_twitter = '''<meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://devhandbook.io/og-images/{{ page.fileSlug }}.png">'''
            content = content.replace(twitter_section, new_twitter)
        
        layout_path.write_text(content)
        print("✅ Updated _layouts/post.njk with og:image and twitter:image")
        return True
    else:
        print("⚠️  Could not find Open Graph section in post.njk")
        return False

# ── Update Eleventy Config ────────────────────────────────────────
def update_eleventy_config():
    """Add og-images passthrough to .eleventy.js."""
    config_path = PROJECT_ROOT / ".eleventy.js"
    
    if not config_path.exists():
        print("❌ .eleventy.js not found")
        return False
    
    content = config_path.read_text()
    
    if "og-images" in content:
        print("ℹ️  og-images passthrough already in .eleventy.js")
        return True
    
    # Find the last passthrough copy line and add after it
    lines = content.split('\n')
    last_passthrough_idx = -1
    for i, line in enumerate(lines):
        if 'addPassthroughCopy' in line:
            last_passthrough_idx = i
    
    if last_passthrough_idx >= 0:
        lines.insert(last_passthrough_idx + 1, '  eleventyConfig.addPassthroughCopy("og-images");')
        config_path.write_text('\n'.join(lines))
        print("✅ Updated .eleventy.js with og-images passthrough")
        return True
    else:
        print("⚠️  Could not find passthrough lines in .eleventy.js")
        return False

# ── Update Post-Commit Hook ──────────────────────────────────────
def update_post_commit_hook():
    """Add OG image generation to the post-commit hook."""
    hook_path = PROJECT_ROOT / ".git" / "hooks" / "post-commit"
    
    if not hook_path.exists():
        print("❌ post-commit hook not found")
        return False
    
    content = hook_path.read_text()
    
    if "generate-og-image.py" in content:
        print("ℹ️  OG image generation already in post-commit hook")
        return True
    
    # Find the deploy line and add OG generation before it
    if 'npx wrangler pages deploy' in content:
        new_content = content.replace(
            'npx wrangler pages deploy',
            '''# Generate OG images for new blog posts
echo "🎨 Generating OG images..."
python3 generate-og-image.py

npx wrangler pages deploy'''
        )
        hook_path.write_text(new_content)
        print("✅ Updated post-commit hook with OG image generation")
        return True
    else:
        print("⚠️  Could not find deploy line in post-commit hook")
        return False

# ── Main ─────────────────────────────────────────────────────────
def main():
    if len(sys.argv) > 1:
        slug = sys.argv[1]
        if slug == "--setup":
            print("🔧 Running OG Image Generator Setup")
            print("=" * 50)
            update_post_layout()
            update_eleventy_config()
            update_post_commit_hook()
            print("=" * 50)
            print("✅ Setup complete!")
            print()
            print("Next: Generate OG images for all posts:")
            print("  python3 generate-og-image.py")
            return
        elif slug == "--all":
            generate_all_missing()
            return
        else:
            generate_for_post(slug)
            return
    
    # Default: generate all missing
    generate_all_missing()

if __name__ == "__main__":
    main()
