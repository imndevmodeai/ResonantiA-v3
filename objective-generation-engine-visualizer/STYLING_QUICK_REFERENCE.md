# Styling Quick Reference Guide

## 🎨 Color Palette Quick Reference

```
Backgrounds:
  bg-gray-900        → Main page background
  bg-gray-800/50     → Glass panels (standard)
  bg-gray-800/60     → Glass panels (more opaque)
  bg-gray-800/30     → Glass panels (subtle)
  bg-gray-900        → Inputs, code blocks

Text:
  text-gray-200      → Primary text
  text-gray-300      → Secondary text
  text-gray-400      → Tertiary text
  text-gray-500      → Muted text
  text-cyan-300      → Code text
  text-cyan-400      → Accent text
  text-cyan-500      → Strong accent

Borders:
  border-gray-700    → Standard border
  border-gray-600    → Input border
  border-cyan-500   → Accent border
  border-cyan-600    → Hover accent

Gradients:
  from-purple-400 to-cyan-400  → Primary gradient
  from-cyan-900/50 to-purple-900/50  → Card gradient
```

---

## 🧩 Component Templates

### Glass Panel
```tsx
<div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700 backdrop-blur-sm">
  {/* Content */}
</div>
```

### Gradient Heading
```tsx
<h1 className="text-3xl sm:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
  Title
</h1>
```

### Primary Button
```tsx
<button className="bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-3 px-4 rounded-lg transition-all duration-300 transform hover:scale-105">
  Click Me
</button>
```

### Input Field
```tsx
<input className="w-full bg-gray-900 border border-gray-600 rounded-md p-3 text-gray-200 focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition duration-200" />
```

### Card with Hover
```tsx
<div className="bg-gray-800/60 rounded-lg p-4 border border-gray-700 transition-all duration-300 hover:border-cyan-600 hover:shadow-lg hover:shadow-cyan-900/20">
  {/* Content */}
</div>
```

### Code Block
```tsx
<code className="block w-full bg-gray-900 text-cyan-300 p-3 rounded-md overflow-x-auto">
  {/* Code */}
</code>
```

### Loading Spinner
```tsx
<div className="w-24 h-24 border-4 border-cyan-500 border-dashed rounded-full animate-spin"></div>
```

---

## 📐 Spacing Cheat Sheet

```
Padding:
  p-3  → 12px  (Small)
  p-4  → 16px  (Standard)
  p-6  → 24px  (Medium)
  p-8  → 32px  (Large)

Margin:
  m-2  → 8px   (Tight)
  m-4  → 16px  (Standard)
  m-6  → 24px  (Medium)
  m-8  → 32px  (Large)

Gap:
  gap-2  → 8px   (Tight)
  gap-4  → 16px  (Standard)
  gap-8  → 32px  (Large)
```

---

## 🎯 Common Patterns

### Responsive Container
```tsx
<div className="w-full max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
```

### Responsive Grid
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
```

### Flex Layout
```tsx
<div className="flex flex-col lg:flex-row gap-8">
```

### Sticky Sidebar
```tsx
<div className="lg:w-1/3 lg:sticky lg:top-8 self-start">
```

---

## ⚡ Animation Shortcuts

```
Standard Transition:
  transition-all duration-300

Fast Transition:
  transition duration-200

Hover Scale:
  transform hover:scale-105

Spin Animation:
  animate-spin
```

---

## 🔍 Focus States

```
Input Focus:
  focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500

Button Focus:
  focus:outline-none focus:ring-2 focus:ring-cyan-500
```

---

## 📱 Responsive Breakpoints

```
sm:  → 640px   (Small tablets)
md:  → 768px   (Tablets)
lg:  → 1024px  (Desktops)
xl:  → 1280px  (Large desktops)
```

---

## 🎨 Shadow Effects

```
Subtle:    shadow-lg shadow-cyan-900/20
Medium:    shadow-xl shadow-cyan-500/10
Strong:    shadow-2xl shadow-cyan-500/10
Hover:     hover:shadow-lg hover:shadow-cyan-900/20
```

---

## 💡 Pro Tips

1. **Always use transitions** on interactive elements
2. **Consistent opacity** values (`/50`, `/60`, `/30`)
3. **Gradient text** only for primary headings
4. **Hover states** on all clickable elements
5. **Mobile-first** approach with progressive enhancement
6. **Backdrop blur** for true glassmorphism effect

---

## 🚀 Copy-Paste Starter

```tsx
<div className="min-h-screen bg-gray-900 text-gray-200 font-sans p-4 sm:p-6 lg:p-8">
  <div className="w-full max-w-7xl mx-auto">
    
    {/* Header */}
    <header className="mb-8">
      <h1 className="text-3xl sm:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
        Your Title
      </h1>
      <p className="text-gray-400 mt-2">Your subtitle</p>
    </header>
    
    {/* Content */}
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="bg-gray-800/60 rounded-lg p-4 border border-gray-700 transition-all duration-300 hover:border-cyan-600 hover:shadow-lg hover:shadow-cyan-900/20">
        <h3 className="font-bold text-gray-200 mb-2">Card Title</h3>
        <p className="text-gray-300">Card content</p>
      </div>
    </div>
    
  </div>
</div>
```

---

This quick reference gives you everything you need to replicate this styling system in any project!





























