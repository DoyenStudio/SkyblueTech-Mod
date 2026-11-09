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
    // Match the full-length cargo belts, compensating the split model's 3px rear section.
    float scrollPhase = mod(TIME * 0.5 - 3.0 / 32.0, 0.5);
    // Reverse V before scrolling; keep both atlas copies available for interpolation.
    uv = vec2(TEXCOORD_0.x, 0.5 - TEXCOORD_0.y + scrollPhase);
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
