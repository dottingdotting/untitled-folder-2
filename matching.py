import pygame
import random
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize mixer for audio
# Initialize clock
clock = pygame.time.Clock()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1400, 1200
GRID_ROWS, GRID_COLS = 4, 5
CARD_WIDTH, CARD_HEIGHT = 190, 186
HOVER_SCALE = 1.25  # Scale factor when hovering
MARGIN = 10
FPS = 60
FONT_SIZE = 20
SCORE_INCREMENT = 10

# Colors
BLACK = (64, 224, 208)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (169, 169, 169)

# Path to the folder containing card sprites
SPRITE_FOLDER = "card_sprites"
MUSIC_FOLDER = "audio"  # Folder for audio files

# Audio files
BACKGROUND_MUSIC = os.path.join("audio", "background_music.mp3")
SELECT_SOUND = os.path.join("audio", "card_select.mp3")
MATCH_SOUND = os.path.join("audio", "card_match.mp3")

# Load sounds
#pygame.mixer.music.load(BACKGROUND_MUSIC)  # Background music
#card_select_sound = pygame.mixer.Sound(SELECT_SOUND)  # Card selection sound
#card_match_sound = pygame.mixer.Sound(MATCH_SOUND)  # Card match sound
pygame.mixer.music.load("/Users/davidlopez/Documents/projects/card_match_demo/background_music.mp3")
card_select_sound = pygame.mixer.Sound("/Users/davidlopez/Documents/projects/card_match_demo/card_select.mp3")
card_match_sound = pygame.mixer.Sound("/Users/davidlopez/Documents/projects/card_match_demo/card_match.mp3")


# Sprites dictionary (filenames must match these keys)
SPRITES = {
    "closed": "closed_card.png",
    "circle_red": "circle_red.png",
    "circle_blue": "circle_blue.png",
    "square_green": "square_green.png",
    "triangle_blue": "triangle_blue.png",
    "rectangle_orange": "rectangle_orange.png",
    "pentagon_purple": "pentagon_purple.png",
    "pentagon_pink": "pentagon_pink.png",
    "hexagon_cyan": "hexagon_cyan.png",
    "hexagon_navy": "hexagon_navy.png",
    "half_circle_orange": "half_circle_orange.png",
}

# Shapes with corresponding sprite keys
# Dynamically generate the SHAPES list to match the number of cards
unique_shapes = [
    "circle_red", "circle_blue",
    "square_green",
    "triangle_blue",
    "rectangle_orange",
    "pentagon_purple", "pentagon_pink",
    "hexagon_cyan", "hexagon_navy",
    "half_circle_orange"
]
# Ensure the number of shapes matches half the number of cards
SHAPES = unique_shapes[:GRID_ROWS * GRID_COLS // 2] * 2

# Shuffle the shapes
random.shuffle(SHAPES)

# Shuffle the cards
random.shuffle(SHAPES)

# Calculate grid dimensions
GRID_WIDTH = GRID_COLS * CARD_WIDTH + (GRID_COLS - 1) * MARGIN
GRID_HEIGHT = GRID_ROWS * CARD_HEIGHT + (GRID_ROWS - 1) * MARGIN
GRID_START_X = (SCREEN_WIDTH - GRID_WIDTH) // 2
GRID_START_Y = (SCREEN_HEIGHT - GRID_HEIGHT) // 2

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Matching Game")

# Load and scale sprites
def load_sprites(scale_factor=1):
    sprites = {}
    for key, filename in SPRITES.items():
        path = os.path.join(SPRITE_FOLDER, filename)
        sprite = pygame.image.load(path).convert_alpha()  # Load sprite with transparency
        sprite = pygame.transform.scale(sprite, (int(CARD_WIDTH * scale_factor), int(CARD_HEIGHT * scale_factor)))
        sprites[key] = sprite
    return sprites

# Initial scaling
scale_factor = 1  # Adjust scale factor if needed
loaded_sprites = load_sprites(scale_factor)

# Card class
class Card:
    def __init__(self, x, y, shape):
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.shape = shape
        self.flipped = False
        self.matched = False
        self.animation_progress = 0  # For flip animation
        self.hovered = False
        self.falling = False  # To animate falling

    def draw(self):
        if self.falling:
            # Falling animation
            self.rect.y += 10  # Move downward
            if self.rect.top > SCREEN_HEIGHT:
                return

        scale = HOVER_SCALE if self.hovered else 1
        scaled_width = int(CARD_WIDTH * scale)
        scaled_height = int(CARD_HEIGHT * scale)
        center_x, center_y = self.rect.center
        draw_rect = pygame.Rect(
            center_x - scaled_width // 2,
            center_y - scaled_height // 2,
            scaled_width,
            scaled_height
        )

        if self.animation_progress < 1:
            # Draw flipping animation
            flip_scale = 1 - abs(0.5 - self.animation_progress) * 2
            flip_width = int(CARD_WIDTH * flip_scale)
            flip_rect = pygame.Rect(center_x - flip_width // 2, center_y - scaled_height // 2, flip_width, scaled_height)
            if self.animation_progress < 0.5:
                self.draw_back(flip_rect)
            else:
                self.draw_shape(flip_rect, self.shape)
        else:
            sprite_key = self.shape if self.flipped else "closed"
            sprite = loaded_sprites[sprite_key]
            sprite = pygame.transform.scale(sprite, (scaled_width, scaled_height))  # Adjust size for hover effect
            screen.blit(sprite, draw_rect.topleft)

    def draw_back(self, rect):
        sprite = loaded_sprites["closed"]
        sprite = pygame.transform.scale(sprite, (rect.width, rect.height))
        screen.blit(sprite, rect.topleft)

    def draw_shape(self, rect, shape):
        sprite = loaded_sprites[shape]
        sprite = pygame.transform.scale(sprite, (rect.width, rect.height))
        screen.blit(sprite, rect.topleft)

    def update(self, dt, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.animation_progress < 1:
            self.animation_progress += dt * 2
        elif self.flipped:
            self.animation_progress = 1

# Helper function to create a new game
def create_new_game():
    pygame.mixer.music.play(-1)  # Play background music in a loop

    global cards, flipped_cards, score, game_over
    score = 0
    game_over = False
    flipped_cards = []
    #random.shuffle(SHAPES)
    cards = []
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x = GRID_START_X + col * (CARD_WIDTH + MARGIN)
            y = GRID_START_Y + row * (CARD_HEIGHT + MARGIN)
            cards.append(Card(x, y, SHAPES.pop()))

# Game variables
create_new_game()
font = pygame.font.Font("PixelOperatorMono8.ttf", 20)
show_time = 0  # Timer for showing non-matching cards

# Main game loop
running = True
while running:
    dt = clock.tick(FPS) / 1000  # Time delta in seconds
    mouse_pos = pygame.mouse.get_pos()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_over:
                # Check if retry button is clicked
                retry_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)
                if retry_rect.collidepoint(event.pos):
                    create_new_game()
            elif len(flipped_cards) < 2:
                for card in cards:
                    if card.rect.collidepoint(event.pos) and not card.flipped and not card.matched:
                        pygame.mixer.Sound.play(card_select_sound)  # Play card selection sound
                        card.flipped = True
                        card.animation_progress = 0
                        flipped_cards.append(card)
                        break

    # Game logic
    if len(flipped_cards) == 2 and show_time == 0:
        show_time = pygame.time.get_ticks()  # Start the timer

    if show_time > 0 and pygame.time.get_ticks() - show_time > 1000:  # Show cards for 1 second
        card1, card2 = flipped_cards
        if card1.shape == card2.shape:
            pygame.mixer.Sound.play(card_match_sound)  # Play match sound
            card1.matched = True
            card2.matched = True
            card1.falling = True
            card2.falling = True
            score += SCORE_INCREMENT
        else:
            card1.flipped = False
            card2.flipped = False
        flipped_cards = []
        show_time = 0

    # Check if game is over
    if all(card.matched for card in cards) and not game_over:
        game_over = True

    # Update cards
    for card in cards:
        card.update(dt, mouse_pos)

    # Draw everything
    screen.fill(BLACK)
    for card in cards:
        card.draw()

    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 20))

    # Draw game over and retry button
    if game_over:
        game_over_text = font.render("Game Over!", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        retry_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)
        pygame.draw.rect(screen, GRAY, retry_rect)
        retry_text = font.render("EXIT", True, BLACK)
        screen.blit(retry_text, (retry_rect.centerx - retry_text.get_width() // 2, retry_rect.centery - retry_text.get_height() // 2))

    pygame.display.flip()

pygame.quit()