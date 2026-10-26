// __multiversion__
precision highp float;

#include "fragmentVersionCentroidUV.h"
#include "uniformEntityConstants.h"
#include "uniformPerFrameConstants.h"
#include "uniformShaderConstants.h"

LAYOUT_BINDING(0) uniform sampler2D TEXTURE_0;
// x: frame count; y: frames per second. x == 0 means unknown texture layout.
uniform vec4 EXTRA_ACTOR_UNIFORM1;
varying vec4 fogColor;

void main() {
    float frameCount = EXTRA_ACTOR_UNIFORM1.x;
    float frameRate = max(EXTRA_ACTOR_UNIFORM1.y, 0.0);
    if (frameCount < 1.0) {
#if __VERSION__ >= 300
        ivec2 texSize = textureSize(TEXTURE_0, 0);
        frameCount = max(1.0, floor(float(texSize.y) / float(texSize.x)));
        frameRate = frameCount > 1.0 ? 10.0 : 0.0;
#else
        // No textureSize on GLES2: an unknown path is static, never assumed 32-frame.
        frameCount = 1.0;
        frameRate = 0.0;
#endif
    }
    frameCount = max(1.0, floor(frameCount));
    float frame = floor(mod(TIME * frameRate, frameCount));
    // Tile each square frame before selecting it in the vertical strip.
    vec2 animUV = fract(uv);
    animUV.y = (animUV.y + frame) / frameCount;
    vec4 color = texture2D(TEXTURE_0, animUV);
    // Keep the baked texture's RGB/alpha. Full-bright avoids black closed vessels.
    color.rgb = mix(color.rgb, fogColor.rgb, fogColor.a);
    gl_FragColor = color;
}
