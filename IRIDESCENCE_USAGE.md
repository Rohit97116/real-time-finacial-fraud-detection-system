# Iridescence Component - WebGL Iridescent Effect

## Overview
Iridescence is a WebGL-powered component that creates stunning iridescent color effects with optional mouse reactivity. Perfect for accent elements, decorative sections, or creating visual interest on interactive surfaces.

## Files
- `statics/js/iridescence.js` - Main component logic
- `statics/css/iridescence.css` - Styling
- `Templates/details_single.html` - Active implementation (form accent)

## Installation

### 1. Add OGL Library (CDN)
```html
<script src="https://cdn.jsdelivr.net/npm/ogl@0.0.8/dist/ogl.umd.js"></script>
```

### 2. Include CSS & JS
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/iridescence.css') }}">
<script src="{{ url_for('static', filename='js/iridescence.js') }}"></script>
```

## Basic Usage

### HTML
```html
<div id="iridescence" class="iridescence-container" style="width: 100%; height: 400px;"></div>
```

### JavaScript
```javascript
new Iridescence('#iridescence', {
  color: [0.5, 0.6, 0.8],
  mouseReact: true,
  amplitude: 0.1,
  speed: 1
});
```

## Configuration Options

### Color Options
| Option | Type | Format | Default | Description |
|--------|------|--------|---------|-------------|
| `color` | Array | [R, G, B] (0-1) | [0.5, 0.6, 0.8] | Base iridescence color |

Examples:
- Pure Red: `[1, 0, 0]`
- Pure Green: `[0, 1, 0]`
- Pure Blue: `[0, 0, 1]`
- Mid Blue: `[0.5, 0.6, 0.8]`
- Cyan: `[0, 1, 1]`
- Purple: `[1, 0, 1]`
- Yellow: `[1, 1, 0]`

### Animation Options
| Option | Type | Range | Default | Description |
|--------|------|-------|---------|-------------|
| `speed` | Float | 0.1-5 | 1 | Animation speed multiplier |
| `amplitude` | Float | 0-0.5 | 0.1 | Wave amplitude intensity |

### Interaction Options
| Option | Type | Values | Default | Description |
|--------|------|--------|---------|-------------|
| `mouseReact` | Boolean | true/false | true | Enable mouse tracking |

## Usage Examples

### Example 1: Form Accent (Current Implementation)
```javascript
new Iridescence('#iridescence-accent', {
  color: [0.5, 0.6, 0.8],
  mouseReact: true,
  amplitude: 0.15,
  speed: 0.8
});
```

### Example 2: Static Blue Iridescence
```javascript
new Iridescence('#iridescence-element', {
  color: [0.2, 0.5, 1],      // Bright blue
  mouseReact: false,          // No mouse interaction
  amplitude: 0.08,
  speed: 0.5
});
```

### Example 3: Interactive Pink Iridescence
```javascript
new Iridescence('#iridescence-element', {
  color: [1, 0.4, 0.8],       // Pink
  mouseReact: true,           // React to mouse
  amplitude: 0.2,             // Strong response
  speed: 1.5                  // Fast animation
});
```

### Example 4: Subtle Cyan Accent
```javascript
new Iridescence('#iridescence-element', {
  color: [0.3, 1, 1],         // Cyan
  mouseReact: true,
  amplitude: 0.05,            // Very subtle
  speed: 0.6
});
```

### Example 5: Full Screen Interactive
```javascript
new Iridescence('#iridescence-fullscreen', {
  color: [0.8, 0.2, 1],       // Purple
  mouseReact: true,           // Fully interactive
  amplitude: 0.25,
  speed: 2                    // Fast
});
```

### Example 6: Hypnotic Pattern
```javascript
new Iridescence('#iridescence-element', {
  color: [1, 0.5, 0],         // Orange
  mouseReact: true,
  amplitude: 0.3,             // High amplitude
  speed: 3                    // Very fast
});
```

## Color Palette Guide

### Cool Tones
| Color | RGB Values | Use Case |
|-------|-----------|----------|
| Cyan | [0, 1, 1] | Tech, fresh |
| Blue | [0.4, 0.6, 1] | Professional, calm |
| Purple | [0.7, 0, 1] | Premium, creative |
| Teal | [0.2, 0.8, 0.8] | Balanced, modern |

### Warm Tones
| Color | RGB Values | Use Case |
|-------|-----------|----------|
| Orange | [1, 0.6, 0] | Energy, warmth |
| Pink | [1, 0.4, 0.8] | Fun, playful |
| Red | [1, 0.2, 0.2] | Alert, attention |
| Yellow | [1, 1, 0.3] | Bright, happy |

### Custom Blends
```javascript
// Turquoise
color: [0, 0.9, 1]

// Magenta
color: [1, 0, 1]

// Lime
color: [0.5, 1, 0]

// Coral
color: [1, 0.5, 0.5]

// Indigo
color: [0.3, 0, 0.8]
```

## Positioning Strategies

### Top Accent Bar
```html
<div id="iridescence-accent" 
     style="position: absolute; top: 0; left: 0; right: 0; height: 80px; 
             border-radius: 18px 18px 0 0; opacity: 0.6; pointer-events: none;"></div>
```

### Side Panel Highlight
```html
<div id="iridescence-panel" 
     style="position: absolute; left: 0; top: 0; bottom: 0; width: 60px; 
             opacity: 0.5; pointer-events: none;"></div>
```

### Floating Element
```html
<div id="iridescence-float" 
     style="position: fixed; bottom: 20px; right: 20px; 
             width: 200px; height: 200px; border-radius: 50%;"></div>
```

### Full Background
```html
<div id="iridescence-bg" 
     style="position: fixed; inset: 0; z-index: -1; width: 100%; height: 100%;"></div>
```

## Advanced Techniques

### Responsive Sizing
```javascript
const container = document.getElementById('iridescence');

function resize() {
  if (window.innerWidth < 768) {
    // Mobile: smaller amplitude
    container.style.height = '200px';
  } else {
    // Desktop: normal
    container.style.height = '400px';
  }
}

window.addEventListener('resize', resize);
resize();
```

### Multiple Iridescence Elements
```javascript
// Create different iridescence effects
const irid1 = new Iridescence('#accent-1', {
  color: [0.5, 0.6, 0.8],
  mouseReact: true
});

const irid2 = new Iridescence('#accent-2', {
  color: [1, 0.4, 0.8],
  mouseReact: false
});
```

### Dynamic Color Switching
```javascript
let currentColor = [0.5, 0.6, 0.8];

function switchColor() {
  currentColor = [Math.random(), Math.random(), Math.random()];
  
  // Destroy and recreate with new color
  iridescence.destroy();
  iridescence = new Iridescence('#element', {
    color: currentColor,
    mouseReact: true
  });
}

setInterval(switchColor, 5000);
```

### Speed Control Based on Scroll
```javascript
let speedMultiplier = 1;

window.addEventListener('scroll', () => {
  speedMultiplier = 0.5 + (window.scrollY / window.innerHeight);
  // Update speed programmatically if needed
});
```

## Performance Optimization

### Mobile Optimization
```javascript
const isMobile = /iPhone|iPad|Android/i.test(navigator.userAgent);

new Iridescence('#element', {
  color: [0.5, 0.6, 0.8],
  mouseReact: !isMobile,    // Disable on mobile
  amplitude: isMobile ? 0.08 : 0.15,
  speed: isMobile ? 0.5 : 1
});
```

### Conditional Rendering
```javascript
if (window.devicePixelRatio > 2) {
  // High DPI: simpler animation
  amplitude: 0.1;
} else {
  amplitude: 0.2;
}
```

## CSS Customization

### Opacity Control
```css
.iridescence-container {
  opacity: 0.7;  /* Semi-transparent */
}
```

### Blend Mode Effects
```css
.iridescence-container {
  mix-blend-mode: screen;    /* Additive blend */
}

.iridescence-container {
  mix-blend-mode: multiply;  /* Multiplicative blend */
}

.iridescence-container {
  mix-blend-mode: overlay;   /* Overlay blend */
}
```

### Border & Shadow
```css
.iridescence-container {
  border-radius: 50%;
  box-shadow: 0 0 20px rgba(100, 150, 255, 0.5);
}
```

## Accessibility Considerations

The component respects `prefers-reduced-motion`:
- If enabled, shows static gradient fallback
- Canvas animation is hidden
- Device resources preserved

```css
@media (prefers-reduced-motion: reduce) {
  .iridescence-container {
    background: linear-gradient(45deg, #6f8eff, #4df2ff);
  }

  .iridescence-container canvas {
    display: none;
  }
}
```

## Browser Support

- Chrome/Edge: ✅ Full WebGL2 support
- Firefox: ✅ Full WebGL2 support
- Safari: ✅ Full WebGL2 support (iOS 15+)
- Mobile: ✅ Supported (optimized)

## Cleanup

```javascript
const iridescence = new Iridescence('#element');

// Later, destroy the animation
iridescence.destroy();
```

## Current Implementation

Active on `details_single.html`:
- Position: Absolute, top-aligned on form card
- Height: 80px accent bar
- Opacity: 0.6 for subtle effect
- Mouse Reactive: True
- Color: [0.5, 0.6, 0.8] (blue)
- Speed: 0.8 (moderate)
- Amplitude: 0.15 (noticeable but not overwhelming)

## Troubleshooting

### Canvas Not Rendering
- Check OGL library is loaded
- Verify container has dimensions
- Inspect browser console for errors

### Mouse Not Responding
- Ensure `mouseReact: true`
- Check mouse coordinates are in valid range (0-1)
- Verify event listeners are attached

### Colors Look Wrong
- RGB values should be 0-1, not 0-255
- Test with solid colors like [1, 0, 0] (red)
- Check display color profile

### Performance Issues
- Reduce `amplitude` value
- Lower `speed` value
- Use static iridescence (mouseReact: false)
- Check GPU temperature

## Creative Ideas

1. **Form Enhancement**: Use on form headers for visual interest
2. **Card Accents**: Add iridescence to card corners
3. **Button Highlights**: Animated button overlays
4. **Background Frames**: Fixed position background accent
5. **Loading Indicators**: Dynamic iridescence during async operations
6. **Interactive Gallery**: Iridescence follows cursor
7. **Product Showcase**: Highlight premium features

---

**Library**: OGL v0.0.8
**WebGL Version**: 2.0
**Last Updated**: 2026-05-04
