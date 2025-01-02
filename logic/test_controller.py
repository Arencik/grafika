class TestController:
    def __init__(self):
        self.images = []
        self.current_index = 0
        self.num_iterations = 0
        self.channel = "blue"  # Domyślny kanał

    def setup_test(self, images, num_iterations=10, channel="blue"):
        self.images = images
        self.num_iterations = num_iterations
        self.current_index = 0
        self.channel = channel

    def get_next_image(self):
        if self.current_index < self.num_iterations and self.current_index < len(self.images):
            img_path = self.images[self.current_index % len(self.images)]
            self.current_index += 1
            return img_path
        else:
            return None