import pygame
import sys
import random

# Initialize PyGame
pygame.init()

# Setting game window
screen_width = 1024
screen_height = 768
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Invader-ish (kinda)')

# Set the frame rate
clock = pygame.time.Clock()

# Player settings
player_width = 50
player_height = 60
player_x = screen_width // 2 - player_width // 2
player_y = screen_height - player_height - 10
player_speed = 6

# Player HP settings
player_hp = 5
hp_bar_width = 20
hp_bar_height = 20
hp_bar_space = 5

score = 0
font = pygame.font.Font(None, 24)

# Bullet settings
bullet_width = 5
bullet_height = 10
bullet_speed = 5
bullets = []

# Enemy settings
enemy_width = 50
enemy_height = 60
enemy_speed = 2
enemies = []

# Let's spawn an enemy every 2 seconds
enemy_timer = 0
enemy_spawn_time = 2000

##########################################
# UPDATE: Adding additional game logic:
#   Each time a score increases by 100
#   speed up the enemy spawn rate by .3 seconds
#   and add an HP bar
###########################################
next_threshold = 25
spawn_decrease = 300
min_spawn_time = 300


# Collision detection function
def check_collision(rect1, rect2):
    return rect1.colliderect(rect2)


# Draw score
def draw_score():
    score_text = font.render("Score: " + str(score), True, (255, 255, 255))
    screen.blit(score_text, (5, 5))


def draw_hp_bar():
    for i in range(player_hp):
        pygame.draw.rect(screen, (255, 0, 0), (10 + i * (hp_bar_width + hp_bar_space), 50, hp_bar_width, hp_bar_height))

# Game over screen
def game_over_screen():
    # Display the "Game over!" message
    screen.fill((0,0,0)) # Clear the screen
    game_over_text = font.render("Game Over!", True, (255, 0, 0))
    instructions_text = font.render("Press SPACE to play again or ESC to quit the game", True, (255, 255, 255))

    # Center the text
    game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 3))
    instructions_rect = instructions_text.get_rect(center=(screen_width // 2, screen_height // 2))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(instructions_text, instructions_rect)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


# Main game loop
while True:
    # Reset the variables at the start of a new round
    player_hp = 5
    score = 0
    paused = False
    pause_menu_selected = 0
    bullets = []
    enemies = []

    while player_hp > 0:
        # Handle all events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused  # toggle pause
                    pause_menu_selected = 0  # Reset to "Resume" when paused

                if paused:
                    if event.key == pygame.K_DOWN:
                        pause_menu_selected = (pause_menu_selected + 1) % 2
                    elif event.key == pygame.K_UP:
                        pause_menu_selected = (pause_menu_selected - 1) % 2
                    elif event.key == pygame.K_RETURN:
                        if pause_menu_selected == 0:  # Resume
                            paused = False
                        elif pause_menu_selected == 1:  # Exit
                            pygame.quit()
                            sys.exit()
                    continue  # Don't process other keys when paused

                if event.key == pygame.K_SPACE and not paused:
                    # Create a bullet at the current location
                    bullet_x = player_x + player_width // 2 - bullet_width // 2
                    bullet_y = player_y
                    bullets.append(pygame.Rect(bullet_x, bullet_y, bullet_width, bullet_height))

        # If paused, draw menu and skip rest of game logic
        if paused:
            screen.fill((0, 0, 0))
            menu_options = ["Resume", "Exit Game"]

            for i, option in enumerate(menu_options):
                color = (0, 255, 0) if i == pause_menu_selected else (255, 255, 255)
                text = font.render(option, True, color)
                text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 + i * 30))
                screen.blit(text, text_rect)

            pygame.display.flip()
            clock.tick(10)
            continue  # skip the rest of the game logic

        # Handle player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
            player_x += player_speed

        # Update bullet positions
        for bullet in bullets:
            bullet.y -= bullet_speed

        # Update enemy positions and spawn new ones
        current_time = pygame.time.get_ticks()
        if current_time - enemy_timer > enemy_spawn_time:
            enemy_x = random.randint(0, screen_width - enemy_width)
            enemy_y = -enemy_height
            enemies.append(pygame.Rect(enemy_x, enemy_y, enemy_width, enemy_height))
            enemy_timer = current_time

        for enemy in enemies:
            enemy.y += enemy_speed

        # Check for collisions with bullets
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if check_collision(bullet, enemy):
                    score += 1
                    bullets.remove(bullet)
                    enemies.remove(enemy)

                    ##########################################
                    # UPDATE: Adding additional game logic:
                    #   Each time a score increases by 25
                    #   speed up the enemy spawn rate by .3 seconds
                    #   and add an HP bar
                    ###########################################
                    if score >= next_threshold:
                        if enemy_spawn_time > min_spawn_time:
                            enemy_spawn_time = max(min_spawn_time,
                                                   enemy_spawn_time - spawn_decrease)  # increase enemy spawn time
                        player_hp += 1  # Reward extra HP
                        player_speed += 1
                        next_threshold += 25
                    break

        # Check for collisions with player
        for enemy in enemies[:]:
            if check_collision(enemy, pygame.Rect(player_x, player_y, player_width, player_height)):
                player_hp -= 1  # reduce hp
                enemies.remove(enemy)

        ###############################################################
        # UPDATE: Adjustment to game logic - if enemies either collide
        # or move past user .y position, cause damage
        ###############################################################

        # ENHANCEMENT: Adding enemy passing .y check
        # Check if enemies passed the player
        for enemy in enemies[:]:
            if enemy.y >= player_y + player_height:
                player_hp -= 1
                enemies.remove(enemy)

        # Remove bullets that are off the screen
        bullets = [bullet for bullet in bullets if bullet.y > 0]

        # Fill the screen with a color
        screen.fill((0, 0, 0))

        # Draw the player
        pygame.draw.rect(screen, (0, 128, 255), (player_x, player_y, player_width, player_height))

        # Draw the bullets
        for bullet in bullets:
            pygame.draw.rect(screen, (255, 255, 255), bullet)

        # Draw the enemies
        for enemy in enemies:
            pygame.draw.rect(screen, (255, 0, 0), enemy)

        # Draw the HP bar
        draw_hp_bar()

        # Draw the score
        draw_score()

        # Update the display
        pygame.display.flip()

        # Cap the frame rate at 60 fps
        clock.tick(60)

    # If the player loses, show game over screen
    if not game_over_screen():
        break
