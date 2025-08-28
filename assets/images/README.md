# Image Assets

Place your application images and graphics here:

## Recommended Images

- `background.png` - Application background
- `splash.png` - Splash screen image
- `banner.png` - Header/banner images
- `buttons/` - Custom button graphics
- `themes/` - Theme-specific images

## Image Guidelines

- **Format**: PNG for transparency, JPG for photos
- **Size**: Optimize for target screen resolutions
- **Quality**: High quality but reasonable file size
- **Naming**: Use descriptive, lowercase names with underscores

## Usage in Code

```python
from PIL import Image
import customtkinter as ctk

# Load image
image = ctk.CTkImage(
    light_image=Image.open("assets/images/logo_light.png"),
    dark_image=Image.open("assets/images/logo_dark.png"),
    size=(100, 50)
)

# Use in widget
label = ctk.CTkLabel(parent, image=image)
```
