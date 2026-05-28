// Canonical mesh-gradient fragment shader — ultra-modern-lovable-style
// For OGL or react-three-fiber use cases (Paper Shaders handles its own internally).
// Uses Lygia (https://lygia.xyz) for noise. Install: include lygia/generative/snoise.glsl
//
// Inputs:
//   uTime    — time in seconds (uniform float)
//   uColor0  — first gradient color (uniform vec3)
//   uColor1  — second gradient color (uniform vec3)
//   uColor2  — third gradient color (uniform vec3)
//   uSpeed   — animation speed multiplier (uniform float, default 0.3)
//   uDistortion — domain warp strength (uniform float, default 0.8)
//   vUv      — normalized UV coords (varying vec2)

precision highp float;

uniform float uTime;
uniform vec3 uColor0;
uniform vec3 uColor1;
uniform vec3 uColor2;
uniform float uSpeed;
uniform float uDistortion;

varying vec2 vUv;

#include "lygia/generative/snoise.glsl"

void main() {
  vec2 uv = vUv;
  float t = uTime * uSpeed;

  // Domain warp using simplex noise
  vec2 warp = vec2(
    snoise(vec2(uv.x * 2.0, uv.y * 2.0 + t)),
    snoise(vec2(uv.x * 2.0 + t, uv.y * 2.0 + 5.0))
  ) * uDistortion;

  vec2 p = uv + warp;

  // Three-band gradient mix
  float band1 = smoothstep(0.0, 0.5, p.x);
  float band2 = smoothstep(0.3, 0.8, p.y);

  vec3 col = mix(uColor0, uColor1, band1);
  col = mix(col, uColor2, band2 * 0.7);

  gl_FragColor = vec4(col, 1.0);
}
