// __multiversion__
#include "entityVertexUtil.h"

varying vec4 light;
varying vec4 fogColor;

#ifdef RNGL_LOCAL_LIGHT
varying vec4 worldSpacePos;
varying vec4 worldSpaceNormal;
#endif

void main() {
    POS4 entitySpacePosition, entitySpaceNormal;
    getEntitySpacePositionAndNormal(entitySpacePosition, entitySpaceNormal);
    calculateOverlayColor();
    calculateGlint();
    entityCommonVert();
    light = getLightColor(entitySpacePosition, entitySpaceNormal);
    // Keep the model's U=0..10px range; the atlas repeats every 16px in V.
#ifdef REVERSE_BELT_UV
    uv = vec2(TEXCOORD_0.x, 0.5 - TEXCOORD_0.y + mod(TIME * 0.5, 0.5));
#else
    uv = TEXCOORD_0 + vec2(0.0, mod(TIME * 0.5, 0.5));
#endif
    calculateSpecificProcess(entitySpacePosition, entitySpaceNormal);
    POS4 projSpacePos = WORLDVIEWPROJ * entitySpacePosition;
    gl_Position = projSpacePos;
#ifdef RNGL_LOCAL_LIGHT
    worldSpacePos = WORLD * entitySpacePosition;
    worldSpaceNormal = WORLD * entitySpaceNormal;
    worldSpaceNormal.xyz = normalize(worldSpaceNormal.xyz);
#endif
    fogColor = getFogColor(projSpacePos);
}
