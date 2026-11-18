# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.facing_utils import RelativeFacingStrEnum

OUTPUT_FACES = (
    RelativeFacingStrEnum.FRONT,
    RelativeFacingStrEnum.BACK,
    RelativeFacingStrEnum.LEFT,
    RelativeFacingStrEnum.RIGHT,
    RelativeFacingStrEnum.TOP,
    RelativeFacingStrEnum.DOWN,
)
OUTPUT_FACE_LABELS = ("前", "后", "左", "右", "上", "下")
ALL_OUTPUT_FACES = (1 << len(OUTPUT_FACES)) - 1
K_OUTPUT_FACE_MASK = "fluid_output_faces_"
K_OUTPUT_FACE_REVISION = "fluid_output_faces_revision"

OUTPUT_SLOT_COLORS = (
    (0.25, 0.65, 1.0),
    (1.0, 0.55, 0.25),
    (0.40, 0.82, 0.45),
    (0.76, 0.48, 0.95),
    (0.95, 0.78, 0.25),
    (0.25, 0.82, 0.82),
)
