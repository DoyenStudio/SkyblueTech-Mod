# coding=utf-8
if 0:
    from typing import Literal


class UICtrlPosData:
    def __init__(
        self,
        follow_type="none", # type: Literal["none", "parent", "maxChildren", "maxSibling", "children", "x", "y"]
        relative_value=0.0, # type: float
        absolute_value=0.0, # type: float
    ):
        self.follow_type = follow_type
        self.relative_value = relative_value
        self.absolute_value = absolute_value

    @classmethod
    def from_dict(cls, data):
        return cls(
            follow_type=data["followType"],
            relative_value=data["relativeValue"],
            absolute_value=data["absoluteValue"],
        )

    def marshal(self):
        return {
            "followType": self.follow_type,
            "relativeValue": self.relative_value,
            "absoluteValue": self.absolute_value,
        }
