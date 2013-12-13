
class MenuItem (pygame.font.Font):
    
    def __init__(self,text, position,fontSize=36, antialias = 1, color = (255, 255, 255), background=None):
        pygame.font.Font.__init__(self,None, fontSize)
        self.text = text
        if background == None:
            self.textSurface = self.render(self.text,antialias,(255,255,255))
        else:
            self.textSurface = self.render(self.text,antialias,(255,255,255),background)
        self.position=self.textSurface.get_rect(centerx=position[0],centery=position[1])
    
    def get_pos(self):
        return self.position
    
    def get_text(self):
        return self.text
    
    def get_surface(self):
        return self.textSurface

class Menu:
    
    MENUCLICKEDEVENT = USEREVENT +1

    def __init__(self, menuEntries, menuCenter = None):
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.background = pygame.Surface(screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        self.active = False

        if pygame.font:
            fontSize = 36
            fontSpace= 4
            # font = pygame.font.Font(None, fontSize)

            menuHeight = (fontSize+fontSpace) * len(menuEntries)
            startY = self.background.get_height()/2 - menuHeight/2  

            #listOfTextPositions = list()
            self.menuEntries = list()
            
            for menuEntry in menuEntries:
                centerX = self.background.get_width()/2
                centerY = startY + fontSize + fontSpace
                newEnty = MenuItem(menuEntry,(centerX,centerY))
                self.menuEntries.append(newEnty)
                self.background.blit(newEnty.get_surface(), newEnty.get_pos())
                startY += fontSize + fontSpace

    def drawMenu(self):
        self.active = True            
        screen = pygame.display.get_surface()
        screen.blit(self.background, (0, 0))

    def isActive(self):
        return self.active
    
    def activate(self,):
        self.active = True
    
    def deactivate(self):
        self.active = False
    
    def handleEvent(self,event):
        if event.type == MOUSEBUTTONDOWN and isActive():
            # initiate with menu Item 0
            curItem = 0
            # get x and y of the current event 
            eventX = event.pos[0]
            eventY = event.pos[1]
            # for each text position 
            for menuItem in self.menuEntries:
                textPos = menuItem.get_pos()
                #if eventX > textPos.left and eventX < textPos.right and eventY > textPos.top and eventY

