import random  # For generating random numbers
import sys     # For system-specific parameters and functions (e.g., sys.exit)
import pygame  # Pygame library for game development
from pygame.locals import *  # Basic Pygame imports

# Global variables
FPS = 32  # Frames per second, controls the game's speed
SCREENWIDTH = 289  # Width of the game screen
SCREENHEIGHT = 511  # Height of the game screen
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))  # Initialize the game window
GROUNDY = SCREENHEIGHT * 0.8  # Y-coordinate for the ground level
GAME_SPRITES = {}  # Dictionary to store game images (sprites)
GAME_SOUNDS = {}  # Dictionary to store game sounds

# File paths for the game assets
PLAYER = 'gallery/sprites/bird.png'  # Path for the player image (bird)
BACKGROUND = 'gallery/sprites/background.png'  # Path for the background image
PIPE = 'gallery/sprites/pipe.png'  # Path for the pipe image


def welcomeScreen():
    """
    Shows the welcome screen until a key is pressed to start the game.
    """
    playerx = int(SCREENWIDTH / 5)  # Initial x-position of the player
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height()) / 2)  # Center the player vertically
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width()) / 2)  # Center the message horizontally
    messagey = int(SCREENHEIGHT * 0.13)  # Y-position for the message (slightly below the top)
    basex = 0  # Initial x-position for the base

    while True:
        # Event handling loop
        for event in pygame.event.get():
            # If the user clicks the close button or presses ESC, exit the game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # Start the game if the user presses the spacebar or up arrow key
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return  # Start the game
                
            else:
                # Blit the background, player, and message to the screen
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))    
                SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))    
                SCREEN.blit(GAME_SPRITES['message'], (messagex, messagey))    
                pygame.display.update()  # Update the display
                FPSCLOCK.tick(FPS)  # Control the frame rate


def mainGame():
    """
    This function contains the main game loop.
    """
    score = 0  # Initial score
    playerx = int(SCREENWIDTH / 5)  # X-position of the player
    playery = int(SCREENHEIGHT / 2)  # Y-position of the player (centered vertically)
    basex = 0  # Initial x-position for the base

    # Create two new pipes for the game
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # Lists to store upper and lower pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},  # Upper pipe 1
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']}  # Upper pipe 2
    ]
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},  # Lower pipe 1
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']}  # Lower pipe 2
    ]

    pipeVelX = -4  # Speed at which pipes move to the left

    playerVelY = -9  # Initial velocity of the player in the Y direction
    playerMaxVelY = 10  # Maximum downward velocity
    playerMinVelY = -8  # Maximum upward velocity
    playerAccY = 1  # Player acceleration (gravity effect)

    playerFlapAccv = -8  # Velocity when the player flaps
    playerFlapped = False  # True only when the player flaps

    while True:
        # Event handling
        for event in pygame.event.get():
            # Exit the game on quit or ESC key press
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            # Make the player flap if the spacebar or up arrow key is pressed
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()

        # Check if the player collides with any pipes or the ground
        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)
        if crashTest:
            return  # End the game if there's a collision

        # Check for scoring
        playerMidPos = playerx + GAME_SPRITES['player'].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1  # Increment score
                print(f"Your score is {score}")
                GAME_SOUNDS['point'].play()

        # Apply gravity
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False

        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

        # Move pipes to the left
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Add a new pipe when the first pipe moves off the screen
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # Remove pipes that have moved off the screen
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # Blit (draw) the sprites to the screen
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))

        # Display the score on the screen
        myDigits = [int(x) for x in list(str(score))]  # Convert score to individual digits
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()  # Calculate the width needed to display the score
        Xoffset = (SCREENWIDTH - width) / 2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()

        pygame.display.update()  # Update the display
        FPSCLOCK.tick(FPS)  # Control the frame rate


def isCollide(playerx, playery, upperPipes, lowerPipes):
    """
    Checks for collisions between the player and pipes or the ground.
    """
    if playery > GROUNDY - 25 or playery < 0:  # Collision with ground or ceiling
        GAME_SOUNDS['hit'].play()
        print("Collision with ground or ceiling")
        return True

    playerRect = pygame.Rect(playerx, playery, GAME_SPRITES['player'].get_width(), GAME_SPRITES['player'].get_height())

    for pipe in upperPipes:
        pipeRect = pygame.Rect(pipe['x'], pipe['y'], GAME_SPRITES['pipe'][0].get_width(), GAME_SPRITES['pipe'][0].get_height())
        if playerRect.colliderect(pipeRect):  # Collision with upper pipe
            GAME_SOUNDS['hit'].play()
            print(f"Collision with upper pipe at ({pipe['x']}, {pipe['y']})")
            return True

    for pipe in lowerPipes:
        pipeRect = pygame.Rect(pipe['x'], pipe['y'], GAME_SPRITES['pipe'][1].get_width(), GAME_SPRITES['pipe'][1].get_height())
        if playerRect.colliderect(pipeRect):  # Collision with lower pipe
            GAME_SOUNDS['hit'].play()
            print(f"Collision with lower pipe at ({pipe['x']}, {pipe['y']})")
            return True

    return False


def getRandomPipe():
    """
    Returns a random pair of pipes (upper and lower) for the game.
    """
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT / 3  # Vertical distance between pipes
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2 * offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset  # Calculate y-position for the upper pipe

    pipe = [
        {'x': pipeX, 'y': -y1},  # Upper pipe
        {'x': pipeX, 'y': y2}    # Lower pipe
    ]
    return pipe


# Main block of the game
if __name__ == "__main__":
    # Initialize the Pygame module
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird by Pythonist')

    # Load game images (sprites)
    GAME_SPRITES['numbers'] = (
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha(),
    )
    GAME_SPRITES['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load('gallery/sprites/base.png').convert_alpha()
    GAME_SPRITES['pipe'] = (
        pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
        pygame.image.load(PIPE).convert_alpha(),
    )

    # Load game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')

    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()

    while True:
        welcomeScreen()  # Show the welcome screen
        mainGame()  # Start the main game
