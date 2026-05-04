# Gradient Text Component - Usage Guide

## Overview
The Gradient Text component is a vanilla JavaScript implementation that adds animated gradient backgrounds to text. It works seamlessly with your Flask templates without requiring React.

## Files Added
- `statics/js/gradient-text.js` - Main component logic
- `statics/css/gradient-text.css` - Styling
- `Templates/welcome.html` - Updated with example usage

## Quick Start

### 1. Add to Your Template Header
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/gradient-text.css') }}">
```

### 2. Add Script Before Closing `</body>` Tag
```html
<script src="{{ url_for('static', filename='js/gradient-text.js') }}"></script>
```

### 3. Use in Your HTML
```html
<span class="gradient-text" 
      data-colors='["#5227FF","#FF9FFC","#B497CF"]' 
      data-speed="8"
      data-auto-init="gradient-text">
  Your text here
</span>
```

## Configuration Options

### Data Attributes
| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `data-colors` | JSON Array | `["#5227FF","#FF9FFC","#B497CF"]` | Gradient colors (must start & end with same color for smooth loop) |
| `data-speed` | Number | `8` | Animation speed in seconds |
| `data-direction` | String | `horizontal` | Animation direction: `horizontal`, `vertical`, or `diagonal` |
| `data-pause-on-hover` | Boolean | `false` | Pause animation on hover if `true` |
| `data-yoyo` | Boolean | `true` | If `true`, animation reverses; if `false`, loops continuously |
| `data-show-border` | Boolean | `false` | Show border around text if `true` |
| `data-auto-init` | String | N/A | Set to `gradient-text` to auto-initialize |

## Usage Examples

### Example 1: Hero Headline (Current Implementation)
```html
<h1>Introducing <span 
    class="gradient-text" 
    data-colors='["#5227FF","#FF9FFC","#B497CF"]' 
    data-speed="8"
    data-auto-init="gradient-text">Fraud Detection Pro</span></h1>
```

### Example 2: With Border
```html
<span class="gradient-text" 
      data-colors='["#FF6B6B","#4ECDC4","#45B7D1"]' 
      data-speed="5"
      data-show-border="true"
      data-auto-init="gradient-text">
  Premium Feature
</span>
```

### Example 3: Vertical Animation
```html
<h2 class="gradient-text" 
    data-colors='["#00D4FF","#0099FF","#00D4FF"]' 
    data-direction="vertical"
    data-speed="10"
    data-auto-init="gradient-text">
  Vertical Gradient
</h2>
```

### Example 4: Pause on Hover
```html
<span class="gradient-text" 
      data-colors='["#FFD700","#FFA500","#FF8C00"]' 
      data-pause-on-hover="true"
      data-speed="6"
      data-auto-init="gradient-text">
  Hover to pause
</span>
```

### Example 5: Continuous Loop (No Yoyo)
```html
<span class="gradient-text" 
      data-colors='["#FF1493","#FF69B4","#FFB6C1"]' 
      data-yoyo="false"
      data-speed="8"
      data-auto-init="gradient-text">
  Continuous Loop
</span>
```

## Manual Initialization (Optional)

If you don't use `data-auto-init`, initialize manually:

```html
<script>
  // Initialize all elements with class 'gradient-text'
  new GradientText('.gradient-text');

  // Or with custom options
  new GradientText('.gradient-text', {
    animationSpeed: 10,
    showBorder: true,
    pauseOnHover: true
  });

  // Or for specific elements
  const elements = document.querySelectorAll('.my-custom-class');
  elements.forEach(el => {
    new GradientText(el, { animationSpeed: 5 });
  });
</script>
```

## CSS Customization

### Override Default Styles
```css
.animated-gradient-text {
  font-size: 2rem;
  font-weight: bold;
  border-radius: 0.75rem;
}

.animated-gradient-text.with-border {
  background: rgba(30, 20, 50, 0.9);
  border: 2px solid #5227FF;
}
```

## Gradient Color Tips

### Best Practices
- **For YoYo Animation**: Start and end with the same color for seamless transitions
  ```json
  ["#5227FF","#FF9FFC","#5227FF"]
  ```

- **Smooth Transitions**: Use 3-5 colors for natural gradients
  ```json
  ["#FF0080","#FF8C00","#40E0D0","#FF0080"]
  ```

- **High Contrast**: Mix bright and dark colors for visibility
  ```json
  ["#FFFFFF","#000000","#FFFFFF"]
  ```

### Recommended Color Palettes

**Cyan to Pink (Current)**
```
["#5227FF","#FF9FFC","#B497CF"]
```

**Ocean Blue**
```
["#00D4FF","#0099FF","#005FFF"]
```

**Sunset**
```
["#FF6B6B","#FFA500","#FFD700"]
```

**Forest**
```
["#00AA44","#00FF88","#00AA44"]
```

## Performance Considerations

- Uses `requestAnimationFrame` for smooth 60fps animations
- Respects `prefers-reduced-motion` for accessibility
- Minimal DOM manipulation
- Can handle multiple gradient texts simultaneously

## Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- IE11: ❌ Not supported

## Cleanup (If Needed)

```javascript
// Stop and remove all gradient animations
const gradientText = new GradientText('.gradient-text');
gradientText.destroy('.gradient-text');
```

## Common Issues

### Text Not Showing Gradient
- Ensure `data-colors` is valid JSON format
- Check that colors are in hex format (#RRGGBB)
- Verify that text color is NOT explicitly set to black

### Animation Too Fast/Slow
- Increase/decrease `data-speed` value (in seconds)
- Example: `data-speed="5"` for faster, `data-speed="15"` for slower

### Border Not Showing
- Set `data-show-border="true"`
- Adjust background color in CSS if needed

## Advanced: Custom Animation Speed

For finer control, modify the `animationSpeed` directly:

```javascript
const gradient = new GradientText('.my-text', {
  animationSpeed: 3.5,  // 3.5 seconds per cycle
  yoyo: true
});
```

---

**Last Updated**: 2026-05-04
**Version**: 1.0
