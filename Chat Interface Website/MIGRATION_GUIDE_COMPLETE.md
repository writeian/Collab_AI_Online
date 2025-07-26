# AI Collab Online - Complete Style Migration Guide

## 🎯 Overview

This guide will transform your AI Collab Online Flask project with modern, professional styling from a chat interface design system.

## 📁 Files to Copy

### 1. Core CSS Files

**File:** `static/css/globals.css`
```css
@custom-variant dark (&:is(.dark *));

:root {
  --font-size: 14px;
  --background: #ffffff;
  --foreground: oklch(0.145 0 0);
  --card: #ffffff;
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);
  --primary: #030213;
  --primary-foreground: oklch(1 0 0);
  --secondary: oklch(0.95 0.0058 264.53);
  --secondary-foreground: #030213;
  --muted: #ececf0;
  --muted-foreground: #717182;
  --accent: #e9ebef;
  --accent-foreground: #030213;
  --destructive: #d4183d;
  --destructive-foreground: #ffffff;
  --border: rgba(0, 0, 0, 0.1);
  --input: transparent;
  --input-background: #f3f3f5;
  --switch-background: #cbced4;
  --font-weight-medium: 500;
  --font-weight-normal: 400;
  --ring: oklch(0.708 0 0);
  --chart-1: oklch(0.646 0.222 41.116);
  --chart-2: oklch(0.6 0.118 184.704);
  --chart-3: oklch(0.398 0.07 227.392);
  --chart-4: oklch(0.828 0.189 84.429);
  --chart-5: oklch(0.769 0.188 70.08);
  --radius: 0.625rem;
  --sidebar: oklch(0.985 0 0);
  --sidebar-foreground: oklch(0.145 0 0);
  --sidebar-primary: #030213;
  --sidebar-primary-foreground: oklch(0.985 0 0);
  --sidebar-accent: oklch(0.97 0 0);
  --sidebar-accent-foreground: oklch(0.205 0 0);
  --sidebar-border: oklch(0.922 0 0);
  --sidebar-ring: oklch(0.708 0 0);
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.145 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.145 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: oklch(0.985 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.396 0.141 25.723);
  --destructive-foreground: oklch(0.637 0.237 25.331);
  --border: oklch(0.269 0 0);
  --input: oklch(0.269 0 0);
  --ring: oklch(0.439 0 0);
  --font-weight-medium: 500;
  --font-weight-normal: 400;
  --chart-1: oklch(0.488 0.243 264.376);
  --chart-2: oklch(0.696 0.17 162.48);
  --chart-3: oklch(0.769 0.188 70.08);
  --chart-4: oklch(0.627 0.265 303.9);
  --chart-5: oklch(0.645 0.246 16.439);
  --sidebar: oklch(0.205 0 0);
  --sidebar-foreground: oklch(0.985 0 0);
  --sidebar-primary: oklch(0.488 0.243 264.376);
  --sidebar-primary-foreground: oklch(0.985 0 0);
  --sidebar-accent: oklch(0.269 0 0);
  --sidebar-accent-foreground: oklch(0.985 0 0);
  --sidebar-border: oklch(0.269 0 0);
  --sidebar-ring: oklch(0.439 0 0);
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-input-background: var(--input-background);
  --color-switch-background: var(--switch-background);
  --color-ring: var(--ring);
  --color-chart-1: var(--chart-1);
  --color-chart-2: var(--chart-2);
  --color-chart-3: var(--chart-3);
  --color-chart-4: var(--chart-4);
  --color-chart-5: var(--chart-5);
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
  --color-sidebar: var(--sidebar);
  --color-sidebar-foreground: var(--sidebar-foreground);
  --color-sidebar-primary: var(--sidebar-primary);
  --color-sidebar-primary-foreground: var(--sidebar-primary-foreground);
  --color-sidebar-accent: var(--sidebar-accent);
  --color-sidebar-accent-foreground: var(--sidebar-accent-foreground);
  --color-sidebar-border: var(--sidebar-border);
  --color-sidebar-ring: var(--sidebar-ring);
}

@layer base {
  * {
    @apply border-border outline-ring/50;
  }

  body {
    @apply bg-background text-foreground;
  }
}

@layer base {
  :where(:not(:has([class*=" text-"]), :not(:has([class^="text-"])))) {
    h1 {
      font-size: var(--text-2xl);
      font-weight: var(--font-weight-medium);
      line-height: 1.5;
    }

    h2 {
      font-size: var(--text-xl);
      font-weight: var(--font-weight-medium);
      line-height: 1.5;
    }

    h3 {
      font-size: var(--text-lg);
      font-weight: var(--font-weight-medium);
      line-height: 1.5;
    }

    h4 {
      font-size: var(--text-base);
      font-weight: var(--font-weight-medium);
      line-height: 1.5;
    }

    p {
      font-size: var(--text-base);
      font-weight: var(--font-weight-normal);
      line-height: 1.5;
    }

    label {
      font-size: var(--text-base);
      font-weight: var(--font-weight-medium);
      line-height: 1.5;
    }

    button {
      font-size: var(--text-base);
      font-weight: var(--font-weight-medium);
      line-height: 1.5;
    }

    input {
      font-size: var(--text-base);
      font-weight: var(--font-weight-normal);
      line-height: 1.5;
    }
  }
}

html {
  font-size: var(--font-size);
}
```

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

**File:** `templates/base.html`
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

## 🎨 Updated Chat Template

**File:** `templates/chat/view.html`
```html
{% extends "base.html" %}

{% block title %}Chat - {{ chat.title }}{% endblock %}

{% block content %}
<div class="size-full flex bg-background h-screen">
    <!-- Sidebar -->
    <div class="w-80 bg-card border-r border-border flex flex-col h-full">
        <!-- Header -->
        <div class="p-4 border-b border-border">
            <div class="flex items-center justify-between mb-4">
                <h2 class="flex items-center gap-2">
                    <i data-lucide="message-circle" class="w-5 h-5"></i>
                    {{ room.name }}
                </h2>
                <a href="{{ url_for('room.view', room_id=room.id) }}" 
                   class="text-sm text-muted-foreground hover:text-foreground">
                    Back to Room
                </a>
            </div>
            
            <!-- Chat Info -->
            <div class="space-y-2">
                <h3 class="font-medium">{{ chat.title }}</h3>
                <p class="text-sm text-muted-foreground">
                    Writing Mode: {{ chat.writing_mode }}
                </p>
                {% if chat.google_doc_url %}
                <p class="text-sm text-muted-foreground">
                    📄 Google Doc Linked
                </p>
                {% endif %}
            </div>
        </div>

        <!-- Chat List (if multiple chats) -->
        <div class="flex-1 overflow-y-auto p-4">
            <h4 class="text-sm font-medium mb-3">Other Chats</h4>
            <!-- Add other chats in room here -->
        </div>
    </div>
    
    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col">
        <!-- Chat Header -->
        <div class="p-4 border-b border-border bg-card">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-lg font-medium">{{ chat.title }}</h1>
                    <p class="text-sm text-muted-foreground">
                        {{ chat.created_at.strftime('%B %d, %Y') }}
                    </p>
                </div>
                <div class="flex items-center gap-2">
                    <a href="{{ url_for('chat.edit', chat_id=chat.id) }}" 
                       class="btn btn-secondary btn-sm">
                        <i data-lucide="settings" class="w-4 h-4"></i>
                        Settings
                    </a>
                </div>
            </div>
        </div>

        <!-- Messages Area -->
        <div class="flex-1 overflow-y-auto p-4 space-y-4">
            {% for message in messages %}
            <div class="flex {% if message.is_user %}justify-end{% else %}justify-start{% endif %}">
                <div class="max-w-[70%] {% if message.is_user %}bg-primary text-primary-foreground{% else %}bg-muted{% endif %} rounded-lg p-3">
                    <div class="flex items-start gap-3">
                        {% if not message.is_user %}
                        <div class="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground text-sm font-medium">
                            AI
                        </div>
                        {% endif %}
                        
                        <div class="flex-1">
                            <div class="{% if message.is_user %}text-right{% endif %}">
                                <p class="text-sm">{{ message.content }}</p>
                                <p class="text-xs text-muted-foreground mt-1">
                                    {{ message.timestamp.strftime('%I:%M %p') }}
                                </p>
                            </div>
                            
                            <!-- Comments -->
                            {% if message.comments %}
                            <div class="mt-2 space-y-2">
                                {% for comment in message.comments %}
                                <div class="bg-background rounded p-2 text-xs">
                                    <p class="font-medium">{{ comment.user.username }}</p>
                                    <p>{{ comment.content }}</p>
                                </div>
                                {% endfor %}
                            </div>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

        <!-- Message Input -->
        <div class="p-4 border-t border-border bg-card">
            <form method="POST" class="flex gap-2">
                <input type="text" name="message" 
                       placeholder="Type your message..." 
                       class="flex-1 px-3 py-2 border border-border rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                       required>
                <button type="submit" 
                        class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors">
                    <i data-lucide="send" class="w-4 h-4"></i>
                </button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

## 🚀 Implementation Steps

1. **Create the CSS files** in your AI Collab Online project
2. **Update your base template** with the new CSS imports
3. **Replace your chat template** with the modern version
4. **Test the styling** by adding a test card to any page
5. **Update other templates** gradually using the new design system

## 🎯 Key Benefits

- ✅ **Professional appearance** for your educational platform
- ✅ **Better user experience** for students and instructors
- ✅ **Responsive design** that works on all devices
- ✅ **Accessibility features** important for educational use
- ✅ **Consistent design language** across all pages
- ✅ **Modern chat interface** perfect for AI conversations

## 📋 Quick Test

Add this to any template to test the styling:

```html
<div class="bg-card rounded-lg border border-border p-6">
    <h3 class="font-semibold mb-4">Test Card</h3>
    <p class="text-muted-foreground">This should have the new styling!</p>
    <button class="btn btn-primary">Test Button</button>
</div>
```

That's it! Your AI Collab Online project will now have beautiful, modern styling perfect for educational use. 