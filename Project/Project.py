import pygame
from sys import exit
import math
import threading
import time

width = 1400
height = 800

pygame.init()

#Setting up the important stuff
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Incremental')
clock = pygame.time.Clock()

#Text things
text = pygame.font.SysFont(None, 60)
subText = pygame.font.SysFont(None, 40)
subberText = pygame.font.SysFont(None, 30)

#COLOURS
moneyGreen = (133, 187, 101)

#MOST IMPORTANT VARIABLE IN EXISTANCE DO NOT ERASE NOR CHANGE
#-----------------------------------------------
money = 0
#-----------------------------------------------

#Load and prepare the image
original_image = pygame.image.load('TabIcon.PNG').convert_alpha()       #Image for the tab menu
button_image = pygame.transform.scale(original_image, (60, 60))     #reshape it to good size

#Tint function (simple multiply)
def tint_image(image, tint_color):
    tinted_image = image.copy()
    tint_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    tint_surface.fill(tint_color)
    tinted_image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted_image

#Button class
#----------------------------------------------------------------------------------------------------------------------
class button():
    #MAIN BUTTON THINGS

    def __init__(self, bWidth, bHeight, left, top, number, type, int, price):   #All the variables for the button
        self.button = pygame.rect.Rect(left, top, bWidth, bHeight)      #Setting up the button
        self.display_text = text.render(f'{number}', True, 'BLACK')     #Setting up the what button number it is
        self.type = type.lower()        #Variable for the type of button (exponential, additive, multiplicitive...)
        self.int = int      #Variable for the value of the button
        self.clicked = False    #Boolean to check if button is clicked
        self.flag = False       #Just a flag for threading
        self.price = price      #Variable for the price tag

    def draw_button(self, description, colour, textsize):   #Setting up the variables to draw the button
        pygame.draw.rect(screen, colour, self.button, border_radius=20)  #Draws the button onto the screen
        self.display_text_rect = self.display_text.get_rect(center=(self.button.centerx, self.button.centery - 20))     #Sets up the description text
        screen.blit(self.display_text, self.display_text_rect)  #Renders the button number text
        if textsize == subText:     #Checks how small the text should be
            self.renderSubText(desc = description)      #Regular description text size
        elif textsize == subberText:
            self.renderSubberText(desc = description)   #Smaller description text size
        self.draw_price(price=self.price, colour=colour)    #(see down below)

    def draw_price(self,price,colour):     #Setting up the price box
        pHeight = 50                        #All the variables to set up the price rect.
        pWidth = self.button.width / 2
        pLeft = self.button.centerx - pWidth / 2
        pTop = self.button.bottom + 10  #(MAKE SURE ITS NOT A TUPLE!!!)
        self.priceBox = pygame.rect.Rect(pLeft, pTop, pWidth, pHeight)      #Setting up price rect
        pygame.draw.rect(screen, colour, self.priceBox, border_radius = 10) #drawing the price rect

        self.display_subtext = subText.render(f'£{price}', True, (0,0,0))   #setting up the price text
        self.priceText_rect = self.display_subtext.get_rect(center=(self.priceBox.centerx, self.priceBox.centery))  #setting up the position of the price text
        screen.blit(self.display_subtext, self.priceText_rect)  #drawing the price text



    #Stuff to chance the description text size
    def renderSubText(self, desc):  #A little smaller
        self.display_subtext = subText.render(f'{desc}', True, (0,0,0))
        self.subtext_rect = self.display_subtext.get_rect(center=(self.button.centerx, self.button.centery + 20))
        screen.blit(self.display_subtext, self.subtext_rect)

    def renderSubberText(self, desc):   #Small text
        self.display_subtext = subberText.render(f'{desc}', True, (0,0,0))
        self.subtext_rect = self.display_subtext.get_rect(center=(self.button.centerx, self.button.centery + 20))
        screen.blit(self.display_subtext, self.subtext_rect)


    #Click detection and money increment system
    def clickDetection(self):   #This is in the events area so only runs when you click the mouse button
        global money
        mousepos = pygame.mouse.get_pos()   #Gets position of the mouse
        if self.button.collidepoint(mousepos) and self.clicked == False:    #If mouse is over a button and its not been clicked
            self.clicked = True     #Sets the clicked value to true and turns flag on
            self.flag = True
            self.colour = (83,133,51)   #in theory should change the colour...
            print(self.clicked)

    def moneyIncrement(self):   #Used in the threading, just increases the money by a set amount
        global money
        while True:
            if self.flag == True:   #When button has been pressed
                if self.type == 'add':  #If its additive then add money by the value
                    money += self.int
                if self.type == 'mult': #If its multiplicitive then multiply money by the value
                    money *= self.int
                if self.type == 'exp':  #If its exponential then do the money to the power of the value
                    money = pow(money, self.int)
            time.sleep(1)
#----------------------------------------------------------------------------------------------------------------------


#UI BUTTONS CLASS (inheriting the button class)
#-------------------------------------------------------------------------------
class UIbutton(button):
    def __init__(self, bWidth, bHeight, left, top):
        super().__init__(bWidth, bHeight, left, top, number='',type='',int=0, price='') #Setting up the button

    def draw_UIbutton(self, image):
        pygame.draw.rect(screen, (255,255,255), self.button, border_radius=5) #Draws the button
        screen.blit(image, self.button.topleft)  #Blits the correct image onto the button

tinted_image_button = tint_image(button_image, (124,124,124))  #Tints a button image gray
#-------------------------------------------------------------------------------


#BUTTONS WILL GO HERE
#-------------------------------------------------------------------------------
# £ MONEY BUTTONS
moneyUp1 = button(300,120,550,550,1,'add',0.1, '0')         #BUTTON VARIABLES ([Width], [Height], [Left], [Top], [Button number], [Type], [Value], [Price])
moneyUp2 = button(300,120,550,325,2,'mult',1.05, '1')       #Don't forget to THREAD EACH BUTTON
moneyUp3 = button(300,120,550,100,3,'exp',1.02,'5')            #And to ADD THE CLICK DETECTION AND DRAW THE BUTTON IN THE WHILE LOOP

#UI BUTTONS
menuButton = UIbutton(60,60,10,100)    #UI BUTTON VARIABLES ([Width], [Height], [Left], [Top])
#-------------------------------------------------------------------------------

#ALL THREADS WILL GO HERE
#-------------------------------------------------------------------------------
t1 = threading.Thread(target=moneyUp1.moneyIncrement, daemon=True)  #Creates a thread that targets the button, specifically the moneyIncrement function.
t1.start()                                                          #No arguments to add

t2 = threading.Thread(target=moneyUp2.moneyIncrement, daemon=True)  #Always have daemon set to true
t2.start()                                                          #The .start() just starts the thread when it sees the flag has been turned on (button is pressed)

t3 = threading.Thread(target=moneyUp3.moneyIncrement, daemon=True)
t3.start()
#-------------------------------------------------------------------------------

#Main game loop
while True:
    screen.fill((0,0,0))    #Makes background black
    for event in pygame.event.get():    #Event system
        if event.type == pygame.QUIT:   #If you leave the game, close the game
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:    #If you click
            #ALL CLICK DETECTION WILL GO HERE
            #-------------------------------------------------------------------------------
            menuButton.clickDetection()
            moneyUp1.clickDetection()
            moneyUp2.clickDetection()
            moneyUp3.clickDetection()
            #-------------------------------------------------------------------------------

    #Making the money visible on the screen
    moneyText = text.render(f'£ {round(money,2)}', True, 'WHITE')   #Shows the value of the money (and rounds it to two decimal places)
    moneyTextRect = moneyText.get_rect(center=(width/2,50))     #Positions the money at the top middle of the screen
    screen.blit(moneyText,moneyTextRect)    #Draws it onto the screen (keep in the while loop to constantly update it)

    menuButton.draw_UIbutton(tinted_image_button)   #Draws the Menu Tab button to the screen

    moneyUp1.draw_button('0.1 Money per second', moneyGreen, subText)
    moneyUp2.draw_button('Multiplies money by \n   1.05 per second', moneyGreen, subberText)
    moneyUp3.draw_button('Exponents money by \n   1.02 each second', moneyGreen, subberText)


    pygame.display.update()
    clock.tick(60)
