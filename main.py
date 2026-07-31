import math
import random
import sys
import pygame
from pygame.math import Vector2
from settings import *
from asset_manager import AssetManager
from entities import Player, Background, Coin, Asteroid, Monster, Portal, Projectile
from hud import HUD
pygame.mixer.init()
pygame.mixer.music.load("spacemusic.mp3")
pygame.mixer.music.play(-1)

def spawn_position_around(center, min_r, max_r):
    angle = random.uniform(0, math.pi * 2)
    dist = random.uniform(min_r, max_r)
    return center + Vector2(math.cos(angle), math.sin(angle)) * dist

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Survivor")
        self.clock = pygame.time.Clock()
        self.assets = AssetManager()
        self._load_assets()
        self.hud = HUD()
        self.background = Background()
        self.reset()

    def _load_assets(self):
        self.assets.load_image('player', 'spaceship.png', (38, 38), 'triangle', (90, 200, 255))
        self.assets.load_image('monster', 'monstergreen.png', (34, 34), 'diamond', (230, 70, 70))
        self.assets.load_image('asteroid', 'asteroid.png', (46, 46), 'circle', (150, 120, 95))
        self.assets.load_image('coin', 'coin.png', (20, 20), 'circle', (255, 215, 0))
        self.assets.load_image('portal', 'portal.png', (74, 74), 'circle', (180, 90, 255))
        self.assets.load_image('projectile', 'projectile.png', (10, 10), 'circle', (255, 255, 140))
        self.assets.load_sound('shoot', 'spaceship shoot.mp3')
        self.assets.load_sound('hit', 'hit.mp3')
        self.assets.load_sound('coin', 'coin2.mp3')
        self.assets.load_sound('explosion', 'explosion.mp3')
        self.assets.load_sound('portal', 'portal2.mp3')

    def reset(self):
        self.player = Player(self.assets)
        self.projectiles = []
        self.asteroids = []
        self.coins = []
        self.monsters = []
        self.portal = None
        self.state = 'playing'
        self.asteroid_timer = 0.0
        self.coin_timer = 0.0
        self.monster_timer = 0.0
        for _ in range(6):
            self._spawn_asteroid()
        for _ in range(8):
            self._spawn_coin()
        for _ in range(3):
            self._spawn_monster()

    def _spawn_asteroid(self):
        pos = spawn_position_around(self.player.world_pos, 350, 650)
        vel = Vector2(random.uniform(-40, 40), random.uniform(-40, 40))
        self.asteroids.append(Asteroid(pos, vel, self.assets))

    def _spawn_coin(self):
        pos = spawn_position_around(self.player.world_pos, 200, 600)
        self.coins.append(Coin(pos, self.assets))

    def _spawn_monster(self):
        pos = spawn_position_around(self.player.world_pos, 400, 700)
        self.monsters.append(Monster(pos, self.assets))

    def _spawn_portal(self):
        pos = spawn_position_around(self.player.world_pos, 150, 250)
        self.portal = Portal(pos, self.assets)
        self.assets.play('portal')

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self._handle_events()
            if self.state == 'playing':
                self._update(dt)
            self._draw()
            pygame.display.flip()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and self.state in ('game_over', 'victory'):
                    self.reset()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.state == 'playing':
                if self.player.can_shoot():
                    mouse_screen = Vector2(pygame.mouse.get_pos())
                    mouse_world = mouse_screen - Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2) + self.player.world_pos
                    projectile = self.player.shoot(mouse_world, self.assets)
                    self.projectiles.append(projectile)
                    self.assets.play('shoot')

    def _update(self, dt):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys, dt)
        self.player.update(dt)
        camera = self.player.world_pos

        for projectile in self.projectiles:
            projectile.update(dt)
        for asteroid in self.asteroids:
            asteroid.update(dt)
        for coin in self.coins:
            coin.update(dt)
        for monster in self.monsters:
            monster.update(dt, self.player.world_pos)
        if self.portal is not None:
            self.portal.update(dt)

        self._handle_collisions()

        self.projectiles = [p for p in self.projectiles if p.alive() and (p.world_pos - camera).length() < DESPAWN_DISTANCE]
        self.asteroids = [a for a in self.asteroids if (a.world_pos - camera).length() < DESPAWN_DISTANCE]
        self.coins = [c for c in self.coins if (c.world_pos - camera).length() < DESPAWN_DISTANCE]
        self.monsters = [m for m in self.monsters if (m.world_pos - camera).length() < DESPAWN_DISTANCE and m.hp > 0]

        self.asteroid_timer += dt
        if self.asteroid_timer > ASTEROID_SPAWN_INTERVAL and len(self.asteroids) < MAX_ASTEROIDS:
            self.asteroid_timer = 0.0
            self._spawn_asteroid()

        self.coin_timer += dt
        if self.coin_timer > COIN_SPAWN_INTERVAL and len(self.coins) < MAX_COINS:
            self.coin_timer = 0.0
            self._spawn_coin()

        self.monster_timer += dt
        if self.monster_timer > MONSTER_SPAWN_INTERVAL and len(self.monsters) < MAX_MONSTERS and self.player.kills < KILLS_TO_WIN:
            self.monster_timer = 0.0
            self._spawn_monster()

        if self.player.kills >= KILLS_TO_WIN and self.portal is None:
            self._spawn_portal()

        if self.portal is not None:
            if (self.portal.world_pos - self.player.world_pos).length() < self.portal.radius + self.player.radius:
                self.state = 'victory'

        if self.player.hp <= 0:
            self.state = 'game_over'

    def _handle_collisions(self):
        for projectile in self.projectiles:
            if not projectile.alive():
                continue
            for monster in self.monsters:
                if monster.hp <= 0:
                    continue
                if (projectile.world_pos - monster.world_pos).length() < projectile.radius + monster.radius:
                    projectile.kill()
                    dead = monster.take_damage(PROJECTILE_DAMAGE)
                    if dead:
                        self.player.kills += 1
                        self.assets.play('explosion')
                    break

        for asteroid in self.asteroids:
            if (asteroid.world_pos - self.player.world_pos).length() < asteroid.radius + self.player.radius:
                self.player.take_damage(ASTEROID_DAMAGE)
                self.assets.play('hit')

        for monster in self.monsters:
            if monster.hp <= 0:
                continue
            if monster.contact_cooldown <= 0 and (monster.world_pos - self.player.world_pos).length() < monster.radius + self.player.radius:
                self.player.take_damage(MONSTER_DAMAGE)
                monster.contact_cooldown = MONSTER_CONTACT_COOLDOWN
                self.assets.play('hit')

        remaining_coins = []
        for coin in self.coins:
            if (coin.world_pos - self.player.world_pos).length() < coin.radius + self.player.radius:
                self.player.coins += coin.value
                self.assets.play('coin')
            else:
                remaining_coins.append(coin)
        self.coins = remaining_coins

    def _draw(self):
        camera = self.player.world_pos
        self.background.draw(self.screen, camera)
        for coin in self.coins:
            coin.draw(self.screen, camera)
        for asteroid in self.asteroids:
            asteroid.draw(self.screen, camera)
        for monster in self.monsters:
            monster.draw(self.screen, camera)
        if self.portal is not None:
            self.portal.draw(self.screen, camera)
        for projectile in self.projectiles:
            projectile.draw(self.screen, camera)
        self.player.draw(self.screen, camera)
        self.hud.draw(self.screen, self.player)
        if self.state == 'game_over':
            self.hud.draw_overlay(self.screen, "GAME OVER", (220, 60, 60), "Press R to restart")
        elif self.state == 'victory':
            self.hud.draw_overlay(self.screen, "VICTORY!", (80, 220, 110), "Press R to restart")

if __name__ == '__main__':
    Game().run()