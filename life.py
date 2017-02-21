import pygame
import sys
import numpy as np
from numpy import random as rnd
from pygame.locals import *
from collections import deque

pygame.init()
pygame.event.set_allowed([QUIT])
UNIVERSE_WIDTH = 800
UNIVERSE_HEIGHT = 600
flags = DOUBLEBUF | HWACCEL
screen = pygame.display.set_mode((UNIVERSE_WIDTH, UNIVERSE_HEIGHT), flags)
screen.set_alpha(None) #Alpha isnt really needed yet.

pygame.display.set_caption('Microverse')
clock = pygame.time.Clock()

done = False

MAX_OBJ_ENERGY = 50000

extinction_list = []
particles = []
food_available = []
cubeanoids = []
big_reds = []
elipsalottles = []
newcreatures = []

particles_append = particles.append
food_available_append = food_available.append
cubeanoids_append = cubeanoids.append
big_reds_append = big_reds.append
elipsalottles_append = elipsalottles.append
new_creatures_append = newcreatures.append
extinction_list_append = extinction_list.append

particles_remove = particles.remove
food_available_remove = food_available.remove
cubeanoids_remove = cubeanoids.remove
big_reds_remove = big_reds.remove
elipsalottles_remove = elipsalottles.remove
new_creatures_remove = newcreatures.remove

pg_draw_elipse = pygame.draw.ellipse
pg_draw__rect = pygame.draw.rect

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
        pg_draw__rect(screen, self.color, pygame.Rect(self.x, self.y, self.size, self.size))

    def getRect(self):
        rectsize = self.size if self.size >= 3 else 3
        return pygame.Rect(self.x, self.y, rectsize, rectsize)

    def CheckCollision(self, oobj):
        return self.getRect().colliderect(oobj.getRect())

class food(base_object):
    energy = 200    
    def __init__(self, name, x, y):
        rgb_r = particle_type_data[0]['color'][0] if  particle_type_data[0]['r_str'] > particle_type_data[2]['r_str'] else particle_type_data[2]['color'][0]
        rgb_g = particle_type_data[0]['color'][1] if  particle_type_data[0]['g_str'] > particle_type_data[2]['g_str'] else particle_type_data[2]['color'][1]
        rgb_b = particle_type_data[0]['color'][2] if  particle_type_data[0]['b_str'] > particle_type_data[2]['b_str'] else particle_type_data[2]['color'][2]
        base_object.__init__(self, "food", name, 1, (rgb_r,rgb_g,rgb_b), x, y)
        
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

    def die(self):
        is_dead = True
        
class animal(entity):
    targetx = 0
    targety = 0
    velocity = 1
    current_attention_span = 0
    max_attention_span = 10000
    is_adult = False

    freeze_counter = 0
    
    tail_length = 10
    tail_update_timer = 0
    
    def __init__(self, objtype, name, size, color, x, y, max_energy, start_energy, living_energy_expenditure, velocity):
        self.targetx = x
        self.targety = y
        self.velocity = velocity
        self.tails = deque()
        
        append_tails = self.tails.append
        for i in range(1, self.tail_length):
           append_tails(base_object('tail', 'tail', self.size, color, x, y))
           
        entity.__init__(self, objtype, name, size, color, x, y, max_energy, start_energy, living_energy_expenditure)

    def getNewTarget(self):
        self.targetx = rnd.randint(0, np.subtract(UNIVERSE_WIDTH, self.size))
        self.targety = rnd.randint(0, np.subtract(UNIVERSE_HEIGHT, self.size))

    def eat(self, energy_value):
        self.energy += np.subtract(energy_value, self.energy_expenditure)

    def need_to_eat(self):
        return self.energy <= self.max_energy

    def want_to_mate(self):
        if(self.energy >= np.divide(self.max_energy, 2) and self.is_adult):
            return bool(rnd.randint(0, 2))
        else:
            return False

    def want_to_eat(self):
        if(self.need_to_eat()):
            return True
        else:
            if(self.current_attention_span == 0):
                return bool(rnd.randint(0, 2))
            else:
                return False
        
    def NeedToMove(self):
        return self.energy <= np.divide(self.max_energy, 2)

    def WantToMove(self):
        if(self.energy > 1000):
            return bool(rnd.randint(0, 2))
        else:
            return self.NeedToMove()

    def Wanna(self):
        if(self.current_attention_span == 0):
            return bool(rnd.randint(0, 2))
        else:
            return False

    def move(self):
        movx = 0
        movy = 0
        difx = np.subtract(self.targetx, self.x)
        dify = np.subtract(self.targety, self.y)
        if(self.targetx < self.x): movx = -self.velocity if difx < np.subtract(-self.velocity, 1) else difx
        if(self.targetx > self.x): movx = self.velocity if difx > np.subtract(self.velocity, 1) else difx
        if(self.targety < self.y): movy = -self.velocity if dify < np.subtract(-self.velocity, 1) else dify
        if(self.targety > self.y): movy = self.velocity if dify > np.subtract(self.velocity, 1) else dify
        expval = movx if movx > movy else movy
        self.energy -= np.multiply(self.energy_expenditure, expval)

        #Check for freeze to ensure no one gets stuck
        if(self.x == movx and self.y == movy):
            self.freeze_counter += 1
            if(self.freeze_counter == 1000):
                self.freeze_counter == 0
                self.current_attention_span == 0
                self.getNewTarget()
        self.x += movx
        self.y += movy
        if(np.add(self.x, self.size) >= UNIVERSE_WIDTH): self.x = np.subtract(UNIVERSE_WIDTH, self.size)
        if(self.x < 0): self.x = 0
        if(np.add(self.y, self.size) >= UNIVERSE_HEIGHT): self.y = np.subtract(UNIVERSE_HEIGHT, self.size)
        if(self.y < 0): self.y = 0
    
    def move_me(self, moverval):
        if(moverval == 1):
            if(self.x == self.targetx and self.y == self.targety): self.getNewTarget()
        elif(moverval == 2):
            if(self.targetx == 0 and self.targety == 0): return
            if(self.energy >= self.max_energy): self.energy -= self.energy_expenditure
            if(self.x == self.targetx and self.y == self.targety and (self.NeedToMove() or self.WantToMove())): self.getNewTarget()
    
            if(self.tail_update_timer == 0 and len(self.tails) > 0):
               self.tails.rotate(1)
               self.tails[0].x = self.x
               self.tails[0].y = self.y
               self.tail_update_timer = self.velocity
        elif(moverval == 3):
            if(self.energy >= self.max_energy): self.energy -= self.energy_expenditure
            elif(self.energy <= 0):
                self.is_dead = True
                #print(self.name + " died. RIP.")
                return
        
            if(self.x == self.targetx and self.y == self.targety and (self.NeedToMove() or self.WantToMove())): self.getNewTarget()
        elif(moverval == 4):
            return
        else:
            return
        self.move()

    def process(self):
        if(self.current_attention_span > 0): self.current_attention_span -= 1

particle_type_data = {}
class particle(animal):
    particle_type = 0
    particle_mover = 0
    mover = ()
    particle_age = 500
    
    def __init__(self, name, x, y):
        self.particle_type = rnd.randint(0, 5)
        if(self.particle_type not in particle_type_data):
            particle_type_data[self.particle_type] = {'energy': rnd.randint(1, 25000), 'color': (rnd.randint(0, 256),rnd.randint(0, 256),rnd.randint(0, 256)), 'r_str': rnd.randint(0,100), 'g_str': rnd.randint(0,100), 'b_str': rnd.randint(0,100), 'speed': rnd.randint(0,6), 'speed_str': rnd.randint(0, 100), 'tail_len': rnd.randint(1, 11), 'size': rnd.randint(1, 20), 'size_str': rnd.randint(0, 100)}        
        self.particle_mover = rnd.randint(1, 5)
        animal.__init__(self, "particle", name, 1, particle_type_data[self.particle_type]['color'], x, y, 1, 1, 0, particle_type_data[self.particle_type]['speed'])
    
    #def move(self):
    #    self.move_me(self.particle_mover)

    def process(self):
        if(self.particle_age > 0): self.particle_age -= 1
        if(self.targetx == 0 and self.targety == 0): self.getNewTarget()
        super(particle, self).process()
    
#New and randomly generated creature
class NewCreature(animal):
    my_mover = 0
    
    def __init__(self, name, x, y, p1, p2):
        rgb_r = particle_type_data[p1.particle_type]['color'][0] if particle_type_data[p1.particle_type]['r_str'] > particle_type_data[p2.particle_type]['r_str'] else particle_type_data[p2.particle_type]['color'][0]
        rgb_g = particle_type_data[p1.particle_type]['color'][1] if particle_type_data[p1.particle_type]['g_str'] > particle_type_data[p2.particle_type]['g_str'] else particle_type_data[p2.particle_type]['color'][1]
        rgb_b = particle_type_data[p1.particle_type]['color'][2] if particle_type_data[p1.particle_type]['b_str'] > particle_type_data[p2.particle_type]['b_str'] else particle_type_data[p2.particle_type]['color'][2]
        velocity = particle_type_data[p1.particle_type]['speed'] if particle_type_data[p1.particle_type]['speed_str'] > particle_type_data[p2.particle_type]['speed_str'] else particle_type_data[p2.particle_type]['speed']
        max_energy = particle_type_data[p1.particle_type]['energy'] if particle_type_data[p1.particle_type]['energy'] > particle_type_data[p2.particle_type]['energy'] else particle_type_data[p2.particle_type]['energy']
        size = particle_type_data[p1.particle_type]['size'] if particle_type_data[p1.particle_type]['size_str'] > particle_type_data[p2.particle_type]['size_str'] else particle_type_data[p2.particle_type]['size']
        self.my_mover = p1.particle_mover if p1.energy > p2.energy else p2.particle_mover
        animal.__init__(self, "newcreature", name, size, (rgb_r,rgb_g,rgb_b), x, y, max_energy, np.divide(max_energy, 2), np.divide(max_energy, size), velocity)

    #def move(self):
    #    super(NewCreature, self).move_me(self.my_mover)
        
#Double cell life, never grows but able to self-replicate
class cubeanoid(animal):
    my_mover = 1
    def __init__(self, name, x, y):
        #print(name + ": I'm Alive!")
        rgb_r = particle_type_data[0]['color'][0] if particle_type_data[0]['r_str'] > particle_type_data[1]['r_str'] else particle_type_data[1]['color'][0]
        rgb_g = particle_type_data[0]['color'][1] if particle_type_data[0]['g_str'] > particle_type_data[1]['g_str'] else particle_type_data[1]['color'][1]
        rgb_b = particle_type_data[0]['color'][2] if particle_type_data[0]['b_str'] > particle_type_data[1]['b_str'] else particle_type_data[1]['color'][2]
        velocity = particle_type_data[0]['speed'] if particle_type_data[0]['speed_str'] > particle_type_data[1]['speed_str'] else particle_type_data[1]['speed']
        animal.__init__(self, "cubenoid", name, 2, (rgb_r,rgb_g,rgb_b), x, y, 10000, 5000, 1, velocity)

    def move(self):
        if(self.energy >= self.max_energy): self.energy -= self.energy_expenditure
            
        elif(self.energy <= 0):
            self.is_dead = True
            cubeanoids_remove(cn)
            DisposeToParticle(cn.size, cn.x, cn.y)
            #print(self.name + " died. RIP.")
            return
        
        if(self.x == self.targetx and self.y == self.targety and (self.NeedToMove() or self.WantToMove())): self.getNewTarget()

        super(cubeanoid, self).move()

    def CanSplit(self):
        return self.energy >= np.subtract(self.max_energy, 1000)

    def process(self):
        if((self.WantToMove() or self.NeedToMove()) and (self.targetx == 0 and self.targety == 0)): self.getNewTarget()
        super(cubeanoid, self).process()

#Static, unmoving creature that absorbs any cubanoids stupid enough to crawl inside.
#Will grow and shrink based on energy.
class BigRed(entity):
    hunger = 10000
    eat_expenditure = 1

    def __init__(self, name, x, y):
        #print(name + ": I Live.")
        rgb_r = particle_type_data[0]['color'][0] if  particle_type_data[0]['r_str'] > particle_type_data[4]['r_str'] else particle_type_data[4]['color'][0]
        rgb_g = particle_type_data[0]['color'][1] if  particle_type_data[0]['g_str'] > particle_type_data[4]['g_str'] else particle_type_data[4]['color'][1]
        rgb_b = particle_type_data[0]['color'][2] if  particle_type_data[0]['b_str'] > particle_type_data[4]['b_str'] else particle_type_data[4]['color'][2]
        velocity = particle_type_data[0]['speed'] if  particle_type_data[0]['speed_str'] > particle_type_data[4]['speed_str'] else particle_type_data[4]['speed']
        entity.__init__(self, "bigred", name, 3, (rgb_r,rgb_g,rgb_b), x, y, 100000, 50000, velocity)

    def need_to_eat(self):
        return self.energy <= np.divide(self.max_energy, 2)
    
    def eat(self, energy_value):         
        self.energy += np.subtract(np.divide(energy_value, 2), self.eat_expenditure)
        self.size += 2
        self.hunger -= np.divide(energy_value, 2)
        self.x -= 1
        self.y -= 1
         
    def process(self):
        self.energy -= self.energy_expenditure
        self.hunger += 1

        if(self.energy > 0 and self.energy <= np.divide(self.max_energy, 4)):
            if(self.size > 0): self.size -= 2
            if(self.size > 0):
                self.hunger -= 1
                self.energy += np.divide(np.divide(self.energy, self.size), 2)
                self.x += 1
                self.y += 1

        if(self.size <= 0 or self.energy <= 0):
            self.is_dead = True
            big_reds_remove(bg)
            DisposeToParticle(bg.size, bg.x, bg.y)

#Slightly intelligent moving creature that eats BigReds.
class elipsalottle(animal):
    my_mover = 2
    hunger = 5000
    eat_expenditure = 3
    mate_expenditure = 3000
    poo_timer = 0
    disposal = 0
    field_of_vision = 1000
    gender = "male"
    max_size = 15
    birth_limit = 5 #elipsalottles have a finite ability to reproduce. This limit is applied to both male and females.

    def __init__(self, name, x, y):
        #print(name + ": What am I?")
        self.gender = "male" if rnd.randint(0, 2) == 0 else "female"
        base_color = particle_type_data[0]['color'] if(self.gender == "male") else particle_type_data[3]['color']
        velocity = particle_type_data[0]['speed'] if  particle_type_data[0]['speed_str'] > particle_type_data[3]['speed_str'] else particle_type_data[3]['speed']
        self.tails = deque()
        append_tails = self.tails.append
        for i in range(1, self.tail_length):
           append_tails(base_object('tail', 'tail', self.size, base_color, x, y))

        animal.__init__(self, "elipsalottle", name, 5, base_color, x, y, 10000, 5000, 2, velocity)
        
    def getFieldOfView(self):
        return pygame.Rect(np.subtract(self.x, 25), np.subtract(self.y, 25), 50, 50)

    def draw(self):
        for tail in self.tails:
           pg_draw_elipse(screen, tail.color, pygame.Rect(tail.x, tail.y, self.size, self.size))
           
        pg_draw_elipse(screen, self.color, pygame.Rect(self.x, self.y, self.size, self.size))

    def need_to_poo(self):
        return self.disposal > 0

    def poo(self):
        if(self.poo_timer == 0 and self.need_to_poo()):
            self.energy = self.max_energy
            ScatterFood(int(self.disposal), self.x, self.y)
            if(bool(rnd.randint(0, 2))): DropBigRedSeed(self.name, self.x, self.y)
            self.disposal = 0

    def eat(self, energy_value):
        if(energy_value > 0):
            self.energy += np.subtract(energy_value, self.eat_expenditure)
            self.hunger -= energy_value / 2
            if(self.energy > self.max_energy):
                if(self.size < self.max_size):
                    self.size += 1
                else:
                    self.is_adult = True
                self.disposal = np.divide((np.subtract(self.energy, self.max_energy)), 200) # + (self.energy / 4)) / 200
                self.poo_timer = 1000

    def mate(self):
        self.birth_limit -= 1
        self.energy -= self.mate_expenditure
        self.getNewTarget()
        if(self.birth_limit == 0): self.is_dead = True #sorry....
        
    def move(self):
        if(self.targetx == 0 and self.targety == 0): return
        if(self.energy >= self.max_energy): self.energy -= self.energy_expenditure
        if(self.x == self.targetx and self.y == self.targety and (self.NeedToMove() or self.WantToMove())): self.getNewTarget()

        if(self.tail_update_timer == 0 and len(self.tails) > 0):
           self.tails.rotate(1)
           self.tails[0].x = self.x
           self.tails[0].y = self.y
           self.tail_update_timer = 3

        super(elipsalottle, self).move()
       
    def process(self):
        if(self.poo_timer > 0): self.poo_timer -= 1
        if(self.tail_update_timer > 0): self.tail_update_timer -= 1
        
        self.poo()
        
        if(self.energy > 0): self.energy -= self.energy_expenditure
        if((self.WantToMove() or self.NeedToMove()) and (self.targetx == 0 and self.targety == 0)): self.getNewTarget()

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

        print("%s has become a %s." % (self.name, self.gender))

def SpawnParticle():
    particles_append(particle("particle" + str(len(particles)), rnd.randint(0, np.subtract(UNIVERSE_WIDTH, 5)), rnd.randint(0, np.subtract(UNIVERSE_HEIGHT, 5))))

def SpawnParticles(amnt):
    for i in range(amnt):
        particles_append(particle("particle" + str(len(particles)), rnd.randint(0, np.subtract(UNIVERSE_WIDTH, 5)), rnd.randint(0, np.subtract(UNIVERSE_HEIGHT, 5))))

def SpawnFood():
    food_available_append(food("food" + str(len(food_available)), rnd.randint(0, np.subtract(UNIVERSE_WIDTH, 5), rnd.randint(0, np.subtract(UNIVERSE_HEIGHT, 5)))))

def ScatterFood(amount, basex, basey):
    for i in range(amount):
        spread = 50
        food_available_append(food("food" + str(len(food_available)), rnd.randint(np.subtract(basex, spread), np.add(basex, spread)), rnd.randint(np.subtract(basey, spread), np.add(basey, spread))))

def DropBigRedSeed(droppername, x, y):
    big_reds_append(BigRed("BigRed" + str(len(big_reds)), x, y))

#Add particles to begin the cycle...
SpawnParticles(500)

while not done:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if(event.type == pygame.QUIT):
            done = True
            pygame.quit()
            sys.exit()

    for p in particles:
        p.process()
        p.move_me(p.particle_mover)
        #p.draw()
        
        if(p.particle_age == 0):
            for p2 in [x for x in particles if x != p and x.particle_type != p.particle_type and p.CheckCollision(x) and x.particle_age == 0]:
                #0-0 = nothing, 0-1 = cubanoid, 0-2 = food, 0-3 = Elipsalottle, 0-4 = Big Red
                if(p.particle_type == 0 and p2.particle_type == 1):
                    cubeanoids_append(cubeanoid("cubeanoid" + str(len(cubeanoids)), p.x, p.y))
                elif(p.particle_type == 0 and p2.particle_type == 2):
                    food_available_append(food("food" + str(len(food_available)), p.x, p.y))
                elif(p.particle_type == 0 and p2.particle_type == 3):
                    elipsalottles_append(elipsalottle("elipsalottle" + str(len(elipsalottles)), p.x, p.y))
                elif(p.particle_type == 0 and p2.particle_type == 4):
                    big_reds_append(BigRed("BigRed" + str(len(big_reds)), p.x, p.y))
                else:
                    #No object can have greater energy than the max. This prevents some particles from bonding.
                    if(np.add(p.energy, p2.energy) <= MAX_OBJ_ENERGY):
                        new_creatures_append(NewCreature("newcreature" + str(len(newcreatures)), p.x, p.y, p, p2))
                    else:
                        #prevent the next fee lines cleaning up particles that should be free to roam
                        continue
                try:
                    particles_remove(p)
                    particles_remove(p2)
                except:
                    #sometimes particles can't be removed because at this point they are already gone.
                    #print("Problem removing particle")
                    pass

    for cn in cubeanoids:
        if(cn.is_dead):
            print(cn.name + " died. :(")
            cubeanoids_remove(cn)
            DisposeToParticle(cn.size, cn.x, cn.y)
            continue
        
        for f in [x for x in food_available if cn.CheckCollision(x)]:
            cn.eat(f.energy)
            food_available_remove(f)

        if(cn.CanSplit()):
            cubeanoids_append(cubeanoid(str(cn.name) + str(len(cubeanoids)), np.add(cn.x, cn.size), np.add(cn.y, cn.size)))
            cn.energy = np.divide(cn.energy,2)
        cn.move_me(cn.my_mover)
        cn.draw()

    for el in elipsalottles:
        if(el.is_dead):
            print(el.name + " died. :(")
            elipsalottles_remove(el)
            DisposeToParticle(el.size, el.x, el.y)
            continue
        
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
                    if(bool(rnd.randint(0, 2))):
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
        el.move_me(el.my_mover)
        el.draw()

    for bg in big_reds:
        if(bg.is_dead):
            print(bg.name + " died. :(")
            big_reds_remove(bg)
            DisposeToParticle(bg.size, bg.x, bg.y)
            continue
        
        if(bg.need_to_eat()):
            for cn in [x for x in cubeanoids if bg.CheckCollision(x) > 0]:
                bg.eat(cn.energy)
                cn.die()

            for bg2 in [x for x in big_reds if x != bg and bg.CheckCollision(x)]:
                #absorb the other big red
                bg.eat(bg2.energy)
                big_reds_remove(bg2)
                        
        bg.process()
        bg.draw()

    for nc in newcreatures:
        if(nc.is_dead):
            new_creatures_remove(nc)
            DisposeToParticle(nc.size, nc.x, nc.y)
            continue
        nc.move_me(nc.my_mover)
        nc.draw()
        
    for f in food_available: f.draw()

    pygame.display.flip()
    clock.tick(60)
