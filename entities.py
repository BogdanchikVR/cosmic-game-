import math
import random
import pygame
from pygame.math import Vector2
from settings import *

class Background:
    def __init__(self):
        self.tile_size = 140

    def draw(self, surface, camera):
        surface.fill(SPACE_BG_COLOR)
        ts = self.tile_size
        start_tx = int(math.floor((camera.x - SCREEN_WIDTH / 2) / ts)) - 1
        end_tx = int(math.floor((camera.x + SCREEN_WIDTH / 2) / ts)) + 1
        start_ty = int(math.floor((camera.y - SCREEN_HEIGHT / 2) / ts)) - 1
        end_ty = int(math.floor((camera.y + SCREEN_HEIGHT / 2) / ts)) + 1
        for tx in range(start_tx, end_tx + 1):
            for ty in range(start_ty, end_ty + 1):
                rng = random.Random((tx * 92821) ^ (ty * 68917) ^ 0x5bd1e995)
                count = rng.randint(3, 6)
                for _ in range(count):
                    lx = rng.randint(0, ts)
                    ly = rng.randint(0, ts)
                    wx = tx * ts + lx
                    wy = ty * ts + ly
                    sx = wx - camera.x + SCREEN_WIDTH / 2
                    sy = wy - camera.y + SCREEN_HEIGHT / 2
                    size = rng.choice([1, 1, 1, 2])
                    shade = rng.randint(140, 255)
                    pygame.draw.circle(surface, (shade, shade, min(255, shade + 20)), (int(sx), int(sy)), size)

class Projectile:
    def __init__(self, world_pos, direction, assets):
        self.world_pos = Vector2(world_pos)
        self.direction = Vector2(direction)
        self.radius = PROJECTILE_RADIUS
        self.lifetime = PROJECTILE_LIFETIME
        self.image = assets.get_image('projectile')
        self._alive = True

    def update(self, dt):
        self.world_pos += self.direction * PROJECTILE_SPEED * dt
        self.lifetime -= dt
        if self.lifetime <= 0:
            self._alive = False

    def alive(self):
        return self._alive

    def kill(self):
        self._alive = False

    def draw(self, surface, camera):
        sx = self.world_pos.x - camera.x + SCREEN_WIDTH / 2
        sy = self.world_pos.y - camera.y + SCREEN_HEIGHT / 2
        rect = self.image.get_rect(center=(sx, sy))
        surface.blit(self.image, rect)

class Player:
    def __init__(self, assets):
        self.world_pos = Vector2(0, 0)
        self.radius = PLAYER_RADIUS
        self.max_hp = PLAYER_MAX_HP
        self.hp = PLAYER_MAX_HP
        self.coins = 0
        self.kills = 0
        self.speed = PLAYER_SPEED
        self.shoot_cooldown = 0.0
        self.invuln_timer = 0.0
        self.image = assets.get_image('player')

    def handle_input(self, keys, dt):
        move = Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move.x += 1
        if move.length_squared() > 0:
            move = move.normalize()
            self.world_pos += move * self.speed * dt

    def update(self, dt):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        if self.invuln_timer > 0:
            self.invuln_timer -= dt

    def can_shoot(self):
        return self.shoot_cooldown <= 0

    def shoot(self, target_world_pos, assets):
        self.shoot_cooldown = PROJECTILE_COOLDOWN
        direction = target_world_pos - self.world_pos
        if direction.length_squared() == 0:
            direction = Vector2(1, 0)
        direction = direction.normalize()
        return Projectile(self.world_pos, direction, assets)

    def take_damage(self, amount):
        if self.invuln_timer <= 0:
            self.hp -= amount
            self.invuln_timer = 0.4
            if self.hp < 0:
                self.hp = 0

    def draw(self, surface, camera):
        sx = self.world_pos.x - camera.x + SCREEN_WIDTH / 2
        sy = self.world_pos.y - camera.y + SCREEN_HEIGHT / 2
        rect = self.image.get_rect(center=(sx, sy))
        surface.blit(self.image, rect)

class Asteroid:
    def __init__(self, world_pos, velocity, assets):
        self.world_pos = Vector2(world_pos)
        self.velocity = Vector2(velocity)
        self.radius = ASTEROID_RADIUS
        self.image = assets.get_image('asteroid')
        self.rotation = 0.0
        self.rotation_speed = random.uniform(-40, 40)

    def update(self, dt):
        self.world_pos += self.velocity * dt
        self.rotation += self.rotation_speed * dt

    def draw(self, surface, camera):
        sx = self.world_pos.x - camera.x + SCREEN_WIDTH / 2
        sy = self.world_pos.y - camera.y + SCREEN_HEIGHT / 2
        rotated = pygame.transform.rotate(self.image, self.rotation)
        rect = rotated.get_rect(center=(sx, sy))
        surface.blit(rotated, rect)

class Coin:
    def __init__(self, world_pos, assets):
        self.world_pos = Vector2(world_pos)
        self.radius = COIN_RADIUS
        self.value = COIN_VALUE
        self.image = assets.get_image('coin')
        self.bob_timer = random.uniform(0, math.pi * 2)

    def update(self, dt):
        self.bob_timer += dt * 4

    def draw(self, surface, camera):
        sx = self.world_pos.x - camera.x + SCREEN_WIDTH / 2
        sy = self.world_pos.y - camera.y + SCREEN_HEIGHT / 2 + math.sin(self.bob_timer) * 3
        rect = self.image.get_rect(center=(sx, sy))
        surface.blit(self.image, rect)

class Monster:
    def __init__(self, world_pos, assets):
        self.world_pos = Vector2(world_pos)
        self.radius = MONSTER_RADIUS
        self.hp = MONSTER_HP
        self.speed = MONSTER_SPEED
        self.contact_cooldown = 0.0
        self.image = assets.get_image('monster')

    def update(self, dt, target_pos):
        direction = target_pos - self.world_pos
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.world_pos += direction * self.speed * dt
        if self.contact_cooldown > 0:
            self.contact_cooldown -= dt

    def take_damage(self, amount):
        self.hp -= amount
        return self.hp <= 0

    def draw(self, surface, camera):
        sx = self.world_pos.x - camera.x + SCREEN_WIDTH / 2
        sy = self.world_pos.y - camera.y + SCREEN_HEIGHT / 2
        rect = self.image.get_rect(center=(sx, sy))
        surface.blit(self.image, rect)
        bar_w = 30
        hp_ratio = max(self.hp, 0) / MONSTER_HP
        pygame.draw.rect(surface, (60, 20, 20), (sx - bar_w / 2, sy - self.radius - 12, bar_w, 5))
        pygame.draw.rect(surface, (220, 60, 60), (sx - bar_w / 2, sy - self.radius - 12, bar_w * hp_ratio, 5))

class Portal:
    def __init__(self, world_pos, assets):
        self.world_pos = Vector2(world_pos)
        self.radius = PORTAL_RADIUS
        self.image = assets.get_image('portal')
        self.timer = 0.0

    def update(self, dt):
        self.timer += dt

    def draw(self, surface, camera):
        sx = self.world_pos.x - camera.x + SCREEN_WIDTH / 2
        sy = self.world_pos.y - camera.y + SCREEN_HEIGHT / 2
        scale = 1.0 + 0.08 * math.sin(self.timer * 3)
        w = max(int(self.image.get_width() * scale), 1)
        h = max(int(self.image.get_height() * scale), 1)
        scaled = pygame.transform.smoothscale(self.image, (w, h))
        rect = scaled.get_rect(center=(sx, sy))
        surface.blit(scaled, rect)