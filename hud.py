import pygame
from settings import *

class HUD:
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont('consolas', 24)
        self.font_small = pygame.font.SysFont('consolas', 18)
        self.font_big = pygame.font.SysFont('consolas', 64, bold=True)

    def draw(self, surface, player):
        bar_w = 240
        bar_h = 22
        x, y = 20, 20
        pygame.draw.rect(surface, (40, 40, 50), (x, y, bar_w, bar_h))
        ratio = max(player.hp, 0) / player.max_hp
        pygame.draw.rect(surface, (200, 60, 60), (x, y, int(bar_w * ratio), bar_h))
        pygame.draw.rect(surface, (230, 230, 230), (x, y, bar_w, bar_h), 2)
        hp_text = self.font_small.render(f"HP {max(player.hp, 0)}/{player.max_hp}", True, (255, 255, 255))
        surface.blit(hp_text, (x + 8, y + 2))

        coins_text = self.font.render(f"монети: {player.coins}", True, (255, 215, 0))
        surface.blit(coins_text, (x, y + bar_h + 10))

        kills_text = self.font.render(f"кіли: {player.kills}/{KILLS_TO_WIN}", True, (255, 255, 255))
        surface.blit(kills_text, (x, y + bar_h + 40))

        hint = self.font_small.render("WASD/Arrows move, Left Click shoot", True, (180, 180, 190))
        surface.blit(hint, (20, SCREEN_HEIGHT - 30))

    def draw_overlay(self, surface, title, color, subtitle):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        title_surf = self.font_big.render(title, True, color)
        rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        surface.blit(title_surf, rect)
        sub_surf = self.font.render(subtitle, True, (230, 230, 230))
        rect2 = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        surface.blit(sub_surf, rect2)