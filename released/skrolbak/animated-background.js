// $REQ_ABC_001: Custom Element Tag Name
class AnimatedBackground extends HTMLElement {
  constructor() {
    super();

    // $REQ_ANIM_001: State Variables Per Axis
    this._state = {
      panX: { position: 0, velocity: 0 },
      panY: { position: 0, velocity: 0 },
      panZ: { position: 0, velocity: 0 },
      rotX: { position: 0, velocity: 0 },
      rotY: { position: 0, velocity: 0 },
      rotZ: { position: 0, velocity: 0 }
    };

    // $REQ_REPLAY_001: Time Counter Initialization
    this._t = 0;
    this._lastTickTime = 0;
    this._animationFrame = null;
    this._wall = null;
  }

  // $REQ_ABC_001: Custom Element Tag Name
  connectedCallback() {
    this._initialize();
  }

  disconnectedCallback() {
    if (this._animationFrame) {
      cancelAnimationFrame(this._animationFrame);
    }
  }

  static get observedAttributes() {
    return ['src', 't', 'pan-x', 'pan-y', 'pan-z', 'rot-x', 'rot-y', 'rot-z'];
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (this._wall && name === 'src') {
      this._updateWallImage();
    }
  }

  _initialize() {
    // $REQ_ABC_002: Wall Dimensions
    // Create the wall element
    this._wall = document.createElement('div');
    this._wall.style.position = 'fixed';
    this._wall.style.top = '0';
    this._wall.style.left = '0';
    this._wall.style.width = '100vw';
    this._wall.style.height = '100vh';
    this._wall.style.transformOrigin = 'center center';
    this._wall.style.zIndex = '-1';

    // Create inner wall that is 10x viewport size
    const innerWall = document.createElement('div');
    innerWall.style.position = 'absolute';
    innerWall.style.width = '1000%';
    innerWall.style.height = '1000%';
    innerWall.style.left = '-450%';
    innerWall.style.top = '-450%';

    // $REQ_ABC_003: Image Tiling
    this._updateWallImage();
    innerWall.style.backgroundRepeat = 'repeat';
    innerWall.style.backgroundPosition = 'center center';

    this._wall.appendChild(innerWall);
    this._innerWall = innerWall;

    this.appendChild(this._wall);

    // $REQ_REPLAY_001: Time Counter Initialization
    this._t = this._parseT();

    // $REQ_ANIM_007: Initial Position Values
    // All positions start at 0
    for (let axis of ['panX', 'panY', 'panZ', 'rotX', 'rotY', 'rotZ']) {
      this._state[axis].position = 0;
    }

    // $REQ_ANIM_008: Initial Velocity Assignment
    this._initializeVelocities();

    // $REQ_ABC_014: T Attribute Fast-Forward
    if (this._t > 0) {
      this._fastForward(this._t);
    }

    // $REQ_REPLAY_003: Tick Console Logging
    console.log(`t=${this._t}`);

    // Start animation
    this._lastTickTime = performance.now() / 1000;
    this._animate();
  }

  _parseT() {
    // $REQ_ELEM_ATTR_003: Debug Tick Attribute Type and Default
    const t = parseInt(this.getAttribute('t') || '0', 10);
    return Math.max(0, t);
  }

  _updateWallImage() {
    if (this._innerWall && this.hasAttribute('src')) {
      const src = this.getAttribute('src');
      this._innerWall.style.backgroundImage = `url('${src}')`;
    }
  }

  // $REQ_ANIM_008: Initial Velocity Assignment
  _initializeVelocities() {
    const axes = ['panX', 'panY', 'panZ', 'rotX', 'rotY', 'rotZ'];
    for (let axis of axes) {
      const range = this._getRange(axis);
      // $REQ_ANIM_009: Zero Range Axes Stationary
      if (range === 0) {
        this._state[axis].velocity = 0;
      } else {
        // $REQ_REPLAY_006: PRNG Initial Velocity Direction
        const direction = this._prng(0, `${axis}-init`) ? 1 : -1;
        this._state[axis].velocity = direction * 1; // 1% per second
      }
    }
  }

  // $REQ_ABC_014: T Attribute Fast-Forward
  _fastForward(targetT) {
    // Simulate from t=0 to t=targetT-1
    for (let t = 0; t < targetT; t++) {
      this._tick(t);
    }
  }

  // $REQ_ABC_015: Deterministic PRNG
  _prng(t, salt) {
    // Simple hash-based PRNG
    const str = `${t}:${salt}`;
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return (hash & 1) === 0;
  }

  _getRange(axis) {
    // $REQ_ABC_005: Range Attributes Clamped
    const attrName = axis.replace(/([A-Z])/g, '-$1').toLowerCase();
    const value = parseFloat(this.getAttribute(attrName) || '0');
    return Math.max(0, Math.min(100, value));
  }

  _getAllowedInterval(axis, range) {
    if (axis === 'rotX' || axis === 'rotY' || axis === 'rotZ') {
      // $REQ_ABC_006: Rotation Range Mapping
      const maxAngle = (range / 100) * 45;
      return { min: -maxAngle, max: maxAngle };
    } else if (axis === 'panZ') {
      // $REQ_ABC_008: Pan Z Range Mapping
      // Zoom ranges from 0.5 to 1.5 at 100%
      // At range%, we scale around 1.0
      const fullRange = 0.5; // 1.0 ± 0.5
      const scaledRange = (range / 100) * fullRange;
      return { min: 1.0 - scaledRange, max: 1.0 + scaledRange };
    } else {
      // $REQ_ABC_007: Pan XY Range Mapping
      // Pan ranges from -50% to +50% at 100%
      const maxPan = (range / 100) * 50;
      return { min: -maxPan, max: maxPan };
    }
  }

  // $REQ_ANIM_010: Animation Loop Integration
  _animate() {
    const currentTime = performance.now() / 1000;
    const deltaTime = currentTime - this._lastTickTime;

    // Check if a second has passed for velocity update
    // $REQ_REPLAY_002: Time Counter Increment
    if (deltaTime >= 1.0) {
      this._t++;
      this._tick(this._t);
      this._lastTickTime = currentTime;
      // $REQ_REPLAY_003: Tick Console Logging
      console.log(`t=${this._t}`);
    }

    // Integrate velocities to update positions
    const dt = 1 / 60; // Approximate frame time
    this._integrateVelocities(dt);

    // Apply transforms
    this._applyTransforms();

    this._animationFrame = requestAnimationFrame(() => this._animate());
  }

  _tick(t) {
    const axes = ['panX', 'panY', 'panZ', 'rotX', 'rotY', 'rotZ'];
    for (let axis of axes) {
      const range = this._getRange(axis);
      if (range === 0) continue;

      // $REQ_ANIM_005: Velocity Magnitude Change
      const increase = this._prng(t, `${axis}-vel`);
      const currentVel = this._state[axis].velocity;
      const currentMag = Math.abs(currentVel);
      const sign = currentVel >= 0 ? 1 : -1;

      let newMag = increase ? currentMag + 1 : currentMag - 1;

      // $REQ_ANIM_003: No Zero Velocity
      if (newMag <= 0) {
        newMag = 1;
      }

      this._state[axis].velocity = sign * newMag;
    }
  }

  _integrateVelocities(dt) {
    const axes = ['panX', 'panY', 'panZ', 'rotX', 'rotY', 'rotZ'];
    for (let axis of axes) {
      const range = this._getRange(axis);
      if (range === 0) continue;

      const interval = this._getAllowedInterval(axis, range);
      const velocity = this._state[axis].velocity;

      // $REQ_ANIM_002: Velocity Units
      // Velocity is in percent of allowed range per second
      const intervalSize = interval.max - interval.min;
      const deltaPosition = (velocity / 100) * intervalSize * dt;

      let newPosition = this._state[axis].position + deltaPosition;

      // $REQ_ANIM_006: Range Boundary Reversal
      if (newPosition <= interval.min) {
        newPosition = interval.min;
        this._state[axis].velocity *= -1;
      } else if (newPosition >= interval.max) {
        newPosition = interval.max;
        this._state[axis].velocity *= -1;
      }

      this._state[axis].position = newPosition;
    }
  }

  _applyTransforms() {
    if (!this._wall) return;

    // Get current positions
    const panX = this._state.panX.position;
    const panY = this._state.panY.position;
    const panZ = this._state.panZ.position;
    const rotX = this._state.rotX.position;
    const rotY = this._state.rotY.position;
    const rotZ = this._state.rotZ.position;

    // Convert positions to transform values
    // Pan X/Y: -50% to +50% maps to translation
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const translateX = (panX / 100) * vw * 4.5; // 10x wall means ±4.5x viewport
    const translateY = (panY / 100) * vh * 4.5;

    // Pan Z: zoom scale
    const scale = panZ;

    // Build transform
    const transform = `
      translateX(${translateX}px)
      translateY(${translateY}px)
      scale(${scale})
      rotateX(${rotX}deg)
      rotateY(${rotY}deg)
      rotateZ(${rotZ}deg)
    `;

    this._wall.style.transform = transform;
    this._wall.style.perspective = '1000px';
  }

  // $REQ_JSAPI_001: Attribute Accessors for Range Attributes
  get panX() { return this._getRange('panX'); }
  set panX(value) { this.setAttribute('pan-x', value); }

  get panY() { return this._getRange('panY'); }
  set panY(value) { this.setAttribute('pan-y', value); }

  get panZ() { return this._getRange('panZ'); }
  set panZ(value) { this.setAttribute('pan-z', value); }

  get rotX() { return this._getRange('rotX'); }
  set rotX(value) { this.setAttribute('rot-x', value); }

  get rotY() { return this._getRange('rotY'); }
  set rotY(value) { this.setAttribute('rot-y', value); }

  get rotZ() { return this._getRange('rotZ'); }
  set rotZ(value) { this.setAttribute('rot-z', value); }

  // $REQ_JSAPI_002: Attribute Accessor for src
  get src() { return this.getAttribute('src') || ''; }
  set src(value) { this.setAttribute('src', value); }

  // $REQ_JSAPI_003: Position Accessors
  get panXPosition() { return this._state.panX.position; }
  set panXPosition(value) { this._state.panX.position = Math.max(-50, Math.min(50, value)); }

  get panYPosition() { return this._state.panY.position; }
  set panYPosition(value) { this._state.panY.position = Math.max(-50, Math.min(50, value)); }

  get panZPosition() { return this._state.panZ.position; }
  set panZPosition(value) { this._state.panZ.position = Math.max(0.5, Math.min(1.5, value)); }

  get rotXPosition() { return this._state.rotX.position; }
  set rotXPosition(value) { this._state.rotX.position = Math.max(-45, Math.min(45, value)); }

  get rotYPosition() { return this._state.rotY.position; }
  set rotYPosition(value) { this._state.rotY.position = Math.max(-45, Math.min(45, value)); }

  get rotZPosition() { return this._state.rotZ.position; }
  set rotZPosition(value) { this._state.rotZ.position = Math.max(-45, Math.min(45, value)); }

  // $REQ_JSAPI_005: Velocity Accessors
  get panXVelocity() { return this._state.panX.velocity; }
  set panXVelocity(value) { this._state.panX.velocity = value; }

  get panYVelocity() { return this._state.panY.velocity; }
  set panYVelocity(value) { this._state.panY.velocity = value; }

  get panZVelocity() { return this._state.panZ.velocity; }
  set panZVelocity(value) { this._state.panZ.velocity = value; }

  get rotXVelocity() { return this._state.rotX.velocity; }
  set rotXVelocity(value) { this._state.rotX.velocity = value; }

  get rotYVelocity() { return this._state.rotY.velocity; }
  set rotYVelocity(value) { this._state.rotY.velocity = value; }

  get rotZVelocity() { return this._state.rotZ.velocity; }
  set rotZVelocity(value) { this._state.rotZ.velocity = value; }
}

// $REQ_ABC_001: Custom Element Tag Name
customElements.define('animated-background', AnimatedBackground);
