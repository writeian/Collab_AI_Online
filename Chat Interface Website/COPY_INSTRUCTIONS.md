# Copy Instructions for AI Collab Online

## 📁 Step-by-Step File Copying

### Option 1: Manual Copy (Recommended)

1. **Create the CSS file in your AI Collab Online project:**

   In your AI Collab Online project, create a new file:
   ```
   static/css/globals.css
   ```

2. **Copy the content from this file:**
   Copy the entire content from `styles/globals.css` (shown above) and paste it into your new `static/css/globals.css` file.

### Option 2: Using File Explorer

1. **Navigate to your AI Collab Online project folder**
2. **Create the directory structure:**
   ```
   static/
   └── css/
   ```
3. **Copy the file:**
   - Copy `styles/globals.css` from this chat interface project
   - Paste it as `static/css/globals.css` in your AI Collab Online project

### Option 3: Using Command Line

If you have both projects on your computer:

```bash
# Navigate to your AI Collab Online project
cd path/to/your/AI_Collab_Online

# Create the css directory
mkdir -p static/css

# Copy the CSS file (adjust paths as needed)
cp "path/to/chat-interface/styles/globals.css" static/css/globals.css
```

## 🎨 Additional CSS for Button Components

Since your Flask project needs button styling, also create this file:

**File:** `static/css/components.css`

```css
/* Button Components */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
  text-decoration: none;
  border: 1px solid transparent;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  line-height: 1rem;
}

.btn-lg {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  line-height: 1.5rem;
}

/* Primary Button */
.btn-primary {
  background-color: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  border-color: hsl(var(--primary));
}

.btn-primary:hover {
  background-color: hsl(var(--primary) / 0.9);
}

/* Secondary Button */
.btn-secondary {
  background-color: hsl(var(--secondary));
  color: hsl(var(--secondary-foreground));
  border-color: hsl(var(--secondary));
}

.btn-secondary:hover {
  background-color: hsl(var(--secondary) / 0.8);
}

/* Outline Button */
.btn-outline {
  background-color: transparent;
  color: hsl(var(--foreground));
  border-color: hsl(var(--border));
}

.btn-outline:hover {
  background-color: hsl(var(--accent));
  color: hsl(var(--accent-foreground));
}

/* Destructive Button */
.btn-destructive {
  background-color: hsl(var(--destructive));
  color: hsl(var(--destructive-foreground));
  border-color: hsl(var(--destructive));
}

.btn-destructive:hover {
  background-color: hsl(var(--destructive) / 0.9);
}

/* Ghost Button */
.btn-ghost {
  background-color: transparent;
  color: hsl(var(--foreground));
}

.btn-ghost:hover {
  background-color: hsl(var(--accent));
  color: hsl(var(--accent-foreground));
}
```

## 📝 Update Your Base Template

In your AI Collab Online project, update `templates/base.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}AI Collab Online{% endblock %}</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- New Design System CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/globals.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/components.css') }}">
    
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    
    <!-- Your existing styles -->
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body class="bg-background text-foreground">
    {% block content %}{% endblock %}
    
    <!-- Initialize Lucide icons -->
    <script>
        lucide.createIcons();
    </script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

## 🎯 Quick Test

After copying the files, test that the styling works by adding this to any template:

```html
<div class="bg-card rounded-lg border border-border p-6">
    <h3 class="font-semibold mb-4">Test Card</h3>
    <p class="text-muted-foreground">This should have the new styling!</p>
    <button class="btn btn-primary">Test Button</button>
</div>
```

## 📋 Checklist

- [ ] Copy `styles/globals.css` → `static/css/globals.css`
- [ ] Create `static/css/components.css` with button styles
- [ ] Update `templates/base.html` with new CSS imports
- [ ] Test the styling on a page
- [ ] Update your chat templates with the new design

That's it! Your AI Collab Online project will now have the beautiful, modern styling from the chat interface. 