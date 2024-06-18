import random
import sys  # To exit the program
import pygame
from pygame.locals import *

# Global variables for game
fps = 32
screenwidth = 600
screenheight = 480
screen = pygame.display.set_mode((screenwidth, screenheight))

groundy = screenheight * 0.8
game_sprites = {}
game_sounds = {}
player = "Gallery/images/bird.png"
background = "Gallery/images/background.jpg"
pipes = "Gallery/images/pipe.png"
base = "Gallery/images/base.jfif"
level_buttons = ["Gallery/images/l1.png", "Gallery/images/l2.png", "Gallery/images/l3.png"]
message = "Gallery/images/message.png"

def showMenu():
    while True:
        screen.blit(game_sprites['background'], (0, 0))
        screen.blit(game_sprites['message'], (110 ,40))
        
        for i, button in enumerate(game_sprites['buttons']):
            screen.blit(button, (screenwidth // 2 - button.get_width() // 2, 150 + i * 100))

        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            
            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos
                for i, button in enumerate(game_sprites['buttons']):
                    if (screenwidth // 2 - button.get_width() // 2 < x < screenwidth // 2 + button.get_width() // 2) and (150 + i * 100 < y < 150 + i * 100 + button.get_height()):
                        mainGame(level=i+1)

def mainGame(level):
    score = 0
    playerx = int(screenwidth / 5)
    playery = int(screenheight / 2)
    ground = 0

    # Adjust difficulty based on level
    if level == 1:
        pipeVelx = -4  
        offset = screenheight / 3
    elif level == 2:
        pipeVelx = -6
        offset = screenheight / 4
    elif level == 3:
        pipeVelx = -7
        offset = screenheight / 5

    newPipe1 = getRandomPipe(offset)
    newPipe2 = getRandomPipe(offset)

    upperpipes = [
        {"x": screenwidth + 200, "y": newPipe1[0]['y']},
        {"x": screenwidth + 200 + (screenwidth / 2), "y": newPipe2[0]['y']}
    ]

    lowerpipes = [
        {"x": screenwidth + 200, "y": newPipe1[1]['y']},
        {"x": screenwidth + 200 + (screenwidth / 2), "y": newPipe2[1]['y']}
    ]

    playerVely = -9
    playerMaxVel = 10
    playerMinVel = -8
    playerAccY = 1

    playerFlapAccv = -8  # velocity while flapping
    playerFlapped = False  # True only when bird is flapping

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVely = playerFlapAccv
                    playerFlapped = True

        crashTest = iscollide(playerx, playery, upperpipes, lowerpipes)  # Return true if player is crashed
        if crashTest:
            return

        playerMidPos = playerx + game_sprites['player'].get_width() / 2
        for pipe in upperpipes:
            pipeMidPos = pipe['x'] + game_sprites['pipe'][0].get_width() / 2
            if pipeMidPos -4 <= playerMidPos < pipeMidPos + 4 and level ==3 :
                score += 1
                print(f"Your score is {score}")
                game_sounds['hit'].play()
            elif pipeMidPos -2  <= playerMidPos < pipeMidPos + 4 and level == 2:
                score += 1
                print(f"Your score is {score}")
                game_sounds['hit'].play()
            elif pipeMidPos  <= playerMidPos < pipeMidPos + 4:
                score += 1
                game_sounds['hit'].play()
                print(f"Your score is {score}")

        if playerVely < playerMaxVel and not playerFlapped:
            playerVely += playerAccY

        if playerFlapped:
            playerFlapped = False
        playerHeight = game_sprites['player'].get_height()
        playery = playery + min(playerVely, groundy - playery - playerHeight)

        for upperpipe, lowerpipe in zip(upperpipes, lowerpipes):
            upperpipe['x'] += pipeVelx
            lowerpipe['x'] += pipeVelx

        if 0 < upperpipes[0]['x'] < 5:
            newpipe = getRandomPipe(offset)
            upperpipes.append(newpipe[0])
            lowerpipes.append(newpipe[1])

        if upperpipes[0]['x'] < -game_sprites['pipe'][0].get_width():
            upperpipes.pop(0)
            lowerpipes.pop(0)

        screen.blit(game_sprites['background'], (0, 0))
        for upperpipe, lowerpipe in zip(upperpipes, lowerpipes):
            screen.blit(game_sprites['pipe'][0], (upperpipe['x'], upperpipe['y']))
            screen.blit(game_sprites['pipe'][1], (lowerpipe['x'], lowerpipe['y']))

        screen.blit(game_sprites['base'], (ground, groundy))
        screen.blit(game_sprites['player'], (playerx, playery))

        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += game_sprites['numbers'][digit].get_width()
        xoffset = (screenwidth - width) / 2

        for digit in myDigits:
            screen.blit(game_sprites['numbers'][digit], (xoffset, screenheight * 0.12))
            xoffset += game_sprites['numbers'][digit].get_width()
        pygame.display.update()
        fpsclock.tick(fps)

def iscollide(playerx, playery, upperpipes, lowerpipes):
    playerHeight = game_sprites['player'].get_height()
    playerWidth = game_sprites['player'].get_width()
    
    if playery + playerHeight >= groundy:
        game_sounds['die'].play()
        return True
    
    if playery < 0:
        game_sounds['die'].play()
        return True
    
    for pipe in upperpipes:
        pipeHeight = game_sprites['pipe'][0].get_height()
        if playery < pipeHeight + pipe['y'] and playerx + playerWidth > pipe['x'] and playerx < pipe['x'] + game_sprites['pipe'][0].get_width():
            game_sounds['die'].play()
            return True
    
    for pipe in lowerpipes:
        if playery + playerHeight > pipe['y'] and playerx + playerWidth > pipe['x'] and playerx < pipe['x'] + game_sprites['pipe'][0].get_width():
            game_sounds['die'].play()
            return True
    
    return False

def getRandomPipe(offset):
    pipeHeight = game_sprites['pipe'][0].get_height()
    # offset = screenheight / 3
    y2 = offset + random.randrange(0, int(screenheight - game_sprites['base'].get_height() - 1.2 * offset))
    pipex = screenwidth + 10
    y1 = pipeHeight - y2 + offset

    pipe = [
        {'x': pipex, 'y': -y1},
        {'x': pipex, 'y': y2}
    ]
    return pipe

if __name__ == "__main__":
    pygame.init()
    fpsclock = pygame.time.Clock()
    pygame.display.set_caption("Flappy Bird by Abhay")

    game_sprites['numbers'] = (
        pygame.image.load("Gallery/images/0.png").convert_alpha(),
        pygame.image.load("Gallery/images/1.png").convert_alpha(),
        pygame.image.load("Gallery/images/2.png").convert_alpha(),
        pygame.image.load("Gallery/images/3.png").convert_alpha(),
        pygame.image.load("Gallery/images/4.png").convert_alpha(),
        pygame.image.load("Gallery/images/5.png").convert_alpha(),
        pygame.image.load("Gallery/images/6.png").convert_alpha(),
        pygame.image.load("Gallery/images/7.png").convert_alpha(),
        pygame.image.load("Gallery/images/8.png").convert_alpha(),
        pygame.image.load("Gallery/images/9.png").convert_alpha(),
    )
    game_sprites['message'] = pygame.image.load("Gallery/images/message.png").convert_alpha()   

    game_sprites['pipe'] = (
        pygame.transform.rotate(pygame.image.load(pipes).convert_alpha(), 180),
        pygame.image.load(pipes).convert_alpha()
    )

    game_sounds['hit'] = pygame.mixer.Sound("Gallery/audio/hit.mp3")
    game_sounds['die'] = pygame.mixer.Sound("Gallery/audio/die.mp3")

    game_sprites['background'] = pygame.image.load(background).convert()
    game_sprites['player'] = pygame.image.load(player).convert_alpha()
    game_sprites['base'] = pygame.image.load(base).convert_alpha()

    game_sprites['buttons'] = [pygame.image.load(btn).convert_alpha() for btn in level_buttons]

    while True:
        showMenu()
