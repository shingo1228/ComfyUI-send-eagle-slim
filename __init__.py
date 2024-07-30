from .send_eagle import SendEagle
from .send_eagle_with_text import SendEagleWithText
from .fai9_send_eagle import Fai9SendEagle

NODE_CLASS_MAPPINGS = {
    "Send Webp Image to Eagle": SendEagle,
    "Send Eagle with text": SendEagleWithText,
    "Send Image to Eagle (fai-9)": Fai9SendEagle,
}
__all__ = ["NODE_CLASS_MAPPINGS"]
