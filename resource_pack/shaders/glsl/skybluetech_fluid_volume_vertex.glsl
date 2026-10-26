// __multiversion__
// Unit-cube fluid rendering, following ArrisCreate's tank surface tiling.
precision highp float;

#include "vertexVersionCentroidUV.h"
#include "uniformWorldConstants.h"
#include "uniformEntityConstants.h"
#include "uniformPerFrameConstants.h"
#ifdef USE_SKINNING
#include "uniformAnimationConstants.h"
#endif

attribute highp vec4 POSITION;
attribute vec2 TEXCOORD_0;
attribute vec4 NORMAL;
#ifdef USE_SKINNING
#ifdef MCPE_PLATFORM_NX
attribute uint BONEID_0;
#else
attribute float BONEID_0;
#endif
#endif

varying vec4 fogColor;

void main() {
    POS4 entitySpacePosition;
    vec3 scale = vec3(1.0);
#ifdef USE_SKINNING
#ifdef NETEASE_SKINNING
    MAT4 boneMat = GetBoneMatForNetease(int(BONEID_0));
#elif defined(LARGE_VERTEX_SHADER_UNIFORMS)
    MAT4 boneMat = BONES[int(BONEID_0)];
#else
    MAT4 boneMat = BONE;
#endif
    entitySpacePosition = boneMat * POSITION;
    scale.x = length(vec3(boneMat[0][0], boneMat[1][0], boneMat[2][0]));
    scale.y = length(vec3(boneMat[0][1], boneMat[1][1], boneMat[2][1]));
    scale.z = length(vec3(boneMat[0][2], boneMat[1][2], boneMat[2][2]));
#else
    entitySpacePosition = POSITION;
#endif

    POS4 pos = WORLDVIEWPROJ * entitySpacePosition;
    gl_Position = pos;

    // Side faces use their horizontal axis and Y; top/bottom use X and Z.
    vec3 face = abs(NORMAL.xyz);
    float scaleU = face.x * scale.z + (face.y + face.z) * scale.x;
    float scaleV = (face.x + face.z) * scale.y + face.y * scale.z;
    uv = TEXCOORD_0 * vec2(scaleU, scaleV);

    fogColor.rgb = FOG_COLOR.rgb;
    fogColor.a = clamp(
        ((pos.z / RENDER_DISTANCE) - FOG_CONTROL.x)
        / (FOG_CONTROL.y - FOG_CONTROL.x),
        0.0, 1.0
    );
}
