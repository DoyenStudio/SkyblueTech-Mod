// __multiversion__
precision highp float;

#include "vertexVersionCentroidUV.h"
#include "uniformWorldConstants.h"
#ifdef USE_SKINNING
#include "uniformAnimationConstants.h"
#endif

attribute highp vec4 POSITION;
attribute vec2 TEXCOORD_0;
#ifdef USE_SKINNING
#ifdef MCPE_PLATFORM_NX
attribute uint BONEID_0;
#else
attribute float BONEID_0;
#endif
#endif

// xyz: half extents in blocks; w: edge thickness in blocks.
uniform vec4 EXTRA_ACTOR_UNIFORM1;
varying float rangeFrameWidthUV;

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
    // Pass the configured width explicitly; the fragment stage must not rely
    // on the actor uniform retaining its value across native shader stages.
    rangeFrameWidthUV = EXTRA_ACTOR_UNIFORM1.w
        / max(EXTRA_ACTOR_UNIFORM1.x * 2.0, 0.001);
}
