# Shader snippets — ultra-modern-lovable-style

Canonical mesh-gradient hero-background snippet bundled with Lintel v3.7 Fas A2.

## Recommended approach: Paper Shaders (declarative React)

The bundled `mesh-gradient.tsx` snippet uses [Paper Shaders](https://github.com/paper-design/shaders) for a low-complexity, mid-tier-mobile-safe mesh gradient. Fragment-shader-only, 1 fullscreen quad.

### Install

```bash
npm i @paper-design/shaders-react
```

### Usage

See [`mesh-gradient.tsx`](./mesh-gradient.tsx).

## Custom GLSL fallback

For full control (with OGL or react-three-fiber), [`mesh-gradient.glsl`](./mesh-gradient.glsl) provides a hand-curated mesh-gradient shader (3-color, controllable speed + distortion + swirl). Uses [Lygia](https://lygia.xyz) `lygia/generative/snoise.glsl` for noise.

### OGL example

```ts
import { Renderer, Triangle, Program, Mesh } from 'ogl'

const renderer = new Renderer({ canvas })
const gl = renderer.gl
const geometry = new Triangle(gl)
const program = new Program(gl, {
  vertex: vertexShader,
  fragment: fragmentShader,  // mesh-gradient.glsl content
  uniforms: { uTime: { value: 0 }, uColor0: { value: [0.0, 0.47, 0.83] } }
})
const mesh = new Mesh(gl, { geometry, program })
```

## Fallback strategy

- **No WebGL:** static CSS conic-gradient
- **prefers-reduced-motion:** disable animation, render single frame
- **Mid-tier mobile:** downscale canvas resolution to 50%
- **Off-screen:** IntersectionObserver pauses requestAnimationFrame loop

## L-001 note

This snippet is canonical schema-by-example. Operator-extracted shader-snippets via `/li:frontend-style-extract` go to `~/.lintel/brand/shader-snippets/<name>/` and live alongside this one.
