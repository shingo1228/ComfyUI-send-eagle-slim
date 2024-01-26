from .send_eagle import SendEagle
from .send_eagle_with_text import SendEagleWithText

NODE_CLASS_MAPPINGS = {
    "Send Webp Image to Eagle": SendEagle,
    "Send Eagle with text": SendEagleWithText,
}
__all__ = ["NODE_CLASS_MAPPINGS"]
