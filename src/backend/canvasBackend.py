import pygame
import sys
import firebase_admin
import datetime
import base64
import random
from firebase_admin import credentials, db, storage, initialize_app
from google.oauth2 import service_account

class Pixel:

    def __init__(self, x, y, color, message):
        self.x = x
        self.y = y
        self.color = color
        self.message = message

    def __str__(self):
        return f"Pixel at ({self.x}, {self.y}) with color {self.color} and message: {self.message}"

firebase_credentials = credentials.Certificate('csc305-canvas-map-firebase-adminsdk-tyup6-e975a68617.json')
firebase_app = firebase_admin.initialize_app(firebase_credentials, {
    'databaseURL' : 'https://csc305-canvas-map-default-rtdb.firebaseio.com',
    'storageBucket': 'csc305-canvas-map.appspot.com'
})

### CANVAS


pygame.init()

### CONSTANTS
PIXEL_SIZE = 5
WIDTH = 150*PIXEL_SIZE
HEIGHT = 150*PIXEL_SIZE
TICKRATE = 5

RED1 = (225,30,100)        #Ceris Red
RED2 = (240,40,50)         #Red
ORANGE1 = (250,95,50)      #Orange
ORANGE2 = (245,155,45)     #Sea Bucklthorn
ORANGE3 = (250,180,70)     #Casablanca (Yellow Orange)
YELLOW1 = (255,235,50)     #Yellow
YELLOW2 = (220,225,35)     #Pear
YELLOW3 = (150,200,70)     #Atlantis (yellow with some green)
GREEN1 = (70,185,80)       #Chateau-Green
GREEN2 = (15,150,80)       #Green
GREEN3 = (15,115,70)       #Jewel
BLUE1 = (80,195,190)       #Fountain Blue
BLUE2 = (70,180,230)       #Piction Blue
BLUE3 = (25,125,195)       #Denim
BLUE4 = (40,40,105)        #Jacarta
PURPLE1 = (110,55,150)     #Royal Purple
PURPLE2 = (150,55,150)     #Plum
PURPLE3 = (160,35,120)     #Hibiscus
BLACK = (0,0,0)
WHITE = (255,255,255)

IMAGE_PATH = "canvas.png"
LOCAL_IMAGE_PATH = "canvas.png"

BUCKET = storage.bucket(app=firebase_app)

COLORTEST = False
RANDOMTEST = False

### OTHER VARS

TickReady = True #bool to check if the next tick is ready to be fired
pixelQueue = []  #Queue of pixels to be placed, fetched from the firebase based on TICKRATE
uploadImage = False

colorList = [RED1,RED2,ORANGE1,ORANGE2,ORANGE3,YELLOW1,YELLOW2,YELLOW3,GREEN1,GREEN2,GREEN3,BLUE1,BLUE2,BLUE3,BLUE4,PURPLE1,PURPLE2,PURPLE3,BLACK,WHITE]
colorListTable = ["RED1","RED2","ORANGE1","ORANGE2","ORANGE3","YELLOW1","YELLOW2","YELLOW3","GREEN1","GREEN2","GREEN3","BLUE1","BLUE2","BLUE3","BLUE4","PURPLE1","PURPLE2","PURPLE3","BLACK","WHITE"]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Canvas")

drawing_surface = pygame.Surface((WIDTH, HEIGHT))
drawing_surface.fill(WHITE)

def draw_pixel(x, y, color):
    pygame.draw.rect(drawing_surface, colorList[colorListTable.index(color)], (x*PIXEL_SIZE, y*PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
    pygame.display.flip()

running = True

if(COLORTEST == True):
    
    x = 0
    y = 0
    for i in colorList:
        for y in range(0,25):
            draw_pixel(25+x, 25+y, i)
        x += 1

while running:

    if(RANDOMTEST == True and datetime.datetime.now().second % 3 == 0):
        randX = random.randint(0, 150)
        randY = random.randint(0, 150)
        randColor = random.randint(0,len(colorList)-2)
        draw_pixel(randX,randY,colorListTable[randColor])
        #draw_pixel(randX,randY,"RED1")
        
    if(len(pixelQueue) > 0):
        for tempPixel in pixelQueue:
            draw_pixel(tempPixel.x, tempPixel.y, tempPixel.color)
            print(tempPixel)
        pixelQueue = []
        uploadImage == False
        pygame.image.save(screen, "canvas.png")
        print("Screenshot saved at", datetime.datetime.now().second)  

        #Upload Image to file
        blob = BUCKET.blob(IMAGE_PATH)
        blob.metadata = {"firebaseStorageDownloadTokens": "1"}
        blob.upload_from_filename(LOCAL_IMAGE_PATH)
        blob.update()

    if(datetime.datetime.now().second % TICKRATE == 0 and TickReady): # When time aligns with TICKRATE and tick is ready to fire pull from the queue in Firebase DB

        if(RANDOMTEST == True):
            tempPixel = Pixel(25, 25, "RED1", "No Message")
            pixelQueue.append(tempPixel)
            
            
        ref = db.reference('Queue')
        TickReady = False
        print(TICKRATE, "Seconds passed!")
        data = ref.get()
        if(data is not None):
            pixelQueue = []
            for key, value in data.items():
                x = value.get('X', 0)                         # Default to 0 if 'X' is not present
                y = value.get('Y', 0)                         # Default to 0 if 'Y' is not present
                color = value.get('Color', 'WHITE')           # Default to 'WHITE' if 'Color' is not present
                message = value.get('Message', 'No message')  # Default to 'No message' if 'Message' is not present
                pixel = Pixel(x, y, color, message)
                pixelQueue.append(pixel)
            ref.delete()
        else:
            print("empty queue")
        
    elif(datetime.datetime.now().second % TICKRATE != 0 and TickReady == False): # When time is off of the TICKRATE, allow a new tick to be fired
        TickReady = True
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            draw_pixel(int(mouse_x/PIXEL_SIZE), int(mouse_y/PIXEL_SIZE), "RED2")
        #elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        #    pygame.image.save(screen, "canvas.png")
        #    print("Screenshot saved at", datetime.datetime.now().second)
    
    screen.blit(drawing_surface, (0, 0))

    pygame.display.flip()

pygame.quit()
sys.exit()
