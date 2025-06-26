import pygame
import time
import threading
import math

# Initialize
pygame.init()
screen = pygame.display.set_mode((1400, 800))
clock = pygame.time.Clock()

text = pygame.font.SysFont(None, 60)
subText = pygame.font.SysFont(None, 40)
subberText = pygame.font.SysFont(None, 30)
subbestText = pygame.font.SysFont(None, 20)

#abbreviating the money
millnames = ['',' k',' M',' B',' T',' Qa', ' Qn', ' Sx', ' Sp', ' Oc', ' No', ' De', ' UDe', ' DDe', ' TDe', ' QaDe', ' QnDe', ' SxDe', ' SpDe', ' ODe', ' NDe'
             ,' Vg', ' UVg', ' DVg', ' TVg', ' QaVg', ' QnVg', ' SxVg', ' SpVg', ' OVg', ' NVg', 'Tg']

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



#MOST IMPORTANT VARIABLES IN EXISTANCE DO NOT ERASE NOR CHANGE
#-----------------------------------------------
money = 0
rebirths = 0
tps = 1000
#-----------------------------------------------

moneyGreen = (133, 187, 101)


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
    def __init__(self, w, h, x, y, colour, number, desc, tSize, type, int, price, clicks, price_func=None):   #All the variables for the button
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
        self.flag = False       #Just a flag for threading
        self.price = price      #Variable for the price tag
        self.price_func = price_func    #Price scaling function
        self.ogPrice = price

    def draw_button(self, colour):   #Setting up the variables to draw the button
        if self.clicked == True:
            colour = (83,137,51)
        pygame.draw.rect(screen, colour, self.buttonRect, border_radius=20)

        self.buttonRect = self.button.get_rect(center = self.pos)
        screen.blit(self.button, self.buttonRect)
        self.numberDisplayRect = self.numberDisplay.get_rect(center = (self.buttonRect.centerx, self.buttonRect.centery - 50))
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
            self.display_subtext = subText.render(f'£{self.price}', True, (0,0,0))   #setting up the price text
        self.priceText_rect = self.display_subtext.get_rect(center=(self.buttonRect.centerx, self.buttonRect.centery + 30))  #setting up the position of the price text
        screen.blit(self.display_subtext, self.priceText_rect)  #drawing the price text

    def get_center(self):
        return self.buttonRect.center

    def link(self,y):
        pygame.draw.line(screen, (255,255,255), self.buttonRect.center, y.get_center(), 20)

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
            print('Clicked')
            if self.clicks == (self.maxClicks - 1):
                self.clicked = True     #Sets the clicked value to true and turns flag on
            self.flag = True
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


# Load tileable background image
tile_image = pygame.image.load('croppedBG1.png').convert()
tile_size = tile_image.get_size()

#w, h, x, y, colour, number, desc, tSize, type, int, price, clicks, price_func

                                                #No arguments to add


# Camera
camera = pygame.Vector2(0, 0)
dragging = False
money = 0
moneyUp1 = button(300, 150, 550, 550, moneyGreen, 1, '0.1 Money per tick', subText, 'add', 0.1, 0, 5, price_func=b1Func)
moneyUp2 = button(300, 150, 550, 850, moneyGreen, 2, 'Multiplies money by 0.5', subText, 'mult', 0.05, 1, 3, price_func=b2Func)

moneyButtons = [moneyUp1, moneyUp2]
t1 = threading.Thread(target=moneyUp1.moneyIncrement, daemon=True)  #Creates a thread that targets the button, specifically the moneyIncrement function.
t1.start()          
while True:

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

    moneyText = text.render(f'£ {millify(money)}', True, 'WHITE')   #Shows the value of the money (and rounds it to two decimal places)
    text_pos = pygame.Vector2(550, 300) - camera
    variable_rect = moneyText.get_rect(center=text_pos)
    screen.blit(moneyText, variable_rect)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            for i in moneyButtons:
                i.clickDetection(pygame.Vector2(event.pos), camera)

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

    moneyUp1.link(moneyUp2)

    for i in moneyButtons:
        i.changePos(camera)
        i.draw_button(moneyGreen)

    pygame.display.flip()
