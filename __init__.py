from .nodes.send_image_to_eagle_node import SendImageToEagleNode

NODE_CLASS_MAPPINGS = {
    "Send Image to Eagle": SendImageToEagleNode,
}
__all__ = ["NODE_CLASS_MAPPINGS"]