# Design Consistency Guide

## Overview
This document outlines the standardization of guweb's UI components to match hanayo style with improved consistency and usability.

## Design System

### Color Palette
- **Primary**: `#0088cc` (buttons, links, primary actions)
- **Success**: `#21ba45` (success states, positive actions)
- **Danger**: `#db2828` (errors, destructive actions)
- **Warning**: `#f2c037` (warnings, caution)
- **Background**: `#2d2d42` (cards, containers)
- **Secondary BG**: `#35354a` (inputs, secondary containers)
- **Text**: `#ffffff` (primary text)
- **Text Muted**: `rgba(255, 255, 255, 0.7)` (secondary text)

### Component Standards

#### Buttons
Always use `.btn` base class with modifiers:
```html
<!-- Primary button -->
<button class="btn btn-primary">Click Me</button>

<!-- Secondary button -->
<button class="btn btn-secondary">Cancel</button>

<!-- Full width button -->
<button class="btn btn-primary btn-full">Submit</button>

<!-- Large button -->
<button class="btn btn-primary btn-large">Get Started</button>
```

**DO NOT USE:**
- Inline styles for margins: ❌ `style="margin-top: 0.75rem"`
- Custom button classes without `.btn` base

**DO USE:**
- Utility classes: ✅ `.mt-3`, `.mb-4`
- Consistent class patterns: ✅ `.btn.btn-primary`

#### Form Controls
Always use `.control` pattern with icons:
```html
<div class="control has-icons-left">
  <input type="text" class="input" placeholder="Username" />
  <span class="icon is-left">
    <i class="fa fa-user"></i>
  </span>
</div>
```

**Standardized class**: `.input` (NOT `.input-base`, `.input-with-icon`, etc.)

#### Input Groups
For input + button combinations:
```html
<div class="input-group">
  <div class="input-group-flex">
    <input type="email" class="input" placeholder="Email" />
  </div>
  <button class="btn btn-primary">Send</button>
</div>
```

#### Cards & Containers
```html
<!-- Standard card -->
<div class="card">
  <h3>Title</h3>
  <p>Content</p>
</div>

<!-- Accent card with left border -->
<div class="card card-accent-primary">
  <h3>Important Info</h3>
</div>
```

### Spacing System
**Use utility classes instead of inline styles:**

| Spacing | Class | Value |
|---------|-------|-------|
| Extra small | `.m-1`, `.p-1` | 0.25rem |
| Small | `.m-2`, `.p-2` | 0.5rem |
| Medium | `.m-3`, `.p-3` | 0.75rem |
| Base | `.m-4`, `.p-4` | 1rem |
| Large | `.m-5`, `.p-5` | 1.5rem |
| Extra large | `.m-6`, `.p-6` | 2rem |

**Examples:**
- `.mt-3` - margin-top: 0.75rem
- `.mb-4` - margin-bottom: 1rem
- `.px-5` - padding left/right: 1.5rem
- `.my-6` - margin top/bottom: 2rem

### Layout Utilities
**Flexbox:**
```html
<div class="flex items-center justify-between gap-4">
  <!-- Content -->
</div>
```

**Text Alignment:**
```html
<p class="text-center">Centered text</p>
<p class="text-lg">Large text</p>
<p class="font-bold">Bold text</p>
```

## Common Patterns

### Auth Pages (Login, Register, Forgot)
```html
<div class="main-block is-auth">
  <div class="auth-header">
    <div class="auth-icon">
      <i class="fas fa-sign-in-alt"></i>
    </div>
    <h1 class="title">Page Title</h1>
    <p class="subtitle">Description</p>
  </div>
  
  <div class="box">
    <form>
      <!-- Form controls -->
    </form>
  </div>
</div>
```

### Headers with Icons
```html
<div class="auth-header">
  <div class="auth-icon">
    <i class="fas fa-icon-name"></i>
  </div>
  <h1 class="title">Title</h1>
  <p class="subtitle">Subtitle</p>
</div>
```

### Empty States
```html
<div class="empty-state">
  <div class="empty-icon">
    <i class="fas fa-inbox"></i>
  </div>
  <h3 class="empty-title">No items found</h3>
  <p class="empty-text">Try adding some items first</p>
</div>
```

## Migration Checklist

### ✅ Completed
- [x] Buttons unified to `.btn` pattern
- [x] Boxes/cards unified to `.card` pattern
- [x] Form controls standardized to `.control` + `.input`
- [x] Auth pages (login, register, forgot) cleaned up
- [x] Removed duplicate inline styles from auth pages
- [x] Added utility class system (spacing, flexbox, text)

### 🔄 In Progress
- [ ] Remove all inline styles from templates
- [ ] Replace `style="..."` with utility classes
- [ ] Standardize all form inputs to use `.input` (not `.input-base`)
- [ ] Ensure consistent card usage across pages

### ⏳ Todo
- [ ] Profile page component cleanup
- [ ] Beatmap page inline style removal (partial)
- [ ] Score page inline style removal
- [ ] Home page inline style removal  
- [ ] Leaderboard page inline style removal
- [ ] Rules page inline style removal
- [ ] Verify page inline style removal
- [ ] HowToConnect page inline style removal

## Anti-Patterns to Avoid

### ❌ Don't Do This
```html
<!-- Inline styles -->
<div style="margin-top: 1rem; text-align: center;">
  <button style="background: #0088cc; padding: 12px 24px;">Click</button>
</div>

<!-- Mixed class names -->
<input class="input-base" />
<input class="input-with-icon" />
<input class="input" />

<!-- Custom CSS in <style> tags -->
<style>
  .my-custom-button {
    background: blue;
  }
</style>
```

### ✅ Do This Instead
```html
<!-- Utility classes -->
<div class="mt-4 text-center">
  <button class="btn btn-primary">Click</button>
</div>

<!-- Consistent class names -->
<input class="input" />
<input class="input" />
<input class="input" />

<!-- Use existing component CSS -->
<!-- CSS lives in /static/css/components/ files -->
```

## CSS Architecture

```
/static/css/
├── style-new.css (main import file)
├── design-system.css (CSS variables, base styles)
└── components/
    ├── buttons.css (all button styles)
    ├── boxes.css (cards, containers)
    ├── forms.css (form controls, inputs)
    ├── utilities.css (spacing, flexbox, text utils)
    └── page-components.css (headers, empty states, etc.)
└── pages/
    ├── auth.css (login, register, forgot)
    ├── profile.css (profile page)
    ├── beatmap.css (beatmap page)
    ├── score.css (score page)
    ├── home.css (home page)
    ├── leaderboard.css (leaderboard page)
    └── topplays.css (top plays page)
```

## Component Reference

### Available Components
- `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-success`, `.btn-danger`
- `.btn-large`, `.btn-small`, `.btn-full`
- `.card`, `.card-accent-primary`, `.card-accent-success`, `.card-accent-danger`
- `.input`, `.control`, `.has-icons-left`, `.has-icons-right`
- `.input-group`, `.input-group-flex`
- `.auth-header`, `.auth-icon`
- `.title`, `.subtitle`, `.dialog`
- `.empty-state`, `.empty-icon`, `.empty-title`, `.empty-text`

### Available Utilities
**Spacing**: `.m-{0-6}`, `.mt-`, `.mb-`, `.ml-`, `.mr-`, `.mx-`, `.my-`, `.p-{0-6}`, `.pt-`, etc.

**Flexbox**: `.flex`, `.flex-col`, `.items-center`, `.justify-between`, `.gap-{0-6}`

**Text**: `.text-center`, `.text-left`, `.text-lg`, `.text-sm`, `.font-bold`, `.font-medium`

**Display**: `.block`, `.inline-block`, `.hidden`

**Width**: `.w-full`, `.w-auto`

**Border Radius**: `.rounded`, `.rounded-sm`, `.rounded-lg`, `.rounded-full`

See `/static/css/components/utilities.css` for complete list.

## Best Practices

1. **Always use utility classes for spacing** instead of inline styles
2. **Use consistent component classes** (`.btn`, `.card`, `.input`)
3. **Avoid creating custom CSS** - use existing components
4. **Keep inline styles for dynamic values only** (background images, colors from backend)
5. **Use CSS variables** when creating new components
6. **Test responsive behavior** on mobile, tablet, desktop
7. **Follow the established patterns** from auth pages

## Resources

- Design System: `/static/css/design-system.css`
- Components: `/static/css/components/`
- Utilities: `/static/css/components/utilities.css`
- Auth Template Example: `/templates/login.html`, `/templates/register.html`
