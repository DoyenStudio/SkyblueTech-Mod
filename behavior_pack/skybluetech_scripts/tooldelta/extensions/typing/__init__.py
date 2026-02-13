from . import _fake

setattr(_fake, "Generic", _fake.FakeGeneric)
setattr(_fake, "TypeVar", _fake.FakeTypeVar)

from ._fake import Generic, TypeVar  # noqa
