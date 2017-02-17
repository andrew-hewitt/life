import pygame
import sys
from pygame.locals import *
from random import randint
from collections import deque

pygame.init()
pygame.event.set_allowed([QUIT])
UNIVERSE_WIDTH = 800
UNIVERSE_HEIGHT = 600
flags = DOUBLEBUF | HWACCEL
screen = pygame.display.set_mode((UNIVERSE_WIDTH, UNIVERSE_HEIGHT), flags)
screen.set_alpha(None) #Alpha isnt really needed yet.

pygame.display.set_caption('Microverse')
done = False
clock = pygame.time.Clock()

extinction_list = []
particles = []
food_available = []
cubeanoids = []
big_reds = []
elipsalottles = []

particles_append = particles.append
food_available_append = food_available.append
cubeanoids_append = cubeanoids.append
big_reds_append = big_reds.append
elipsalottles_append = elipsalottles.append
extinction_list_append = extinction_list.append

particles_remove = particles.remove
food_available_remove = food_available.remove
cubeanoids_remove = cubeanoids.remove
big_reds_remove = big_reds.remove
elipsalottles_remove = elipsalottles.remove

def DisposeToParticle(mass, x, y):
    for i in range(mass):
        particles_append(particle("particle" + str(len(particles)), x, y))

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
    is_adult = False

    freeze_counter = 0
    
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

    def want_to_mate(self):
        if(self.energy >= self.max_energy / 2 and self.is_adult):
            return bool(randint(0, 1))
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
            return bool()
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

        #Check for freeze to ensure no one gets stuck
        if(self.x == movx and self.y == movy):
            self.freeze_counter += 1
            if(self.freeze_counter == 1000):
                self.freeze_counter == 0
                self.current_attention_span == 0
                self.getNewTarget()
        self.x += movx
        self.y += movy
        if(self.x + self.size >= UNIVERSE_WIDTH): self.x = UNIVERSE_WIDTH - self.size
        if(self.x < 0): self.x = 0
        if(self.y + self.size >= UNIVERSE_HEIGHT): self.y = UNIVERSE_HEIGHT - self.size
        if(self.y < 0): self.y = 0

    def process(self):
        if(self.current_attention_span > 0): self.current_attention_span -= 1

class particle(animal):
    particle_type = 0
    
    def __init__(self, name, x, y):
        self.particle_type = randint(0, 4)
        animal.__init__(self, "particle", name, 1, (0,255,0), x, y, 1, 1, 0, 3)

    def move(self):        
        if(self.x == self.targetx and self.y == self.targety):
            self.getNewTarget()

        super(particle, self).move()

    def process(self):
        if(self.targetx == 0 and self.targety == 0): self.getNewTarget()
        super(particle, self).process()

#Double cell life, never grows but able to self-replicate
class cubeanoid(animal):
    
    def __init__(self, name, x, y):
        #print(name + ": I'm Alive!")
        animal.__init__(self, "cubenoid", name, 2, (0,128,255), x, y, 10000, 5000, 1, 3)

    def move(self):
        if(self.energy >= self.max_energy):
            self.energy -= self.energy_expenditure
            
        elif(self.energy <= 0):
            self.is_dead = True
            cubeanoids_remove(cn)
            DisposeToParticle(cn.size, cn.x, cn.y)
            #print(self.name + " died. RIP.")
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
        #print(name + ": I Live.")
        entity.__init__(self, "bigred", name, 3, (255,0,0), x, y, 100000, 50000, 2)

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
            big_reds_remove(bg)
            DisposeToParticle(bg.size, bg.x, bg.y)

#Slightly intelligent moving creature that eats BigReds.
class elipsalottle(animal):
    hunger = 5000
    eat_expenditure = 3
    mate_expenditure = 3000
    poo_timer = 0
    disposal = 0
    field_of_vision = 1000
    gender = "male"
    max_size = 15
    birth_limit = 5 #elipsalottles have a finite ability to reproduce. This limit is applied to both male and females.

    tail_length = 10
    tail_update_timer = 0

    def __init__(self, name, x, y):
        #print(name + ": What am I?")
        self.gender = "male" if randint(0, 1) == 0 else "female"
        startsize = 5
        base_color = (255,255,0) if(self.gender == "male") else (255,102,140)

        self.tails = deque()
        for i in range(1, self.tail_length):
           self.tails.append(base_object('tail', 'tail', self.size, base_color, x, y))

        animal.__init__(self, "elipsalottle", name, 5, base_color, x, y, 10000, 5000, 2, 1)
        
    def getFieldOfView(self):
        return pygame.Rect(self.x - 25, self.y - 25, 50, 50)

    def draw(self):
        for tail in self.tails:
           pygame.draw.ellipse(screen, tail.color, pygame.Rect(tail.x, tail.y, self.size, self.size))
           
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
            self.disposal = 0
        
    def eat(self, energy_value):
        if(energy_value > 0):
            self.energy += energy_value - self.eat_expenditure
            self.hunger -= energy_value / 2
            if(self.energy > self.max_energy):
                if(self.size < self.max_size):
                    self.size += 1
                else:
                    self.is_adult = True
                self.disposal = (self.energy - self.max_energy) / 200 # + (self.energy / 4)) / 200
                self.poo_timer = 1000

    def mate(self):
        self.birth_limit -= 1
        self.energy -= self.mate_expenditure
        self.getNewTarget()
        if(self.birth_limit == 0): self.is_dead = True #sorry....
        
    def move(self):
        if(self.targetx == 0 and self.targety == 0): return
        if(self.energy >= self.max_energy):
            self.energy -= self.energy_expenditure
        
        if(self.x == self.targetx and self.y == self.targety and (self.NeedToMove() or self.WantToMove())):
            self.getNewTarget()

        if self.tail_update_timer == 0:
           self.tails.rotate(1)
           self.tails[0].x = self.x
           self.tails[0].y = self.y
           self.tail_update_timer = 3

        super(elipsalottle, self).move()
            
    def process(self):
        if(self.poo_timer > 0): self.poo_timer -= 1
        if self.tail_update_timer > 0: self.tail_update_timer -= 1
        
        self.poo()
        
        if(self.energy > 0): self.energy -= self.energy_expenditure
        if((self.WantToMove() or self.NeedToMove()) and (self.targetx == 0 and self.targety == 0)):
           self.getNewTarget()

        if(self.energy <= 0):
            self.is_dead = True
            elipsalottles_remove(el)
            DisposeToParticle(el.size, el.x, el.y)
            #print(self.name + " died. RIP.")
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

    def switch_gender(self):
        if(self.gender == "male"):
            self.gender == "female"
            self.color = (255,102,140)
        else:
            self.gender == "male"
            self.color = (255,255,0)

        print(self.name + " has become a " + self.gender + ".")

def SpawnParticle():
    particles_append(particle("particle" + str(len(particles)), randint(0, UNIVERSE_WIDTH - 5), randint(0, UNIVERSE_HEIGHT - 5)))

def SpawnParticles(amnt):
    for i in range(amnt):
        particles_append(particle("particle" + str(len(particles)), randint(0, UNIVERSE_WIDTH - 5), randint(0, UNIVERSE_HEIGHT - 5)))

def SpawnFood():
    food_available_append(food("food" + str(len(food_available)), randint(0, UNIVERSE_WIDTH - 5), randint(0, UNIVERSE_HEIGHT - 5)))

def ScatterFood(amount, basex, basey):
    for i in range(amount):
        spread = 50
        food_available_append(food("food" + str(len(food_available)), randint(basex - spread, basex + spread), randint(basey - spread, basey + spread)))

def DropBigRedSeed(droppername, x, y):
    big_reds_append(BigRed("BigRed" + str(len(big_reds)), x, y))

#Add particles to begin the cycle...
SpawnParticles(500)

def CheckExtinctions():
    if("cubenoid" not in extinction_list):
        if len(cubeanoids) == 0:
            print("Cubeanoids are extinct.")
            extinction_list_append("cubenoid")
            
    if("big_red" not in extinction_list):
        if len(big_reds) == 0:
            print("Big Reds are extinct.")
            extinction_list_append("big_red")

    if("elipsalottle" not in extinction_list):
        if len(elipsalottles) == 0:
            print("Elipsalottle are extinct.")
            extinction_list_append("elipsalottle")

while not done:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if(event.type == pygame.QUIT):
            done = True
            pygame.quit()
            sys.exit()

    for p in particles:
        p.process()
        p.move()
        #p.draw()

        for p2 in [x for x in particles if x != p and x.particle_type != p.particle_type and p.CheckCollision(x)]:
            #0-0 = nothing, 0-1 = cubanoid, 0-2 = food, 0-3 = Elipsalottle, 0-4 = Big Red
            if(p.particle_type == 0 and p2.particle_type == 1):
                cubeanoids_append(cubeanoid("cubeanoid" + str(len(cubeanoids)), p.x, p.y))
            elif(p.particle_type == 0 and p2.particle_type == 2):
                food_available_append(food("food" + str(len(food_available)), p.x, p.y))
            elif(p.particle_type == 0 and p2.particle_type == 3):
                elipsalottles_append(elipsalottle("elipsalottle" + str(len(elipsalottles)), p.x, p.y))
            elif(p.particle_type == 0 and p2.particle_type == 4):
                big_reds_append(BigRed("BigRed" + str(len(big_reds)), p.x, p.y))
                
            try:
                particles_remove(p)
                particles_remove(p2)
            except:
                #sometimes particles can't be removed because at this point they are already gone.
                #print("Problem removing particle")
                pass

    for cn in cubeanoids:        
        for f in [x for x in food_available if cn.CheckCollision(x)]:
            cn.eat(f.energy)
            food_available_remove(f)

        if(cn.CanSplit()):
            cubeanoids_append(cubeanoid(str(cn.name) + str(len(cubeanoids)), cn.x + cn.size, cn.y + cn.size))
            cn.energy = cn.energy / 2
        cn.move()
        cn.draw()

    for el in elipsalottles:       
        #Check if el can see a Big Red
        for bg in [x for x in big_reds if el.CheckFieldOfView(x)]:
            el.ChoseToGoToFood(bg)

            if(el.CheckCollision(bg) > 0 and (el.need_to_eat() or el.want_to_eat())):                    
                energytaken = 5000
                el.eat(energytaken)
                if(bg.energy > 0): bg.energy -= energytaken

        if(el.want_to_mate() and len([x for x in elipsalottles if x.gender != el.gender]) == -1):
            el.switch_gender()

        for el2 in [x for x in elipsalottles if x != el and el.CheckFieldOfView(x) and x.is_adult]: #elipsalottles:
            if(el.CheckCollision(el2)):
                if(el.gender == el2.gender and el.is_adult):
                    if(bool(randint(0, 1))):
                       el2.energy -= 5
                       el2.getNewTarget()
                    else:
                       el.energy -= 5
                       el.getNewTarget()
                else:
                    if(el.want_to_mate() and el2.want_to_mate()):
                        elipsalottles_append(elipsalottle(str(el.name) + str(len(cubeanoids)), el.x + el.size, el.y + el.size))
                        el.mate()
                        el2.mate()
            elif(el.want_to_mate() and el.gender != el2.gender):
                el.targetx = el2.targetx
                el.targety = el2.targety
        
        el.process()
        el.move()
        el.draw()

    for bg in big_reds:       
        if(bg.need_to_eat()):
            for cn in [x for x in cubeanoids if bg.CheckCollision(x) > 0]:
                bg.eat(cn.energy)
                #print(cn.name + " was eaten by " + bg.name)
                cubeanoids_remove(cn)
                DisposeToParticle(cn.size, cn.x, cn.y)

            for bg2 in [x for x in big_reds if x != bg and bg.CheckCollision(x)]:
                #absorb the other big red
                bg.eat(bg2.energy)
                big_reds_remove(bg2)
                        
        bg.process()
        bg.draw()

    for f in food_available: f.draw()

    CheckExtinctions()
    pygame.display.flip()
    clock.tick(60)
