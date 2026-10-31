// Portable WebGL 1 material core; connect uniforms/varyings in your engine adapter.
// All inputs are full 0..1 artwork UVs, NOT atlas UVs. Disable sRGB conversion:
// legacy art's modulation is intentionally in byte/sRGB space.
precision highp float;
varying vec2 vMaterialUV;
uniform sampler2D uBase;       // premultiplied RGBA (Pixi default upload)
uniform sampler2D uMask;       // L mask, white = paintable
uniform sampler2D uRegion;     // L region; bind 1x1 white to paint full material
uniform sampler2D uIndex;      // 512x512 L, byte values 0..4; NEAREST, no mipmaps
uniform vec3 uPalette[5];      // RGB / 255
uniform vec3 uSolid;           // RGB / 255
uniform float uKind;           // 0=base, 1=solid, 2=camouflage
uniform float uShadeDivisor;   // 175 helmet_1, 160 other models
vec3 paletteAt(float n) {
  if (n < .5) return uPalette[0];
  if (n < 1.5) return uPalette[1];
  if (n < 2.5) return uPalette[2];
  if (n < 3.5) return uPalette[3];
  return uPalette[4];
}
void main() {
  vec4 b = texture2D(uBase, vMaterialUV);
  if (b.a <= 0.0 || uKind < .5) { gl_FragColor = b; return; }
  vec3 rgb = b.rgb / b.a;
  float mask = texture2D(uMask, vMaterialUV).r * texture2D(uRegion, vMaterialUV).r;
  float shade = clamp(dot(rgb, vec3(1.0/3.0)) * 255.0 / uShadeDivisor, .02, 1.55);
  vec3 paint = uKind < 1.5 ? uSolid : paletteAt(floor(texture2D(uIndex, vMaterialUV).r * 255.0 + .5));
  // Clamp AFTER blending; preserve alpha and hardware beneath mask=0.
  gl_FragColor = vec4(clamp(mix(rgb, paint * shade, mask), 0.0, 1.0) * b.a, b.a);
}
