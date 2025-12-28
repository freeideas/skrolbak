// Animated Background Web Component
class AnimatedBackground extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });

    // $REQ_ANIMATEDBG_011: Initial camera state - all velocities 0, all rotations 0°, zoom 100%
    this.state = {
      xPanVel: 0,      // $REQ_CAMERA_002: pixels/sec
      yPanVel: 0,      // $REQ_CAMERA_003: pixels/sec
      xRotVel: 0,      // $REQ_CAMERA_004: degrees/sec
      yRotVel: 0,      // $REQ_CAMERA_005: degrees/sec
      zRotVel: 0,      // $REQ_CAMERA_006: degrees/sec
      zoomVel: 0,      // $REQ_CAMERA_007: percent/sec
      xPan: 0,         // $REQ_CAMERA_002: pixels
      yPan: 0,         // $REQ_CAMERA_003: pixels
      xRot: 0,         // $REQ_CAMERA_004: degrees
      yRot: 0,         // $REQ_CAMERA_005: degrees
      zRot: 0,         // $REQ_CAMERA_006: degrees
      zoom: 100        // $REQ_CAMERA_007: percent
    };

    this.startTime = null;
    this.lastLogTime = -1;
  }

  connectedCallback() {
    // $REQ_ANIMATEDBG_002: Parse src attribute
    this.src = this.getAttribute('src');
    // $REQ_ANIMATEDBG_003: Parse start-offset attribute (defaults to 0)
    this.startOffset = parseFloat(this.getAttribute('start-offset') || '0');

    // $REQ_ANIMATEDBG_004: Parse X-pan velocity bounds (defaults to -5, 5)
    this.xPanMin = parseFloat(this.getAttribute('x-pan-pps-min') || '-5');
    this.xPanMax = parseFloat(this.getAttribute('x-pan-pps-max') || '5');
    // $REQ_ANIMATEDBG_005: Parse Y-pan velocity bounds (defaults to -5, 5)
    this.yPanMin = parseFloat(this.getAttribute('y-pan-pps-min') || '-5');
    this.yPanMax = parseFloat(this.getAttribute('y-pan-pps-max') || '5');

    // $REQ_ANIMATEDBG_006: Parse X-rotation bounds (defaults to -10, 10)
    this.xRotMin = parseFloat(this.getAttribute('x-rot-min') || '-10');
    this.xRotMax = parseFloat(this.getAttribute('x-rot-max') || '10');
    // $REQ_ANIMATEDBG_007: Parse Y-rotation bounds (defaults to -10, 10)
    this.yRotMin = parseFloat(this.getAttribute('y-rot-min') || '-10');
    this.yRotMax = parseFloat(this.getAttribute('y-rot-max') || '10');
    // $REQ_ANIMATEDBG_008: Parse Z-rotation bounds (defaults to -20, 20)
    this.zRotMin = parseFloat(this.getAttribute('z-rot-min') || '-20');
    this.zRotMax = parseFloat(this.getAttribute('z-rot-max') || '20');

    // $REQ_ANIMATEDBG_009: Parse zoom bounds (defaults to 50, 200)
    this.zoomMin = parseFloat(this.getAttribute('z-pan-min') || '50');
    this.zoomMax = parseFloat(this.getAttribute('z-pan-max') || '200');

    this.render();
    this.startAnimation();
  }

  render() {
    // $REQ_ANIMATEDBG_010: Element fills parent container
    // $REQ_ANIMATEDBG_025: Background z-index
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          overflow: hidden;
          z-index: -1;  /* $REQ_ANIMATEDBG_025 */
        }

        #container {
          position: absolute;
          width: 200%;
          height: 200%;
          left: -50%;
          top: -50%;
          perspective: 1000px;  /* $REQ_ANIMATEDBG_024: 3D perspective */
        }

        #tileWrapper {
          position: absolute;
          width: 100%;
          height: 100%;
          transform-origin: center center;
        }

        .tile {
          position: absolute;
          background-image: url('${this.src}');
          background-size: 100% 100%;
        }
      </style>
      <div id="container">
        <div id="tileWrapper"></div>
      </div>
    `;

    this.container = this.shadowRoot.getElementById('container');
    this.tileWrapper = this.shadowRoot.getElementById('tileWrapper');
  }

  startAnimation() {
    this.startTime = performance.now() - (this.startOffset * 1000);
    this.boundAnimate = this.animate.bind(this);
    this.boundAnimate();
  }

  // $REQ_ANIMATEDBG_018: Deterministic noise function
  noise(seconds, channel) {
    const frac = (x) => x - Math.floor(x);
    return frac(Math.sin(seconds * 12.9898 + channel * 78.233) * 43758.5453);
  }

  // $REQ_ANIMATEDBG_021: Frame-rate independent state computation
  computeState(t) {
    const state = {
      xPanVel: 0, yPanVel: 0, xRotVel: 0, yRotVel: 0, zRotVel: 0, zoomVel: 0,
      xPan: 0, yPan: 0, xRot: 0, yRot: 0, zRot: 0, zoom: 100
    };

    // Process each second independently
    const totalSeconds = Math.floor(t);
    for (let sec = 0; sec <= totalSeconds; sec++) {
      const dt = (sec === totalSeconds) ? (t - sec) : 1.0;

      // Update velocities at the start of each second
      if (sec <= totalSeconds) {
        // $REQ_ANIMATEDBG_020: Unbounded parameters (pan) - velocity clamps at limit, acceleration reverses
        const xPanRange = this.xPanMax - this.xPanMin;
        const xPanVelMin = this.xPanMin * 0.1;
        const xPanVelMax = this.xPanMax * 0.1;
        let xPanAccel = (this.noise(sec, 0) < 0.5 ? -1 : 1) * xPanRange * 0.01;
        // (no $REQ_ID specified): Reverse acceleration if at velocity limit and would exceed it
        const newXPanVel = state.xPanVel + xPanAccel;
        if (newXPanVel < xPanVelMin || newXPanVel > xPanVelMax) {
          xPanAccel = -xPanAccel;
        }
        state.xPanVel += xPanAccel;
        if (state.xPanVel < xPanVelMin) state.xPanVel = xPanVelMin;
        if (state.xPanVel > xPanVelMax) state.xPanVel = xPanVelMax;

        // $REQ_ANIMATEDBG_020: Y-Pan velocity (unbounded parameter - velocity clamps, acceleration reverses)
        const yPanRange = this.yPanMax - this.yPanMin;
        const yPanVelMin = this.yPanMin * 0.1;
        const yPanVelMax = this.yPanMax * 0.1;
        let yPanAccel = (this.noise(sec, 1) < 0.5 ? -1 : 1) * yPanRange * 0.01;
        // (no $REQ_ID specified): Reverse acceleration if at velocity limit and would exceed it
        const newYPanVel = state.yPanVel + yPanAccel;
        if (newYPanVel < yPanVelMin || newYPanVel > yPanVelMax) {
          yPanAccel = -yPanAccel;
        }
        state.yPanVel += yPanAccel;
        if (state.yPanVel < yPanVelMin) state.yPanVel = yPanVelMin;
        if (state.yPanVel > yPanVelMax) state.yPanVel = yPanVelMax;

        // X-Rot velocity
        const xRotRange = this.xRotMax - this.xRotMin;
        const xRotAccel = (this.noise(sec, 2) < 0.5 ? -1 : 1) * xRotRange * 0.01;
        state.xRotVel += xRotAccel;
        if (state.xRotVel < -xRotRange * 0.1) state.xRotVel = -xRotRange * 0.1;
        if (state.xRotVel > xRotRange * 0.1) state.xRotVel = xRotRange * 0.1;

        // Y-Rot velocity
        const yRotRange = this.yRotMax - this.yRotMin;
        const yRotAccel = (this.noise(sec, 3) < 0.5 ? -1 : 1) * yRotRange * 0.01;
        state.yRotVel += yRotAccel;
        if (state.yRotVel < -yRotRange * 0.1) state.yRotVel = -yRotRange * 0.1;
        if (state.yRotVel > yRotRange * 0.1) state.yRotVel = yRotRange * 0.1;

        // Z-Rot velocity
        const zRotRange = this.zRotMax - this.zRotMin;
        const zRotAccel = (this.noise(sec, 4) < 0.5 ? -1 : 1) * zRotRange * 0.01;
        state.zRotVel += zRotAccel;
        if (state.zRotVel < -zRotRange * 0.1) state.zRotVel = -zRotRange * 0.1;
        if (state.zRotVel > zRotRange * 0.1) state.zRotVel = zRotRange * 0.1;

        // Zoom velocity
        const zoomRange = this.zoomMax - this.zoomMin;
        const zoomAccel = (this.noise(sec, 5) < 0.5 ? -1 : 1) * zoomRange * 0.01;
        state.zoomVel += zoomAccel;
        if (state.zoomVel < -zoomRange * 0.1) state.zoomVel = -zoomRange * 0.1;
        if (state.zoomVel > zoomRange * 0.1) state.zoomVel = zoomRange * 0.1;
      }

      // $REQ_ANIMATEDBG_012: Integrate position from velocity (unbounded pan)
      state.xPan += state.xPanVel * dt;  // $REQ_ANIMATEDBG_012: X-Pan
      state.yPan += state.yPanVel * dt;  // $REQ_ANIMATEDBG_013: Y-Pan

      // $REQ_ANIMATEDBG_019: Bounded parameters - value clamps at limit, velocity reverses
      state.xRot += state.xRotVel * dt;  // $REQ_ANIMATEDBG_014: X-Rotation
      if (state.xRot < this.xRotMin) { state.xRot = this.xRotMin; state.xRotVel = -state.xRotVel; }
      if (state.xRot > this.xRotMax) { state.xRot = this.xRotMax; state.xRotVel = -state.xRotVel; }

      state.yRot += state.yRotVel * dt;  // $REQ_ANIMATEDBG_015: Y-Rotation
      if (state.yRot < this.yRotMin) { state.yRot = this.yRotMin; state.yRotVel = -state.yRotVel; }
      if (state.yRot > this.yRotMax) { state.yRot = this.yRotMax; state.yRotVel = -state.yRotVel; }

      state.zRot += state.zRotVel * dt;  // $REQ_ANIMATEDBG_016: Z-Rotation
      if (state.zRot < this.zRotMin) { state.zRot = this.zRotMin; state.zRotVel = -state.zRotVel; }
      if (state.zRot > this.zRotMax) { state.zRot = this.zRotMax; state.zRotVel = -state.zRotVel; }

      state.zoom += state.zoomVel * dt;  // $REQ_ANIMATEDBG_017: Zoom
      if (state.zoom < this.zoomMin) { state.zoom = this.zoomMin; state.zoomVel = -state.zoomVel; }
      if (state.zoom > this.zoomMax) { state.zoom = this.zoomMax; state.zoomVel = -state.zoomVel; }
    }

    return state;
  }

  animate() {
    try {
      const now = performance.now();
      const elapsed = (now - this.startTime) / 1000;

      // $REQ_ANIMATEDBG_022: Log time offset once per second
      const currentSecond = Math.floor(elapsed);
      if (currentSecond > this.lastLogTime) {
        console.log(`t=${currentSecond}`);
        this.lastLogTime = currentSecond;
      }

      // Compute state analytically
      this.state = this.computeState(elapsed);

      // Update transform
      this.updateTransform();

      requestAnimationFrame(this.boundAnimate);
    } catch(e) {
      console.error('Animation error:', e);
      throw e;
    }
  }

  updateTransform() {
    // Load image to get tile size
    if (!this.tileSize) {
      const img = new Image();
      img.onload = () => {
        this.tileSize = { width: img.width, height: img.height };
        this.updateTiles();
      };
      img.src = this.src;
      return;
    }

    this.updateTiles();
  }

  // Dynamic tiling based on transform
  updateTiles() {
    const vw = window.innerWidth;
    const vh = window.innerHeight;

    // $REQ_ANIMATEDBG_023: Dynamic tiling - apply transform
    const scale = this.state.zoom / 100;  // $REQ_ANIMATEDBG_017: Zoom
    const transform = `
      translate(-50%, -50%)
      rotateX(${this.state.xRot}deg)
      rotateY(${this.state.yRot}deg)
      rotateZ(${this.state.zRot}deg)
      scale(${scale})
      translate(${-this.state.xPan}px, ${-this.state.yPan}px)
    `;
    this.tileWrapper.style.transform = transform;

    // Calculate visible tile range
    const margin = 2;
    const tileW = this.tileSize.width * scale;
    const tileH = this.tileSize.height * scale;

    const centerX = this.state.xPan;
    const centerY = this.state.yPan;

    const minCol = Math.floor((centerX - vw) / this.tileSize.width) - margin;
    const maxCol = Math.ceil((centerX + vw) / this.tileSize.width) + margin;
    const minRow = Math.floor((centerY - vh) / this.tileSize.height) - margin;
    const maxRow = Math.ceil((centerY + vh) / this.tileSize.height) + margin;

    // Render tiles dynamically
    this.tileWrapper.innerHTML = '';
    for (let row = minRow; row <= maxRow; row++) {
      for (let col = minCol; col <= maxCol; col++) {
        const tile = document.createElement('div');
        tile.className = 'tile';
        tile.style.left = `${col * this.tileSize.width}px`;
        tile.style.top = `${row * this.tileSize.height}px`;
        tile.style.width = `${this.tileSize.width}px`;
        tile.style.height = `${this.tileSize.height}px`;
        this.tileWrapper.appendChild(tile);
      }
    }
  }
}

// Register custom element
customElements.define('animated-background', AnimatedBackground);
