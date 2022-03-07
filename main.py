import pygame
import random
import os
import sys

# Initial variables
WIDTH = 800
HEIGHT = 650
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "img")

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Run Forest")
clock = pygame.time.Clock()
screen_pos = 0
font_name = pygame.font.match_font('arial')


def draw_text(surf, text, size, x, y,):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, False, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.score = 0
        self.hp = 3
        self.radius = 70

        self.anim_speed = 4
        self.frame = 0
        self.images = []
        for i in range(1, 9):
            img = pygame.image.load(os.path.join(img_folder, 'run' + str(i) + '.png')).convert()
            img = pygame.transform.scale(img, (250, 250))
            self.images.append(img)

        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = 100
        self.rect.bottom = HEIGHT - 125

        self.speedy = 0
        self.is_jumping = True
        self.is_falling = True

    def gravity(self):
        # Constant "pulling down" the character
        if self.is_jumping:
            self.speedy += 1.2  # Gravity force
        # When the character hits the ground switch off is_jumping
        if self.rect.bottom >= HEIGHT - 125:
            self.speedy = 0
            self.rect.bottom = HEIGHT - 125
            self.is_jumping = False

    def jump(self):
        # Switch on is_jumping from keystroke
        if self.is_jumping is False:
            self.is_falling = False
            self.is_jumping = True

    def update(self):
        # Initialise jumping and turn it off
        if self.is_jumping and self.is_falling is False:
            self.is_falling = True
            self.speedy -= 15  # How high to jump

        self.rect.y += self.speedy  # Update character position
        self.gravity()

        # Animate player character
        if self.is_jumping is False:
            self.frame += 1
            if self.frame > 7 * self.anim_speed:
                self.frame = 0
            self.image = self.images[self.frame // self.anim_speed]
        elif self.is_jumping is True:
            self.frame = 0
            self.image = self.images[5]


class Heart(pygame.sprite.Sprite):
    def __init__(self, hp):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(img_folder, 'heart.png')).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        self.count = hp
        self.rect.x = 50 + hp * 20  # Every heart gets offset farther right
        self.rect.y = 50

    def update(self):
        if self.count > player.hp:
            self.kill()     # Lose hp


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.frame = 0
        self.anim_speed = 20
        self.images = []
        for i in range(1, 3):
            img = pygame.image.load(os.path.join(img_folder, 'enemy' + str(i) + '.png')).convert()
            img = pygame.transform.scale(img, (75, 75))
            img.convert_alpha()
            img.set_colorkey(BLACK)
            self.images.append(img)

        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(int(WIDTH * 0.9), int(WIDTH * 1.4))
        self.rect.bottom = random.randrange(HEIGHT - 160, HEIGHT - 150)
        self.speedx = random.randrange(-16, -10)

    def update(self):
        self.rect.x += self.speedx
        hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_circle)  # Check for collision

        if hits:
            player.hp -= 1
            self.respawn()
            self.rect.x = int(WIDTH * 2.5)

        if self.rect.right < -90:
            player.score += 1
            self.respawn()

        # Animate the enemy
        self.frame += 1
        if self.frame > 2 * self.anim_speed - 1:
            self.frame = 0
        self.image = self.images[self.frame // self.anim_speed]

    def respawn(self):
        self.rect.x = random.randrange(int(WIDTH), int(WIDTH * 1.4))
        self.rect.bottom = random.randrange(HEIGHT - 160, HEIGHT - 150)
        self.speedx = random.randrange(-16, -10)


# Load graphics
bg_image = pygame.image.load(os.path.join(img_folder, "bg.png")).convert()
bg_image = pygame.transform.scale(bg_image, (800, 650))
bg_rect = bg_image.get_rect()


# Sprites and groups
all_sprites = pygame.sprite.Group()
player = Player()
mobs = pygame.sprite.Group()
all_sprites.add(player)
hearts = pygame.sprite.Group()


for blob in range(1):   # Enemy quantity
    enemy = Enemy()
    all_sprites.add(enemy)
    mobs.add(enemy)

for hitpoint in range(1, player.hp + 1):    # HP quantity
    heart = Heart(hitpoint)
    all_sprites.add(heart)
    hearts.add(heart)

# Game loop
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == ord('q'):
                pygame.quit()
                try:
                    sys.exit()
                finally:
                    running = False
            if event.key == pygame.K_SPACE or event.key == ord('w'):
                player.jump()

    if player.hp == 0:
        running = False

    # Update
    all_sprites.update()

    # Render
    screen.fill(BLACK)

    rel_pos = screen_pos % bg_image.get_rect().width
    screen.blit(bg_image, (rel_pos - bg_image.get_rect().width, 0))
    if rel_pos < WIDTH:
        screen.blit(bg_image, (rel_pos, 0))
    screen_pos -= 5     # Screen scrolling speed

    all_sprites.draw(screen)
    draw_text(screen, str(player.score), 35, WIDTH / 2, 25)

    pygame.display.flip()

pygame.quit()
