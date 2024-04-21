#Ethan McIntosh (EM),
#Matthew Roberto (MR),
#Mathias Giorgi (MG)
#CHE120 Project
#----------GAME SETUP-------------------------------------------------------------------------------------

import pygame, numpy,random #MR - needed modules are brought in


WIDTH = 900 #MR - the game window's width and height are defined, the background image is loaded in
HEIGHT = 900
BACKGROUND = pygame.image.load("background.png")
#-----------------Sets up Sprites--------------------------------------------------------------------------

class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, startx, starty): #MR - sprite setup starts with class definition, parameters also defined
        super().__init__()

        self.image = pygame.image.load(image) #MR - assigns image to sprite
        self.rect = self.image.get_rect() #MR - calls it, sets up bounds

        self.rect.center = [startx, starty] #MR - places sprite in a starting location

    def update(self): #MR - defined here so it can be called later
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect) #MR - draws on to screen at specifiec coordinates to make sprite visible

#-----------------------PLAYER SETTINGS----------------------------------------------------------------------

class Player(Sprite):
    def __init__(self, startx, starty):
        super().__init__("PlayerIdle.png", startx, starty) # MG - function to establish default sprite for player, starting location and necessary variables 
        self.stand_image = self.image    # MG- when no movement occuring show idle animation
        self.jump_image = pygame.image.load("PlayerJump.png") 

        self.walk_cycle = [pygame.image.load(f"PlayerMove{i:0>2}.png") for i in range(1,3)] #MG - allows to alternate between the walking sprites to create a walk cycle
        self.animation_index = 0
        self.facing_left = False #MG- Defaults to facing right when game starts

        self.speed = 4 
        self.jumpspeed = 20 
        self.vsp = 0 #MG - vertical speed of player
        self.gravity = 1
        self.min_jumpspeed = 4
        self.prev_key = pygame.key.get_pressed() #MG - checks if the last key pressed is still being pressed

    #----------------------ANIMATION SETTINGS i.e screen settings, movement, etc-------------------------------

    def walk_animation(self):
        self.image = self.walk_cycle[self.animation_index]
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

        if self.animation_index < len(self.walk_cycle)-1:
            self.animation_index += 1
        else:
            self.animation_index = 0

    def jump_animation(self):
        self.image = self.jump_image
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

#--------------------USER INPUT SETTINGS-----------------------------------------------------------------------
    
    def update(self, platform):
        hsp = 0
        onground = self.check_collision(0, 1, platform)
        # check keys
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.facing_left = True
            self.walk_animation()
            hsp = -self.speed
        elif key[pygame.K_RIGHT]:
            self.facing_left = False
            self.walk_animation()
            hsp = self.speed
        else:
            self.image = self.stand_image

        if key[pygame.K_UP] and onground:
            self.vsp = -self.jumpspeed

        # variable height jumping
        if self.prev_key[pygame.K_UP] and not key[pygame.K_UP]:
            if self.vsp < -self.min_jumpspeed:
                self.vsp = -self.min_jumpspeed

        self.prev_key = key

        # gravity
        if self.vsp < 10 and not onground:  # 9.8 rounded up
            self.jump_animation()
            self.vsp += self.gravity

        if onground and self.vsp > 0:
            self.vsp = 0
            
        # movement
        self.move(hsp, self.vsp, platform)

    def move(self, x, y, platform):
        dx = x
        dy = y

        while self.check_collision(0, dy, platform):
            dy -= numpy.sign(dy)

        while self.check_collision(dx, dy, platform):
            dx -= numpy.sign(dx)

        self.rect.move_ip([dx, dy])

    def check_collision(self, x, y, grounds):
        self.rect.move_ip([x, y])
        collide = pygame.sprite.spritecollideany(self, grounds)
        self.rect.move_ip([-x, -y])
        return collide
        
class Goose(Sprite): #Ethan McIntosh
    def __init__(self, startx, starty, direction): #EM - Function for inializing a new goose
        super().__init__("goos.png", startx, starty) #EM - Call this objects parent class to initialize their properties
        
        if direction == True: #EM - Set the gooses direction variable. This is used for determining which direction it moves
            self.faceLeft = False
        else:
            self.image = pygame.transform.flip(self.image, True, False) #EM - If the goose will be moving left, make the goose face the correct direction
            self.faceLeft = True
            
        self.movespeed = random.randint(2,5) #EM - Movespeed is how many pixels a goose will move per frame, can be between 2 and 5
        
    def update(self): #EM - This function is for updating the position of the goose, as well as despawning.
        if self.faceLeft == False: #EM - Determine which direction the goose will move, this depends on their direction variable
            self.rect.right += self.movespeed
        else:
            self.rect.right -= self.movespeed
            
        if self.rect.x < -50 or self.rect.x > 950: #EM - When a goose goes far enough off screen, it will be removed in order to not waste processing power.
           del self

class Box(Sprite):
    def __init__(self, startx, starty):
        super().__init__("tile.png", startx, starty)

#------------------CODE GETS EXECUTED----------------------------------

def main():
    
    Score = 0
    pygame.init()  #MG - initializes all pygame functions
    pygame.font.init() #MG - grants access to produce fonts and therefore words to the pygame window
    font = pygame.font.Font(None, 36) #MG- establishes a font size for when we writes something
    screen = pygame.display.set_mode((WIDTH, HEIGHT)) #MG - opens the pygame window to the players view
    clock = pygame.time.Clock() #MG-lines up in game clock to the system clock
    pygame.time.set_timer(pygame.USEREVENT, 1000) # MG- causes a custom event to trigger every 1000 milliseconds
    spawnDelay = 0 #EM - A counter that will spawn a goose once it reaches a certain threshold
    geese = [] #EM - A list that stores all existing geese. Allows code to work with geese that are changing in amount.
    playerHit = False #EM - Determines whether the game should continue or not

    player = Player(100, 200)

    platform = pygame.sprite.Group() #EM - This group contains all tiles in the game
    for bx in range(0, 970, 32): #EM - Create terrain, the terrain is a box around the window, and three platforms.
        platform.add(Box(bx, 830))
        platform.add(Box(bx, 20))
        platform.add(Box(0, bx))
        platform.add(Box(900, bx))
    for bx in range(0, 560, 32):
        platform.add(Box(bx + 200, 270))
        platform.add(Box(bx + 300, 460))
        platform.add(Box(bx + 200, 650))
    
    while playerHit == False: #EM - The game will continue running so long as the player has not been hit.
        for i in range(len(geese)): #EM - Loop for updating the position of every goose, and checking if the player has been hit
            geese[i].update()
            if geese[i].rect.colliderect(player.rect): #EM - Check if the current goose is colliding with the player.
                playerHit = True
                
        pygame.event.pump()
        player.update(platform) 
        for event in pygame.event.get(): #MG checks for an event to occur and executes a function if it does
            if event.type == pygame.QUIT: #MG - event.type is the specification of what the user does i this case if the user closes the window that means that event is pygame.QUIT
                pygame.quit() #MG- immediately ends the code when excuted
            if event.type == pygame.USEREVENT:
                Score+= 1 #MG- when a second passes and 1 point to the score
        score_text = font.render(f"Score: {Score}", True, (255, 255, 255)) #MG- creates word Score and displays score in a white font
        screen.blit(score_text,(10,10))# MG - places score at coordinates (10,10) as measured from the top left corner of the window
        pygame.display.update() #MG- update display to include the score

        
        
        spawnDelay += 1 #EM - The spawnDelay counter increases every frame.
        if spawnDelay == 60: #EM - Once spawnDelay reaches the specified threshold, spawn a goose going either left or right.
            if random.randint(1, 10) > 5:
                geese.insert(0,Goose(0, random.randint(25,800), True))
                spawnDelay = 0 #EM - Once a goose is spawned, set the spawnDelay back to 0. This is so that more geese are able to spawn
            else:
                geese.insert(0,Goose(900, random.randint(25, 800), False))
                spawnDelay = 0
        
                
        # Draw loop
        screen.blit(BACKGROUND, (0,0))
        player.draw(screen)
        platform.draw(screen)
        for i in range(len(geese)): #EM - Redraw all geese onto the screen
            geese[i].draw(screen)
        pygame.display.flip()
        

        clock.tick(60)
        if playerHit == True: #EM - When the player is hit, display text indicating the loss, as well as display the users score.
            screen.blit(font.render('Game Over',True, (255,255,255)), (400, 400))
            screen.blit(font.render("Your score was: " + str(Score),True, (255,255,255)), (400, 450))
            pygame.display.update()
            pygame.quit()

if __name__ == "__main__":
    main()
