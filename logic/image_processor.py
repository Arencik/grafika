from PIL import Image

def resize_image(path, max_width, max_height):
    img = Image.open(path)
    img.thumbnail((max_width, max_height), Image.ANTIALIAS)
    return img

def modify_image_intensity(img: Image, intensity: int) -> Image:
    img = img.convert("RGB")
    pixels = img.load()

    for x in range(img.width):
        for y in range(img.height):
            r, g, b = pixels[x, y]
            r = min(intensity, 255)  # modyfikujemy kanał R
            pixels[x, y] = (r, g, b)

    return img
