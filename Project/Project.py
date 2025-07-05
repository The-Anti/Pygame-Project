import pygame, random
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
             ,' Vg', ' UVg', ' DVg', ' TVg', ' QaVg', ' QnVg', ' SxVg', ' SpVg', ' OVg', ' NVg', ' Tg', ' UTg', ' DTg', ' TTg', ' QaTg', ' QnTg', ' SxTg', ' SpTg'
             , ' OTg', ' NTg', ' Qag', ' UQag', ' DQag', ' TQag', ' QaQg', ' QnQag', ' SxQag', ' SpQag', ' OQag', ' NQag', ' Qng']

def millify(n):
    n = float(n)
    if n == float('inf'):
        return n
    else:
        millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
    if n < 1000:
        return '{:.2f}{}'.format(n / 10**(3 * millidx), millnames[millidx])
    else:
        return '{:.1f}{}'.format(n / 10**(3 * millidx), millnames[millidx])



#Setting up the important stuff
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Incremental')
clock = pygame.time.Clock()


#background stuff
WORLD_SIZE = (10000, 10000)
background = pygame.Surface(WORLD_SIZE)

tile_image = pygame.image.load('croppedBG1.png').convert()
tile_size = tile_image.get_size()

dragging = False

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
rebirthFlag = False
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
    #w, h, x, y, colour, number, desc, tSize, type, int, price, clicks, price_func
    def __init__(self, w, h, x, y, colour, number, desc, tSize, type, int, price, clicks, price_func=None, prevButton = None):   #All the variables for the button
        self.button = pygame.Surface((w,h),pygame.SRCALPHA)
        self.number = number
        self.colour = colour
        self.startingpos = pygame.Vector2(x,y)
        self.buttonRect = self.button.get_rect(center = self.startingpos)
        self.numberDisplay = subText.render(f'{number}', True, 'Black')
        if tSize == text:
            self.desc = text.render(desc, True, 'Black')
            text.metrics()
        elif tSize == subText:
            self.desc = subText.render(desc, True, 'Black')
        elif tSize == subberText:
            self.desc = subberText.render(desc, True, 'Black')
        else:
            self.desc = subbestText.render(desc, True, 'Black')
        self.type = type.lower()        #Variable for the type of button (exponential, additive, multiplicitive...)
        self.int = int      #Variable for the value of the button
        self.clicks = 0     #how many times you clicked
        self.maxClicks = clicks #how many times you can click
        self.clicked = False    #Boolean to check if button is clicked
        self.clickFlag = False       #Just a flag for threading
        self.price = price      #Variable for the price tag
        self.price_func = price_func    #Price scaling function
        self.ogPrice = price
        self.prev = prevButton
        self.previous = None
        self.prevFlag = False
        self.drawFlag = False

    def draw_button(self, colour):   #Setting up the variables to draw the button
        if self.clicked == True:
            colour = (83,137,51)

        if self.drawFlag:
            pygame.draw.rect(screen, colour, self.buttonRect, border_radius=20)
            self.buttonRect = self.button.get_rect(center = self.pos)
            screen.blit(self.button, self.buttonRect)
            self.numberDisplayRect = self.numberDisplay.get_rect(center = (self.buttonRect.centerx, self.buttonRect.centery - 40))
            screen.blit(self.numberDisplay, self.numberDisplayRect)
            self.descRect = self.desc.get_rect(center = (self.buttonRect.centerx, self.buttonRect.centery))
            screen.blit(self.desc, self.descRect)
            self.draw_price()

            self.upgradeCount = subberText.render(f'{self.clicks}/{self.maxClicks}', True, 'BLACK')
            self.upgradeCountRect = self.upgradeCount.get_rect(topright = (self.buttonRect.centerx+140, self.buttonRect.centery-55))
            screen.blit(self.upgradeCount, self.upgradeCountRect)


    def draw_price(self):     #Setting up the price box
        if self.price <= 0:     #If upgrade is free then display it to be free
            self.display_subtext = subText.render('Free', True, (0,0,0))
        elif self.clicks == self.maxClicks:
            self.display_subtext = subText.render('Max', True, (0,0,0)) #If its maxxed out then say its maxxed out
        else: 
            self.display_subtext = subText.render(f'£{millify(self.price)}', True, (0,0,0))   #setting up the price text
        self.priceText_rect = self.display_subtext.get_rect(center=(self.buttonRect.centerx, self.buttonRect.centery + 40))  #setting up the position of the price text
        screen.blit(self.display_subtext, self.priceText_rect)  #drawing the price text

    def get_center(self):
        return self.buttonRect.center

    def getPrev(self):
        if self.prev == None:
            self.drawFlag = True
        elif self.prev != None and len(previousMoneyButtons) != 0:
            if self.prev in previousMoneyButtons:
                self.previous = moneyButtons[self.prev-1]
                self.drawFlag = True

    def link(self):
        if self.prev != None and self.previous != None:
            pygame.draw.line(screen, (255,255,255), self.buttonRect.center, self.previous.get_center(), 20)

    def setPos(self):
        self.pos = pygame.Vector2(self.startingpos)
        self.virtualpos = pygame.Vector2(self.startingpos)

    def changePos(self, camera):
        self.setPos()
        self.pos -= camera
        self.buttonRect = self.button.get_rect(center = self.pos)

    def hitboxDetect(self, camera):
        self.setPos()
        self.virtualpos -= camera
        self.buttonRect = self.button.get_rect(center=self.virtualpos)        

    #Click detection and money increment system
    def clickDetection(self, mousepos, camera):   #This is in the events area so only runs when you click the mouse button
        global money
        self.hitboxDetect(camera)
        if self.buttonRect.collidepoint(mousepos) and self.clicked == False and money >= self.price:    #If mouse is over a button, you can click it and you have enough money then...
            if self.clicks == (self.maxClicks - 1):
                self.clicked = True     #Sets the clicked value to true and turns flag on
            self.clickFlag = True
            money -= self.price
            self.clicks += 1
            self.prevFlag = True
            if self.clicks == 1 and self.prevFlag == True:
                previousMoneyButtons.append(self.number)

            if self.price_func:
                self.price = round(self.price_func(self.price, self.clicks), 2)
            return self.button
        

    def moneyIncrement(self):   #Used in the threading, just increases the money by a set amount
        global money
        global tps
        while True:
            if self.clickFlag == True:   #When button has been pressed
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
        self.clickflag = False
        self.price = self.ogPrice    #MAIN BUTTON THINGS
#----------------------------------------------------------------------------------------------------------------------



#UI BUTTONS CLASS (inheriting the button class)
#-------------------------------------------------------------------------------
class UIbutton(button):
    def __init__(self, w, h, x, y):
        super().__init__(w, h, x, y, colour='', number='',desc='',tSize='',type='',int=0, price=0, clicks=0) #Setting up the button
        self.button = pygame.Surface((w,h),pygame.SRCALPHA)
        self.buttonRect = self.button.get_rect(center = (x,y))
        self.clicked = False    #Boolean to check if button is clicked

    def draw_UIbutton(self, image):
        pygame.draw.rect(screen, (255,255,255), self.buttonRect, border_radius=5) #Draws the button
        screen.blit(image, self.buttonRect.topleft)  #Blits the correct image onto the button

    #Click detection and money increment system
    def clickDetection(self):   #This is in the events area so only runs when you click the mouse button
        global money
        mousepos = pygame.mouse.get_pos()   #Gets position of the mouse
        if self.buttonRect.collidepoint(mousepos) and self.clicked == False:
            print('Menu Clicked')
            self.flag = True



tinted_image_button = tint_image(button_image, (124,124,124))  #Tints a button image gray
#-------------------------------------------------------------------------------



#REBIRTH BUTTON CLASS (inheriting the button class)
#-------------------------------------------------------------------------------
class rButton(button):
    def __init__(self, w, h, x, y, colour, number, desc, tSize, type, int, price, clicks, price_func=None, prevButton = None):   #All the variables for the button
        super().__init__(w, h, x, y, colour, number,desc, tSize, type, int, price, clicks, price_func, prevButton)
        self.tick_upgrade_purchased = False
        self.numberDisplay = subText.render(f'г{number}', True, 'Black')

    def draw_button(self, colour):   #Setting up the variables to draw the button
        if self.clicked == True:
            colour = (205, 124, 16)

        if self.drawFlag:
            pygame.draw.rect(screen, colour, self.buttonRect, border_radius=20)
            self.buttonRect = self.button.get_rect(center = self.pos)
            screen.blit(self.button, self.buttonRect)
            self.numberDisplayRect = self.numberDisplay.get_rect(center = (self.buttonRect.centerx, self.buttonRect.centery - 40))
            screen.blit(self.numberDisplay, self.numberDisplayRect)
            self.descRect = self.desc.get_rect(center = (self.buttonRect.centerx, self.buttonRect.centery))
            screen.blit(self.desc, self.descRect)
            self.draw_price()
    
            global rebirths
            if self.type == 'rebirth':  #If its the rebirth button
                if money / self.price >= 0.5:         #if you have enough for the rebirth
                    self.rebirthCount = subberText.render(f'{millify(pow((money/self.price), 0.95))}', True, 'BLACK')       #displays how much you will get from it
                    self.rebirthCountRect = self.rebirthCount.get_rect(topright = (self.buttonRect.centerx+140, self.buttonRect.centery-55))
                    screen.blit(self.rebirthCount, self.rebirthCountRect)
            else:   #if its a rebirth upgrade button
                self.upgradeCount = subberText.render(f'{self.clicks}/{self.maxClicks}', True, 'BLACK')     #display how many times u can upgrade it
                self.upgradeCountRect = self.upgradeCount.get_rect(topright = (self.buttonRect.centerx+140, self.buttonRect.centery-55))
                screen.blit(self.upgradeCount, self.upgradeCountRect)

    def draw_price(self):     #Setting up the price box
        if self.price <= 0:     #If upgrade is free then display it to be free
            self.display_subtext = subText.render('Free', True, (0,0,0))
        elif self.clicks == self.maxClicks:
            self.display_subtext = subText.render('Max', True, (0,0,0)) #If its maxxed out then say its maxxed out
        elif self.type == 'rebirth': 
            self.display_subtext = subText.render(f'£{millify(self.price)}', True, (0,0,0))   #Have it show you can buy it with money if its the rebirth button
        else:
            self.display_subtext = subText.render(f'Г {millify(self.price)}', True, (0,0,0))   #Show you have to spend rebirth tokens to buy it
        self.priceText_rect = self.display_subtext.get_rect(center=(self.buttonRect.centerx, self.buttonRect.centery + 40))  #setting up the position of the price text
        screen.blit(self.display_subtext, self.priceText_rect)  #drawing the price text

    def getPrev(self):
        if self.prev == None:
            self.drawFlag = True
        elif self.prev != None and len(previousRebirthButtons) != 0:
            if self.prev in previousRebirthButtons:
                self.previous = rebirthButtons[self.prev]
                self.drawFlag = True

    def link(self):
        if self.prev != None and self.previous != None:
            pygame.draw.line(screen, (255,255,255), self.buttonRect.center, self.previous.get_center(), 20)

    def clickDetection(self, mousepos, camera):   #This is in the events area so only runs when you click the mouse button
        global money
        global rebirths
        global rebirthFlag
        self.hitboxDetect(camera)
        if self.type == 'rebirth':
            if self.buttonRect.collidepoint(mousepos) and self.clicked == False and money >= self.price:    #If mouse is over a button, you can click it and you have enough money then...
                rebirths += round(pow((money/self.price), 0.95),2)  #turns money into rebirths
                money = 0
                if rebirths > 0 and rebirthFlag == False:
                    previousRebirthButtons.append(self.number)
                    rebirthFlag = True
                for i in moneyButtons:  #when rebirthed, resets all the money buttons
                    i.resetButton()
        else:
            if self.buttonRect.collidepoint(mousepos) and self.clicked == False and rebirths >= self.price:   #Checks if you can click the upgrade and have enough rebirths
                if self.clicks == (self.maxClicks - 1):
                    self.clicked = True
                if self.type == 'tick':     #Just checks if you bought an upgrade that changes the tick
                    self.tick_upgrade_purchased = True  #If you did, says that you did
                self.clickFlag = True
                rebirths -= self.price
                self.clicks += 1
                self.prevFlag = True
                if self.clicks == 1 and self.prevFlag == True:
                    previousMoneyButtons.append(self.number)                
                if self.price_func:
                    self.price = round(self.price_func(self.price, self.clicks), 2)



    def moneyIncrement(self):   #Used in the threading, just increases the money by a set amount
        global money
        global tps
        while True:
            if self.clickFlag == True:   #When button has been pressed
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
    
def snowball(curp, clicks):
    if clicks < 3:
        return curp * 1.05
    if clicks < 6:
        return curp * 1.2
    if clicks < 9:
        return curp * 1.5
    else: return curp * 1.8
    

camera = pygame.Vector2(0, 0)


#BUTTONS WILL GO HERE
#BUTTON VARIABLES ([Width], [Height], [x pos], [y pos], [Colour], [Button number], [Description], [Text size], [Type], [Value], [Price], [Clicks], [Price function (default = None)])
#Type = add (additive), mult (multiplicitive), exp (exponential), tick (changes ticks per second [input in ms])
#-------------------------------------------------------------------------------
# £ MONEY BUTTONS
moneyUp1 = button(300, 120, 550, 550, moneyGreen, 1, 'Adds 0.1 per tick', subText, 'add', 10.1, 0, 5, price_func=b1Func)         
moneyUp2 = button(300,120,550,325, moneyGreen, 2, 'Multiplies money by \n        0.02 per tick', subberText, 'mult',0.02,1,5, price_func=b2Func, prevButton=1)       #Don't forget to THREAD EACH BUTTON
moneyUp3 = button(300,120,550,100, moneyGreen,3, 'Add 0.5 per tick', subText, 'add', 0.5, 3, 10, price_func = snowball, prevButton=2)            #And to ADD THE CLICK DETECTION AND DRAW THE BUTTON IN THE WHILE LOOP
moneyUp4 = button(300,120,200,-125, moneyGreen,4, 'Multiplies money by \n    0.05 per tick', subberText, 'mult', 0.1, 8, 10, price_func=default, prevButton=3)            #And to ADD THE CLICK DETECTION AND DRAW THE BUTTON IN THE WHILE LOOP
moneyUp5 = button(300,120,900,-125, moneyGreen,5, 'Money boosts itself', subText, 'exp', 0.05, 15, 1, prevButton=3)            #And to ADD THE CLICK DETECTION AND DRAW THE BUTTON IN THE WHILE LOOP

#Class for buttons
moneyButtons = [moneyUp1, moneyUp2, moneyUp3, moneyUp4, moneyUp5]
previousMoneyButtons = []

#REBIRTH BUTTONS
rebirthButton = rButton(300,120,2000,550,rebirthYellow,0,'Rebirth',subText,'rebirth', 0, 100, 2)
rebirth1 = rButton(300,120,2000,325,rebirthYellow,1,'Multiply money by \n     0.02 per tick', subberText, 'mult', 0.02, 1, 25, price_func=default, prevButton=0)
rebirth2 = rButton(300,120,2350,550,rebirthYellow,2,'Decreases ticks per \n  second by 0.05', subberText, 'tick', 50, 3, 10, price_func=default, prevButton=0)
rebirth3 = rButton(300,120,2000,775,rebirthYellow,3,'Money boosts itself by \n      0.01', subberText, 'exp', 0.01, 5, 100, price_func=default, prevButton=0)

#Class for rebirth buttons
rebirthButtons = [rebirthButton, rebirth1, rebirth2, rebirth3]
previousRebirthButtons = []

#UI BUTTONS
menuButton = UIbutton(60,60,30,100)    #UI BUTTON VARIABLES ([Width], [Height], [X], [Y])
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
t4 = threading.Thread(target=moneyUp4.moneyIncrement, daemon=True)  #Always have daemon set to true
t4.start()                                                          #The .start() just starts the thread when it sees the flag has been turned on (button is pressed)
t5 = threading.Thread(target=moneyUp5.moneyIncrement, daemon=True)
t5.start()


#Rebirth button threading
tr1 = threading.Thread(target=rebirth1.moneyIncrement, daemon=True)  #Always have daemon set to true
tr1.start()                                                          #The .start() just starts the thread when it sees the flag has been turned on (button is pressed)
tr2 = threading.Thread(target=rebirth2.moneyIncrement, daemon=True)
tr2.start()
tr3 = threading.Thread(target=rebirth3.moneyIncrement, daemon=True)
tr3.start()
#-------------------------------------------------------------------------------

#Main game loop
while True:
    screen.fill((0,0,0))

    # Determine visible area
    screen_rect = pygame.Rect(camera.x, camera.y, *screen.get_size())

    if camera.x <= -3000:
        camera.x = -3000
    if camera.x >= 13000:
        camera.x = 13000
    if camera.y <= -3000:
        camera.y = -3000
    if camera.y >= 13000:
        camera.y = 13000

    # Get tile range to draw based on camera view
    start_x = int(screen_rect.left // tile_size[0])
    end_x = int(screen_rect.right // tile_size[0]) + 1
    start_y = int(screen_rect.top // tile_size[1])
    end_y = int(screen_rect.bottom // tile_size[1]) + 1

    for x in range(start_x, end_x):
        for y in range(start_y, end_y):
            tile_pos = pygame.Vector2(x * tile_size[0], y * tile_size[1])
            draw_pos = tile_pos - camera
            screen.blit(tile_image, draw_pos)

    for event in pygame.event.get():    #Event system
        if event.type == pygame.QUIT:   #If you leave the game, close the game
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:    #When you click, things below happen.
            #ALL CLICK DETECTION WILL GO HERE
            #-------------------------------------------------------------------------------
            menuButton.clickDetection()

            for i in moneyButtons:
                i.clickDetection(pygame.Vector2(event.pos), camera)

            for i in rebirthButtons:
                i.clickDetection(pygame.Vector2(event.pos), camera)

            # rebirthButton.clickDetection()
            #-------------------------------------------------------------------------------

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            dragging = True
            last_mouse_pos = pygame.Vector2(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            dragging = False
        elif event.type == pygame.MOUSEMOTION and dragging:
            mouse_pos = pygame.Vector2(event.pos)
            delta = mouse_pos - last_mouse_pos
            camera -= delta
            last_mouse_pos = mouse_pos


    #Making the money visible on the screen
    moneyText = text.render(f'£ {millify(money)}', True, 'WHITE')   #Shows the value of the money (and rounds it to two decimal places)
    text_pos = pygame.Vector2(550, 750) - camera
    moneyText_rect = moneyText.get_rect(center=text_pos)
    screen.blit(moneyText, moneyText_rect)

    #Making rebirths visble on the screen
    rebirthText = text.render(f'Г {millify(rebirths)}', True, 'WHITE')   #Shows the value of the money (and rounds it to two decimal places)
    text_pos = pygame.Vector2(1700, 550) - camera
    rebirthText_rect = rebirthText.get_rect(center=text_pos)
    screen.blit(rebirthText, rebirthText_rect)

    menuButton.draw_UIbutton(tinted_image_button)   #Draws the Menu Tab button to the screen

    #Drawing money upgrade buttons
    for i in moneyButtons:
        i.getPrev()
        i.link()

    for i in moneyButtons:
        i.changePos(camera)
        i.draw_button(moneyGreen)

    for i in rebirthButtons:
        i.getPrev()
        i.link()

    for i in rebirthButtons:
        i.changePos(camera)
        i.draw_button(rebirthYellow)


    pygame.display.flip()
    clock.tick(60)
