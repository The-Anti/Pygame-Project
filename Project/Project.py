import pygame
from sys import exit
import math
import threading
import time
import sqlite3

width = 1400
height = 800

pygame.init()

#abbreviating the money
millnames = ['',' k',' M',' B',' T',' Qa', ' Qn', ' Sx', ' Sp', ' Oc', ' No', ' De', ' UDe', ' DDe', ' TDe', ' QaDe', ' QnDe', ' SxDe', ' SpDe', ' ODe', ' NDe'
             ,' Vg', ' UVg', ' DVg', ' TVg', ' QaVg', ' QnVg', ' SxVg', ' SpVg', ' OVg', ' NVg', 'Tg']

#i have no clue what happens here but it works so :D
def millify(n):
    n = float(n)
    if n == float('inf'):
        return n
    else:
        millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
    if n < 1000:    #Just checks if the number is above 1 thousand, if it is then just display to 1dp instead of 2
        return '{:.2f}{}'.format(n / 10**(3 * millidx), millnames[millidx])
    else:
        return '{:.1f}{}'.format(n / 10**(3 * millidx), millnames[millidx])



#Setting up the important stuff
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Incremental')
clock = pygame.time.Clock()

#Text things
text = pygame.font.SysFont(None, 60)
subText = pygame.font.SysFont(None, 40)
subberText = pygame.font.SysFont(None, 30)
subbestText = pygame.font.SysFont(None, 20)

#COLOURS
moneyGreen = (133, 187, 101)
rebirthYellow = (255, 174, 66)

#MOST IMPORTANT VARIABLES IN EXISTANCE DO NOT ERASE NOR CHANGE
#-----------------------------------------------
money = 0
rebirths = 0
tps = 1000
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

    def __init__(self, bWidth, bHeight, left, top, number, type, int, price, clicks, price_func=None):   #All the variables for the button
        self.button = pygame.rect.Rect(left, top, bWidth, bHeight)      #Setting up the button
        self.display_text = text.render(f'{number}', True, 'BLACK')     #Setting up the what button number it is
        self.type = type.lower()        #Variable for the type of button (exponential, additive, multiplicitive...)
        self.int = int      #Variable for the value of the button
        self.clicks = 0     #how many times you clicked
        self.maxClicks = clicks #how many times you can click
        self.clicked = False    #Boolean to check if button is clicked
        self.flag = False       #Just a flag for threading
        self.price = price      #Variable for the price tag
        self.price_func = price_func    #Price scaling function
        self.ogPrice = price

    def draw_button(self, description, colour, textsize):   #Setting up the variables to draw the button
        pygame.draw.rect(screen, colour, self.button, border_radius=20)  #Draws the button onto the screen
        self.display_text_rect = self.display_text.get_rect(center=(self.button.centerx, self.button.centery - 20))     #Sets up the description text
        screen.blit(self.display_text, self.display_text_rect)  #Renders the button number text
        if textsize == subText:     #Checks how small the text should be
            self.renderSubText(desc = description)      #Regular description text size
        elif textsize == subberText:
            self.renderSubberText(desc = description)   #Smaller description text size
        self.draw_price(colour=colour)    #(see down below)

        self.upgradeCount = subberText.render(f'{self.clicks}/{self.maxClicks}', True, 'BLACK')
        self.upgradeCountRect = self.upgradeCount.get_rect(topright = (self.button.centerx+140, self.button.centery-55))
        screen.blit(self.upgradeCount, self.upgradeCountRect)

    def get_center(self):
        return self.button.center

    def link(self,y):
        pygame.draw.line(screen, (255,255,255), self.button.center, y.get_center(), 20)


    def draw_price(self,colour):     #Setting up the price box
        pHeight = 50                        #All the variables to set up the price rect.
        pWidth = self.button.width / 2
        pLeft = self.button.centerx - pWidth / 2
        pTop = self.button.bottom - 5  #(MAKE SURE ITS NOT A TUPLE!!!)
        self.priceBox = pygame.rect.Rect(pLeft, pTop, pWidth, pHeight)      #Setting up price rect
        pygame.draw.rect(screen, colour, self.priceBox, border_radius = 10) #drawing the price rect

        if self.price <= 0:     #If upgrade is free then display it to be free
            self.display_subtext = subText.render('Free', True, (0,0,0))
        elif self.clicks == self.maxClicks:
            self.display_subtext = subText.render('Max', True, (0,0,0)) #If its maxxed out then say its maxxed out
        else: 
            self.display_subtext = subText.render(f'£{self.price}', True, (0,0,0))   #setting up the price text
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
        if self.button.collidepoint(mousepos) and self.clicked == False and money >= self.price:    #If mouse is over a button, you can click it and you have enough money then...
            print('Clicked')
            if self.clicks == (self.maxClicks - 1):
                self.clicked = True     #Sets the clicked value to true and turns flag on
            self.flag = True
            self.colour = (83,137,51)   #in theory should change the colour...
            money -= self.price
            self.clicks += 1
            if self.price_func:
                self.price = round(self.price_func(self.price, self.clicks), 2)
        

    def moneyIncrement(self):   #Used in the threading, just increases the money by a set amount
        global money
        global tps
        while True:
            if self.flag == True:   #When button has been pressed
                if self.type == 'add':  #If its additive then add money by the value
                    money += round(self.clicks * self.int,4)
                if self.type == 'mult': #If its multiplicitive then multiply money by the value
                    money = money + (money * round(self.clicks * self.int,4))
                if self.type == 'exp':  #If its exponential then do the money to the power of the value
                    money = money + pow(money, round(self.clicks * self.int,4))
            time.sleep(tps/1000)

    def resetButton(self):
        self.clicks = 0
        self.clicked = False
        self.flag = False
        self.price = self.ogPrice
#----------------------------------------------------------------------------------------------------------------------



#UI BUTTONS CLASS (inheriting the button class)
#-------------------------------------------------------------------------------
class UIbutton(button):
    def __init__(self, bWidth, bHeight, left, top):
        super().__init__(bWidth, bHeight, left, top, number='',type='',int=0, price=0, clicks=0) #Setting up the button

    def draw_UIbutton(self, image):
        pygame.draw.rect(screen, (255,255,255), self.button, border_radius=5) #Draws the button
        screen.blit(image, self.button.topleft)  #Blits the correct image onto the button

tinted_image_button = tint_image(button_image, (124,124,124))  #Tints a button image gray
#-------------------------------------------------------------------------------



#REBIRTH BUTTON CLASS (inheriting the button class)
#-------------------------------------------------------------------------------
class rButton(button):
    def __init__(self, bWidth, bHeight, left, top, number, type, int, price, clicks, price_func=None):
        super().__init__(bWidth, bHeight, left, top, number,type, int, price, clicks, price_func)
        self.tick_upgrade_purchased = False

    def draw_button(self, description, colour, textsize):   #Setting up the variables to draw the button
        pygame.draw.rect(screen, colour, self.button, border_radius=20)  #Draws the button onto the screen
        self.display_text_rect = self.display_text.get_rect(center=(self.button.centerx, self.button.centery - 20))     #Sets up the description text
        screen.blit(self.display_text, self.display_text_rect)  #Renders the button number text
        if textsize == subText:     #Checks how small the text should be
            self.renderSubText(desc = description)      #Regular description text size
        elif textsize == subberText:
            self.renderSubberText(desc = description)   #Smaller description text size
        self.draw_price(colour=colour)    #(see down below)

        global rebirths
        if self.type == 'rebirth':  #If its the rebirth button
            if money / self.price >= 0.5:         #if you have enough for the rebirth
                self.rebirthCount = subberText.render(f'{millify(pow((money/self.price), 0.95))}', True, 'BLACK')       #displays how much you will get from it
                self.rebirthCountRect = self.rebirthCount.get_rect(topright = (self.button.centerx+140, self.button.centery-55))
                screen.blit(self.rebirthCount, self.rebirthCountRect)
        else:   #if its a rebirth upgrade button
            self.upgradeCount = subberText.render(f'{self.clicks}/{self.maxClicks}', True, 'BLACK')     #display how many times u can upgrade it
            self.upgradeCountRect = self.upgradeCount.get_rect(topright = (self.button.centerx+140, self.button.centery-55))
            screen.blit(self.upgradeCount, self.upgradeCountRect)

    def draw_price(self,colour):     #Setting up the price box
        pHeight = 50                        #All the variables to set up the price rect.
        pWidth = self.button.width / 2
        pLeft = self.button.centerx - pWidth / 2
        pTop = self.button.bottom - 5  #(MAKE SURE ITS NOT A TUPLE!!!)
        self.priceBox = pygame.rect.Rect(pLeft, pTop, pWidth, pHeight)      #Setting up price rect
        pygame.draw.rect(screen, colour, self.priceBox, border_radius = 10) #drawing the price rect

        if self.price <= 0:     #If upgrade is free then display it to be free
            self.display_subtext = subText.render('Free', True, (0,0,0))
        elif self.clicks == self.maxClicks:
            self.display_subtext = subText.render('Max', True, (0,0,0)) #If its maxxed out then say its maxxed out
        elif self.type == 'rebirth': 
            self.display_subtext = subText.render(f'£{self.price}', True, (0,0,0))   #Have it show you can buy it with money if its the rebirth button
        else:
            self.display_subtext = subText.render(f'г {self.price}', True, (0,0,0))   #Show you have to spend rebirth tokens to buy it Ӷ
        self.priceText_rect = self.display_subtext.get_rect(center=(self.priceBox.centerx, self.priceBox.centery))  #setting up the position of the price text
        screen.blit(self.display_subtext, self.priceText_rect)  #drawing the price text


    def clickDetection(self):   #This is in the events area so only runs when you click the mouse button
        global money
        global rebirths
        mousepos = pygame.mouse.get_pos()   #Gets position of the mouse
        if self.type == 'rebirth':
            if self.button.collidepoint(mousepos) and money >= self.price:    #If mouse is over a button, you can click it and you have enough money then...
                rebirths += round(pow((money/self.price), 0.95),2)  #turns money into rebirths
                money = 0
                for i in moneyButtons:  #when rebirthed, resets all the money buttons
                    i.resetButton()
        else:
            if self.button.collidepoint(mousepos) and self.clicked == False and rebirths >= self.price:   #Checks if you can click the upgrade and have enough rebirths
                if self.clicks == (self.maxClicks - 1):
                    self.clicked = True
                if self.type == 'tick':     #Just checks if you bought an upgrade that changes the tick
                    self.tick_upgrade_purchased = True  #If you did, says that you did
                self.flag = True
                rebirths -= self.price
                self.clicks += 1
                if self.price_func:
                    self.price = round(self.price_func(self.price, self.clicks), 2)



    def moneyIncrement(self):   #Used in the threading, just increases the money by a set amount
        global money
        global tps
        while True:
            if self.flag == True:   #When button has been pressed
                if self.type == 'mult': #If its multiplicitive then multiply money by the value
                    money = money + (money * round(self.clicks * self.int,4))
                if self.type == 'exp':  #If its exponential then do the money to the power of the value
                    money = money + pow(money, round(self.clicks * self.int,4))
                if self.type == 'tick' and self.tick_upgrade_purchased == True: #if its a tick upgrade and you HAVE clicked the upgrade
                    self.tick_upgrade_purchased = False     #resets the boolean so that the function doesn't repeat constantly
                    tps = tps - self.int                    #(if it does then it BREAKS THE GAME, tps > 0)
            time.sleep(tps/1000)

    def rebirthIncrement(self):   #Used in the threading, just increases the rebirths by a set amount
        global rebirths
        global tps
        while True:
            if self.flag == True:   #When button has been pressed
                if self.type == 'mult': #If its multiplicitive then multiply rebirths by the value
                    rebirths = rebirths + (rebirths * round(self.clicks * self.int,4))
                if self.type == 'exp':  #If its exponential then do the rebirths to the power of the value
                    rebirths = rebirths + pow(rebirths, round(self.clicks * self.int,4))
            time.sleep(tps/1000)


#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def b1Func(curPrice, click):
    if click == 1:
        return 0.1
    elif click < 3:
        curPrice = curPrice + (curPrice * 0.2)
        return curPrice
    else:
        curPrice = curPrice + (curPrice * 0.5)
        return curPrice
    
def b2Func(curp, click):
    if click == 1:
        return curp * 1.3
    else:
        return curp * 1.5
    
def default(curp, click):
    if click < 3:
        return curp * 1.8
    if click < 6:
        return curp * 1.5
    if click < 9:
        return curp * 1.2
    else:
        return curp * 1.05
    
#-------------------------------------------------------------------------------

#BUTTONS WILL GO HERE
#BUTTON VARIABLES ([Width], [Height], [Left], [Top], [Button number], [Type], [Value], [Price], [Clicks], [Price function (default = None)])
#Type = add (additive), mult (multiplicitive), exp (exponential), tick (changes ticks per second [input in ms])
#-------------------------------------------------------------------------------
# £ MONEY BUTTONS
moneyUp1 = button(300, 120, 550, 550, 1, 'add', 0.1, 0, 5, price_func=b1Func)         
moneyUp2 = button(300,120,550,325,2,'mult',0.05,1,3, price_func=b2Func)       #Don't forget to THREAD EACH BUTTON
moneyUp3 = button(300,120,550,100,3,'exp',0.02,5,1)            #And to ADD THE CLICK DETECTION AND DRAW THE BUTTON IN THE WHILE LOOP

#list for buttons
moneyButtons = [moneyUp1, moneyUp2, moneyUp3]

#REBIRTH BUTTONS ᒥ
rebirthButton = rButton(300,120,1000,550,'г0','rebirth',0,1,2)
rebirth1 = rButton(300,120,1000,325,'г1','mult',0.25,1,10,price_func=default)
rebirth2 = rButton(300,120,1000,100,'г2','tick',100,3,5,price_func=default)

#list for rebirth buttons
rebirthButtons = [rebirth1, rebirth2]

#UI BUTTONS
menuButton = UIbutton(60,60,10,100)    #UI BUTTON VARIABLES ([Width], [Height], [Left], [Top])
#-------------------------------------------------------------------------------

#ALL THREADS WILL GO HERE
#-------------------------------------------------------------------------------
#Money button threading
t1 = threading.Thread(target=moneyUp1.moneyIncrement, daemon=True)  #Creates a thread that targets the button, specifically the moneyIncrement function.
t1.start()                                                          #No arguments to add
t2 = threading.Thread(target=moneyUp2.moneyIncrement, daemon=True)  #Always have daemon set to true
t2.start()                                                          #The .start() just starts the thread when it sees the flag has been turned on (button is pressed)
t3 = threading.Thread(target=moneyUp3.moneyIncrement, daemon=True)
t3.start()

#Rebirth button threading
tr1 = threading.Thread(target=rebirth1.moneyIncrement, daemon=True)  #Always have daemon set to true
tr1.start()                                                          #The .start() just starts the thread when it sees the flag has been turned on (button is pressed)
tr2 = threading.Thread(target=rebirth2.moneyIncrement, daemon=True)
tr2.start()
#-------------------------------------------------------------------------------

#Main game loop
while True:
    screen.fill((0,0,0))    #Makes background black
    for event in pygame.event.get():    #Event system
        if event.type == pygame.QUIT:   #If you leave the game, close the game
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:    #When you click, things below happen.
            #ALL CLICK DETECTION WILL GO HERE
            #-------------------------------------------------------------------------------
            menuButton.clickDetection()

            for i in moneyButtons:
                i.clickDetection()

            for i in rebirthButtons:
                i.clickDetection()

            rebirthButton.clickDetection()
            #-------------------------------------------------------------------------------

    #Making the money visible on the screen
    moneyText = text.render(f'£ {millify(money)}', True, 'WHITE')   #Shows the value of the money (and rounds it to two decimal places)
    moneyTextRect = moneyText.get_rect(center=(width/2,50))     #Positions the money at the top middle of the screen
    screen.blit(moneyText,moneyTextRect)    #Draws it onto the screen (keep in the while loop to constantly update it)

    #Making rebirths visble on the screen
    rebirthText = text.render(f'Г {millify(rebirths)}', True, 'WHITE')   #Shows the value of the money (and rounds it to two decimal places) Ӷ
    rebirthTextRect = rebirthText.get_rect(center=(moneyTextRect.centerx + 450,50))     #Positions the money at the top middle of the screen
    screen.blit(rebirthText,rebirthTextRect)    #Draws it onto the screen (keep in the while loop to constantly update it)

    menuButton.draw_UIbutton(tinted_image_button)   #Draws the Menu Tab button to the screen

    #linking money buttons
    moneyUp1.link(moneyUp2)
    moneyUp2.link(moneyUp3)

    #linking rebirth buttons
    rebirthButton.link(rebirth1)
    rebirth1.link(rebirth2)

    #Drawing money upgrade buttons
    moneyUp1.draw_button('0.1 Money per tick', moneyGreen, subText)   #Draws the buttons onto the screen ([description], [colour], [text size])
    moneyUp2.draw_button('Multiplies money by \n   0.05 per tick', moneyGreen, subberText)
    moneyUp3.draw_button('Money boosts itself', moneyGreen, subberText)

    rebirthButton.draw_button('Rebirth', rebirthYellow, subText)
    rebirth1.draw_button('Multiply money by \n     0.25 per tick', rebirthYellow, subberText)
    rebirth2.draw_button('Decreases ticks per \n  second by 0.1', rebirthYellow, subberText)

    pygame.display.update()
    clock.tick(60)
