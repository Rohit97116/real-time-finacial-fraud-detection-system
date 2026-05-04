/**
 * Iridescence Component - WebGL Iridescent Effect with Mouse Reactivity
 * Vanilla JavaScript version for Flask/HTML templates
 * 
 * Usage:
 * <div id="iridescence" style="width: 100%; height: 400px;"></div>
 * <script>
 *   new Iridescence('#iridescence', {
 *     color: [0.5, 0.6, 0.8],
 *     mouseReact: true,
 *     amplitude: 0.1,
 *     speed: 1
 *   });
 * </script>
 */

class Iridescence {
  constructor(selector, options = {}) {
    this.container = typeof selector === 'string' ? document.querySelector(selector) : selector;
    if (!this.container) {
      console.error('Iridescence: Container not found');
      return;
    }

    this.options = {
      color: [0.5, 0.6, 0.8],
      speed: 1.0,
      amplitude: 0.1,
      mouseReact: true,
      ...options
    };

    this.mousePos = { x: 0.5, y: 0.5 };
    this.init();
  }

  init() {
    if (typeof OGL === 'undefined') {
      console.error('Iridescence: OGL library not loaded');
      return;
    }

    const { Renderer, Program, Mesh, Color, Triangle } = OGL;

    const vertexShader = `
attribute vec2 uv;
attribute vec2 position;

varying vec2 vUv;

void main() {
  vUv = uv;
  gl_Position = vec4(position, 0, 1);
}`;

    const fragmentShader = `
precision highp float;

uniform float uTime;
uniform vec3 uColor;
uniform vec3 uResolution;
uniform vec2 uMouse;
uniform float uAmplitude;
uniform float uSpeed;

varying vec2 vUv;

void main() {
  float mr = min(uResolution.x, uResolution.y);
  vec2 uv = (vUv.xy * 2.0 - 1.0) * uResolution.xy / mr;

  uv += (uMouse - vec2(0.5)) * uAmplitude;

  float d = -uTime * 0.5 * uSpeed;
  float a = 0.0;
  for (float i = 0.0; i < 8.0; ++i) {
    a += cos(i - d - a * uv.x);
    d += sin(uv.y * i + a);
  }
  d += uTime * 0.5 * uSpeed;
  vec3 col = vec3(cos(uv * vec2(d, a)) * 0.6 + 0.4, cos(a + d) * 0.5 + 0.5);
  col = cos(col * cos(vec3(d, a, 2.5)) * 0.5 + 0.5) * uColor;
  gl_FragColor = vec4(col, 1.0);
}`;

    this.renderer = new Renderer({
      webgl: 2,
      alpha: true,
      antialias: true,
      dpr: Math.min(window.devicePixelRatio || 1, 2)
    });

    const gl = this.renderer.gl;
    gl.clearColor(1, 1, 1, 1);

    const geometry = new Triangle(gl);
    this.program = new Program(gl, {
      vertex: vertexShader,
      fragment: fragmentShader,
      uniforms: {
        uTime: { value: 0 },
        uColor: { value: new Color(...this.options.color) },
        uResolution: {
          value: new Color(
            gl.canvas.width,
            gl.canvas.height,
            gl.canvas.width / gl.canvas.height
          )
        },
        uMouse: { value: new Float32Array([this.mousePos.x, this.mousePos.y]) },
        uAmplitude: { value: this.options.amplitude },
        uSpeed: { value: this.options.speed }
      }
    });

    this.mesh = new Mesh(gl, { geometry, program: this.program });
    this.container.appendChild(gl.canvas);

    const resize = () => {
      const scale = 1;
      this.renderer.setSize(this.container.offsetWidth * scale, this.container.offsetHeight * scale);
      this.program.uniforms.uResolution.value = new Color(
        gl.canvas.width,
        gl.canvas.height,
        gl.canvas.width / gl.canvas.height
      );
    };

    window.addEventListener('resize', resize, false);
    resize();

    const update = (t) => {
      this.animationFrameId = requestAnimationFrame(update);
      this.program.uniforms.uTime.value = t * 0.001;
      this.renderer.render({ scene: this.mesh });
    };
    this.animationFrameId = requestAnimationFrame(update);

    this.resizeListener = resize;
    this.handleMouseMove = (e) => {
      const rect = this.container.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = 1.0 - (e.clientY - rect.top) / rect.height;
      this.mousePos = { x, y };
      this.program.uniforms.uMouse.value[0] = x;
      this.program.uniforms.uMouse.value[1] = y;
    };

    if (this.options.mouseReact) {
      this.container.addEventListener('mousemove', this.handleMouseMove);
    }

    this.gl = gl;
  }

  destroy() {
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
    window.removeEventListener('resize', this.resizeListener);
    if (this.options.mouseReact) {
      this.container.removeEventListener('mousemove', this.handleMouseMove);
    }
    if (this.container && this.container.querySelector('canvas')) {
      try {
        this.container.removeChild(this.container.querySelector('canvas'));
      } catch (e) {
        // Ignore
      }
    }
    if (this.gl) {
      try {
        const ext = this.gl.getExtension('WEBGL_lose_context');
        if (ext) ext.loseContext();
      } catch (e) {
        // Ignore
      }
    }
  }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Iridescence;
}
