// $REQ_ABC_001: Custom Element Tag Name
class AnimatedBackground extends HTMLElement {
  // Tick interval in seconds (see Timing Model in ANIMATED_BACKGROUND.md)
  static TICK_INTERVAL = 0.5;

  constructor() {
    super();

    // $REQ_ANIM_001: State Variables Per Axis
    // $REQ_BOOST-VEL_002: Boost Default Value
    this._state = {
      panX: { position: 0, velocity: 0, boost: 0, range: 0 },
      panY: { position: 0, velocity: 0, boost: 0, range: 0 },
      panZ: { position: 0, velocity: 0, boost: 0, range: 0 },
      rotX: { position: 0, velocity: 0, boost: 0, range: 0 },
      rotY: { position: 0, velocity: 0, boost: 0, range: 0 },
      rotZ: { position: 0, velocity: 0, boost: 0, range: 0 }
    };

    // $REQ_REPLAY_001: Time Counter Starts at t Attribute Value
    this._t = 0;
    this._lastTickTime = 0;
    this._lastFrameTime = 0;

    // Mouse tracking for boost
    this._mousePos = null;
    this._lastMouseSample = null;
    this._mouseSampleInterval = null;
    this._mouseButtonPressed = false;

    this._wall = null;
    this._animationFrameId = null;
  }

  connectedCallback() {
    this._parseAttributes();
    this._initializeElement();
    // $REQ_ATTR_003: t Attribute Fast-Forward Behavior
    this._fastForward();
    this._startAnimation();
    this._setupMouseTracking();
  }

  disconnectedCallback() {
    if (this._animationFrameId) {
      cancelAnimationFrame(this._animationFrameId);
    }
    if (this._mouseSampleInterval) {
      clearInterval(this._mouseSampleInterval);
    }
  }

  static get observedAttributes() {
    return ['src', 'pan-x', 'pan-y', 'pan-z', 'rot-x', 'rot-y', 'rot-z', 't'];
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue && this._wall) {
      this._parseAttributes();
    }
  }

  // $REQ_ABC_010: Range Attribute Parsing
  _parseAttributes() {
    // $REQ_ABC_011: Range Attributes Default to Zero
    this._state.panX.range = this._parseRange(this.getAttribute('pan-x'));
    this._state.panY.range = this._parseRange(this.getAttribute('pan-y'));
    this._state.panZ.range = this._parseRange(this.getAttribute('pan-z'));
    this._state.rotX.range = this._parseRange(this.getAttribute('rot-x'));
    this._state.rotY.range = this._parseRange(this.getAttribute('rot-y'));
    this._state.rotZ.range = this._parseRange(this.getAttribute('rot-z'));

    // $REQ_ATTR_002: t Attribute Default Value
    const tAttr = this.getAttribute('t');
    this._tStart = tAttr ? Math.max(0, parseInt(tAttr, 10)) : 0;
  }

  _parseRange(value) {
    if (value === null || value === undefined) return 0;
    const parsed = parseFloat(value);
    // Range Attributes Clamped to 0-100
    return Math.max(0, Math.min(100, isNaN(parsed) ? 0 : parsed));
  }

  // $REQ_ABC_003: Virtual Wall Dimensions
  _initializeElement() {
    this.style.position = 'fixed';
    this.style.top = '0';
    this.style.left = '0';
    this.style.width = '100vw';
    this.style.height = '100vh';
    this.style.overflow = 'hidden';
    // $REQ_ABC_013: Background Z-Index
    this.style.zIndex = '-1';

    this._wall = document.createElement('div');
    this._wall.style.position = 'absolute';
    this._wall.style.width = '1000vw';
    this._wall.style.height = '1000vh';
    this._wall.style.left = '-450vw';
    this._wall.style.top = '-450vh';
    // $REQ_ABC_004: Tiled Background Image
    // $REQ_ABC_002: Required src Attribute
    const src = this.getAttribute('src');
    if (src) {
      this._wall.style.backgroundImage = `url('${src}')`;
      this._wall.style.backgroundRepeat = 'repeat';
      this._wall.style.backgroundPosition = 'center';
    }
    this._wall.style.transformStyle = 'preserve-3d';

    this.appendChild(this._wall);

    // $REQ_ANIM_007: Initial Position Values
    // Already set to 0 in constructor

    // $REQ_ANIM_008: Initial Velocity Assignment
    const axes = ['panX', 'panY', 'panZ', 'rotX', 'rotY', 'rotZ'];
    for (const axis of axes) {
      if (this._state[axis].range > 0) {
        // $REQ_REPLAY_006: Initial Velocity Direction via PRNG
        this._state[axis].velocity = this._prng(0, `${axis}-init`) ? 1 : -1;
      }
    }

    // $REQ_ANIM_015: Boost Initial Value
    // Already set to 0 in constructor
  }

  // $REQ_ATTR_003: t Attribute Fast-Forward Behavior
  // $REQ_BOOST-VEL_006: Boost Not Simulated During Fast-Forward
  _fastForward() {
    this._t = this._tStart;

    if (this._tStart > 0) {
      // Simulate from t=0 to t=N-1 without rendering
      // Boost remains 0 as it's only set by mouse interaction or JS API
      // To achieve deterministic replay, we simulate using small time steps
      // (approx 60fps = 1/60 sec per step) to match real-time animation behavior
      const frameTime = 1 / 60;
      const stepsPerTick = Math.ceil(AnimatedBackground.TICK_INTERVAL / frameTime);

      for (let t = 0; t < this._tStart; t++) {
        // $REQ_REPLAY_008: Fast-Forward Produces Identical State
        // Simulate one tick of animation in small steps
        for (let step = 0; step < stepsPerTick; step++) {
          this._updatePositions(frameTime);
        }
        // Then update velocity for the next interval (same as real-time tick)
        this._tickUpdate(t);
      }
    }

    // $REQ_REPLAY_004: Animation Begins at Specified Tick
    this._lastTickTime = performance.now() / 1000;
    // $REQ_REPLAY_003: Console Tick Logging
    console.log(`t=${this._t}`);
  }

  _startAnimation() {
    this._lastFrameTime = performance.now() / 1000;
    this._animate();
  }

  _animate() {
    const currentTime = performance.now() / 1000;
    const deltaTime = currentTime - this._lastFrameTime;
    this._lastFrameTime = currentTime;

    // $REQ_REPLAY_002: Time Counter Increments Each Tick
    if (currentTime - this._lastTickTime >= AnimatedBackground.TICK_INTERVAL) {
      this._t++;
      this._lastTickTime = currentTime;

      this._tickUpdate(this._t - 1);

      // $REQ_ANIM_011: Tick Console Logging
      console.log(`t=${this._t}`);
    }

    // $REQ_ANIM_010: Animation Loop Integration
    this._updatePositions(deltaTime);
    this._applyTransform();

    this._animationFrameId = requestAnimationFrame(() => this._animate());
  }

  // $REQ_ANIM_004: Velocity Update Frequency
  _tickUpdate(t) {
    const axes = ['panX', 'panY', 'panZ', 'rotX', 'rotY', 'rotZ'];

    for (const axis of axes) {
      const state = this._state[axis];

      if (state.range > 0) {
        // $REQ_ANIM_005: Velocity Magnitude Change
        // $REQ_REPLAY_007: Velocity Magnitude Change via PRNG
        const increase = this._prng(t, `${axis}-vel`);
        const currentMag = Math.abs(state.velocity);
        const newMag = increase ? currentMag + 1 : Math.max(1, currentMag - 1);

        // $REQ_ANIM_003: No Zero Velocity
        state.velocity = state.velocity >= 0 ? newMag : -newMag;
      }
    }

    // $REQ_ANIM_013: Boost Decay Per Tick
    // $REQ_BOOST-VEL_004: Boost Decay Toward Zero
    for (const axis of axes) {
      const state = this._state[axis];

      if (state.boost > 0) {
        state.boost = Math.max(0, state.boost - 1);
      } else if (state.boost < 0) {
        state.boost = Math.min(0, state.boost + 1);
      }

      if (state.boost > -1 && state.boost < 1) {
        state.boost = 0;
      }
    }
  }

  _updatePositions(deltaTime) {
    const axes = ['panX', 'panY', 'panZ', 'rotX', 'rotY', 'rotZ'];

    for (const axis of axes) {
      const state = this._state[axis];

      if (state.range > 0) {
        // $REQ_ANIM_012: Boost Effective Velocity
        // $REQ_BOOST-VEL_003: Effective Velocity Calculation
        const effectiveVelocity = state.velocity + state.boost;

        // Only update position if there's actual velocity
        // (don't clamp manually-set positions if there's no movement)
        if (effectiveVelocity !== 0) {
          // Update position
          state.position += effectiveVelocity * deltaTime;

          // $REQ_ANIM_006: Range Boundary Reversal
          const limits = this._getLimits(axis);
          if (state.position <= limits.min) {
            state.position = limits.min;
            state.velocity = Math.abs(state.velocity);
            // $REQ_ANIM_014: Boost Boundary Reversal
            // $REQ_BOOST-VEL_005: Boost Reversal at Boundaries
            state.boost = Math.abs(state.boost);
          } else if (state.position >= limits.max) {
            state.position = limits.max;
            state.velocity = -Math.abs(state.velocity);
            // $REQ_ANIM_014: Boost Boundary Reversal
            // $REQ_BOOST-VEL_005: Boost Reversal at Boundaries
            state.boost = -Math.abs(state.boost);
          }
        }
      }
    }
  }

  _getLimits(axis) {
    const state = this._state[axis];
    const range = state.range;

    // Position is stored as percentage of full range (-50 to +50)
    // Range attribute scales this
    const scale = range / 100;
    return {
      min: -50 * scale,
      max: 50 * scale
    };
  }

  // $REQ_ABC_012: Wall Transform Application
  _applyTransform() {
    // Calculate actual pixel/degree values from position percentages
    const vw = window.innerWidth;
    const vh = window.innerHeight;

    // $REQ_ATTR_009: pan-x Translation Range Mapping
    // Wall is 10x viewport. At 100% range, wall moves ±4.5 viewport widths
    const panXPixels = (this._state.panX.position / 100) * 4.5 * vw;

    // $REQ_ATTR_010: pan-y Translation Range Mapping
    const panYPixels = (this._state.panY.position / 100) * 4.5 * vh;

    // $REQ_ATTR_011: pan-z Zoom Range Mapping
    // 0% = 1.0 (nominal), -50% = 0.5, +50% = 1.5
    const panZScale = 1.0 + (this._state.panZ.position / 100);

    // $REQ_ATTR_006, $REQ_ATTR_007, $REQ_ATTR_008: Rotation Range Mapping
    // Position is -50 to +50, which maps to -45° to +45°
    const rotXDeg = (this._state.rotX.position / 50) * 45;
    const rotYDeg = (this._state.rotY.position / 50) * 45;
    const rotZDeg = (this._state.rotZ.position / 50) * 45;

    this._wall.style.transform = `
      translate(${panXPixels}px, ${panYPixels}px)
      scale(${panZScale})
      rotateX(${rotXDeg}deg)
      rotateY(${rotYDeg}deg)
      rotateZ(${rotZDeg}deg)
    `;
  }

  // $REQ_REPLAY_005: Deterministic PRNG Function
  _prng(t, salt) {
    const str = `${t}-${salt}`;
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) - hash) + str.charCodeAt(i);
      hash = hash & hash;
    }
    return (hash & 1) === 1;
  }

  // $REQ_MOUSE_001, $REQ_MOUSE_002: Mouse Position Sampling Rate and Coordinates
  _setupMouseTracking() {
    // $REQ_MOUSE_007: Mouse Interaction Always Enabled
    this.addEventListener('mouseenter', (e) => {
      this._mousePos = this._getMousePercentage(e);
      this._lastMouseSample = this._mousePos;

      // $REQ_MOUSE_001: Sample once per tick
      this._mouseSampleInterval = setInterval(() => {
        this._sampleMouse();
      }, AnimatedBackground.TICK_INTERVAL * 1000);
    });

    this.addEventListener('mousemove', (e) => {
      this._mousePos = this._getMousePercentage(e);
    });

    // $REQ_MOUSE_008: Sampling Pauses When Mouse Leaves Element
    this.addEventListener('mouseleave', () => {
      if (this._mouseSampleInterval) {
        clearInterval(this._mouseSampleInterval);
        this._mouseSampleInterval = null;
      }
      this._mousePos = null;
      this._lastMouseSample = null;
    });

    this.addEventListener('mousedown', () => {
      this._mouseButtonPressed = true;
    });

    this.addEventListener('mouseup', () => {
      this._mouseButtonPressed = false;
    });

    // $REQ_MOUSE_010: Touch Events Equivalence
    this.addEventListener('touchstart', (e) => {
      if (e.touches.length > 0) {
        this._mousePos = this._getTouchPercentage(e.touches[0]);
        this._lastMouseSample = this._mousePos;
        this._mouseButtonPressed = true;

        if (!this._mouseSampleInterval) {
          this._mouseSampleInterval = setInterval(() => {
            this._sampleMouse();
          }, AnimatedBackground.TICK_INTERVAL * 1000);
        }
      }
    });

    this.addEventListener('touchmove', (e) => {
      if (e.touches.length > 0) {
        this._mousePos = this._getTouchPercentage(e.touches[0]);
      }
    });

    this.addEventListener('touchend', () => {
      this._mouseButtonPressed = false;
      if (this._mouseSampleInterval) {
        clearInterval(this._mouseSampleInterval);
        this._mouseSampleInterval = null;
      }
      this._mousePos = null;
      this._lastMouseSample = null;
    });
  }

  _getMousePercentage(e) {
    const rect = this.getBoundingClientRect();
    return {
      x: ((e.clientX - rect.left) / rect.width) * 100,
      y: ((e.clientY - rect.top) / rect.height) * 100
    };
  }

  _getTouchPercentage(touch) {
    const rect = this.getBoundingClientRect();
    return {
      x: ((touch.clientX - rect.left) / rect.width) * 100,
      y: ((touch.clientY - rect.top) / rect.height) * 100
    };
  }

  _sampleMouse() {
    if (!this._mousePos || !this._lastMouseSample) {
      return;
    }

    const deltaX = this._mousePos.x - this._lastMouseSample.x;
    const deltaY = this._mousePos.y - this._lastMouseSample.y;

    // $REQ_MOUSE_009: Non-Cumulative Boost Replacement
    if (deltaX !== 0 || deltaY !== 0) {
      if (this._mouseButtonPressed) {
        // $REQ_MOUSE_004: Rotation Mode Boost Calculation
        if (deltaX !== 0) {
          this._state.rotY.boost = deltaX * 2;
        }
        if (deltaY !== 0) {
          this._state.rotX.boost = deltaY * 2;
        }

        // $REQ_MOUSE_006: Rotation Mode Console Logging
        console.log(`mouse rotate: deltaX=${deltaX} deltaY=${deltaY} → rotXBoost=${this._state.rotX.boost} rotYBoost=${this._state.rotY.boost}`);
      } else {
        // $REQ_MOUSE_003: Pan Mode Boost Calculation
        if (deltaX !== 0) {
          this._state.panX.boost = deltaX * 2;
        }
        if (deltaY !== 0) {
          this._state.panY.boost = deltaY * 2;
        }

        // $REQ_MOUSE_005: Pan Mode Console Logging
        console.log(`mouse pan: deltaX=${deltaX} deltaY=${deltaY} → panXBoost=${this._state.panX.boost} panYBoost=${this._state.panY.boost}`);
      }
    }

    this._lastMouseSample = { ...this._mousePos };
  }

  // $REQ_ABC_007: Attribute Accessors via JavaScript
  // $REQ_JSAPI_002: Attribute Accessor for src
  get src() { return this.getAttribute('src'); }  // $REQ_JSAPI_002
  set src(value) { this.setAttribute('src', value); }  // $REQ_JSAPI_002

  // $REQ_JSAPI_001: Attribute Accessors for Range Attributes
  get panX() { return this._state.panX.range; }  // $REQ_JSAPI_001
  set panX(value) {  // $REQ_JSAPI_001
    this._state.panX.range = this._parseRange(value);
    this.setAttribute('pan-x', this._state.panX.range);
  }

  get panY() { return this._state.panY.range; }  // $REQ_JSAPI_001
  set panY(value) {  // $REQ_JSAPI_001
    this._state.panY.range = this._parseRange(value);
    this.setAttribute('pan-y', this._state.panY.range);
  }

  get panZ() { return this._state.panZ.range; }  // $REQ_JSAPI_001
  set panZ(value) {  // $REQ_JSAPI_001
    this._state.panZ.range = this._parseRange(value);
    this.setAttribute('pan-z', this._state.panZ.range);
  }

  get rotX() { return this._state.rotX.range; }  // $REQ_JSAPI_001
  set rotX(value) {  // $REQ_JSAPI_001
    this._state.rotX.range = this._parseRange(value);
    this.setAttribute('rot-x', this._state.rotX.range);
  }

  get rotY() { return this._state.rotY.range; }  // $REQ_JSAPI_001
  set rotY(value) {  // $REQ_JSAPI_001
    this._state.rotY.range = this._parseRange(value);
    this.setAttribute('rot-y', this._state.rotY.range);
  }

  get rotZ() { return this._state.rotZ.range; }  // $REQ_JSAPI_001
  set rotZ(value) {  // $REQ_JSAPI_001
    this._state.rotZ.range = this._parseRange(value);
    this.setAttribute('rot-z', this._state.rotZ.range);
  }

  // $REQ_ABC_008: Position Accessors via JavaScript
  // $REQ_JSAPI_003: Position Accessors
  // $REQ_JSAPI_004: Position Value Semantics
  get panXPosition() { return this._state.panX.position; }  // $REQ_JSAPI_003, $REQ_JSAPI_004
  // $REQ_JSAPI_005: Position Setter Allows Full Range
  set panXPosition(value) { this._state.panX.position = Math.max(-50, Math.min(50, value)); }  // $REQ_JSAPI_005

  get panYPosition() { return this._state.panY.position; }  // $REQ_JSAPI_003, $REQ_JSAPI_004
  set panYPosition(value) { this._state.panY.position = Math.max(-50, Math.min(50, value)); }  // $REQ_JSAPI_005

  get panZPosition() { return this._state.panZ.position; }  // $REQ_JSAPI_003, $REQ_JSAPI_004
  set panZPosition(value) { this._state.panZ.position = Math.max(-50, Math.min(50, value)); }  // $REQ_JSAPI_005

  get rotXPosition() { return this._state.rotX.position; }  // $REQ_JSAPI_003, $REQ_JSAPI_004
  set rotXPosition(value) { this._state.rotX.position = Math.max(-50, Math.min(50, value)); }  // $REQ_JSAPI_005

  get rotYPosition() { return this._state.rotY.position; }  // $REQ_JSAPI_003, $REQ_JSAPI_004
  set rotYPosition(value) { this._state.rotY.position = Math.max(-50, Math.min(50, value)); }  // $REQ_JSAPI_005

  get rotZPosition() { return this._state.rotZ.position; }  // $REQ_JSAPI_003, $REQ_JSAPI_004
  set rotZPosition(value) { this._state.rotZ.position = Math.max(-50, Math.min(50, value)); }  // $REQ_JSAPI_005

  // $REQ_ABC_009: Velocity Accessors via JavaScript
  // $REQ_JSAPI_006: Velocity Accessors
  get panXVelocity() { return this._state.panX.velocity; }  // $REQ_JSAPI_006
  set panXVelocity(value) { this._state.panX.velocity = value; }  // $REQ_JSAPI_006

  get panYVelocity() { return this._state.panY.velocity; }  // $REQ_JSAPI_006
  set panYVelocity(value) { this._state.panY.velocity = value; }  // $REQ_JSAPI_006

  get panZVelocity() { return this._state.panZ.velocity; }  // $REQ_JSAPI_006
  set panZVelocity(value) { this._state.panZ.velocity = value; }  // $REQ_JSAPI_006

  get rotXVelocity() { return this._state.rotX.velocity; }  // $REQ_JSAPI_006
  set rotXVelocity(value) { this._state.rotX.velocity = value; }  // $REQ_JSAPI_006

  get rotYVelocity() { return this._state.rotY.velocity; }  // $REQ_JSAPI_006
  set rotYVelocity(value) { this._state.rotY.velocity = value; }  // $REQ_JSAPI_006

  get rotZVelocity() { return this._state.rotZ.velocity; }  // $REQ_JSAPI_006
  set rotZVelocity(value) { this._state.rotZ.velocity = value; }  // $REQ_JSAPI_006

  // $REQ_JSAPI_007: Boost Accessors
  // $REQ_JSAPI_008: Boost Value Semantics
  // $REQ_BOOST-VEL_001: Boost Accessors
  get panXBoost() { return this._state.panX.boost; }  // $REQ_JSAPI_007, $REQ_JSAPI_008
  set panXBoost(value) { this._state.panX.boost = value; }  // $REQ_JSAPI_007, $REQ_JSAPI_008

  get panYBoost() { return this._state.panY.boost; }  // $REQ_JSAPI_007, $REQ_JSAPI_008
  set panYBoost(value) { this._state.panY.boost = value; }  // $REQ_JSAPI_007, $REQ_JSAPI_008

  get panZBoost() { return this._state.panZ.boost; }  // $REQ_JSAPI_007, $REQ_JSAPI_008
  set panZBoost(value) { this._state.panZ.boost = value; }  // $REQ_JSAPI_007, $REQ_JSAPI_008

  get rotXBoost() { return this._state.rotX.boost; }  // $REQ_JSAPI_007, $REQ_JSAPI_008
  set rotXBoost(value) { this._state.rotX.boost = value; }  // $REQ_JSAPI_007, $REQ_JSAPI_008

  get rotYBoost() { return this._state.rotY.boost; }  // $REQ_JSAPI_007, $REQ_JSAPI_008
  set rotYBoost(value) { this._state.rotY.boost = value; }  // $REQ_JSAPI_007, $REQ_JSAPI_008

  get rotZBoost() { return this._state.rotZ.boost; }  // $REQ_JSAPI_007, $REQ_JSAPI_008
  set rotZBoost(value) { this._state.rotZ.boost = value; }  // $REQ_JSAPI_007, $REQ_JSAPI_008
}

// $REQ_ABC_001: Register the custom element
customElements.define('animated-background', AnimatedBackground);
