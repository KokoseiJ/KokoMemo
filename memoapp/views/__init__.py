import os
from memoapp.utils.misc import gen_bp

print(__file__, __name__)
bp = gen_bp(__name__, os.path.dirname(__file__), name="")
del os
