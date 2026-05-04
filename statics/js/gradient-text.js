/**
 * Gradient Text Animation Component
 * Vanilla JavaScript version for Flask/HTML templates
 * 
 * Usage:
 * <div class="gradient-text" data-colors="['#5227FF','#FF9FFC','#B497CF']" data-speed="8">
 *   Your text here
 * </div>
 * 
 * Then initialize with: new GradientText('.gradient-text');
 */

class GradientText {
  constructor(selector = '.gradient-text', options = {}) {
    this.elements = document.querySelectorAll(selector);
    this.defaults = {
      animationSpeed: 8,
      showBorder: false,
      direction: 'horizontal',
      pauseOnHover: false,
      yoyo: true,
      colors: ['#5227FF', '#FF9FFC', '#B497CF']
    };

    this.elements.forEach((element) => {
      this.initElement(element, options);
    });
  }

  initElement(element, options) {
    const config = {
      ...this.defaults,
      colors: this.parseColors(element),
      animationSpeed: parseFloat(element.dataset.speed || options.animationSpeed || this.defaults.animationSpeed),
      showBorder: element.dataset.showBorder === 'true' || options.showBorder || false,
      direction: element.dataset.direction || options.direction || 'horizontal',
      pauseOnHover: element.dataset.pauseOnHover === 'true' || options.pauseOnHover || false,
      yoyo: element.dataset.yoyo !== 'false' && (options.yoyo !== false),
      ...options
    };

    element.classList.add('animated-gradient-text');
    if (config.showBorder) element.classList.add('with-border');

    const state = {
      isPaused: false,
      elapsedTime: 0,
      lastTime: null,
      animationFrame: null,
      progress: 0
    };

    const animationDuration = config.animationSpeed * 1000;
    const gradientStyle = this.buildGradientStyle(config);

    // Apply gradient style
    element.style.backgroundImage = gradientStyle.backgroundImage;
    element.style.backgroundSize = gradientStyle.backgroundSize;
    element.style.backgroundRepeat = 'repeat';
    element.style.backgroundClip = 'text';
    element.style.webkitBackgroundClip = 'text';
    element.style.color = 'transparent';

    // Pause on hover
    if (config.pauseOnHover) {
      element.addEventListener('mouseenter', () => {
        state.isPaused = true;
      });
      element.addEventListener('mouseleave', () => {
        state.isPaused = false;
      });
    }

    // Animation loop
    const animate = (time) => {
      if (state.isPaused) {
        state.lastTime = null;
        state.animationFrame = requestAnimationFrame(animate);
        return;
      }

      if (state.lastTime === null) {
        state.lastTime = time;
        state.animationFrame = requestAnimationFrame(animate);
        return;
      }

      const deltaTime = time - state.lastTime;
      state.lastTime = time;
      state.elapsedTime += deltaTime;

      let progress;
      if (config.yoyo) {
        const fullCycle = animationDuration * 2;
        const cycleTime = state.elapsedTime % fullCycle;

        if (cycleTime < animationDuration) {
          progress = (cycleTime / animationDuration) * 100;
        } else {
          progress = 100 - ((cycleTime - animationDuration) / animationDuration) * 100;
        }
      } else {
        progress = (state.elapsedTime / animationDuration) * 100;
      }

      const backgroundPosition = this.calculateBackgroundPosition(progress, config.direction);
      element.style.backgroundPosition = backgroundPosition;

      state.animationFrame = requestAnimationFrame(animate);
    };

    state.animationFrame = requestAnimationFrame(animate);

    // Store state for cleanup
    element._gradientAnimationState = state;
  }

  parseColors(element) {
    const colorsAttr = element.dataset.colors;
    if (!colorsAttr) return this.defaults.colors;

    try {
      return JSON.parse(colorsAttr.replace(/'/g, '"'));
    } catch (e) {
      console.warn('Invalid colors format. Using defaults.', e);
      return this.defaults.colors;
    }
  }

  buildGradientStyle(config) {
    const gradientAngle =
      config.direction === 'horizontal'
        ? 'to right'
        : config.direction === 'vertical'
          ? 'to bottom'
          : 'to bottom right';

    const gradientColors = [...config.colors, config.colors[0]].join(', ');
    const backgroundSize =
      config.direction === 'horizontal'
        ? '300% 100%'
        : config.direction === 'vertical'
          ? '100% 300%'
          : '300% 300%';

    return {
      backgroundImage: `linear-gradient(${gradientAngle}, ${gradientColors})`,
      backgroundSize,
      backgroundRepeat: 'repeat'
    };
  }

  calculateBackgroundPosition(progress, direction) {
    if (direction === 'horizontal') {
      return `${progress}% 50%`;
    } else if (direction === 'vertical') {
      return `50% ${progress}%`;
    } else {
      return `${progress}% 50%`;
    }
  }

  destroy(selector = '.gradient-text') {
    document.querySelectorAll(selector).forEach((element) => {
      if (element._gradientAnimationState) {
        cancelAnimationFrame(element._gradientAnimationState.animationFrame);
        delete element._gradientAnimationState;
      }
    });
  }
}

// Auto-initialize if data-auto-init attribute is present
document.addEventListener('DOMContentLoaded', () => {
  if (document.querySelector('[data-auto-init="gradient-text"]')) {
    new GradientText('[data-auto-init="gradient-text"]');
  }
});
