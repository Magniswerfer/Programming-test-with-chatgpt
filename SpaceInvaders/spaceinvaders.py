import pygame
import sys
from pygame.locals import *

pygame.init()

# Screen settings
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Colors
WHITE = (255, 255, 255)

# Spaceship settings
spaceship_speed = 5
spaceship_image = pygame.image.load("spaceship.png")
scaled_height = int(HEIGHT * 0.1)
spaceship_image = pygame.transform.scale(spaceship_image, (spaceship_image.get_width() * scaled_height // spaceship_image.get_height(), scaled_height))
spaceship_rect = spaceship_image.get_rect()
spaceship_rect.centerx = WIDTH // 2
spaceship_rect.y = HEIGHT - spaceship_image.get_height() - 10

# Bullet settings
bullet_image = pygame.Surface((5, 15))
bullet_image.fill((255, 0, 0))
bullet_speed = 10
bullets = []
clock = pygame.time.Clock()

bg_image = pygame.image.load("background.png").convert()
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

# Enemy settings
enemy_image = pygame.image.load("enemy.png")
scaled_height = int(HEIGHT * 0.1)
enemy_image = pygame.transform.scale(enemy_image, (enemy_image.get_width() * scaled_height // enemy_image.get_height(), scaled_height))
enemy_rects = []
num_rows = 5
num_columns = 10
enemy_speed = 1
enemy_move_down = 10

visible_enemies = []

game_over = False

# Text settings
font_large = pygame.font.Font(None, 72)
victory_text = font_large.render("VICTORY", True, (255, 255, 255))
victory_text_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
defeat_text = font_large.render("DEFEAT", True, (255, 0, 0))
defeat_text_rect = defeat_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))


# Button settings
font_small = pygame.font.Font(None, 36)
button_text = font_small.render("RESTART", True, (255, 255, 255))
button_rect = pygame.Rect(0, 0, 150, 50)
button_rect.center = (WIDTH // 2, HEIGHT // 2 + 50)
button_text_rect = button_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

def create_enemy_grid():
    enemy_width, enemy_height = enemy_image.get_size()
    for row in range(num_rows):
        enemy_row = []
        visible_row = []
        for column in range(num_columns):
            enemy_rect = enemy_image.get_rect()
            enemy_rect.x = column * (enemy_width + 10) + (WIDTH - num_columns * (enemy_width + 10)) // 2
            enemy_rect.y = row * (enemy_height + 10) + 50 - ((num_rows - 1) * (enemy_height + 10))
            enemy_row.append(enemy_rect)
            visible_row.append(True)  # Set all enemies as initially visible
        enemy_rects.append(enemy_row)
        visible_enemies.append(visible_row)

create_enemy_grid()

last_fire_time = pygame.time.get_ticks()

def handle_input():
    global last_fire_time

    keys = pygame.key.get_pressed()

    if keys[K_LEFT] and spaceship_rect.left > 0:
        spaceship_rect.x -= spaceship_speed
    if keys[K_RIGHT] and spaceship_rect.right < WIDTH:
        spaceship_rect.x += spaceship_speed

    current_time = pygame.time.get_ticks()
    if keys[K_SPACE] and current_time - last_fire_time >= 300:
        last_fire_time = current_time
        bullet_rect = pygame.Rect(spaceship_rect.x + spaceship_rect.width // 2 - 2, spaceship_rect.y, 4, 10)
        bullets.append(bullet_rect)

def check_collisions():
    global bullets, enemy_rects, game_over
    
    # Check bullet-enemy collisions
    for bullet in bullets.copy():
        for row, enemy_row in enumerate(enemy_rects):
            for col, enemy in enumerate(enemy_row):
                if visible_enemies[row][col] and bullet.colliderect(enemy):
                    bullets.remove(bullet)
                    visible_enemies[row][col] = False
                    break

    # Check spaceship-enemy collisions
    for row, enemy_row in enumerate(enemy_rects):
        for col, enemy in enumerate(enemy_row):
            if visible_enemies[row][col] and spaceship_rect.colliderect(enemy):
                game_over = True


def move_enemies():
    global enemy_speed
    move_down = False
    for row, enemy_row in enumerate(enemy_rects):
        direction = -1 if row % 2 == 0 else 1
        for c, enemy in enumerate(enemy_row):
            if not visible_enemies[row][c]:
                continue
            enemy.x += direction * enemy_speed
            if enemy.right >= WIDTH or enemy.left <= 0:
                move_down = True
                break
        if move_down:
            break

    if move_down:
        for r, enemy_row in enumerate(enemy_rects):
            for c, enemy in enumerate(enemy_row):
                if not visible_enemies[r][c]:
                    continue
                enemy.y += enemy_move_down
                if enemy.bottom > 0 and not visible_enemies[r][c]:
                    visible_enemies[r][c] = True
        enemy_speed *= -1


def restart_game():
    global spaceship_rect, bullets, enemy_rects, visible_enemies
    spaceship_rect.center = (WIDTH // 2, HEIGHT - spaceship_image.get_height())
    bullets = []
    enemy_rects = []
    visible_enemies = []
    create_enemy_grid()


print("Button text rect:", button_text_rect)
while True:
    screen.blit(bg_image, (0, 0))
    screen.blit(spaceship_image, spaceship_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet_rect = bullet_image.get_rect(center=(spaceship_rect.centerx, spaceship_rect.y))
                bullets.append(bullet_rect)
                pygame.time.set_timer(pygame.USEREVENT, 300)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(pygame.mouse.get_pos()):
                restart_game()


    if not game_over:
        handle_input()
        move_enemies()
        check_collisions()

        for bullet in bullets:
            bullet.y -= bullet_speed
            if bullet.y < 0:
                bullets.remove(bullet)

        for bullet in bullets[:]:
            for r, enemy_row in enumerate(enemy_rects):
                for c, enemy in enumerate(enemy_row):
                    if visible_enemies[r][c] and bullet.colliderect(enemy):
                        visible_enemies[r][c] = False
                        bullets.remove(bullet)
                        break

        for bullet_rect in bullets:
            screen.blit(bullet_image, bullet_rect)

        for r, enemy_row in enumerate(enemy_rects):
            for c, enemy in enumerate(enemy_row):
                if visible_enemies[r][c]:
                    screen.blit(enemy_image, enemy)

    if all(not visible for row in visible_enemies for visible in row):
        screen.blit(victory_text, victory_text_rect)
        pygame.draw.rect(screen, (0, 255, 0), button_rect)
        screen.blit(button_text, button_text_rect)

    if game_over:
        screen.blit(defeat_text, defeat_text_rect)
        pygame.draw.rect(screen, (0, 255, 0), button_rect)
        screen.blit(button_text, button_text_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(pygame.mouse.get_pos()):
                if game_over or all(not visible for row in visible_enemies for visible in row):
                    restart_game()
                    game_over = False  # Reset the game_over variable to resume the game

    pygame.display.flip()
    clock.tick(60)