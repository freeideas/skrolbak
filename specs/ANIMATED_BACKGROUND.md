# **Specification: \<drift-bg\> Custom Element**

## **1\. Overview**

Create a custom HTML Web Component (\<drift-bg\>) that renders an infinite, drifting, 3D-tiled background of a specific image. The background moves in a spiral pattern, oscillates in depth and tilt, and responds to mouse interaction with a "follow" physics effect.

## **2\. Component Interface**

* **Tag Name:** \<drift-bg\>  
* **Attributes:**  
  * src: The URL of the image to display. If changed, the new image must load and replace the current one.  
* **Styling:**  
  * The component acts as a block-level container.  
  * It contains a \<canvas\> that fills the component dimensions.  
  * Default background color: Black (\#000).

## **3\. Coordinate System & Projection**

* **World Units:**  
  * The logical "World" extends from **\-50 to \+50** on both X and Y axes.  
  * **Total Range:** 100 units.  
* **Camera:**  
  * **Camera Offset (Z):** 80 units.  
* **Perspective Projection:**  
  * Calculate a projection constant ($K$) dynamically such that **100 World Units exactly fill the canvas width** when at depth $Z=0$.  
  * Projection formula for a point $(x, y, z)$:  
    $$\\text{scale} \= \\frac{K}{z \+ 80}$$$$x\_{screen} \= x\_{center} \+ x \\cdot \\text{scale}$$$$y\_{screen} \= y\_{center} \+ y \\cdot \\text{scale}$$

## **4\. Animation Drivers (The "Target")**

The system is driven by a continuous time $t$ (seconds). Several variables oscillate based on $t$ to define a **Target State** $\\{x, y, z, v, w, u\\}$.

### **A. Spiral Motion (X, Y)**

* **Growth Speed:** 2.0 units/second.  
* **Cycle Duration:** $50 / 2.0 \= 25$ seconds.  
* **Logic:**  
  * $t\_{local} \= t \\pmod{25}$  
  * $r \= t\_{local} \\times 2.0$  
  * $x\_{target} \= r \\cos(t\_{local})$  
  * $y\_{target} \= r \\sin(t\_{local})$

### **B. Oscillations (Z, Tilt, Rotation)**

All angles are in radians. Max Tilt \= 20 degrees ($\\approx 0.349$ rad).

1. **Depth (**$z$**):** Sine wave, Period 20s, Amplitude 48\.  
   * $z\_{target} \= 48 \\sin(\\frac{2\\pi t}{20})$  
2. **Pitch (**$v$**, X-axis tilt):** Sine wave, Period 13s.  
   * $v\_{target} \= 20^\\circ \\sin(\\frac{2\\pi t}{13})$  
3. **Yaw (**$w$**, Y-axis tilt):** Cosine wave, Period 17s.  
   * $w\_{target} \= 20^\\circ \\cos(\\frac{2\\pi t}{17})$  
4. **Roll (**$u$**, Z-axis rotation):** Sine wave, Period 23s.  
   * $u\_{target} \= 20^\\circ \\sin(\\frac{2\\pi t}{23})$

## **5\. The "Follower" System (Smoothing)**

The visual center of the grid does not snap instantly to the Target State. Instead, a **Follower State** approaches the Target State using an easing function (Xeno's paradox).

$$\\text{current} \+= (\\text{target} \- \\text{current}) \\times \\text{rate} \\times \\Delta t$$

### **Follow Rates**

* **Standard Rate:** 10% per second ($0.1$).  
  * Used for $z, v, w, u$ at all times.  
  * Used for $x, y$ in **Spiral Mode**.  
* **Active Rate:** 50% per second ($0.5$).  
  * Used for $x, y$ **only** during **Mouse Mode**.

## **6\. Interaction Behavior**

The system switches between **Spiral Mode** and **Mouse Mode**.

* **Mouse Move Event:**  
  * Map the mouse pointer's screen coordinates back to World Coordinates ($z=0$) to determine a new $Target\_{x,y}$.  
  * Update lastMouseMoveTime.  
* **Mode Switching:**  
  * **Mouse Mode:** If time \- lastMouseMoveTime \< 2000ms.  
    * $Target\_{x,y}$ \= Mouse Position.  
    * $Target\_{z,v,w,u}$ \= Calculated from Time $t$ (same as spiral).  
  * **Spiral Mode:** If inactive for \> 2 seconds.  
    * $Target\_{x,y}$ \= Calculated from Time $t$ (Spiral function).

## **7\. Rendering & Tiling**

The visual output is a grid of images centered on the **Follower** position.

1. **Grid Definition:**  
   * **Tile Size:** Width \= 30 World Units. Height \= Based on image aspect ratio.  
   * **Grid Extent:** 15x15 grid (Indices \-7 to \+7 on both axes).  
2. 3D Transformation per Tile:  
   For each tile at index $(k, m)$:  
   * Calculate local offset: $lx \= k \\cdot W, ly \= m \\cdot H, lz \= 0$.  
   * **Rotate** the local offset by the Follower angles in this order:  
     1. **Roll (**$u$**)** around Z.  
     2. **Yaw (**$w$**)** around Y.  
     3. **Pitch (**$v$**)** around X.  
   * **Translate** by adding the Follower position $(Follower\_x, Follower\_y, Follower\_z)$.  
3. **Draw:**  
   * Project the transformed 3D point to 2D screen coordinates.  
   * Scale the image dimensions based on the perspective scale factor.  
   * **Context Rotation:** Rotate the 2D drawing context by $Follower\_u$ (Roll) to align the image visually with the grid rotation.  
   * If image is not loaded, draw white dots as placeholders.