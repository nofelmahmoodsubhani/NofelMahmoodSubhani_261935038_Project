import pygame
import random

# Initialize Pygame
pygame.init()

#colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

#display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Adventure")

#background image
background_image = pygame.image.load("background.png").convert()

#sound effects
explosion_sound = pygame.mixer.Sound("explosion1.wav")

#background music
pygame.mixer.music.load("background.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

#class of spacecraft
class Spacecraft(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("spaceship.png").convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed_x = 0
        self.speed_y = 0
        self.health = 100

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH

        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            global lives
            lives -= 1
            if lives == 0:
                global running, game_over
                running = False
                game_over = True

    def draw_health_bar(self):
        bar_width = 100
        bar_height = 10
        health_bar_rect = pygame.Rect(self.rect.x, self.rect.y - 20, bar_width, bar_height)
        remaining_health = max(self.health, 0)
        remaining_bar_width = int((remaining_health / 100) * bar_width)
        health_bar_fill_rect = pygame.Rect(self.rect.x, self.rect.y - 20, remaining_bar_width, bar_height)

        pygame.draw.rect(screen, RED, health_bar_rect)
        pygame.draw.rect(screen, GREEN, health_bar_fill_rect)

#class of asteroid
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.image.load("asteroid.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)

#class of bullet
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()

#sprite/image groups
all_sprites = pygame.sprite.Group()#Aggregation: all_sprites group contains multiple sprites
asteroids = pygame.sprite.Group()#Aggregation: asteroids group contains multiple asteroid sprites
bullets = pygame.sprite.Group()#Aggregation: bullets group contains multiple bullet sprites

#spacecraft
spacecraft = Spacecraft()#Composition: spacecraft is composed of a Spacecraft object
all_sprites.add(spacecraft)

#initial asteroids
asteroid_speed = 3
asteroid_count_per_level = 5

for _ in range(asteroid_count_per_level):
    asteroid = Asteroid(asteroid_speed)#Composition: asteroid is composed of an Asteroid object
    all_sprites.add(asteroid)
    asteroids.add(asteroid)

#game variables
clock = pygame.time.Clock()
score = 0
level = 1
lives = 3
running = True
game_over = False

#Game loop
while running:
    #events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                spacecraft.speed_x = -5
            elif event.key == pygame.K_RIGHT:
                spacecraft.speed_x = 5
            elif event.key == pygame.K_UP:
                spacecraft.speed_y = -5
            elif event.key == pygame.K_DOWN:
                spacecraft.speed_y = 5
            elif event.key == pygame.K_SPACE:
                spacecraft.shoot()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                spacecraft.speed_x = 0
            elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                spacecraft.speed_y = 0

    #Update
    all_sprites.update()

    #Check for collisions between spacecraft and asteroids
    hits = pygame.sprite.spritecollide(spacecraft, asteroids, True)#Association: spacecraft collides with asteroids
    for asteroid in hits:
        explosion_sound.play()
        spacecraft.take_damage(20)

    #Check for collisions between bullets and asteroids
    asteroid_bullet_collisions = pygame.sprite.groupcollide(asteroids, bullets, True, True)#Association: spacecraft collides with asteroids
    for asteroid, bullet_list in asteroid_bullet_collisions.items():
        explosion_sound.play()
        score += 10

    #Check if all asteroids are destroyed
    if len(asteroids) == 0:
        level += 1
        asteroid_count_per_level += 2
        asteroid_speed += 1

        for _ in range(asteroid_count_per_level):
            asteroid = Asteroid(asteroid_speed)
            all_sprites.add(asteroid)
            asteroids.add(asteroid)

    #Draw
    screen.blit(background_image, (0, 0))
    all_sprites.draw(screen)#Polymorphic Behavior: draw() method called on all_sprites group, which contains different sprite objects

    #text
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))
    screen.blit(lives_text, (10, 50))

    #health bar
    spacecraft.draw_health_bar()

    #Game over display
    if game_over:
        game_over_text = font.render("Game Over", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))

    #Update the display
    pygame.display.flip()

    #frame rate
    clock.tick(60)

#stoping background music when the game ends
pygame.mixer.music.stop()

#Quit the game
pygame.quit()

