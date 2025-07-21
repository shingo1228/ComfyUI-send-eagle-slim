# ComfyUI-send-Eagle(slim)

**Languages:** [English](README.md) | [日本語](README_ja.md)

[![License](https://img.shields.io/github/license/shingo1228/ComfyUI-send-eagle-slim)](LICENSE)

A ComfyUI extension node that integrates generated images with Eagle, a powerful image management software.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Changelog](#changelog)

## Features

This extension node sends images generated in [ComfyUI](https://github.com/comfyanonymous/ComfyUI) to locally running [Eagle](https://en.eagle.cool/).

![](misc/sss_node_visual.jpg)

- **Image Format Selection**: Send images in `webp` or `png` format.
  - For `webp` format, choose between lossy compression (with quality settings) and lossless compression.
- **Flexible Text Input**: Directly input `prompt_text`, `negative_text`, and `memo_text` for use as annotations and tags in Eagle. These inputs are optional.
- **Custom Folder Selection**: Specify a `folder_name` within Eagle to save images. If the specified folder doesn't exist, images will be saved to Eagle's root folder.
- **PNG Metadata Preservation**: When saving images in `png` format, ComfyUI workflow information (`prompt` and `extra_pnginfo`) is embedded as metadata. This allows you to recreate the generation workflow by dragging and dropping the image from Eagle back into ComfyUI.

## Installation

1. Navigate to ComfyUI's `custom_nodes` directory.
   ```bash
   cd path/to/ComfyUI/custom_nodes
   ```
2. Clone this repository with the following command.
   ```bash
   git clone https://github.com/shingo1228/ComfyUI-send-eagle-slim.git
   ```
3. Restart ComfyUI.

## Usage

Add the `Send Image to Eagle` node to your ComfyUI workflow.

<img src="misc/workflow.svg" alt="Workflow Example" style="width:800px; height:auto;">

Connect an image to the node's input port and configure the following parameters as needed:

- `images`: The image to send.
- `format`: Image save format (`webp` or `png`).
- `lossless_webp`: For `webp` format, enable lossless compression (`Enabled`) or use lossy compression (`Disabled`).
- `compression`: Compression quality for `webp` format (1-100).
- `folder_name`: Destination folder name within Eagle (e.g., `My Project/Generated Images`).
- `prompt_text`: Prompt text to associate with the image.
- `negative_text`: Negative prompt text to associate with the image.
- `memo_text`: Memo or additional information to associate with the image.

**Screenshots:**

### Custom Node
![Node](misc/sss_node_visual.jpg)
### Annotation Display in Eagle
![Annotation Example](misc/sss_annotation.jpg)
### Filename Display in Eagle
![Filename Example](misc/sss_filename.jpg)
### Tags Display in Eagle
![Tags Example](misc/sss_tags.jpg)
### Exif Information Display:
<img src="misc/sss_exif.jpg" alt="Exif Information in Eagle" style="width:512px; height:auto;">

## Configuration

This extension node uses `config/default_config.json` for some settings.

To customize settings:

1. Copy `config.json.template` to `config/default_config.json` in the `config` directory.
2. Edit `config/default_config.json` to adjust parameters.

If `config/default_config.json` is not found, default settings will be used.

## Testing

Run the test suite to ensure everything works correctly:

```bash
# Run unit tests
python -m pytest tests/unit/

# Run integration tests
python tests/integration/run_integration_test.py
```

## Contributing

Bug reports, feature suggestions, and pull requests are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Developers and community of [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- Developers of [Eagle](https://en.eagle.cool/)
- Contributors to the predecessor [ComfyUI-send-Eagle](https://github.com/shingo1228/ComfyUI-send-eagle)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.
