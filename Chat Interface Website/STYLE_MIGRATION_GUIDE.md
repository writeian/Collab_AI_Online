# Chat Interface Style Migration Guide

This guide will help you bring the styling from this chat interface website to another Cursor project.

## 🎨 Design System Overview

This project uses:
- **shadcn/ui** components for UI elements
- **Tailwind CSS** for styling
- **Custom CSS variables** for theming (light/dark mode)
- **Lucide React** for icons

## 📁 Files to Copy

### 1. Core Styling Files
```
styles/globals.css          # Main CSS with design tokens and theming
components/ui/              # All shadcn/ui components
```

### 2. Key Components to Reference
```
components/ChatSidebar.tsx  # Sidebar layout and styling patterns
components/ChatArea.tsx     # Main content area styling
components/MessageInput.tsx # Input component styling
App.tsx                    # Overall layout structure
```

## 🚀 Setup Steps for New Project

### Step 1: Install Dependencies
```bash
npm install tailwindcss @tailwindcss/typography
npm install lucide-react
npm install class-variance-authority clsx tailwind-merge
```

### Step 2: Setup shadcn/ui
```bash
npx shadcn@latest init
```

When prompted, choose:
- Style: Default
- Base color: Slate (or your preference)
- CSS variables: Yes
- React Server Components: No
- Components directory: components/ui
- Utils directory: lib/utils
- Include example components: No

### Step 3: Copy Design System

1. **Copy the CSS variables** from `styles/globals.css` to your new project's global CSS file
2. **Copy all UI components** from `components/ui/` to your new project
3. **Copy the utils.ts** file for utility functions

### Step 4: Install Required shadcn/ui Components

Based on the chat interface, you'll need these components:
```bash
npx shadcn@latest add avatar
npx shadcn@latest add badge
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add card
npx shadcn@latest add separator
```

## 🎯 Key Styling Patterns

### 1. Layout Structure
```tsx
<div className="size-full flex bg-background">
  <Sidebar className="w-80 bg-card border-r border-border" />
  <div className="flex-1 flex flex-col">
    {/* Main content */}
  </div>
</div>
```

### 2. Color System
The project uses semantic color tokens:
- `bg-background` - Main background
- `bg-card` - Card/sidebar backgrounds
- `text-foreground` - Primary text
- `text-muted-foreground` - Secondary text
- `border-border` - Borders
- `bg-accent` - Hover states

### 3. Spacing & Sizing
- `p-4` - Standard padding
- `gap-3` - Standard gaps
- `w-80` - Fixed sidebar width
- `h-12` - Standard heights

### 4. Interactive States
```tsx
className={`hover:bg-accent/50 transition-colors ${
  isSelected ? 'bg-accent' : ''
}`}
```

## 🎨 Custom Design Tokens

The project includes custom CSS variables for:
- **Sidebar theming** (`--sidebar`, `--sidebar-foreground`, etc.)
- **Chart colors** (`--chart-1` through `--chart-5`)
- **Custom radius** (`--radius: 0.625rem`)
- **Font weights** (`--font-weight-medium`, `--font-weight-normal`)

## 🔧 Tailwind Configuration

Make sure your `tailwind.config.js` includes:
```js
module.exports = {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

## 📱 Responsive Design

The chat interface uses:
- Fixed sidebar width (`w-80`)
- Flexible main content area (`flex-1`)
- Mobile-friendly touch targets
- Proper overflow handling

## 🎯 Component Patterns

### Avatar with Online Status
```tsx
<div className="relative">
  <Avatar className="w-12 h-12">
    <AvatarImage src={avatar} alt={name} />
    <AvatarFallback>{name.charAt(0)}</AvatarFallback>
  </Avatar>
  {isOnline && (
    <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-card rounded-full"></div>
  )}
</div>
```

### Search Input with Icon
```tsx
<div className="relative">
  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
  <Input placeholder="Search..." className="pl-10" />
</div>
```

### Badge for Notifications
```tsx
{unreadCount > 0 && (
  <Badge variant="destructive" className="ml-2">
    {unreadCount}
  </Badge>
)}
```

## 🚀 Quick Start Template

For a quick start, copy these files to your new project:

1. `styles/globals.css` → `src/styles/globals.css`
2. `components/ui/` → `src/components/ui/`
3. `components/utils.ts` → `src/lib/utils.ts`

Then update your imports and you'll have the same design system!

## 📝 Notes

- The design uses **oklch color space** for better color management
- **Dark mode** is fully supported with CSS variables
- **Accessibility** is built into shadcn/ui components
- **TypeScript** support is included in all components

This styling approach provides a modern, accessible, and maintainable design system that you can easily adapt to any project! 