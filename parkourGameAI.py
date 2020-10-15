import pygame
import random
import sys
import os
import neat
import math

pygame.init()

clock = pygame.time.Clock()

screenWidth = 800
screenHeight = 600
Score = 0
Frames = 0
Gen = 0


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
    if playerY > platformY + 10:
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


def moveScreen(value, Platform1, Platform2, Platform3, powerUp):
    Platform1.movePlatform(value)
    Platform2.movePlatform(value)
    Platform3.movePlatform(value)
    powerUp.movePowerUp(value)


def regeneratePlatforms(Platform1, Platform2, Platform3, players, Score):
    platforms = [Platform1, Platform2, Platform3]

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
            for player in players:
                player.fitness += 5
                player.fitness += player.heightPercent

    return Score


def collider(x, y, height, width, player, Platform1, Platform2, Platform3):
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


def findSpeed(Score):
    speed = 0.2 * Score + 1
    return speed


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
        self.powerList = ("Big", "Jump", "Small", "Lower")
        self.setup()

    def determineIfInGame(self):
        if not self.inGame:
            rand = random.randint(0, 1000)
            rnd = random.randint(0, 1000)
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

    def findIfColliding(self, Platform1, Platform2, Platform3):
        one = Platform1.isTouching(self.x, self.y, self.height, self.width)
        two = Platform2.isTouching(self.x, self.y, self.height, self.width)
        three = Platform3.isTouching(self.x, self.y, self.height, self.width)
        colliding = [one, two, three]

        if True in colliding:
            self.setup()

    def powerUpRules(self, Platform1, Platform2, Platform3):
        self.determineIfInGame()
        self.findIfColliding(Platform1, Platform2, Platform3)
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

        self.fitness = 0
        self.framesOnTop = 0

        self.Platform1x = 0
        self.Platform1y = 0
        self.Platform1height = 0
        self.Platform1width = 0

        self.Platform2x = 0
        self.Platform2y = 0
        self.Platform2height = 0
        self.Platform2width = 0

        self.Platform3x = 0
        self.Platform3y = 0
        self.Platform3height = 0
        self.Platform3width = 0

        self.PowerUpx = 0
        self.PowerUpy = 0
        self.PowerUpwidth = 0
        self.PowerUpheight = 0
        self.PowerUptype = "Lol"
        self.PowerUpinGame = True

    def displayPlayer(self):
        if self.Alive:
            pygame.draw.rect(gameDisplay, green, (self.x, self.y, self.width, self.height))

    def updateOutsideVariables(self, x, y, w, h, x2, y2, w2, h2, x3, y3, h3, w3, px, py, pw, ph, ptype, pinGame):
        self.Platform1x = x
        self.Platform1y = y
        self.Platform1height = h
        self.Platform1width = w

        self.Platform2x = x2
        self.Platform2y = y2
        self.Platform2height = h2
        self.Platform2width = w2

        self.Platform3x = x3
        self.Platform3y = y3
        self.Platform3height = h3
        self.Platform3width = w3

        self.PowerUpx = px
        self.PowerUpy = py
        self.PowerUpwidth = pw
        self.PowerUpheight = ph
        self.PowerUptype = ptype
        self.PowerUpinGame = pinGame

    def changePosition(self, y_change):
        self.y -= y_change

    def calculateGravity(self):
        if self.canFall:
            self.Y_Change -= self.Gravity

    def goUp(self):
        if self.canJump:
            self.Y_Change += self.jumpHeight
        else:
            self.fitness -= 1

    def changeFall(self, val):
        self.Y_Change = 0
        self.canFall = val

    def limitPlayer(self):
        if self.y <= 0:
            self.y = 0
            self.Y_Change = 0
            self.framesOnTop += 1
            self.fitness -= 5

    def findIfDead(self):
        if self.y > screenHeight:
            self.Alive = False
            self.fitness -= 500
            print("Fell Off Screen")

        if self.framesOnTop >= 100:
            self.Alive = False
            self.fitness -= 500
            print("Stayed on top for too long")

        if self.x + self.width <= 20:
            self.Alive = False
            self.fitness -= 500
            print("Pushed to the left of Screen")

        if self.fitness < -500:
            self.Alive = False
            print("Fitness too low")

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
        x = self.canPlayerJump(self.Platform1x, self.Platform1width, self.Platform1y)
        y = self.canPlayerJump(self.Platform2x, self.Platform2width, self.Platform2y)
        z = self.canPlayerJump(self.Platform3x, self.Platform3width, self.Platform3y)
        list = [x, y, z]
        if False in list:
            self.canJump = False
        else:
            self.canJump = True

    def playerRules(self, Platform1, Platform2, Platform3):
        self.calculateGravity()

        self.changePosition(self.Y_Change)
        self.findIfDead()
        self.sideCollider()
        collider(self.x, self.y, self.height, self.width, self, Platform1, Platform2, Platform3)

        self.stopPlayerJump()

        self.limitPlayer()
        self.findCollidePowerup()
        self.displayPlayer()

        self.HeightAverage()
        playerScore = self.addGlobalScore()
        self.fitness += 0.1
        return playerScore

    def HeightAverage(self):
        global Frames, screenHeight
        self.playerHeightScore += self.y
        x = self.playerHeightScore / Frames
        self.heightPercent = x / screenHeight

    def sideCollider(self):
        o = sideCollisionChecker(self.x, self.y, self.width, self.Platform1x, self.Platform1y, self.Platform1width)
        t = sideCollisionChecker(self.x, self.y, self.width, self.Platform2x, self.Platform2y, self.Platform2width)
        r = sideCollisionChecker(self.x, self.y, self.width, self.Platform3x, self.Platform3y, self.Platform3width)
        sideCollision = [o, t, r]

        platformX = 0
        if True in sideCollision:
            findPlatform = sideCollision.index(True)
            if findPlatform == 0:
                platformX = self.Platform1x
            elif findPlatform == 1:
                platformX = self.Platform2x
            elif findPlatform == 2:
                platformX = self.Platform3x
            self.x = platformX - self.width - 1
            self.fitness -= 1

        else:
            if self.x < 60:
                self.x += 1

            elif self.x > 60:
                self.x = 60

    def findCollidePowerup(self):
        # self.playerPowerUpAlive = [Alive, Dead, TempDead]
        if not self.PowerUpinGame:
            self.playerPowerUpAlive = [False, True, False]

        if self.PowerUpinGame:
            self.playerPowerUpAlive[0] = True
            self.playerPowerUpAlive[1] = False

        collide = collidingChecker(self.x, self.y, self.height, self.width, self.PowerUpx, self.PowerUpy,
                                   self.PowerUpheight,
                                   self.PowerUpwidth)

        if collide and not self.playerPowerUpAlive[2]:
            self.performPowerUp()
            self.playerPowerUpAlive[2] = True

    def performPowerUp(self):
        power = self.PowerUptype
        # ["Big", "Jump", "Small", "Lower", "Wide", "Tall"]
        if power == "Big":
            self.height += 5
            self.width += 5
            self.fitness += 100
        elif power == "Small":
            self.height -= 5
            self.width -= 5
            self.fitness -= 100
        elif power == "Jump":
            self.jumpHeight += 2
            self.fitness += 100
        elif power == "Lower":
            self.jumpHeight -= 2
            self.fitness -= 100
        elif power == "Wide":
            self.width += 5
        elif power == "Tall":
            self.height += 5


def getInputs(player, powerUp, Platform1, Platform2, Platform3):
    platforms = [Platform1, Platform2, Platform3]
    index = 0
    x = 8000
    for platform in platforms:
        y = platform.x
        if x > y:
            x = y
            index = platform.position

    firstPlatform = [platforms[index - 1].x - player.x, platforms[index - 1].y - player.y,
                     platforms[index - 1].x + platforms[index - 1].width - player.x]

    nextIndex = 0
    if index == 1:
        nextIndex = 2
    elif index == 2:
        nextIndex = 3
    elif index == 3:
        nextIndex = 1
    p1 = [player.x, player.y]
    p2 = [platforms[nextIndex - 1].x, platforms[nextIndex - 1].y]
    distance = math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))
    nextPlatform = [platforms[nextIndex - 1].x - player.x, platforms[nextIndex - 1].y - player.y,
                    platforms[nextIndex - 1].x + platforms[nextIndex - 1].width - player.x, distance]

    powerupNumber = powerUp.powerList.index(powerUp.powerupType)

    b = 0
    if powerUp.inGame:
        b = 1
    else:
        b = 0

    returnTuple = (
        player.jumpHeight, player.x, player.y, player.height, player.width, firstPlatform[0], firstPlatform[1],
        firstPlatform[2], nextPlatform[0], nextPlatform[1], nextPlatform[2], nextPlatform[3],
        powerUp.x - player.x, powerUp.y - player.y, powerupNumber, b)
    newList = []
    for val in returnTuple:
        newList.append(round(val, 1))

    return newList


def eval(genomes, config):
    global Frames, Gen
    Score = 0
    Gen += 1
    Frames = 0
    Platform1 = platform(50, 500, 100, 300, 1)
    Platform2 = platform(370, 400, 200, 300, 2)
    Platform3 = platform(790, 500, 100, 300, 3)
    powerUp = PowerUp()

    nets = []
    players = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        players.append(Player())
        ge.append(genome)

    while len(players) > 0:

        if len(players) > 0:
            Frames += 1
            gameDisplay.fill(black)
            speed = findSpeed(Score)
            moveScreen(speed, Platform1, Platform2, Platform3, powerUp)
            Score = regeneratePlatforms(Platform1, Platform2, Platform3, players, Score)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            powerUp.powerUpRules(Platform1, Platform2, Platform3)
            bestFitness = -500
            worstFitness = 10000000
            bestHeightScore = -10
            worstHeightScore = 1000
            for x, player in enumerate(players):
                player.updateOutsideVariables(Platform1.x, Platform1.y, Platform1.width, Platform1.height, Platform2.x,
                                              Platform2.y, Platform2.width, Platform2.height, Platform3.x, Platform3.y,
                                              Platform3.height, Platform3.width, powerUp.x, powerUp.y, powerUp.width,
                                              powerUp.height, powerUp.powerupType, powerUp.inGame)
                player.playerRules(Platform1, Platform2, Platform3)

                if player.heightPercent > bestHeightScore:
                    bestHeightScore = player.heightPercent
                if player.heightPercent < worstHeightScore:
                    worstHeightScore = player.heightPercent

                if player.fitness > bestFitness:
                    bestFitness = player.fitness
                if player.fitness < worstFitness:
                    worstFitness = player.fitness

                # keep this at the end
                if not player.Alive:

                    players.pop(x)
                    nets.pop(x)
                    ge.pop(x)



            for x, player in enumerate(players):
                ge[x].fitness = player.fitness

                output = nets[players.index(player)].activate(
                    getInputs(player, powerUp, Platform1, Platform2, Platform3))

                if output[0] > 0.5:
                    # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                    # It took a really long time to train the AI and it is still not perfect
                    # It took a long time to code this and figure out how neat works and how I can combine it into my initial singleplayer game.
                    player.goUp()
                    player.fitness -= 2

            if True:
                Platform1.displayPlatform()
                Platform2.displayPlatform()
                Platform3.displayPlatform()

                message_display("Players left: " + str(len(players)), 250, 50)
                message_display("Score: " + str(Score), 650, 50)
                message_display("Generation: " + str(Gen), 650, 120, 40)

                if len(players) > 1:
                    message_display("Best Height Score: " + str(round(bestHeightScore * 100, 1)) + "%", 550, 550, 25)
                    message_display("Best Fitness: " + str(round(bestFitness, 1)), 200, 550, 25)
                    message_display("Worst Height Score: " + str(round(worstHeightScore * 100, 1)) + "%", 550, 575, 25)
                    message_display("Worst Fitness: " + str(round(worstFitness, 1)), 200, 575, 25)
                else:
                    message_display("Best Height Score: " + str(round(bestHeightScore * 100, 1)) + "%", 550, 550, 25)
                    message_display("Best Fitness: " + str(round(bestFitness, 1)), 200, 550, 25)

                pygame.display.update()


        if len(players) <= 0:
            break

    print(f"""Final Score: {Score}""")


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    global Platform1, Platform2, Platform3
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')

    run(config_path)
