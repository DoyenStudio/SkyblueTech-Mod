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
    // The 32px atlas belt starts at U=20px and repeats every 16px in V.
    uv = TEXCOORD_0 + vec2(0.625, mod(TIME * 0.5, 0.5));
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
