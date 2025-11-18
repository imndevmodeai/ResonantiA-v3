# Reusable Styling Components

Based on the Objective Generation Engine Visualizer styling patterns, here are reusable component classes and patterns you can apply to any project.

---

## Base Container Classes

### Dark Theme Container
```tsx
className="min-h-screen bg-gray-900 text-gray-200 font-sans"
```

### Responsive Padding Container
```tsx
className="p-4 sm:p-6 lg:p-8"
```

### Centered Max-Width Container
```tsx
className="w-full max-w-7xl mx-auto"
```

---

## Glassmorphism Components

### Standard Glass Panel
```tsx
className="bg-gray-800/50 rounded-lg p-6 border border-gray-700 backdrop-blur-sm"
```

### Glass Panel (More Opaque)
```tsx
className="bg-gray-800/60 rounded-lg p-4 border border-gray-700"
```

### Glass Panel (Subtle)
```tsx
className="bg-gray-800/30 rounded-lg border-2 border-dashed border-gray-700"
```

---

## Gradient Text Components

### Hero Gradient Text
```tsx
className="text-3xl sm:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400"
```

### Section Gradient Text
```tsx
className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-purple-300"
```

### Subtitle Gradient Text
```tsx
className="text-lg font-semibold text-transparent bg-clip-text bg-gradient-to-r from-purple-300 to-cyan-300"
```

---

## Button Components

### Primary Button
```tsx
className="w-full bg-cyan-600 hover:bg-cyan-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center transition-all duration-300 transform hover:scale-105"
```

### Secondary Button
```tsx
className="bg-gray-700 hover:bg-gray-600 text-gray-200 font-semibold py-2 px-4 rounded-lg transition-all duration-300"
```

### Icon Button
```tsx
className="bg-cyan-600 hover:bg-cyan-500 text-white p-2 rounded-lg transition-all duration-300 hover:scale-105"
```

---

## Card Components

### Standard Card
```tsx
className="bg-gray-800/60 rounded-lg p-4 border border-gray-700 transition-all duration-300 hover:border-cyan-600 hover:shadow-lg hover:shadow-cyan-900/20"
```

### Featured Card (Final Stage Style)
```tsx
className="bg-gradient-to-br from-cyan-900/50 to-purple-900/50 rounded-lg p-6 border border-cyan-500 shadow-2xl shadow-cyan-500/10"
```

### Empty State Card
```tsx
className="flex flex-col items-center justify-center h-full min-h-[500px] bg-gray-800/30 rounded-lg border-2 border-dashed border-gray-700 p-8 text-center"
```

---

## Input Components

### Textarea
```tsx
className="w-full h-40 bg-gray-900 border border-gray-600 rounded-md p-3 text-gray-200 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition duration-200 resize-none"
```

### Text Input
```tsx
className="w-full bg-gray-900 border border-gray-600 rounded-md p-3 text-gray-200 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition duration-200"
```

### Label
```tsx
className="block text-sm font-medium text-gray-300 mb-2"
```

---

## Code Display Components

### Code Block
```tsx
className="block w-full text-left text-sm bg-gray-900 text-cyan-300 p-3 rounded-md overflow-x-auto whitespace-pre-wrap break-words"
```

### Inline Code
```tsx
className="text-cyan-400 bg-gray-900 px-2 py-1 rounded-md font-mono text-sm"
```

### Code Badge
```tsx
className="w-16 text-center flex-shrink-0 text-lg font-bold text-cyan-400 bg-gray-900 px-2 py-1 rounded-md"
```

---

## Typography Components

### Heading 1 (Hero)
```tsx
className="text-3xl sm:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400"
```

### Heading 2
```tsx
className="text-2xl font-bold text-gray-200"
```

### Heading 3
```tsx
className="text-xl font-bold text-gray-200"
```

### Body Text
```tsx
className="text-gray-300"
```

### Secondary Text
```tsx
className="text-gray-400"
```

### Muted Text
```tsx
className="text-gray-500"
```

### Label Text
```tsx
className="text-xs text-gray-400 uppercase font-semibold"
```

---

## Loading Components

### Spinner (Large)
```tsx
className="w-24 h-24 border-4 border-cyan-500 border-dashed rounded-full animate-spin"
```

### Spinner (Small)
```tsx
className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"
```

### Loading Text
```tsx
className="text-lg mt-6 font-semibold text-cyan-300"
```

---

## Layout Components

### Responsive Grid (2 Columns)
```tsx
className="grid grid-cols-1 md:grid-cols-2 gap-4"
```

### Responsive Grid (3 Columns)
```tsx
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
```

### Sticky Sidebar
```tsx
className="lg:w-1/3 lg:sticky lg:top-8 self-start"
```

### Flex Column (Mobile) → Row (Desktop)
```tsx
className="flex flex-col lg:flex-row gap-8"
```

### Centered Content
```tsx
className="flex flex-col items-center justify-center"
```

---

## Badge/Indicator Components

### Number Badge
```tsx
className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center"
```

### Status Badge (Success)
```tsx
className="px-3 py-1 rounded-full bg-cyan-900/50 text-cyan-300 text-xs font-semibold"
```

### Status Badge (Warning)
```tsx
className="px-3 py-1 rounded-full bg-yellow-900/50 text-yellow-300 text-xs font-semibold"
```

### Status Badge (Error)
```tsx
className="px-3 py-1 rounded-full bg-red-900/50 text-red-300 text-xs font-semibold"
```

---

## Icon Components

### Icon Container (Centered)
```tsx
className="flex items-center justify-center"
```

### Icon (Large)
```tsx
className="h-16 w-16 text-gray-600"
```

### Icon (Medium)
```tsx
className="h-10 w-10 text-cyan-400"
```

### Icon (Small)
```tsx
className="h-5 w-5 text-cyan-400"
```

---

## Shadow & Glow Effects

### Subtle Glow
```tsx
className="shadow-lg shadow-cyan-900/20"
```

### Medium Glow
```tsx
className="shadow-xl shadow-cyan-500/10"
```

### Strong Glow
```tsx
className="shadow-2xl shadow-cyan-500/10"
```

### Hover Glow
```tsx
className="hover:shadow-lg hover:shadow-cyan-900/20"
```

---

## Border Styles

### Standard Border
```tsx
className="border border-gray-700"
```

### Accent Border
```tsx
className="border border-cyan-500"
```

### Dashed Border
```tsx
className="border-2 border-dashed border-gray-700"
```

### Hover Border
```tsx
className="border border-gray-700 hover:border-cyan-600"
```

---

## Spacing Utilities

### Card Padding (Small)
```tsx
className="p-4"
```

### Card Padding (Medium)
```tsx
className="p-6"
```

### Card Padding (Large)
```tsx
className="p-8"
```

### Gap (Small)
```tsx
className="gap-2"
```

### Gap (Medium)
```tsx
className="gap-4"
```

### Gap (Large)
```tsx
className="gap-8"
```

---

## Complete Component Examples

### Glass Card with Hover
```tsx
<div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700 backdrop-blur-sm transition-all duration-300 hover:border-cyan-600 hover:shadow-lg hover:shadow-cyan-900/20">
  {/* Content */}
</div>
```

### Gradient Heading with Subtitle
```tsx
<div>
  <h1 className="text-3xl sm:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400 mb-2">
    Title
  </h1>
  <p className="text-gray-400">Subtitle</p>
</div>
```

### Feature Card
```tsx
<div className="bg-gray-800/60 rounded-lg p-4 border border-gray-700 transition-all duration-300 hover:border-cyan-600 hover:shadow-lg hover:shadow-cyan-900/20">
  <div className="flex items-center mb-3">
    <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center mr-3">
      <span className="font-bold text-cyan-400">1</span>
    </div>
    <h3 className="font-bold text-gray-200">Title</h3>
  </div>
  <p className="text-gray-400 text-sm">Content</p>
</div>
```

### Input Group
```tsx
<div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700 backdrop-blur-sm">
  <label className="block text-sm font-medium text-gray-300 mb-2">
    Label
  </label>
  <textarea
    className="w-full h-40 bg-gray-900 border border-gray-600 rounded-md p-3 text-gray-200 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition duration-200 resize-none"
    placeholder="Enter text..."
  />
  <button className="w-full mt-4 bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-3 px-4 rounded-lg transition-all duration-300 transform hover:scale-105">
    Submit
  </button>
</div>
```

---

## Color Reference

### Background Colors
- `bg-gray-900` - Base dark background
- `bg-gray-800/50` - Glass panel (50% opacity)
- `bg-gray-800/60` - Glass panel (60% opacity)
- `bg-gray-800/30` - Subtle glass panel
- `bg-gray-900` - Dark input/code background

### Text Colors
- `text-gray-200` - Primary text
- `text-gray-300` - Secondary text
- `text-gray-400` - Tertiary text
- `text-gray-500` - Muted text
- `text-gray-600` - Very muted text
- `text-cyan-300` - Code text
- `text-cyan-400` - Accent text
- `text-cyan-500` - Strong accent

### Border Colors
- `border-gray-700` - Standard border
- `border-gray-600` - Input border
- `border-cyan-500` - Accent border
- `border-cyan-600` - Hover accent border

### Accent Colors
- `cyan-400`, `cyan-500`, `cyan-600` - Primary accent
- `purple-400`, `purple-900` - Secondary accent
- `from-purple-400 to-cyan-400` - Gradient range

---

## Animation Classes

### Standard Transition
```tsx
className="transition-all duration-300"
```

### Fast Transition
```tsx
className="transition-all duration-200"
```

### Slow Transition
```tsx
className="transition-all duration-500"
```

### Spin Animation
```tsx
className="animate-spin"
```

### Scale on Hover
```tsx
className="transform hover:scale-105"
```

---

## Responsive Breakpoints

- `sm:` - 640px and up (small tablets)
- `md:` - 768px and up (tablets)
- `lg:` - 1024px and up (desktops)
- `xl:` - 1280px and up (large desktops)

### Example Usage
```tsx
className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl"
```

---

## Best Practices

1. **Consistency**: Use the same opacity values (`/50`, `/60`, `/30`) throughout
2. **Hierarchy**: Use gradient text only for primary headings
3. **Spacing**: Maintain consistent gaps (`gap-4`, `gap-8`)
4. **Transitions**: Always add `transition-all duration-300` to interactive elements
5. **Hover States**: Include hover effects on all clickable elements
6. **Accessibility**: Ensure sufficient color contrast (light text on dark backgrounds)

---

## Quick Start Template

```tsx
// Main Container
<div className="min-h-screen bg-gray-900 text-gray-200 font-sans p-4 sm:p-6 lg:p-8">
  <div className="w-full max-w-7xl mx-auto">
    
    {/* Header */}
    <header className="mb-8">
      <h1 className="text-3xl sm:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
        Your Title
      </h1>
    </header>
    
    {/* Content Grid */}
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Cards */}
      <div className="bg-gray-800/60 rounded-lg p-4 border border-gray-700 transition-all duration-300 hover:border-cyan-600 hover:shadow-lg hover:shadow-cyan-900/20">
        {/* Card content */}
      </div>
    </div>
    
  </div>
</div>
```

---

This styling system creates a **cohesive, modern dark theme** that's both visually appealing and highly functional.












