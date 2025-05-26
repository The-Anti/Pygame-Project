import pygame
from sys import exit
import math
import threading
import time

width = 1400
height = 800

pygame.init()

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Incremental')
clock = pygame.time.Clock()

text = pygame.font.SysFont(None, 60)
subText = pygame.font.SysFont(None, 40)

#COLOURS
moneyGreen = (133, 187, 101)

money = 0

# Load and prepare the image
original_image = pygame.image.load('TabIcon.PNG').convert_alpha()
button_image = pygame.transform.scale(original_image, (60, 60))

#TIMINGS
oneStimer = pygame.USEREVENT + 1
pygame.time.set_timer(oneStimer, 1000)


# Tint function (simple multiply)
def tint_image(image, tint_color):
    tinted_image = image.copy()
    tint_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    tint_surface.fill(tint_color)
    tinted_image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted_image

#Button class
class button():
    def __init__(self, bWidth, bHeight, left, top, number, type, int):
        self.button = pygame.rect.Rect(left, top, bWidth, bHeight)
        self.display_text = text.render(f'{number}', True, 'BLACK')
        self.type = type.lower()
        self.int = int
        self.clicked = False
        self.flag = False

    def draw_button(self, description, colour):
        pygame.draw.rect(screen, colour, self.button, border_radius=20)  # Rounded corners
        self.display_text_rect = self.display_text.get_rect(center=(self.button.centerx, self.button.centery - 20))
        screen.blit(self.display_text, self.display_text_rect)
        self.renderSubText(desc = description)

    def renderSubText(self, desc):
        self.display_subtext = subText.render(f'{desc}', True, (0,0,0))
        self.subtext_rect = self.display_subtext.get_rect(center=(self.button.centerx, self.button.centery + 20))
        screen.blit(self.display_subtext, self.subtext_rect)

    def clickDetection(self):
        global money
        mousepos = pygame.mouse.get_pos()
        if self.button.collidepoint(mousepos) and self.clicked == False:
            self.clicked = True
            self.flag = True
            print(self.clicked)

    def moneyIncrement(self):
        global money
        while True:
            if self.flag == True:
                if self.type == 'add':
                    money += self.int
                if self.type == 'exp':
                    money *= self.int
            time.sleep(1)
                    
            
    



class UIbutton(button):
    def __init__(self, bWidth, bHeight, left, top):
        super().__init__(bWidth, bHeight, left, top, number='',type='',int=0)

    def draw_UIbutton(self, image):
        pygame.draw.rect(screen, (0,0,0), self.button, border_radius=5)
        screen.blit(image, self.button.center)

tinted_image_button = tint_image(button_image, (124,124,124))  # grey


moneyUp1 = button(300,120,550,550,1,'add',0.1)
moneyUp2 = button(300,120,550,200,2,'exp',1.05)

t1 = threading.Thread(target=moneyUp1.moneyIncrement, daemon=True)
t1.start()

t2 = threading.Thread(target=moneyUp2.moneyIncrement, daemon=True)
t2.start()

while True:
    screen.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            menuButton.clickDetection()
            moneyUp1.clickDetection()
            moneyUp2.clickDetection()

        #if event.type == oneStimer:
        #         moneyUp1.moneyIncrement()


    moneyText = text.render(f'£ {round(money,2)}', True, 'WHITE')
    moneyTextRect = moneyText.get_rect(center=(width/2,50))
    screen.blit(moneyText,moneyTextRect)

    menuButton = UIbutton(60,60,-10,100)
    menuButton.draw_UIbutton(tinted_image_button)

    moneyUp1.draw_button('0.1 Money per second', moneyGreen)
    moneyUp2.draw_button('Exponent 1.05 per seconde', moneyGreen)


    pygame.display.update()
    clock.tick(60)