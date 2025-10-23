# MaxManager Modern UI Guide

## 🎨 **Modern Interface Design**

MaxManager v1.8.0 features a completely redesigned interface with **collapsible sidebar** and **contextual header tabs** - a professional interface design for 3ds Max integration.

### ✨ **Key Features**

- **Collapsible Sidebar**: 80px (icons only) → 160px (icons + text)
- **Contextual Header**: Tabs change based on active sidebar button
- **SVG Logo**: Professional MaxManager logo with fallback
- **QtAwesome Icons**: Professional icon integration
- **Color Indicators**: Individual colors for each category
- **Thin Separators**: Minimalist design with 1px separators
- **Instant Animation**: No jitter, smooth expand/collapse
- **Focus-free Design**: No dotted outlines or hover effects

### 🏗️ **Architecture**

```
MaxManager Modern UI
├── ModernSidebar (collapsible)
│   ├── Logo Button (toggle)
│   ├── Category Buttons (5)
│   └── Separators
├── ModernHeader (contextual)
│   ├── Contextual Tabs
│   ├── Color Indicators
│   └── Version Label
└── Content Area (QStackedWidget)
```

### 🎯 **Categories**

1. **INI** - 3dsmax.ini configuration
   - Security, Performance, Renderer, Viewport, Settings
2. **UI** - Interface settings
   - Interface, Colors, Layout, Themes, Fonts
3. **Script** - MaxScript configuration
   - Startup, Hotkeys, Macros, Libraries, Debug
4. **CUIX** - Custom UI configuration
   - Menus, Toolbars, Quads, Shortcuts, Panels
5. **Projects** - Project management
   - Templates, Paths, Structure, Presets, Export

### 🎨 **Design Principles**

- **Minimalist**: Clean, uncluttered interface
- **Functional**: Every element serves a purpose
- **Consistent**: Uniform styling across all components
- **Professional**: Matches modern software standards
- **Accessible**: Clear visual hierarchy and feedback

### 🔧 **Technical Implementation**

- **PySide6**: Native Qt framework
- **ModernSidebar**: Custom collapsible sidebar widget
- **ModernHeader**: Custom contextual header widget
- **QStackedWidget**: Content switching without duplication
- **CSS Styling**: Professional dark theme (#333333, #4D4D4D)
- **SVG Integration**: Scalable vector graphics
- **QtAwesome**: Professional icon library

### 📱 **Responsive Design**

- **Sidebar**: Fixed width, collapsible
- **Header**: Fixed height (80px)
- **Content**: Flexible, adapts to window size
- **Version Label**: Fixed position (top-right)

### 🚀 **Performance**

- **Instant Response**: No animation delays
- **Memory Efficient**: Minimal widget creation
- **Fast Switching**: Immediate context changes
- **Stable**: No flickering or jitter

---

**Version**: 1.8.0  
**Last Updated**: 2025-10-23  
**Compatible**: 3ds Max 2025+