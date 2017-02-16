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

class base_object(object):
    name = ''
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

    def getRect(self):
        rectsize = self.size if self.size >= 3 else 3
        return pygame.Rect(self.x, self.y, rectsize, rectsize)

    def CheckCollision(self, oobj):
        return self.getRect().colliderect(oobj.getRect())

class food(base_object):
    energy = 200    
    def __init__(self, name, x, y):
        base_object.__init__(self, "food", name, 1, (0,255,0), x, y)
        
class entity(base_object):
    is_dead = False
    max_energy = 1
    energy = 1
    energy_expenditure = 1
    
    def __init__(self, objtype, name, size, color, x, y, max_energy, start_energy, living_energy_expenditure):
        self.max_energy = max_energy
        self.energy = start_energy
        self.energy_expenditure = living_energy_expenditure
        base_object.__init__(self, objtype, name, size, color, x, y)

class animal(entity):
    targetx = 0
    targety = 0
    velocity = 1
    current_attention_span = 0
    max_attention_span = 10000
    
    def __init__(self, objtype, name, size, color, x, y, max_energy, start_energy, living_energy_expenditure, velocity):
        self.targetx = x
        self.targety = y
        self.velocity = velocity
        entity.__init__(self, objtype, name, size, color, x, y, max_energy, start_energy, living_energy_expenditure)

    def getNewTarget(self):
        self.targetx = randint(0, UNIVERSE_WIDTH - self.size)
        self.targety = randint(0, UNIVERSE_HEIGHT - self.size)

    def eat(self, energy_value):
        self.energy += energy_value - self.energy_expenditure

    def need_to_eat(self):
        if(self.energy <= self.max_energy): # / 2):
            return True
        else:
            return False

    def want_to_eat(self):
        if(self.need_to_eat()):
            return True
        else:
            if(self.current_attention_span == 0):
                return bool(randint(0, 1))
            else:
                return False
        
    def NeedToMove(self):
        if(self.energy <= self.max_energy / 2):
            return True
        else:
            return False

    def WantToMove(self):
        if(self.energy > 1000):
            return bool(randint(0, 1))
        else:
            return self.NeedToMove()

    def Wanna(self):
        if(self.current_attention_span == 0):
            return bool(randint(0, 1))
        else:
            return False

    def move(self):
        movx = 0
        movy = 0
        difx = self.targetx - self.x
        dify = self.targety - self.y
        if(self.targetx < self.x): movx = -self.velocity if difx < -self.velocity - 1 else difx
        if(self.targetx > self.x): movx = self.velocity if difx > self.velocity - 1 else difx
        if(self.targety < self.y): movy = -self.velocity if dify < -self.velocity - 1 else dify
        if(self.targety > self.y): movy = self.velocity if dify > self.velocity - 1 else dify
        expval = movx if movx > movy else movy
        self.energy -= self.energy_expenditure * expval

        self.x += movx
        self.y += movy
        if(self.x + self.size >= UNIVERSE_WIDTH): self.x = UNIVERSE_WIDTH - self.size
        if(self.x < 0): self.x = 0
        if(self.y + self.size >= UNIVERSE_HEIGHT): self.y = UNIVERSE_HEIGHT - self.size
        if(self.y < 0): self.y = 0

    def process(self):
        if(self.current_attention_span > 0): self.current_attention_span -= 1

#Double cell life, never grows but able to self-replicate
class cubeanoid(animal):
    
    def __init__(self, name, x, y):
        print(name + ": I'm Alive!")
        animal.__init__(self, "cubenoid", name, 2, (0,128,255), x, y, 10000, 5000, 1, 3)

    def move(self):
        if(self.energy >= self.max_energy):
            self.energy -= self.energy_expenditure
            
        elif(self.energy <= 0):
            self.is_dead = True
            print(self.name + " died. RIP.")
            return
        
        if(self.x == self.targetx and self.y == self.targety and (self.NeedToMove() or self.WantToMove())):
            self.getNewTarget()

        super(cubeanoid, self).move()

    def CanSplit(self):
        return self.energy >= self.max_energy - 1000

    def process(self):
        if((self.WantToMove() or self.NeedToMove()) and (self.targetx == 0 and self.targety == 0)):
           self.getNewTarget()
        super(cubeanoid, self).process()

#Static, unmoving creature that absorbs any cubanoids stupid enough to crawl inside.
#Will grow and shrink based on energy.
class BigRed(entity):
    hunger = 10000
    eat_expenditure = 1

    def __init__(self, name, x, y):
        print(name + ": I Live.")
        entity.__init__(self, "bigred", name, 10, (255,0,0), x, y, 100000, 100000, 2)

    def need_to_eat(self):
        if(self.energy <= self.max_energy / 2):
            return True
        else:
            return False
    
    def eat(self, energy_value):         
        self.energy += (energy_value / 2) - self.eat_expenditure
        self.size += 2
        self.hunger -= energy_value / 2
        self.x -= 1
        self.y -= 1
        if(self.energy >= self.max_energy):
            pass #marker for something to happen at full energy.
            
    def process(self):
        self.energy -= self.energy_expenditure
        self.hunger += 1

        if(self.energy > 0 and self.energy <= self.max_energy / 4):
            if(self.size > 0): self.size -= 2
            if(self.size > 0):
                self.hunger -= 1
                self.energy += self.energy / self.size / 2
                self.x += 1
                self.y += 1

        if(self.size <= 0 or self.energy <= 0):
            self.is_dead = True

class elipsalottle(animal):
    hunger = 5000
    eat_expenditure = 3
    poo_timer = 0
    disposal = 0
    field_of_vision = 1000
    gender = "male"

    def __init__(self, name, x, y):
        print(name + ": What am I?")
        self.gender = "male" if randint(0, 1) == 0 else "female"
        base_color = (255,102,140)
        if(self.gender == "male"):
            base_color = (255,255,0)

        animal.__init__(self, "elipsalottle", name, 20, base_color, x, y, 10000, 5000, 2, 1)
        
    def getFieldOfView(self):
        return pygame.Rect(self.x - 25, self.y - 25, 50, 50)

    def draw(self):
        pygame.draw.ellipse(screen, self.color, pygame.Rect(self.x, self.y, self.size, self.size))

    def need_to_poo(self):
        if(self.disposal > 0):
            return True
        else:
            return False

    def poo(self):
        if(self.poo_timer == 0 and self.need_to_poo()):
            self.energy = self.max_energy
            ScatterFood(int(self.disposal), self.x, self.y)
            if(bool(randint(0, 1))): DropBigRedSeed(self.name, self.x, self.y)
            print(self.name + " left a steaming hunk of Grade A")
            self.disposal = 0
        
    def eat(self, energy_value):
        if(energy_value > 0):
            self.energy += energy_value - self.eat_expenditure
            self.hunger -= energy_value / 2
            if(self.energy > self.max_energy):
                self.disposal = (self.energy - self.max_energy) / 200 # + (self.energy / 4)) / 200
                self.poo_timer = 1000

    def move(self):
        if(self.targetx == 0 and self.targety == 0): return
        if(self.energy >= self.max_energy):
            self.energy -= self.energy_expenditure
        
        if(self.x == self.targetx and self.y == self.targety and (self.NeedToMove() or self.WantToMove())):
            self.getNewTarget()

        super(elipsalottle, self).move()
            
    def process(self):
        if(self.poo_timer > 0): self.poo_timer -= 1
        self.poo()
        if(self.energy > 0): self.energy -= self.energy_expenditure
        if((self.WantToMove() or self.NeedToMove()) and (self.targetx == 0 and self.targety == 0)):
           self.getNewTarget()

        if(self.energy <= 0):
            self.is_dead = True
            print(self.name + " died. RIP.")
            return

        super(elipsalottle, self).process()

    def CheckFieldOfView(self, oobj):
        return self.getFieldOfView().colliderect(oobj.getRect())

    def ChoseToGoToFood(self, big_red):
        if(self.targetx != big_red.x or self.targety != big_red.y):
            if(self.need_to_eat() or self.want_to_eat() or self.Wanna()):
               self.targetx = big_red.x
               self.targety = big_red.y
               self.current_attention_span = self.max_attention_span

cubeanoids = [cubeanoid("Adam", randint(0, UNIVERSE_WIDTH - 5), randint(0, UNIVERSE_HEIGHT - 5)), cubeanoid("Eve", randint(0, UNIVERSE_WIDTH - 5), randint(0, UNIVERSE_HEIGHT - 5))]
food_available = []
big_reds = [BigRed("BigRed1", randint(25, UNIVERSE_WIDTH - 25), randint(10, UNIVERSE_HEIGHT - 25)),
            BigRed("BigRed2", randint(25, UNIVERSE_WIDTH - 25), randint(10, UNIVERSE_HEIGHT - 25)),
            BigRed("BigRed3", randint(25, UNIVERSE_WIDTH - 25), randint(10, UNIVERSE_HEIGHT - 25)),
            BigRed("BigRed4", randint(25, UNIVERSE_WIDTH - 25), randint(10, UNIVERSE_HEIGHT - 25))]
elipsalottles = [elipsalottle("A", randint(0, UNIVERSE_WIDTH - 5), randint(0, UNIVERSE_HEIGHT - 5)), elipsalottle("B", randint(0, UNIVERSE_WIDTH - 5), randint(0, UNIVERSE_HEIGHT - 5)), elipsalottle("C", randint(0, UNIVERSE_WIDTH - 5), randint(0, UNIVERSE_HEIGHT - 5)), elipsalottle("D", randint(0, UNIVERSE_WIDTH - 5), randint(0, UNIVERSE_HEIGHT - 5))]

def SpawnFood():
    x = randint(0, UNIVERSE_WIDTH - 5)
    y = randint(0, UNIVERSE_HEIGHT - 5)
    food_available.append(food("food" + str(len(food_available)), x, y))

def ScatterFood(amount, basex, basey):
    for i in range(amount):
        spread = 50
        x = randint(basex - spread, basex + spread)
        y = randint(basey - spread, basey + spread)
        food_available.append(food("food" + str(len(food_available)), x, y))

def DropBigRedSeed(droppername, x, y):
    big_reds.append(BigRed(droppername + str(len(big_reds)), x, y))
    print(droppername + " dropped a big red seed.")

#Randomly add some food...
for i in range(100): SpawnFood()

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

    if("elipsalottle" not in extinction_list):
        if len(elipsalottles) == 0:
            print("Elipsalottle are extinct.")
            extinction_list.append("elipsalottle")

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

    for el in elipsalottles:
        #Check if el can see a Big Red
        for bg in big_reds:
            if(el.CheckFieldOfView(bg) > 0):
                el.ChoseToGoToFood(bg)
                    
            if(el.CheckCollision(bg) > 0):                    
                if(el.need_to_eat() or el.want_to_eat()):
                    energytaken = 5000
                    el.eat(energytaken)
                    if(bg.energy > 0): bg.energy -= energytaken

        el.process()
        if(el.is_dead):
            elipsalottles.remove(el)
        else:
            el.move()
            el.draw()

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
    #SpawnFood()
    pygame.display.flip()
    clock.tick(60)
