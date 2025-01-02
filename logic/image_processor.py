from PIL import Image

def resize_image(path, max_width, max_height):
    img = Image.open(path)
    # Dobrze zachować oryginalny tryb (np. RGBA) zamiast konwersji do RGB
    img.thumbnail((max_width, max_height), Image.ANTIALIAS)
    return img

def modify_image_intensity(img, intensity, channel="blue"):
    """
    Modyfikuje wartość wybranego kanału (R, G lub B) do poziomu `intensity`.
    Domyślnie modyfikujemy kanał niebieski.
    """
    img = img.convert("RGB")
    pixels = img.load()

    for x in range(img.width):
        for y in range(img.height):
            r, g, b = pixels[x, y]
            if channel == "red":
                r = min(intensity, 255)
            elif channel == "green":
                g = min(intensity, 255)
            elif channel == "blue":
                b = min(intensity, 255)
            pixels[x, y] = (r, g, b)

    return img
