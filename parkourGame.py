import pygame
import random
import sys
import os

pygame.init()

clock = pygame.time.Clock()

screenWidth = 800
screenHeight = 600
Score = 0
Frames = 0


class platform(object):
    def __init__(self, x, y, height, width, position):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.position = position
        self.space = 20

    def isTouching(self, x, y, height, width):
        isTouch = collidingChecker(x, y, height, width, self.x, self.y, self.height, self.width)
        return isTouch

    def colliding(self, player, x, y, height, width):
        isTouch = self.isTouching(x, y, height, width)
        if isTouch:
            player.canFall = False
            player.y = self.y - height

        else:
            player.canFall = True

    def displayPlatform(self):
        pygame.draw.rect(gameDisplay, red, (self.x, self.y, self.width, self.height))

    def movePlatform(self, val):
        self.x -= val

    def changePosition(self, x, y, height, width, space):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.space = space


def collidingChecker(playerX, playerY, playerHeight, playerWidth, platformX, platformY, platformHeight, platformWidth):
    if platformX < playerX < platformX + platformWidth or platformX < playerX + playerWidth < platformX + platformWidth:
        if platformY < playerY < platformY + platformHeight or platformY < playerY + playerHeight < platformY + platformHeight:
            return True
        else:
            return False
    else:
        return False


def sideCollisionChecker(playerX, playerY, playerWidth, platformX, platformY, platformWidth):
    if playerY > platformY:
        if platformX + platformWidth >= playerX + playerWidth >= platformX:
            return True
        else:
            return False
    else:
        return False


white = (255, 255, 255)
black = (0, 0, 0)

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

gameDisplay = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Parkour Box')


def moveScreen(value):
    Platform1.movePlatform(value)
    Platform2.movePlatform(value)
    Platform3.movePlatform(value)
    powerUp.movePowerUp(value)


def regeneratePlatforms(platform_1, platform_2, platform_3):
    global Score
    platforms = [platform_1, platform_2, platform_3]

    for floor in platforms:
        if floor.x + floor.width < -5:
            Score += 1
            lastPlatform = 350
            if floor.position == 1:
                lastPlatform = Platform3
            elif floor.position == 2:
                lastPlatform = Platform1
            elif floor.position == 3:
                lastPlatform = Platform2

            maxWidth = 3 * Score + 150
            newSpace = random.randint(70, maxWidth)
            newX = lastPlatform.x + lastPlatform.width + newSpace
            newY = random.randint(300, 550)
            newHeight = screenHeight - newY
            newWidth = random.randint(100, 800)
            floor.changePosition(newX, newY, newHeight, newWidth, newSpace)


def collider(x, y, height, width, player):
    one = Platform1.isTouching(x, y, height, width)
    two = Platform2.isTouching(x, y, height, width)
    three = Platform3.isTouching(x, y, height, width)
    colliding = [one, two, three]

    if True in colliding:
        player.canFall = False
        player.canJump = True
        platformY = 1
        player.Y_Change = 0
        findPlatform = colliding.index(True)
        if findPlatform == 0:
            platformY = Platform1.y
        elif findPlatform == 1:
            platformY = Platform2.y
        elif findPlatform == 2:
            platformY = Platform3.y

        player.y = platformY - height
    else:
        player.canFall = True
        player.canJump = False


def findSpeed():
    global speed
    speed = 0.2 * Score + 1


def text_objects(text, font):
    textSurface = font.render(text, True, white)
    return textSurface, textSurface.get_rect()


def message_display(text, X, Y, textSize=50):
    largeText = pygame.font.Font('freesansbold.ttf', textSize)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = ((X), (Y))
    gameDisplay.blit(TextSurf, TextRect)


class PowerUp(object):
    def __init__(self):
        self.x = 800
        self.y = 300
        self.width = 50
        self.height = 50
        self.inGame = True
        self.reset = False
        self.powerupType = ""
        self.powerList = ["Big", "Jump", "Small", "Lower", "Wide", "Tall"]
        self.setup()

    def determineIfInGame(self):
        if not self.inGame:
            rand = random.randint(0, 100)
            rnd = random.randint(0, 100)
            if rand == rnd:
                self.inGame = True
                self.setup()

        if self.x + self.width < 0:
            self.inGame = False

    def drawPowerUp(self):
        if self.inGame:
            pygame.draw.rect(gameDisplay, blue, (self.x, self.y, self.width, self.height))
            message_display(self.powerupType, self.x, self.y, 20)

    def setup(self):
        self.x = random.randint(900, 1600)
        self.y = random.randint(50, 650)
        rand = random.randint(0, len(self.powerList) - 1)
        self.powerupType = self.powerList[rand]
        self.inGame = True

    def movePowerUp(self, value):
        self.x -= value

    def findIfColliding(self):
        one = Platform1.isTouching(self.x, self.y, self.height, self.width)
        two = Platform2.isTouching(self.x, self.y, self.height, self.width)
        three = Platform3.isTouching(self.x, self.y, self.height, self.width)
        colliding = [one, two, three]

        if True in colliding:
            self.setup()

    def powerUpRules(self):
        self.determineIfInGame()
        self.findIfColliding()
        self.drawPowerUp()


class Player(object):
    def __init__(self):
        self.x = 60
        self.y = 340
        self.width = 50
        self.height = 50
        self.canFall = True
        self.canJump = False
        self.Alive = True
        self.Gravity = 1
        self.Y_Change = 0
        self.jumpHeight = 25
        self.score = 0
        self.playerHeightScore = 0
        self.heightPercent = 0
        self.playerPowerUpAlive = [False, False, False]

    def displayPlayer(self):
        if self.Alive:
            pygame.draw.rect(gameDisplay, green, (self.x, self.y, self.width, self.height))

    def changePosition(self, y_change):
        self.y -= y_change

    def calculateGravity(self):
        if self.canFall:
            self.Y_Change -= self.Gravity

    def goUp(self):
        if self.canJump:
            self.Y_Change += self.jumpHeight

    def changeFall(self, val):
        self.Y_Change = 0
        self.canFall = val

    def limitPlayer(self):
        if self.y <= 0:
            self.y = 0
            self.Y_Change = 0

    def findIfDead(self):
        if self.y > screenHeight:
            self.Alive = False

        if self.x <= 0 - self.width - 100:
            self.Alive = False

    def addGlobalScore(self):
        global Score
        if self.Alive:
            self.score = Score

        return self.score

    def canPlayerJump(self, platformX, platformWidth, platformY):
        wiggleRoom = 50
        if platformX < self.x < platformX + platformWidth or platformX < self.x + self.width < platformX + platformWidth:
            if platformY - self.height - wiggleRoom < self.y:
                return True
            else:
                return False
        else:
            return True

    def stopPlayerJump(self):
        x = playerBox.canPlayerJump(Platform1.x, Platform1.width, Platform1.y)
        y = playerBox.canPlayerJump(Platform2.x, Platform2.width, Platform2.y)
        z = playerBox.canPlayerJump(Platform3.x, Platform3.width, Platform3.y)
        list = [x, y, z]
        if False in list:
            self.canJump = False
        else:
            self.canJump = True

    def playerRules(self):
        self.calculateGravity()

        self.changePosition(playerBox.Y_Change)
        self.findIfDead()
        self.sideCollider()
        collider(playerBox.x, playerBox.y, playerBox.height, playerBox.width, playerBox)

        self.stopPlayerJump()

        self.limitPlayer()
        self.findCollidePowerup()
        self.displayPlayer()

        self.HeightAverage()
        playerScore = self.addGlobalScore()

        return playerScore

    def HeightAverage(self):
        global Frames, screenHeight
        self.playerHeightScore += self.y
        x = self.playerHeightScore / Frames
        self.heightPercent = x / screenHeight

    def sideCollider(self):
        o = sideCollisionChecker(self.x, self.y, self.width, Platform1.x, Platform1.y, Platform1.width)
        t = sideCollisionChecker(self.x, self.y, self.width, Platform2.x, Platform2.y, Platform2.width)
        r = sideCollisionChecker(self.x, self.y, self.width, Platform3.x, Platform3.y, Platform3.width)
        sideCollision = [o, t, r]

        platformX = 0
        if True in sideCollision:
            findPlatform = sideCollision.index(True)
            if findPlatform == 0:
                platformX = Platform1.x
            elif findPlatform == 1:
                platformX = Platform2.x
            elif findPlatform == 2:
                platformX = Platform3.x
            self.x = platformX - self.width - 5

        else:
            if self.x < 60:
                self.x += 1

            elif self.x > 60:
                self.x = 60

    def findCollidePowerup(self):
        # self.playerPowerUpAlive = [Alive, Dead, TempDead]
        if not powerUp.inGame:
            self.playerPowerUpAlive = [False, True, False]

        if powerUp.inGame:
            self.playerPowerUpAlive[0] = True
            self.playerPowerUpAlive[1] = False

        collide = collidingChecker(self.x, self.y, self.height, self.width, powerUp.x, powerUp.y, powerUp.height,
                                   powerUp.width)

        if collide and not self.playerPowerUpAlive[2]:
            self.performPowerUp()
            self.playerPowerUpAlive[2] = True

    def performPowerUp(self):
        power = powerUp.powerupType
        # ["Big", "Jump", "Small", "Lower", "Wide", "Tall"]
        if power == "Big":
            self.height += 5
            self.width += 5
        elif power == "Small":
            self.height -= 5
            self.width -= 5
        elif power == "Jump":
            self.jumpHeight += 2
        elif power == "Lower":
            self.jumpHeight -= 2
        elif power == "Wide":
            self.width += 5
        elif power == "Tall":
            self.height += 5
        else:
            print("Error PowerUp Not found " + powerUp.powerupType)
            sys.exit()


run = True
speed = 0.7

powerUp = PowerUp()
playerBox = Player()

Platform1 = platform(50, 500, 100, 300, 1)
Platform2 = platform(370, 400, 200, 300, 2)
Platform3 = platform(690, 500, 100, 300, 3)

while run:
    clock.tick(45)
    if playerBox.Alive:
        Frames += 1
        gameDisplay.fill(black)
        findSpeed()
        moveScreen(speed)
        regeneratePlatforms(Platform1, Platform2, Platform3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                    playerBox.goUp()

        powerUp.powerUpRules()
        playerScore = playerBox.playerRules()

        Platform1.displayPlatform()
        Platform2.displayPlatform()
        Platform3.displayPlatform()

        message_display("Height Score: " + str(round(playerBox.heightPercent * 100, 1)) + "%", 250, 50)
        message_display("Score: " + str(playerScore), 650, 50)
        pygame.display.update()

    else:
        playerScore = playerBox.addGlobalScore()
        gameDisplay.fill(black)
        message_display("Game Over", screenWidth // 2, screenHeight // 2)
        message_display("Final Score: " + str(playerScore), screenWidth // 2, screenHeight // 2 + 100)
        message_display("Press any key to exit", screenWidth // 2, screenHeight // 2 + 200)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                pygame.quit()
                sys.exit()

        pygame.display.update()
