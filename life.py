import pygame
import sys
from random import randint

pygame.init()
UNIVERSE_WIDTH = 800
UNIVERSE_HEIGHT = 600
screen = pygame.display.set_mode((UNIVERSE_WIDTH, UNIVERSE_HEIGHT))
pygame.display.set_caption('Microverse')
done = False
extinction_list = []

class entity(object):
    name = ''
    objtype = ''
    color = (0, 128, 255)

    x = 30
    y = 30
    size = 10
    
    def __init__(self, objtype, name, size, color, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, self.size, self.size))

    def move(self, xchange, ychange):
        self.x += xchange
        self.y += ychange
        if(self.x + self.size >= UNIVERSE_WIDTH): self.x = UNIVERSE_WIDTH - self.size
        if(self.x < 0): self.x = 0
        if(self.y + self.size >= UNIVERSE_HEIGHT): self.y = UNIVERSE_HEIGHT - self.size
        if(self.y < 0): self.y = 0

    def getRect(self):
        rectsize = self.size if self.size >= 3 else 3
        return pygame.Rect(self.x, self.y, rectsize, rectsize)

    def CheckCollision(self, oobj):
        return self.getRect().colliderect(oobj.getRect())

#Double cell life, never grows but able to self-replicate
class cubeanoid(entity):
    targetx = 0
    targety = 0

    max_energy = 10000
    energy = 5000

    energy_expenditure = 1

    is_dead = False
    
    def __init__(self, name, x, y):
        self.targetx = x
        self.targety = y
        print(name + ": I'm Alive!")
        entity.__init__(self, "cubenoid", name, 2, (0,128,255), x, y)

    def getNewTarget(self):
        self.targetx = randint(0, UNIVERSE_WIDTH - self.size)
        self.targety = randint(0, UNIVERSE_HEIGHT - self.size)
    
    def eat(self, energy_value):
        self.energy += energy_value - self.energy_expenditure

    def NeedToMove(self):
        if(self.energy <= self.max_energy / 2):
            return True
        else:
            return False

    def WantToMove(self):
        if(self.energy > 1000):
            return randint(0, 1)
        else:
            return self.NeedToMove()

    def move(self):
        if(self.energy >= self.max_energy):
            self.energy -= self.energy_expenditure
            
        elif(self.energy <= 0):
            self.is_dead = True
            print(self.name + " died. RIP.")
            return
        
        if(self.x == self.targetx and self.y == self.targety and (self.NeedToMove() or self.WantToMove())):
            self.getNewTarget()
        movx = 0
        movy = 0
        difx = self.targetx - self.x
        dify = self.targety - self.y
        if(self.targetx < self.x): movx = -3 if difx < -2 else difx
        if(self.targetx > self.x): movx = 3 if difx > 2 else difx
        if(self.targety < self.y): movy = -3 if dify < -2 else dify
        if(self.targety > self.y): movy = 3 if dify > 2 else dify
        expval = movx if movx > movy else movy
        self.energy -= self.energy_expenditure * expval
        super(cubeanoid, self).move(movx, movy)

    def CanSplit(self):
        return self.energy >= self.max_energy - 1000

#Static, unmoving creature that absorbs anything stupid enough to crawl inside.
#Will grow and shrink based on energy.
class BigRed(entity):
    max_energy = 20000
    energy = 10000
    hunger = 10000
    size = 10
    energy_expenditure = 2
    eat_ependiture = 1

    is_dead = False

    def __init__(self, name, x, y):
        print(name + ": I Live.")
        entity.__init__(self, "cubenoid", name, self.size, (255,0,0), x, y)

    def need_to_eat(self):
        if(self.energy <= self.max_energy / 2):
            return True
        else:
            return False
    
    def eat(self, energy_value):         
        self.energy += (energy_value / 2) - self.eat_ependiture
        self.size += 2
        self.hunger -= energy_value / 2
        self.x -= 1
        self.y -= 1
        if(self.energy >= self.max_energy):
            pass #marker for something to happen at full energy.

    def process(self):
        self.energy -= self.energy_expenditure
        self.hunger += 1
        if(self.hunger == 0 or self.size == 0 or self.energy == 0):
            is_dead = True
            return

        if(self.energy <= self.max_energy / 3):
            self.size -= 2
            self.hunger += 1
            self.energy -= max_energy / self.size
            self.x += 1
            self.y += 1
        
class food(entity):
    energy = 200
    
    def __init__(self, name, x, y):
        entity.__init__(self, "food", name, 1, (0,255,0),  x, y)
    

cubeanoids = [cubeanoid("Adam", 30, 30), cubeanoid("Eve", 100, 250)]
food_available = []
big_reds = [BigRed("BigRed", UNIVERSE_WIDTH / 2, UNIVERSE_HEIGHT / 2)]

def SpawnFood():
    x = randint(0, UNIVERSE_WIDTH - 5)
    y = randint(0, UNIVERSE_HEIGHT - 5)
    food_available.append(food("food" + str(len(food_available)), x, y))


#Randomly add some food...
for i in range(50): SpawnFood()

clock = pygame.time.Clock()

def CheckExtinctions():
    if("cubenoid" not in extinction_list):
        if len(cubeanoids) == 0:
            print("Cubeanoids are extinct.")
            extinction_list.append("cubenoid")
            
    if("big_red" not in extinction_list):
        if len(big_reds) == 0:
            print("Big Reds are extinct.")
            extinction_list.append("big_red")

while not done:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if(event.type == pygame.QUIT):
            done = True
            pygame.quit()
            sys.exit()

    for cn in cubeanoids:
        for f in food_available:
            if(cn.CheckCollision(f) > 0):
                cn.eat(f.energy)
                food_available.remove(f)

        if(cn.is_dead):
            cubeanoids.remove(cn)
        else:
            if(cn.CanSplit()):
                cubeanoids.append(cubeanoid(str(cn.name) + str(len(cubeanoids)), cn.x + cn.size, cn.y + cn.size))
                cn.energy = cn.energy / 2
            cn.move()
            cn.draw()

    for bg in big_reds:
        if(bg.need_to_eat()):
            for cn in cubeanoids:
                if(bg.CheckCollision(cn) > 0):
                    bg.eat(cn.energy)
                    print(cn.name + " was eaten by " + bg.name)
                    cubeanoids.remove(cn)           
        bg.process()
        if(bg.is_dead):
            big_reds.remove(bg)
        else:
            bg.draw()

    for f in food_available: f.draw()

    CheckExtinctions()
    SpawnFood()
    pygame.display.flip()
    clock.tick(60)


