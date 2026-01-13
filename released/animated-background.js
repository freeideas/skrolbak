// Custom element <drift-bg> with src attribute
class DriftBg extends HTMLElement {
  constructor() {
    super();
    // Canvas and rendering context
    this.canvas = document.createElement('canvas');  // $REQ_DRIFTBG_003
    this.ctx = this.canvas.getContext('2d');
    this.image = new Image();
    this.imageLoaded = false;

    // World units from -50 to +50 (range 100)
    // Camera offset Z = 80 units
    this.CAMERA_Z = 80;  // $REQ_DRIFTBG_006
    this.WORLD_SIZE = 100;  // $REQ_DRIFTBG_005

    // Time variable for driving animations
    this.startTime = Date.now() / 1000;
    this.lastMouseMoveTime = 0;

    // Follower state variables
    this.followerX = 0;
    this.followerY = 0;
    this.followerZ = 0;
    this.followerU = 0; // Roll (Z-axis rotation)
    this.followerV = 0; // Pitch (X-axis tilt)
    this.followerW = 0; // Yaw (Y-axis tilt)

    // Tile size and grid
    this.TILE_WIDTH = 30;  // $REQ_DRIFTBG_019
    this.imageAspect = 1;

    // Console logging once per second
    this.lastLogTime = 0;
  }

  connectedCallback() {  // $REQ_DRIFTBG_001
    // Setup canvas and styling
    this.style.display = 'block';  // $REQ_DRIFTBG_028
    this.style.backgroundColor = '#000';  // $REQ_DRIFTBG_004
    this.appendChild(this.canvas);  // $REQ_DRIFTBG_003

    // Load image from src attribute  // $REQ_DRIFTBG_002
    const src = this.getAttribute('src');
    if (src) {
      this.loadImage(src);
    }

    // Mouse move event handler  // $REQ_DRIFTBG_015
    this.canvas.addEventListener('mousemove', (e) => {
      this.handleMouseMove(e);
    });

    // Start animation loop
    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
    this.animate();
  }

  static get observedAttributes() {
    // Watch src attribute changes
    return ['src'];
  }

  attributeChangedCallback(name, oldValue, newValue) {  // $REQ_DRIFTBG_002
    // Reload image when src changes
    if (name === 'src' && newValue && newValue !== oldValue) {
      this.loadImage(newValue);
    }
  }

  loadImage(src) {
    this.imageLoaded = false;
    this.image.onload = () => {
      this.imageLoaded = true;
      this.imageAspect = this.image.height / this.image.width;
    };
    this.image.src = src;
  }

  resizeCanvas() {  // $REQ_DRIFTBG_003
    // Canvas fills component dimensions
    this.canvas.width = this.offsetWidth;
    this.canvas.height = this.offsetHeight;
  }

  handleMouseMove(e) {  // $REQ_DRIFTBG_015
    // Map mouse screen coordinates to world coordinates
    const rect = this.canvas.getBoundingClientRect();
    const screenX = e.clientX - rect.left;
    const screenY = e.clientY - rect.top;

    // Project screen to world at Z=0
    const centerX = this.canvas.width / 2;
    const centerY = this.canvas.height / 2;
    const K = this.calculateProjectionConstant();
    const scale = K / this.CAMERA_Z;

    this.mouseWorldX = (screenX - centerX) / scale;  // $REQ_DRIFTBG_015
    this.mouseWorldY = (screenY - centerY) / scale;  // $REQ_DRIFTBG_015
    this.lastMouseMoveTime = Date.now();  // $REQ_DRIFTBG_016
  }

  calculateProjectionConstant() {  // $REQ_DRIFTBG_006
    // K such that 100 world units fill canvas width at Z=0
    return (this.canvas.width * this.CAMERA_Z) / this.WORLD_SIZE;
  }

  getTargetState(t) {  // $REQ_DRIFTBG_007
    // Spiral motion for X, Y
    const GROWTH_SPEED = 2.0;  // $REQ_DRIFTBG_007: 2.0 units/second
    const CYCLE_DURATION = 25;  // $REQ_DRIFTBG_007: 25 seconds
    const tLocal = t % CYCLE_DURATION;
    const r = tLocal * GROWTH_SPEED;
    const spiralX = r * Math.cos(t);  // $REQ_DRIFTBG_007
    const spiralY = r * Math.sin(t);  // $REQ_DRIFTBG_007

    // Depth oscillation (Z)
    const z = 48 * Math.sin((2 * Math.PI * t) / 20);  // $REQ_DRIFTBG_008

    // Pitch (V) oscillation - X-axis tilt
    const MAX_TILT = (20 * Math.PI) / 180; // 20 degrees in radians
    const v = MAX_TILT * Math.sin((2 * Math.PI * t) / 13);  // $REQ_DRIFTBG_009

    // Yaw (W) oscillation - Y-axis tilt
    const w = MAX_TILT * Math.cos((2 * Math.PI * t) / 17);  // $REQ_DRIFTBG_010

    // Roll (U) oscillation - Z-axis rotation
    const u = MAX_TILT * Math.sin((2 * Math.PI * t) / 23);  // $REQ_DRIFTBG_011

    // Mouse mode vs Spiral mode  // $REQ_DRIFTBG_016, $REQ_DRIFTBG_017
    const timeSinceMouseMove = Date.now() - this.lastMouseMoveTime;
    const isMouseMode = timeSinceMouseMove < 2000;  // $REQ_DRIFTBG_016, $REQ_DRIFTBG_017

    let targetX, targetY;
    if (isMouseMode && this.mouseWorldX !== undefined) {
      targetX = this.mouseWorldX;
      targetY = this.mouseWorldY;
    } else {
      targetX = spiralX;
      targetY = spiralY;
    }

    return { x: targetX, y: targetY, z, u, v, w, isMouseMode };
  }

  updateFollower(target, dt) {  // $REQ_DRIFTBG_012
    // Easing function with different rates (per-second rates)
    const STANDARD_RATE = 0.1;  // $REQ_DRIFTBG_013: 10% per second
    const ACTIVE_RATE = 0.5;    // $REQ_DRIFTBG_014: 50% per second

    // XY uses active rate in mouse mode, standard rate in spiral mode
    const xyRate = target.isMouseMode ? ACTIVE_RATE : STANDARD_RATE;  // $REQ_DRIFTBG_013, $REQ_DRIFTBG_014

    this.followerX += (target.x - this.followerX) * xyRate * dt;  // $REQ_DRIFTBG_013, $REQ_DRIFTBG_014
    this.followerY += (target.y - this.followerY) * xyRate * dt;  // $REQ_DRIFTBG_013, $REQ_DRIFTBG_014

    // Z, U, V, W always use standard rate
    this.followerZ += (target.z - this.followerZ) * STANDARD_RATE * dt;  // $REQ_DRIFTBG_013
    this.followerU += (target.u - this.followerU) * STANDARD_RATE * dt;  // $REQ_DRIFTBG_013
    this.followerV += (target.v - this.followerV) * STANDARD_RATE * dt;  // $REQ_DRIFTBG_013
    this.followerW += (target.w - this.followerW) * STANDARD_RATE * dt;  // $REQ_DRIFTBG_013
  }

  rotatePoint3D(x, y, z, u, v, w) {  // $REQ_DRIFTBG_020
    // Apply rotations in order: Roll (U), Yaw (W), Pitch (V)

    // Roll around Z-axis  // $REQ_DRIFTBG_020
    let x1 = x * Math.cos(u) - y * Math.sin(u);
    let y1 = x * Math.sin(u) + y * Math.cos(u);
    let z1 = z;

    // Yaw around Y-axis  // $REQ_DRIFTBG_020
    let x2 = x1 * Math.cos(w) + z1 * Math.sin(w);
    let y2 = y1;
    let z2 = -x1 * Math.sin(w) + z1 * Math.cos(w);

    // Pitch around X-axis  // $REQ_DRIFTBG_020
    let x3 = x2;
    let y3 = y2 * Math.cos(v) - z2 * Math.sin(v);
    let z3 = y2 * Math.sin(v) + z2 * Math.cos(v);

    return { x: x3, y: y3, z: z3 };
  }

  projectToScreen(x, y, z) {  // $REQ_DRIFTBG_021
    // Perspective projection formula
    const K = this.calculateProjectionConstant();
    const scale = K / (z + this.CAMERA_Z);
    const centerX = this.canvas.width / 2;
    const centerY = this.canvas.height / 2;

    return {
      x: centerX + x * scale,
      y: centerY + y * scale,
      scale: scale
    };
  }

  render() {  // $REQ_DRIFTBG_018, $REQ_DRIFTBG_019, $REQ_DRIFTBG_020, $REQ_DRIFTBG_021, $REQ_DRIFTBG_022, $REQ_DRIFTBG_023
    // Clear canvas
    this.ctx.fillStyle = '#000';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // 15x15 grid (-7 to +7)  // $REQ_DRIFTBG_018
    const tileHeight = this.TILE_WIDTH * this.imageAspect;  // $REQ_DRIFTBG_019

    for (let k = -7; k <= 7; k++) {  // $REQ_DRIFTBG_018
      for (let m = -7; m <= 7; m++) {  // $REQ_DRIFTBG_018
        // Calculate local offset for tile
        const localX = k * this.TILE_WIDTH;
        const localY = m * tileHeight;
        const localZ = 0;

        // Rotate by follower angles
        const rotated = this.rotatePoint3D(
          localX, localY, localZ,
          this.followerU, this.followerV, this.followerW
        );

        // Translate by follower position
        const worldX = rotated.x + this.followerX;
        const worldY = rotated.y + this.followerY;
        const worldZ = rotated.z + this.followerZ;

        // Project to screen
        const screen = this.projectToScreen(worldX, worldY, worldZ);

        // Draw image with rotation and scaling
        const scaledWidth = this.TILE_WIDTH * screen.scale;
        const scaledHeight = tileHeight * screen.scale;

        this.ctx.save();
        this.ctx.translate(screen.x, screen.y);
        this.ctx.rotate(this.followerU); // $REQ_DRIFTBG_022: Roll rotation

        if (this.imageLoaded) {
          this.ctx.drawImage(
            this.image,
            -scaledWidth / 2,
            -scaledHeight / 2,
            scaledWidth,
            scaledHeight
          );
        } else {
          // White dots as placeholders  // $REQ_DRIFTBG_023
          this.ctx.fillStyle = '#fff';
          this.ctx.beginPath();
          this.ctx.arc(0, 0, 3, 0, 2 * Math.PI);
          this.ctx.fill();
        }

        this.ctx.restore();
      }
    }
  }

  animate() {
    const now = Date.now() / 1000;
    const t = now - this.startTime;
    const dt = Math.min(1 / 30, now - (this.lastTime || now)); // Cap dt to 30 FPS
    this.lastTime = now;

    // Calculate target state
    const target = this.getTargetState(t);

    // Update follower state
    this.updateFollower(target, dt);

    // Render frame
    this.render();

    // Log state once per second  // $REQ_DRIFTBG_024, $REQ_DRIFTBG_025
    const shouldLog = now - this.lastLogTime >= 1.0;
    if (shouldLog) {
      const mode = target.isMouseMode ? 'MOUSE' : 'SPIRAL';  // $REQ_DRIFTBG_025
      console.log(  // $REQ_DRIFTBG_024
        `drift-bg: [${mode}] x=${this.followerX.toFixed(2)} y=${this.followerY.toFixed(2)} ` +
        `z=${this.followerZ.toFixed(2)} u=${this.followerU.toFixed(2)} ` +
        `v=${this.followerV.toFixed(2)} w=${this.followerW.toFixed(2)}`
      );
      this.lastLogTime = now;
    }

    // Continue animation loop
    requestAnimationFrame(() => this.animate());
  }
}

// Register custom element  // $REQ_DRIFTBG_001
customElements.define('drift-bg', DriftBg);
