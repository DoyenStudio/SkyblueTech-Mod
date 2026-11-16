// __multiversion__
precision highp float;

#include "vertexVersionCentroidUV.h"
#include "uniformWorldConstants.h"
#ifdef USE_SKINNING
#include "uniformAnimationConstants.h"
#endif

attribute highp vec4 POSITION;
attribute vec2 TEXCOORD_0;
attribute vec3 NORMAL;
#ifdef USE_SKINNING
#ifdef MCPE_PLATFORM_NX
attribute uint BONEID_0;
#else
attribute float BONEID_0;
#endif
#endif

// xyz: half extents in blocks; w: edge thickness in blocks.
uniform vec4 EXTRA_ACTOR_UNIFORM1;
varying vec2 faceSize;
varying float overLimit;

void main() {
    MAT4 boneMat = mat4(1.0);
#ifdef USE_SKINNING
#ifdef NETEASE_SKINNING
    boneMat = GetBoneMatForNetease(int(BONEID_0));
#elif defined(LARGE_VERTEX_SHADER_UNIFORMS)
    boneMat = BONES[int(BONEID_0)];
#else
    boneMat = BONE;
#endif
#endif
    // Keep the engine's pixel-to-block conversion in the bone transform.
    // POSITION itself is not a world-space distance for the fragment mask.
    vec3 scaledPosition = POSITION.xyz * (EXTRA_ACTOR_UNIFORM1.xyz * 2.0);
    gl_Position = WORLDVIEWPROJ * boneMat * vec4(scaledPosition, 1.0);
    uv = TEXCOORD_0;
    vec3 size = 2.0 * EXTRA_ACTOR_UNIFORM1.xyz;
    faceSize = abs(NORMAL.y) > 0.5 ? size.xz : (abs(NORMAL.x) > 0.5 ? size.zy : size.xy);
    overLimit = EXTRA_ACTOR_UNIFORM1.w;
}
