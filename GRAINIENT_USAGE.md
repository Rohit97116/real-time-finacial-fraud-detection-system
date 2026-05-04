# Grainient Component - WebGL Animated Gradient

## Overview
Grainient is a WebGL-powered animated gradient component with advanced effects including noise, warp distortion, color blending, and grain texture. It creates smooth, flowing gradient animations perfect for backgrounds and visual effects.

## Files
- `statics/js/grainient.js` - Main component logic
- `statics/css/grainient.css` - Styling
- `Templates/welcome.html` - Active implementation (background)

## Installation

### 1. Add OGL Library (CDN)
```html
<script src="https://cdn.jsdelivr.net/npm/ogl@0.0.8/dist/ogl.umd.js"></script>
```

### 2. Include CSS & JS
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/grainient.css') }}">
<script src="{{ url_for('static', filename='js/grainient.js') }}"></script>
```

## Basic Usage

### HTML
```html
<div id="grainient-bg" class="grainient-container" style="width: 100%; height: 600px; position: relative;"></div>
```

### JavaScript
```javascript
new Grainient('#grainient-bg', {
  color1: '#FF9FFC',
  color2: '#5227FF',
  color3: '#B497CF',
  timeSpeed: 0.25
});
```

## Configuration Options

### Color Options
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `color1` | Hex String | `#FF9FFC` | Primary gradient color |
| `color2` | Hex String | `#5227FF` | Secondary gradient color |
| `color3` | Hex String | `#B497CF` | Tertiary gradient color |

### Animation Options
| Option | Type | Range | Default | Description |
|--------|------|-------|---------|-------------|
| `timeSpeed` | Float | 0.1-2 | 0.25 | Animation speed multiplier |
| `warpStrength` | Float | 0.5-3 | 1 | Warp distortion intensity |
| `warpFrequency` | Float | 1-20 | 5 | Number of warp waves |
| `warpSpeed` | Float | 0.5-5 | 2 | Warp animation speed |
| `warpAmplitude` | Float | 10-100 | 50 | Warp wave height |

### Blend & Rotation Options
| Option | Type | Range | Default | Description |
|--------|------|-------|---------|-------------|
| `colorBalance` | Float | -1 to 1 | 0 | Color blend position |
| `blendAngle` | Float | 0-360 | 0 | Blend direction rotation |
| `blendSoftness` | Float | 0-0.5 | 0.05 | Blend transition smoothness |
| `rotationAmount` | Float | 0-1000 | 500 | Pattern rotation intensity |
| `noiseScale` | Float | 1-5 | 2 | Noise pattern scale |

### Visual Effects Options
| Option | Type | Range | Default | Description |
|--------|------|-------|---------|-------------|
| `grainAmount` | Float | 0-0.5 | 0.1 | Grain texture intensity |
| `grainScale` | Float | 1-5 | 2 | Grain pattern scale |
| `grainAnimated` | Boolean | true/false | false | Animate grain texture |
| `contrast` | Float | 0.5-3 | 1.5 | Color contrast |
| `gamma` | Float | 0.5-2 | 1 | Color gamma correction |
| `saturation` | Float | 0-2 | 1 | Color saturation |

### View Options
| Option | Type | Range | Default | Description |
|--------|------|-------|---------|-------------|
| `centerX` | Float | -1 to 1 | 0 | Horizontal center offset |
| `centerY` | Float | -1 to 1 | 0 | Vertical center offset |
| `zoom` | Float | 0.1-5 | 0.9 | View zoom level |

## Usage Examples

### Example 1: Welcome Page Background (Current)
```javascript
new Grainient('#grainient-bg', {
  color1: '#5227FF',
  color2: '#FF9FFC',
  color3: '#B497CF',
  timeSpeed: 0.25,
  warpStrength: 1,
  warpFrequency: 5,
  warpSpeed: 2,
  warpAmplitude: 50,
  grainAmount: 0.1,
  contrast: 1.5
});
```

### Example 2: Fast Smooth Gradient
```javascript
new Grainient('#grainient-bg', {
  color1: '#00D4FF',
  color2: '#0099FF',
  color3: '#005FFF',
  timeSpeed: 0.5,      // Faster animation
  warpStrength: 0.5,   // Subtle warp
  grainAmount: 0,      // No grain
  contrast: 1.2
});
```

### Example 3: Dramatic Psychedelic
```javascript
new Grainient('#grainient-bg', {
  color1: '#FF0080',
  color2: '#FF8C00',
  color3: '#00FF00',
  timeSpeed: 1,
  warpStrength: 2,     // Strong warp
  warpFrequency: 10,   // More waves
  rotationAmount: 1000, // Heavy rotation
  contrast: 2,
  saturation: 1.5
});
```

### Example 4: Subtle Organic
```javascript
new Grainient('#grainient-bg', {
  color1: '#4DF2FF',
  color2: '#6F8EFF',
  color3: '#4DF2FF',
  timeSpeed: 0.15,     // Very slow
  warpStrength: 0.3,   // Minimal warp
  blendSoftness: 0.2,  // Soft blends
  grainAmount: 0.05,
  contrast: 1.3
});
```

### Example 5: High-Contrast Dynamic
```javascript
new Grainient('#grainient-bg', {
  color1: '#FFFF00',
  color2: '#FF00FF',
  color3: '#00FFFF',
  timeSpeed: 0.8,
  warpAmplitude: 80,
  grainAmount: 0.2,
  contrast: 2,
  zoom: 0.7
});
```

## Advanced Techniques

### Directional Blend Control
Adjust blend angle for different animation directions:

```javascript
// Vertical blend
new Grainient(selector, {
  blendAngle: 90,
  blendSoftness: 0.1
});

// Diagonal blend
new Grainient(selector, {
  blendAngle: 45,
  blendSoftness: 0.15
});
```

### Zoom & Pan Effects
Create focus effects:

```javascript
// Zoomed in
new Grainient(selector, {
  zoom: 0.5,
  centerX: 0.2,
  centerY: -0.1
});

// Wide view
new Grainient(selector, {
  zoom: 1.5,
  centerX: 0,
  centerY: 0
});
```

### Noise & Texture Control
Fine-tune pattern details:

```javascript
// Smooth, clean gradients
new Grainient(selector, {
  noiseScale: 1,    // Fine noise
  grainAmount: 0,   // No grain
  rotationAmount: 200
});

// Textured, organic
new Grainient(selector, {
  noiseScale: 3,      // Coarse noise
  grainAmount: 0.25,  // Heavy grain
  grainAnimated: true // Moving grain
});
```

## Performance Tips

1. **Reduce grain animation** for better performance:
   ```javascript
   grainAnimated: false
   ```

2. **Lower warp frequency** for simpler patterns:
   ```javascript
   warpFrequency: 2  // Instead of 5-10
   ```

3. **Disable high contrast** to reduce shader complexity:
   ```javascript
   contrast: 1  // Natural range
   ```

4. **Use fixed zoom** to avoid recalculations:
   ```javascript
   zoom: 1
   ```

## Color Palette Combinations

### Ocean Vibes
```javascript
color1: '#00D4FF'
color2: '#0099FF'
color3: '#00D4FF'
```

### Sunset Paradise
```javascript
color1: '#FF6B6B'
color2: '#FFA500'
color3: '#FF6B6B'
```

### Forest Green
```javascript
color1: '#00AA44'
color2: '#00FF88'
color3: '#00AA44'
```

### Royal Purple
```javascript
color1: '#9D4EDD'
color2: '#3A86FF'
color3: '#9D4EDD'
```

### Neon Pink
```javascript
color1: '#FF006E'
color2: '#FB5607'
color3: '#FF006E'
```

## Cleanup

```javascript
const grainient = new Grainient('#my-element');

// Later, destroy the animation
grainient.destroy();
```

## Accessibility

The component respects `prefers-reduced-motion`:
- If enabled, shows static gradient fallback
- Canvas animation is hidden
- Device resources preserved

## Browser Support

- Chrome/Edge: ✅ Full WebGL2 support
- Firefox: ✅ Full WebGL2 support
- Safari: ✅ Full WebGL2 support (iOS 15+)
- Mobile: ✅ Supported (with DPR optimization)

## Troubleshooting

### Black/White Screen
- Ensure OGL library is loaded: `typeof OGL !== 'undefined'`
- Check container dimensions are set
- Verify colors are valid hex format

### Performance Issues
- Reduce `warpFrequency` and `grainScale`
- Disable `grainAnimated`
- Lower `contrast` value
- Check device GPU capabilities

### Colors Not Showing
- Ensure container has proper size
- Check that colors are different (same colors = no gradient)
- Verify hex format: `#RRGGBB`

## Current Implementation

The component is actively used as a background on `welcome.html`:
- Positioned fixed behind page content
- Z-index: -1 for background layering
- Responsive to container size
- Optimized for performance with DPR 1-2x

---

**Library**: OGL v0.0.8
**WebGL Version**: 2.0
**Last Updated**: 2026-05-04
