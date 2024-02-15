import datetime
import pygame
import random
import os
from Sqlite3 import *

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Standard RGB colors 
RED = (255, 0, 0) 
GREEN = (0, 255, 0) 
BLUE = (0, 0, 255) 
CYAN = (0, 100, 100)
YELLOW = (255, 255, 0) 
BLACK = (0, 0, 0) 
WHITE = (255, 255, 255) 
BRIGHT_RED = (255,51,51)
BRIGHT_GREEN = (51,204,51)

# Paths
ASSETS_PATH = os.path.join(os.path.dirname(__file__), 'Assets')

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Shooter")

# Load main menu background image
main_menu_background_img = pygame.image.load(os.path.join(ASSETS_PATH, 'main.png'))
main_menu_background_img = pygame.transform.scale(main_menu_background_img, (WIDTH, HEIGHT))

# Load background image
background_img = pygame.image.load(os.path.join(ASSETS_PATH, 'back.png'))
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# Load enemy images
enemy_img = pygame.image.load(os.path.join(ASSETS_PATH, 'Enemy60.png'))
exploded_enemy_img = pygame.image.load(os.path.join(ASSETS_PATH, 'ExplodedEnemy30.png'))

# Load second enemy images
meteo_enemy_img = pygame.image.load(os.path.join(ASSETS_PATH, 'MeteoEnemy60.png'))
exploded_meteo_enemy_img = pygame.image.load(os.path.join(ASSETS_PATH, 'ExplodedMeteoEnemy60.png'))

# Load bullet image
bullet_img = pygame.image.load(os.path.join(ASSETS_PATH, 'Laser.png'))

# Load power-up image
powerup_img = pygame.image.load(os.path.join(ASSETS_PATH, 'Powerup_30.png'))

# Load tripple_laser image
tripple_laser = pygame.image.load(os.path.join(ASSETS_PATH, 'Tripple_Laser.png'))

# Load background music
pygame.mixer.music.load(os.path.join(ASSETS_PATH, 'soundtrack.mp3'))

# Play the music, loop indefinitely
pygame.mixer.music.play(-1)

# Set the volume to half
pygame.mixer.music.set_volume(0.5)

# Load sound effects for hits
enemy_hit_sound = pygame.mixer.Sound('Assets/enemy_hit.wav')
player_hit_sound = pygame.mixer.Sound('Assets/player_hit.wav')

# Enemy modes
ENEMY_NORMAL = 'normal'
ENEMY_EXPLODING = 'exploding'
ENEMY_DESTROYED = 'destroyed'

# Initial Enemy mode
Enemy_mode = ENEMY_NORMAL

# Second Enemy modes
SECOND_ENEMY_NORMAL = 'normal'
SECOND_ENEMY_EXPLODING = 'exploding'
SECOND_ENEMY_DESTROYED = 'destroyed'

# Initial Second Enemy mode
SecondEnemy_mode = SECOND_ENEMY_NORMAL

# Initialize Game Score
score = 0

# Initialize the Game Difficulty
game_difficulty = "Medium"

#  Enemy Speed
enemy_speed = 1.0

# Flag for single or Multi Player 
# True for SinglePlayer and false for multiplayer
game_Flag = True

# Get current time
current_Time = datetime.datetime.now()

# Create clock for controlling the frame rate
clock = pygame.time.Clock()

# Create sprite groups for enemies, bullets, and second enemies
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
second_enemies = pygame.sprite.Group()
powerups = pygame.sprite.Group()
players = pygame.sprite.Group() 




# Global Variable Pause
#pause = False


# Define a Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self, player_number=1, is_multiplayer=False):
        super().__init__()
        #self.all_sprites = pygame.sprite.Group()
        #self.bullets = pygame.sprite.Group()        
        self.player_number = player_number
        self.is_multiplayer = is_multiplayer
        # Load images
        self.load_images()
        self.image = self.normal_image
        self.rect = self.image.get_rect()
        # Positioning
        self.set_initial_position()
        # Speed and shooting delay
        self.speed = 5
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        # Players lives
        #self.lives = 3     

        # Initialize the power-up related attributes
        self.powerup = None  # No power-up initially
        self.powerup_time = 0  # Time when the power-up was activated

    def load_images(self):
        self.normal_image = pygame.image.load(os.path.join(ASSETS_PATH, f'Spaceship80{"_2" if self.player_number == 2 else ""}.png')).convert_alpha()
        self.moving_image = pygame.image.load(os.path.join(ASSETS_PATH, f'MSpaceship80{"_2" if self.player_number == 2 else ""}.png')).convert_alpha()
        self.exploded_image = pygame.image.load(os.path.join(ASSETS_PATH, f'ExplodedSpaceship80{"_2" if self.player_number == 2 else ""}.png')).convert_alpha()

    def set_initial_position(self):
        if self.is_multiplayer:
            position = WIDTH // 4 if self.player_number == 1 else WIDTH * 3 // 4
        else:
            position = WIDTH // 2
        self.rect.midbottom = (position, HEIGHT - 10)

    def update(self, keys=None):
        if keys is None:
            keys = {}  # Set to an empty dictionary if no keys argument is provided
        # Movement for Player 1
        if self.player_number == 1:
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.speed

            # Image update based on movement for Player 1
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.image = self.moving_image
            else:
                self.image = self.normal_image


        # Movement for Player 2
        elif self.player_number == 2:
            if keys[pygame.K_a]:
                self.rect.x -= self.speed
            if keys[pygame.K_d]:
                self.rect.x += self.speed

            # Image update based on movement for Player 2
            if keys[pygame.K_a] or keys[pygame.K_d]:
                self.image = self.moving_image
            else:
                self.image = self.normal_image                

        # Ensure the player stays within the screen bounds
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))

        # Call try_shoot if the shoot key is pressed
        self.try_shoot(keys)

    def try_shoot(self, keys):
        # Check if it's time to shoot based on the player number and key pressed
        can_shoot = (self.player_number == 1 and keys[pygame.K_SPACE]) or \
                    (self.player_number == 2 and keys[pygame.K_LCTRL])
        if can_shoot:
            self.shoot()
   
    def shoot(self):
        # Debug print to confirm shoot is triggered
        #print(f"shoot method triggered for Player {self.player_number}")        
        now = pygame.time.get_ticks()

        #Tripple shooting
        if self.powerup == 'tripple_laser' and now - self.last_shot > self.shoot_delay:
            # Create three triple laser bullets or a single powerful triple laser shot
            bullet1 = TripleLaserBullet(self.rect.centerx - 20, self.rect.top)  
            bullet2 = TripleLaserBullet(self.rect.centerx, self.rect.top)
            bullet3 = TripleLaserBullet(self.rect.centerx + 20, self.rect.top)  
            all_sprites.add(bullet1, bullet2, bullet3)
            bullets.add(bullet1, bullet2, bullet3)
            self.last_shot = now

        #Regular shooting
        elif now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            # Temporarily bypass the shooting delay to test bullet creation and display
            #print("Shooting delay bypassed for testing.")            
            # Create a new bullet instance
            print("Shooting")  # Debug print
            bullet = Bullet(self.rect.centerx, self.rect.top)
            # Debug print to confirm bullet creation
            #print(f"Bullet created for Player {self.player_number}")         
            # Add the new bullet to the all_sprites and bullets groups to be updated and drawn
            all_sprites.add(bullet)
            bullets.add(bullet)
            print("Bullet created and added to groups.")

        self.last_shot = now   
   
       # Create player objects
       # player = Player(player_number=1, is_multiplayer=False)        
       # player1 = Player(player_number=1, is_multiplayer=True)
       # player2 = Player(player_number=2, is_multiplayer=True)

# Enemy class
class Enemy(pygame.sprite.Sprite):
    global enemy_speed
    def __init__(self, image, exploded_image, speed_factor=enemy_speed, explosion_duration=500):
        super().__init__()
        self.image = image
        self.exploded_image = exploded_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(1, 2) * speed_factor
        self.mode = ENEMY_NORMAL
        self.explosion_timer = 0
        self.explosion_duration = explosion_duration

    def update(self, *args, **kwargs):
        if self.mode == ENEMY_NORMAL:
            self.rect.y += self.speed_y
            if self.rect.top > HEIGHT + 10:
                self.rect.topleft = (random.randrange(WIDTH - self.rect.width), random.randrange(-100, -40))
                self.speed_y = random.randrange(1, 2) * self.speed_y
        elif self.mode == ENEMY_EXPLODING:
            # Handle exploding animation logic
            self.explosion_timer += 1
            if self.explosion_timer >= self.explosion_duration:
                self.mode = ENEMY_DESTROYED
                self.explosion_timer = 0
                # Reset the image to the non-exploded state
                self.image = self.exploded_image

        elif self.mode == ENEMY_DESTROYED:
            # Handle logic for destroyed state
            pass

    def hit_by_bullet(self):
        # Perform actions when the enemy is hit by a bullet
        self.mode = ENEMY_EXPLODING
        # Change the image of the sprite directly
        self.image = self.exploded_image

# Second Enemy class
class SecondEnemy(pygame.sprite.Sprite):
    def __init__(self, image, exploded_image, speed_factor=enemy_speed, explosion_duration=60):
        super().__init__()
        self.image = image
        self.exploded_image = exploded_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.uniform(1.3, 2.5) * speed_factor
        self.mode = SECOND_ENEMY_NORMAL
        self.explosion_timer = 0
        self.explosion_duration = explosion_duration

    def update(self, *args, **kwargs):
        if self.mode == SECOND_ENEMY_NORMAL:
            self.rect.y += self.speed_y

            # Ensure the speed does not exceed a maximum value
            max_speed_y = 10  #  maximum speed value
            self.speed_y = min(self.speed_y, max_speed_y)
            
            if self.rect.top > HEIGHT + 10:
                self.rect.topleft = (random.randrange(WIDTH - self.rect.width), random.randrange(-100, -40))
                # Reset speed to a base value instead of increasing it
                self.speed_y = random.uniform(1.3, 2.5)  #  base speed range
        elif self.mode == SECOND_ENEMY_EXPLODING:
            # Handle exploding animation logic
            self.explosion_timer += 1
            if self.explosion_timer >= self.explosion_duration:
                self.mode = SECOND_ENEMY_DESTROYED
                self.explosion_timer = 0
        elif self.mode == SECOND_ENEMY_DESTROYED:
            # Handle logic for destroyed state
            pass

    def hit_by_bullet(self):
        # Perform actions when the second enemy is hit by a bullet
        self.mode = SECOND_ENEMY_EXPLODING
        self.image = self.exploded_image      

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10
#        self.rect.y -= self.speed_y  # Move the bullet up        

    def update(self, *args, **kwargs):
        self.rect.y += self.speed_y
        # Remove the bullet if it goes off the screen
        if self.rect.bottom < 0:
            self.kill()

# PowerUp class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, img, type, *groups):
        super().__init__(*groups)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(1, 4)
        self.type = type  # "tripple_laser" for this case

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT:
            self.kill()


# TripleLaserBullet class
class TripleLaserBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(os.path.join(ASSETS_PATH, 'Tripple_Laser.png'))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()


# Function to display score
def display_score(score):
    font = pygame.font.Font(None, 36)
    score_text = font.render("Score: {}".format(score), True, (255, 255, 0))  # Yellow color
    screen.blit(score_text, (WIDTH - 150, HEIGHT - 50))


#Options screen function
def show_options_screen():
    global game_difficulty
    options_running = True
    difficulty_levels = ["Easy", "Medium", "Hard"]
    selected_difficulty = "Medium"  # Default selection

    # Font settings
    font = pygame.font.Font(None, 48)
    title_font = pygame.font.Font(None, 74)

    # Calculate button positions and sizes
    button_width = 200
    button_height = 50
    button_margin = 20  # Space between buttons
    start_y = 150  # Starting Y position for the first button

    # Generate a list of Rects for each difficulty level
    difficulty_buttons = [pygame.Rect(WIDTH // 2 - button_width // 2, start_y + (button_height + button_margin) * i, button_width, button_height) for i in range(len(difficulty_levels))]

    # Return button setup
    return_rect = pygame.Rect(WIDTH - 220, HEIGHT - 70, 200, 50)  

    while options_running:
        screen.fill(CYAN)  # Background color
        mouse_pos = pygame.mouse.get_pos()

        # Draw the "Options" title
        options_title = title_font.render("Options", True, WHITE)
        screen.blit(options_title, (WIDTH // 2 - options_title.get_rect().width // 2, 50))

        # Draw and interact with the difficulty buttons
        for i, rect in enumerate(difficulty_buttons):
            level = difficulty_levels[i]
            pygame.draw.rect(screen, YELLOW if level == selected_difficulty else WHITE, rect)  # Draw button
            text = font.render(level, True, BLACK)  # Black text on the button
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

            if rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                selected_difficulty = level  # Update the selected difficulty
                game_difficulty = selected_difficulty

        # Draw the "Return to Main Menu" button
        pygame.draw.rect(screen, YELLOW if return_rect.collidepoint(mouse_pos) else WHITE, return_rect)  # Button shape
        return_text = font.render("Return", True, BLACK)  # Black text on the button
        return_text_rect = return_text.get_rect(center=return_rect.center)
        screen.blit(return_text, return_text_rect)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                options_running = False
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and return_rect.collidepoint(mouse_pos):
                options_running = False  # Exit options screen

        pygame.display.flip()
        clock.tick(FPS)

def show_highScore_screen():
    global game_difficulty
    options_running = True

    # Font settings
    font = pygame.font.Font(None, 48)
    title_font = pygame.font.Font(None, 74)

    # Return button setup
    return_rect = pygame.Rect(WIDTH - 220, HEIGHT - 70, 200, 50)  

    while options_running:
        screen.fill(CYAN)  # Background color
        mouse_pos = pygame.mouse.get_pos()

        # Draw the "Options" title
        options_title = title_font.render("Options", True, WHITE)
        screen.blit(options_title, (WIDTH // 2 - options_title.get_rect().width // 2, 50))

        # Display the top 3 scores dynamically using get_High_Score function
        high_scores = get_High_Score()
        text_positions = [(50, 250), (50, 350), (50, 450)]

        for i, score_data in enumerate(high_scores):
            text = f"{score_data[1]} - Score: {score_data[2]}, Time: {score_data[3]}"
            text_surface = font.render(text, True, BLACK)
            text_rect = text_surface.get_rect(topleft=text_positions[i])
            screen.blit(text_surface, text_rect)


        # Draw the "Return to Main Menu" button
        pygame.draw.rect(screen, YELLOW if return_rect.collidepoint(mouse_pos) else WHITE, return_rect)  # Button shape
        return_text = font.render("Return", True, BLACK)  # Black text on the button
        return_text_rect = return_text.get_rect(center=return_rect.center)
        screen.blit(return_text, return_text_rect)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                options_running = False
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and return_rect.collidepoint(mouse_pos):
                options_running = False  # Exit options screen

        pygame.display.flip()
        clock.tick(FPS)


# Main menu function
def main_menu():
    global clock  # Use the global clock variable
    global game_Flag

    font = pygame.font.Font(None, 42)
    title_text = font.render("Game Play", True, (255, 255, 0))  # Yellow color

    # Define colors for button states
    button_color = YELLOW
    button_hover_color = BLUE

    # Define button dimensions and positions
    button_width = 200
    button_height = 50
    gap = 20  # Vertical gap between buttons
    start_y = HEIGHT // 3  # Starting Y position of the first button

    # Define button rectangles
    single_player_rect = pygame.Rect(WIDTH // 2 - button_width // 2, start_y, button_width, button_height)
    multiplayer_rect = pygame.Rect(WIDTH // 2 - button_width // 2, start_y + button_height + gap, button_width, button_height)
    highScore_rect =  pygame.Rect(WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + gap), button_width, button_height)
    options_rect = pygame.Rect(WIDTH // 2 - button_width // 2, start_y + 3 * (button_height + gap), button_width, button_height)
    exit_rect = pygame.Rect(WIDTH // 2 - button_width // 2, start_y + 4 * (button_height + gap), button_width, button_height)

    menu_running = True
    while menu_running:
        screen.blit(main_menu_background_img, (0, 0))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))

        mouse_pos = pygame.mouse.get_pos()

        # Draw buttons and check for mouse hover to change color
        for rect in [single_player_rect, multiplayer_rect,  highScore_rect,options_rect, exit_rect]:
            pygame.draw.rect(screen, button_hover_color if rect.collidepoint(mouse_pos) else button_color, rect)
        
        # Draw button text
        screen.blit(font.render("Single Player", True, BLACK), (single_player_rect.x + 5, single_player_rect.y + 5))
        screen.blit(font.render("Multiplayer", True, BLACK), (multiplayer_rect.x + 5, multiplayer_rect.y + 5))
        screen.blit(font.render("High Score", True, BLACK), (highScore_rect.x + 5, highScore_rect.y + 5))
        screen.blit(font.render("Options", True, BLACK), (options_rect.x + 5, options_rect.y + 5))
        screen.blit(font.render("Exit", True, BLACK), (exit_rect.x + 5, exit_rect.y + 5))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                if single_player_rect.collidepoint(mouse_pos):
                    game_Flag = True
                    start_game(single_player=True)
                    menu_running = False
                elif multiplayer_rect.collidepoint(mouse_pos):
                    game_Flag = False
                    start_game(single_player=False)
                    menu_running = False
                elif highScore_rect.collidepoint(mouse_pos):
                    show_highScore_screen()
                elif options_rect.collidepoint(mouse_pos):
                    show_options_screen()  # Make sure this function returns to main_menu or handles closing properly
                elif exit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    quit()

        pygame.display.flip()
        clock.tick(FPS)

# Game over screen function
def game_over_screen():
    global clock  # Use the global clock variable
    global game_Flag    

    # Load the main menu background image
    game_over_background_img = pygame.image.load(os.path.join(ASSETS_PATH, 'main.png'))
    game_over_background_img = pygame.transform.scale(game_over_background_img, (WIDTH, HEIGHT))

    font = pygame.font.Font(None, 42)

    # Define button dimensions and positions
    button_width = 200
    button_height = 50
    button_gap = 30  # Gap between buttons

    # Define colors
    button_color = YELLOW
    button_hover_color = BLUE

    # Create rectangles for buttons
    restart_button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 - button_height // 2 - button_gap, button_width, button_height)
    exit_button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 - button_height // 2 + button_gap, button_width, button_height)

    game_over_running = True
    while game_over_running:
        screen.blit(game_over_background_img, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        # Draw "You Lost!" text
        game_over_text = font.render("You Lost!", True, (255, 0, 0))
        game_over_text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 3 * button_gap))
        screen.blit(game_over_text, game_over_text_rect)

        # Draw buttons
        pygame.draw.rect(screen, button_hover_color if restart_button_rect.collidepoint(mouse_pos) else button_color, restart_button_rect)
        pygame.draw.rect(screen, button_hover_color if exit_button_rect.collidepoint(mouse_pos) else button_color, exit_button_rect)

        # Draw button texts
        restart_text = font.render("Restart", True, BLACK)
        exit_text = font.render("Exit", True, BLACK)
        screen.blit(restart_text, (restart_button_rect.x + 20, restart_button_rect.y + 5))
        screen.blit(exit_text, (exit_button_rect.x + 50, exit_button_rect.y + 5))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button_rect.collidepoint(mouse_pos):
                    start_game(single_player=game_Flag)
                    game_over_running = False
                elif exit_button_rect.collidepoint(mouse_pos):
                    main_menu()  
                    game_over_running = False

        pygame.display.flip()
        clock.tick(FPS)

# Game loop
def start_game(single_player=True, difficulty='medium'):
    global score, all_sprites, enemies, bullets, second_enemies, players,game_difficulty,enemy_speed

    print("Game difficulty is = " ,game_difficulty)

    if(game_difficulty == "Medium"):
        enemy_speed = 1.0
    elif(game_difficulty == "Easy"):
        enemy_speed = 0.7
    else:
        enemy_speed = 1.5

    print("Enemy speed is = " ,enemy_speed)
    # Reset the score
    score = 0
    
    # Reset the score
    score = 0
    second_enemy_counter = 0

    # Set the threshold for second enemy appearance
    second_enemy_threshold = 200    

    # Initialize sprite groups
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    second_enemies = pygame.sprite.Group()

    # Add the power-up related variables 
    power_up_active = False
    power_up_start_time = 0

    # Clear all existing sprites from previous games
    all_sprites.empty()
    enemies.empty()
    bullets.empty()
    second_enemies.empty()
    players.empty()


    # Create player instances based on the game mode
    if single_player:
        player = Player(player_number=1)
        all_sprites.add(player)
        #players = pygame.sprite.Group()
        players.add(player)  
        all_sprites.add(player)
    else:
        player1 = Player(player_number=1, is_multiplayer=True)
        player2 = Player(player_number=2, is_multiplayer=True)
        players.add(player1)  # Add each player to the players group
        players.add(player2)
        all_sprites.add(player1)
        all_sprites.add(player2)

    # Keys pressed for movement and shooting
    keys = pygame.key.get_pressed()

    # In multiplayer: check and call shoot for both players separately
    if not single_player:
        # Check for Player 1 shooting
        if keys[pygame.K_SPACE]:
            player1.shoot()  

        # Check for Player 2 shooting
        if keys[pygame.K_LCTRL]:  
            player2.shoot()

    # Update players
    if single_player:
        player.update(keys)
    else:
        player1.update(keys)
        player2.update(keys)        

    # Create enemy instances
    for _ in range(9):
        enemy = Enemy(enemy_img, exploded_enemy_img)
        all_sprites.add(enemy)
        enemies.add(enemy)


    # Maximum number of active second enemies
    max_active_second_enemies = 3

    # Counter for second enemy appearance
    second_enemy_counter = 0

    # Clock for controlling the frame rate
    clock = pygame.time.Clock()

    # Game loop
    running = True
    while running:
        # Process events       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


    # Update the current state of the keyboard
        keys = pygame.key.get_pressed()

        # Update player sprites with keys
        for player in players:
            player.update(keys) # Update player position based on keys
#            player.try_shoot(keys) # Check if the player is trying to shoot


        # Update the sprites
        for sprite in all_sprites:
            if sprite not in players:
                sprite.update()

        # Draw screen
        screen.blit(background_img, (0, 0))


        # Draw the sprites 
        all_sprites.draw(screen)
        
        # Increment the second enemy counter when the first enemy is shot
        second_enemy_counter += 1

        # Check if the score exceeds the threshold for second enemy appearance
        if score >= second_enemy_threshold:
            # Check if it's time to spawn the second type of enemy
            if second_enemy_counter >= 20:
            # Count the currently active second enemies
                active_second_enemies = len(second_enemies.sprites())

            # Spawn a new second enemy only if the limit is not reached
            if active_second_enemies < max_active_second_enemies:
                second_enemy = SecondEnemy(meteo_enemy_img, exploded_meteo_enemy_img, speed_factor=1.3)
                all_sprites.add(second_enemy)
                second_enemies.add(second_enemy)

            # Spawning the power-up based on score and randomness
            if score >= 250 and random.random() < 0.005:  # Adjust 0.005 to control frequency
                powerup = PowerUp(powerup_img, 'tripple_laser')
                all_sprites.add(powerup)
                powerups.add(powerup)            


        # Check for collisions between bullets and enemies
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            # Play sound effect for enemy hit
            enemy_hit_sound.play()
            # Add scoring logic for the first enemy
            score += 10
            # Call the hit_by_bullet method for each hit enemy
            hit.hit_by_bullet()            
            # Create a new enemy when one is shot
            enemy = Enemy(enemy_img, exploded_enemy_img)
            all_sprites.add(enemy)
            enemies.add(enemy)

        # Check for collisions between bullets and second enemies
        second_enemy_hits = pygame.sprite.groupcollide(second_enemies, bullets, True, True)
        for hit in second_enemy_hits:
            # Play sound effect for enemy hit
            enemy_hit_sound.play()
            # Add scoring logic for the second enemy
            score += 20
            # Call the hit_by_bullet method for each hit second enemy
            hit.hit_by_bullet()
            # Create a new second enemy when one is shot
            second_enemy = SecondEnemy(meteo_enemy_img, exploded_meteo_enemy_img, speed_factor=1.3)
            all_sprites.add(second_enemy)
            second_enemies.add(second_enemy)

        if single_player:
            # Check for collision with power-ups
            collisions = pygame.sprite.spritecollide(player, powerups, True)  
            for collision in collisions:
                if collision.type == 'tripple_laser':
                    player.powerup = 'tripple_laser'
                    player.powerup_time = pygame.time.get_ticks()   # Capture the start time of the power-up effect
        else:
            # Check for collision with power-ups
            collisions1 = pygame.sprite.spritecollide(player1, powerups, True)  
            collisions2 = pygame.sprite.spritecollide(player2, powerups, True)
            collisions = collisions1,collisions2
            for i in collisions:
                for collision in i:
                    if collision.type == 'tripple_laser':
                        player1.powerup = 'tripple_laser'
                        player1.powerup_time = pygame.time.get_ticks()   # Capture the start time of the power-up effect

                        player2.powerup = 'tripple_laser'
                        player2.powerup_time = pygame.time.get_ticks()   # Capture the start time of the power-up effect



        # Implement the Power-up Timer Logic
        if player.powerup == 'tripple_laser':
            if pygame.time.get_ticks() - player.powerup_time > 10000:  # 10 seconds duration
                player.powerup = None  # Revert to normal bullets

             


        # Check for collisions between the player and the first type of enemies
        if single_player:
            # Single-player collision detection
            player_hits = pygame.sprite.spritecollide(player, enemies, True)
            if player_hits:
                insert_Values("Player",score,str(current_Time.strftime("%Y-%m-%d %H:%M:%S")))
                # Play sound effect for player hit
                player_hit_sound.play()
                game_over_screen()
                running = False
        else:
            # Multiplayer collision detection
            player1_hits = pygame.sprite.spritecollide(player1, enemies, True)
            player2_hits = pygame.sprite.spritecollide(player2, enemies, True)
            if player1_hits or player2_hits:
                # Enters the 
                insert_Values("Player",score,str(current_Time.strftime("%Y-%m-%d %H:%M:%S")))
                # Play sound effect for player hit
                player_hit_sound.play()
                game_over_screen()
                running = False

        # Check for collisions between the player and the second type of enemies
        if single_player:
            # Single-player collision detection
            player_hits = pygame.sprite.spritecollide(player, second_enemies, True)
            if player_hits:
                insert_Values("Player",score,str(current_Time.strftime("%Y-%m-%d %H:%M:%S")))
                # Play sound effect for player hit
                player_hit_sound.play() 
                game_over_screen()
                running = False
        else:
            # Multiplayer collision detection
            player1_hits = pygame.sprite.spritecollide(player1, second_enemies, True)
            player2_hits = pygame.sprite.spritecollide(player2, second_enemies, True)
            if player1_hits or player2_hits:
                insert_Values("Player",score,str(current_Time.strftime("%Y-%m-%d %H:%M:%S"))) 
                # Play sound effect for player hit
                player_hit_sound.play()               
                game_over_screen()
                running = False

        
        # Display score
        display_score(score)

        # Refresh the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)
    
    # Quit Pygame when the game loop exits
    pygame.quit()

# Placeholder function for showing options
def show_options():
    print("Options function placeholder")

# Run the main menu
main_menu()