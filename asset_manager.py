import pygame

class DummySound:
    def play(self):
        pass

def make_fallback_surface(size, shape, color):
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    outline = (min(color[0] + 60, 255), min(color[1] + 60, 255), min(color[2] + 60, 255))
    if shape == 'circle':
        r = min(w, h) // 2
        pygame.draw.circle(surf, color, (w // 2, h // 2), r)
        pygame.draw.circle(surf, outline, (w // 2, h // 2), r, 2)
    elif shape == 'triangle':
        points = [(w // 2, 2), (2, h - 2), (w - 2, h - 2)]
        pygame.draw.polygon(surf, color, points)
        pygame.draw.polygon(surf, outline, points, 2)
    elif shape == 'diamond':
        points = [(w // 2, 0), (w, h // 2), (w // 2, h), (0, h // 2)]
        pygame.draw.polygon(surf, color, points)
        pygame.draw.polygon(surf, outline, points, 2)
    elif shape == 'rect':
        pygame.draw.rect(surf, color, (2, 2, w - 4, h - 4), border_radius=4)
        pygame.draw.rect(surf, outline, (2, 2, w - 4, h - 4), 2, border_radius=4)
    else:
        r = min(w, h) // 2
        pygame.draw.circle(surf, color, (w // 2, h // 2), r)
    return surf

class AssetManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        try:
            pygame.mixer.init()
            self.audio_enabled = True
        except pygame.error:
            self.audio_enabled = False

    def load_image(self, key, path, size, shape, color):
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, size)
        except (FileNotFoundError, pygame.error):
            img = make_fallback_surface(size, shape, color)
        self.images[key] = img

    def get_image(self, key):
        return self.images[key]

    def load_sound(self, key, path):
        snd = DummySound()
        if self.audio_enabled:
            try:
                snd = pygame.mixer.Sound(path)
            except (FileNotFoundError, pygame.error):
                snd = DummySound()
        self.sounds[key] = snd

    def play(self, key):
        sound = self.sounds.get(key)
        if sound is not None:
            sound.play()