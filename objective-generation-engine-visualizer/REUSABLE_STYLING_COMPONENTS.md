# Reusable Styling Components Library

This document provides a complete library of reusable styling components extracted from the Objective Generation Engine Visualizer. Each component is production-ready and can be directly copied into any React + Tailwind CSS project.

---

## 🎨 Base Styles

### Dark Theme Container
```tsx
<div className="min-h-screen bg-gray-900 text-gray-200 font-sans">
  {/* Your content */}
</div>
```

### Responsive Container
```tsx
<div className="w-full max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
  {/* Your content */}
</div>
```

---

## 📦 Glass Panel Components

### Standard Glass Panel
```tsx
const GlassPanel = ({ children, className = "" }) => (
  <div className={`bg-gray-800/50 rounded-lg p-6 border border-gray-700 backdrop-blur-sm ${className}`}>
    {children}
  </div>
);
```

### Opaque Glass Panel
```tsx
const OpaqueGlassPanel = ({ children, className = "" }) => (
  <div className={`bg-gray-800/60 rounded-lg p-4 border border-gray-700 ${className}`}>
    {children}
  </div>
);
```

### Subtle Glass Panel
```tsx
const SubtleGlassPanel = ({ children, className = "" }) => (
  <div className={`bg-gray-800/30 rounded-lg p-8 border-2 border-dashed border-gray-700 ${className}`}>
    {children}
  </div>
);
```

---

## 🎯 Typography Components

### Gradient Heading (Primary)
```tsx
const GradientHeading = ({ children, size = "3xl", className = "" }) => {
  const sizeClass = `text-${size} sm:text-${size === "3xl" ? "4xl" : size}`;
  return (
    <h1 className={`${sizeClass} font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400 ${className}`}>
      {children}
    </h1>
  );
};
```

### Gradient Heading (Secondary)
```tsx
const GradientHeadingSecondary = ({ children, className = "" }) => (
  <h2 className={`text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400 ${className}`}>
    {children}
  </h2>
);
```

### Subtitle Text
```tsx
const Subtitle = ({ children, className = "" }) => (
  <p className={`text-gray-400 ${className}`}>
    {children}
  </p>
);
```

### Muted Text
```tsx
const MutedText = ({ children, className = "" }) => (
  <p className={`text-gray-500 ${className}`}>
    {children}
  </p>
);
```

---

## 🔘 Button Components

### Primary Button
```tsx
const PrimaryButton = ({ 
  children, 
  onClick, 
  disabled = false, 
  isLoading = false,
  className = "" 
}) => (
  <button
    onClick={onClick}
    disabled={disabled || isLoading}
    className={`
      w-full bg-cyan-600 hover:bg-cyan-500 
      disabled:bg-gray-600 disabled:cursor-not-allowed 
      text-white font-bold py-3 px-4 rounded-lg 
      flex items-center justify-center 
      transition-all duration-300 
      transform hover:scale-105
      ${className}
    `}
  >
    {isLoading && (
      <div className="w-5 h-5 border-2 border-white border-dashed rounded-full animate-spin mr-2"></div>
    )}
    {children}
  </button>
);
```

### Secondary Button
```tsx
const SecondaryButton = ({ children, onClick, className = "" }) => (
  <button
    onClick={onClick}
    className={`
      bg-gray-700 hover:bg-gray-600 
      text-gray-200 font-semibold py-2 px-4 rounded-lg 
      transition-all duration-200
      ${className}
    `}
  >
    {children}
  </button>
);
```

### Icon Button
```tsx
const IconButton = ({ icon: Icon, onClick, className = "" }) => (
  <button
    onClick={onClick}
    className={`
      p-2 rounded-lg 
      bg-gray-800 hover:bg-gray-700 
      text-gray-300 hover:text-cyan-400 
      transition-all duration-200
      ${className}
    `}
  >
    <Icon className="w-5 h-5" />
  </button>
);
```

---

## 📝 Form Components

### Text Input
```tsx
const TextInput = ({ 
  value, 
  onChange, 
  placeholder = "", 
  type = "text",
  className = "" 
}) => (
  <input
    type={type}
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    className={`
      w-full bg-gray-900 border border-gray-600 
      rounded-md p-3 text-gray-200 
      placeholder:text-gray-500
      focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 
      transition duration-200
      ${className}
    `}
  />
);
```

### Textarea
```tsx
const Textarea = ({ 
  value, 
  onChange, 
  placeholder = "",
  rows = 4,
  className = "" 
}) => (
  <textarea
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    rows={rows}
    className={`
      w-full bg-gray-900 border border-gray-600 
      rounded-md p-3 text-gray-200 
      placeholder:text-gray-500
      focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 
      transition duration-200
      resize-none
      ${className}
    `}
  />
);
```

---

## 🃏 Card Components

### Standard Card
```tsx
const Card = ({ children, className = "" }) => (
  <div className={`
    bg-gray-800/60 rounded-lg p-4 
    border border-gray-700 
    transition-all duration-300 
    hover:border-cyan-600 hover:shadow-lg hover:shadow-cyan-900/20
    ${className}
  `}>
    {children}
  </div>
);
```

### Gradient Card (Special)
```tsx
const GradientCard = ({ children, className = "" }) => (
  <div className={`
    bg-gradient-to-br from-cyan-900/50 to-purple-900/50 
    rounded-lg p-6 border border-cyan-500 
    shadow-2xl shadow-cyan-500/10
    ${className}
  `}>
    {children}
  </div>
);
```

### Card Header
```tsx
const CardHeader = ({ children, className = "" }) => (
  <div className={`mb-4 ${className}`}>
    {children}
  </div>
);
```

### Card Title
```tsx
const CardTitle = ({ children, className = "" }) => (
  <h3 className={`text-lg font-bold text-gray-200 ${className}`}>
    {children}
  </h3>
);
```

### Card Content
```tsx
const CardContent = ({ children, className = "" }) => (
  <div className={`text-gray-300 ${className}`}>
    {children}
  </div>
);
```

---

## 💻 Code Display Components

### Code Block
```tsx
const CodeBlock = ({ children, className = "" }) => (
  <code className={`
    block w-full bg-gray-900 text-cyan-300 
    p-3 rounded-md overflow-x-auto 
    font-mono text-sm
    ${className}
  `}>
    {children}
  </code>
);
```

### Inline Code
```tsx
const InlineCode = ({ children, className = "" }) => (
  <code className={`
    bg-gray-900 text-cyan-400 px-2 py-1 rounded 
    font-mono text-sm
    ${className}
  `}>
    {children}
  </code>
);
```

---

## ⏳ Loading Components

### Spinner
```tsx
const Spinner = ({ size = "md", className = "" }) => {
  const sizeClasses = {
    sm: "w-8 h-8",
    md: "w-12 h-12",
    lg: "w-24 h-24"
  };
  
  return (
    <div className={`
      ${sizeClasses[size]} 
      border-4 border-cyan-500 border-dashed 
      rounded-full animate-spin
      ${className}
    `}></div>
  );
};
```

### Loading State with Icon
```tsx
const LoadingState = ({ message = "Loading...", icon: Icon }) => (
  <div className="flex flex-col items-center justify-center min-h-[500px] text-center">
    <div className="relative">
      <div className="w-24 h-24 border-4 border-cyan-500 border-dashed rounded-full animate-spin"></div>
      {Icon && (
        <Icon className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-10 w-10 text-cyan-400" />
      )}
    </div>
    <p className="text-lg mt-6 font-semibold text-cyan-300">{message}</p>
  </div>
);
```

### Empty State
```tsx
const EmptyState = ({ 
  icon: Icon, 
  title, 
  description,
  className = "" 
}) => (
  <div className={`
    flex flex-col items-center justify-center 
    h-full min-h-[500px] 
    bg-gray-800/30 rounded-lg 
    border-2 border-dashed border-gray-700 
    p-8 text-center
    ${className}
  `}>
    {Icon && <Icon className="h-16 w-16 text-gray-600 mb-4" />}
    <h2 className="text-xl font-semibold text-gray-400">{title}</h2>
    {description && (
      <p className="text-gray-500 mt-2">{description}</p>
    )}
  </div>
);
```

---

## 📊 Layout Components

### Two Column Layout
```tsx
const TwoColumnLayout = ({ left, right, className = "" }) => (
  <div className={`
    w-full max-w-7xl mx-auto 
    flex flex-col lg:flex-row gap-8
    ${className}
  `}>
    <div className="lg:w-1/3 lg:sticky lg:top-8 self-start">
      {left}
    </div>
    <div className="lg:w-2/3">
      {right}
    </div>
  </div>
);
```

### Responsive Grid
```tsx
const ResponsiveGrid = ({ 
  children, 
  cols = { default: 1, md: 2, lg: 3 },
  gap = 4,
  className = "" 
}) => {
  const gridCols = `grid-cols-${cols.default} md:grid-cols-${cols.md} lg:grid-cols-${cols.lg}`;
  
  return (
    <div className={`
      grid ${gridCols} gap-${gap}
      ${className}
    `}>
      {children}
    </div>
  );
};
```

### Section Container
```tsx
const Section = ({ children, className = "" }) => (
  <section className={`mb-8 ${className}`}>
    {children}
  </section>
);
```

---

## 🎭 Badge Components

### Status Badge
```tsx
const StatusBadge = ({ 
  children, 
  variant = "default",
  className = "" 
}) => {
  const variants = {
    default: "bg-gray-700 text-gray-300",
    success: "bg-green-600/20 text-green-400 border-green-500",
    warning: "bg-yellow-600/20 text-yellow-400 border-yellow-500",
    error: "bg-red-600/20 text-red-400 border-red-500",
    info: "bg-cyan-600/20 text-cyan-400 border-cyan-500"
  };
  
  return (
    <span className={`
      inline-block px-3 py-1 rounded-full 
      text-sm font-semibold border
      ${variants[variant]}
      ${className}
    `}>
      {children}
    </span>
  );
};
```

### Number Badge
```tsx
const NumberBadge = ({ number, className = "" }) => (
  <span className={`
    inline-flex items-center justify-center 
    w-6 h-6 rounded-full 
    bg-cyan-600 text-white 
    text-xs font-bold
    ${className}
  `}>
    {number}
  </span>
);
```

---

## 🔗 Link Components

### Primary Link
```tsx
const PrimaryLink = ({ href, children, className = "" }) => (
  <a
    href={href}
    className={`
      text-cyan-400 hover:text-cyan-300 
      underline underline-offset-2
      transition-colors duration-200
      ${className}
    `}
  >
    {children}
  </a>
);
```

---

## 📋 List Components

### Styled List
```tsx
const StyledList = ({ items, className = "" }) => (
  <ul className={`space-y-2 ${className}`}>
    {items.map((item, index) => (
      <li key={index} className="flex items-start">
        <span className="text-cyan-400 mr-2">•</span>
        <span className="text-gray-300">{item}</span>
      </li>
    ))}
  </ul>
);
```

### Definition List
```tsx
const DefinitionList = ({ items, className = "" }) => (
  <dl className={`space-y-3 ${className}`}>
    {items.map(({ term, definition }, index) => (
      <div key={index} className="flex items-start">
        <dt className="w-16 text-center flex-shrink-0 text-lg font-bold text-cyan-400 bg-gray-900 px-2 py-1 rounded-md mr-4">
          {term}
        </dt>
        <dd className="text-sm text-gray-300 leading-tight pt-1">
          {definition}
        </dd>
      </div>
    ))}
  </dl>
);
```

---

## 🎨 Utility Classes Reference

### Common Combinations

**Glass Panel with Hover:**
```
bg-gray-800/60 rounded-lg p-4 border border-gray-700 transition-all duration-300 hover:border-cyan-600 hover:shadow-lg hover:shadow-cyan-900/20
```

**Gradient Text:**
```
text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400
```

**Focus Ring:**
```
focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500
```

**Smooth Transition:**
```
transition-all duration-300
```

**Hover Scale:**
```
transform hover:scale-105
```

---

## 🚀 Complete Example Usage

```tsx
import { 
  GlassPanel, 
  GradientHeading, 
  PrimaryButton, 
  TextInput,
  Card,
  LoadingState,
  EmptyState 
} from './components';

const MyApp = () => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  
  return (
    <div className="min-h-screen bg-gray-900 text-gray-200 font-sans p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-7xl mx-auto">
        
        <GradientHeading>My Application</GradientHeading>
        
        <GlassPanel className="mt-8">
          <TextInput
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your query..."
          />
          <PrimaryButton 
            onClick={() => setLoading(true)}
            isLoading={loading}
            className="mt-4"
          >
            Submit
          </PrimaryButton>
        </GlassPanel>
        
        {loading && (
          <LoadingState message="Processing..." />
        )}
        
        {!loading && !query && (
          <EmptyState
            icon={FingerprintIcon}
            title="No Data"
            description="Enter a query to get started"
          />
        )}
        
      </div>
    </div>
  );
};
```

---

## 📝 Notes

- All components use Tailwind CSS utility classes
- Components are fully responsive (mobile-first approach)
- All interactive elements have hover and focus states
- Transitions are applied for smooth animations
- Components follow the dark theme aesthetic
- All components are accessible and keyboard-navigable

---

This library provides everything you need to replicate the exact styling system from the Objective Generation Engine Visualizer!





























