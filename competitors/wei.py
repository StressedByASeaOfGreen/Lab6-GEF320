

from shared import *

class Hatsune_Miku(Creature):

    __instance_count = 0

    def __init__(self):
        super().__init__()
        Hatsune_Miku.__instance_count += 1
        self.game_state = EarlyGame(self)
        self.previous_move = Direction.random()
        self.organs = []
        self.cilia = None
        self.type_sensor = None #Creature_type_sensor
        self.womb = None
        self.energy_sensor = None
        self.powerhouse = None #Photogland

    def do_turn(self):
        self.game_state.do_turn()

    #moves randomly to a safe spot (soil or plant) and avoids moving back and forth by remembering its previous move
    def move_rand(self,blocks):
        move_to = []
        for block in blocks:
            if block.block in [Soil,Plant]:
                move_to.append(block.direction)
        if move_to:
            d = random.choice(move_to)
            while d is self.previous_move.opposite:
                d=random.choice(move_to)
            self.cilia.move_in_direction(d)
            self.previous_move = d

    @classmethod
    def instance_count(cls):
        return Hatsune_Miku.__instance_count

    @classmethod
    def destroyed(cls):
        Hatsune_Miku.__instance_count -= 1

    # VALUES------------------------------------------------------------------------------------------------------------

    # Adds up the maintenance cost of all organs and returns it
    def cost_of_life(self):
        cost = 0
        if self.organs:
            for organ in self.organs:
                if organ != PhotoGland:
                    cost += organ.maintenance_cost()
        return cost + 20

    # estimated cost of a turn due to organ use, the entered values changes how many times organs are used
    # Returns cost
    def cost_of_turn(self, scans=8):
          cost = CreatureTypeSensor.USE_COST * scans + EnergySensor.USE_COST * scans + Cilia.USE_COST
          return cost

    # estimates if a bug would survive a complete turn
    def survive_turn(self, scans=8):
        answer = self.strength() > (self.cost_of_turn(scans) + self.cost_of_life())
        return answer

    # when population threshold is reached, it moves on to the next state
    def check_game_state(self):
        if Hatsune_Miku.instance_count() > 4000:
            self.game_state = LateGame(self)
        elif Hatsune_Miku.instance_count() > 2000:
            self.game_state = MidGame(self)

    # ACTIONS-----------------------------------------------------------------------------------------------------------

    # Base organs created: PhotoGland, Propagator, CreatureTypeSensor, EnergySensor, Cillia
    def create_base_organs(self):
        if not self.powerhouse and self.strength() > PhotoGland.CREATION_COST:  # 250
            self.powerhouse = PhotoGland(self)
            self.organs.append(self.powerhouse)
        if not self.cilia and self.strength() > Cilia.CREATION_COST:  # 100
            self.cilia = Cilia(self)
            self.organs.append(self.cilia)
        if not self.type_sensor and self.strength() > CreatureTypeSensor.CREATION_COST:  # 100
            self.type_sensor = CreatureTypeSensor(self)
            self.organs.append(self.type_sensor)
        if not self.energy_sensor and self.strength() > EnergySensor.CREATION_COST:
            self.energy_sensor = EnergySensor(self)
            self.organs.append(self.energy_sensor)
        if not self.womb and self.strength() > Propagator.CREATION_COST:  # 50
            self.womb = Birther(self)
            self.organs.append(self.womb)

    #Uses the type sensor to look around the specified amount of times,by default it will be the 8 squares adjacent.
    # returns a list of block objects that contain both what the block is and its direction.
    def look_around(self, blocks_to_view=8):
        blocks=[]
        if self.type_sensor:
            if blocks_to_view == 8:
                blocks = [Block(d, self.type_sensor.sense(d)) for d in Direction]
            elif blocks_to_view == 4:
                blocks = [Block(d, self.type_sensor.sense(d)) for d in [Direction.N,Direction.E,Direction.S,Direction.W]]
            return blocks

    def find_enemy(self,blocks):
        for block in blocks:
            if block.block not in [Soil, Hatsune_Miku, Birther, Plant, PoisonDrop] and not block is None:
                return True
        return False

    #Uses a list of blocks to gauge enemy strength
    #Returns the direction of the strongest beatable enemy and none if none are found
    def find_weak_enemy(self, blocks):
        weakest_direction=None
        weakest = 0
        if self.energy_sensor:
            for block in blocks:
                if block.block not in [Soil, Birther, Plant, PoisonDrop,Hatsune_Miku] and not block is None:
                    energy = self.energy_sensor.sense(block.direction)
                    if self.strength() - self.cilia.USE_COST - 80 > energy:
                        if energy > weakest:
                            weakest = energy
                            weakest_direction = block.direction
        return weakest_direction

    #Send the bug towards a weak enemy if there is one
    #Returns True if successful and false otherwise
    def eat_enemy_if_possible(self,blocks):
        if self.find_enemy(blocks):
            d=self.find_weak_enemy(blocks)
            if d is not None:
                self.cilia.move_in_direction(d)
                return True
        return False

    # Uses the list of blocks to check for plant tile, if found, attempts to go towards it and make a baby at the same time
    # Returns true or false based on whether a plant block was found
    def find_food(self,blocks):
        for block in blocks:
            if block.block == Plant:
                self.game_state.have_sex(blocks,no_go=block.direction)
                self.cilia.move_in_direction(block.direction)
                return True
        return False

    #puts any energy the bug may have at the end of a turn to good use
    #ethier creates photoglads to ensure self-sufficiency or makes babies
    def use_extra_energy(self,blocks):
        turn_cost = self.cost_of_life()
        if self.strength() > PhotoGland.CREATION_COST + turn_cost - 169 and len(self.organs) < Creature.MAX_ORGANS:
            self.organs.append(PhotoGland(self))
        elif len(self.organs) >= Creature.MAX_ORGANS:
            self.game_state.have_sex(blocks)

# STATES----------------------------------------------------------------------------------------------------------------

# early game strategy is betting on very little encounters with enemies, hence the lack of a life sensor and ability
# to fight back, this state mainly focuses on maximum breeding and eating plants.
class EarlyGame:
    def __init__(self,bug):
        self.bug=bug

    # VALUES------------------------------------------------------------------------------------------------------------

    #propagotor cost is not included since its so small compared with others
    minimum_baby_strength = (Cilia.CREATION_COST + CreatureTypeSensor.CREATION_COST + Propagator.CREATION_COST + EnergySensor.CREATION_COST + PhotoGland.CREATION_COST+1)

    # TURN--------------------------------------------------------------------------------------------------------------

    def do_turn(self):
        if not (self.bug.powerhouse and self.bug.type_sensor and self.bug.womb and self.bug.energy_sensor and self.bug.cilia):
            self.bug.create_base_organs()
        else:
            #if it ain't gonna survive, wait in place to gather energy
            if self.bug.survive_turn():
                vision = self.bug.look_around()

                if not self.bug.eat_enemy_if_possible(vision):
                    if not self.bug.find_food(vision):
                        self.bug.move_rand(vision)

                #If we have energy left over after a turn
                self.bug.use_extra_energy(vision)
            self.bug.check_game_state()

    # ACTIONS-----------------------------------------------------------------------------------------------------------

    #Checks list of blocks for optimal baby deployment, plant blocks are preferred over soil blocks.
    # breed-maxing, favors plant blocks over soil for placement, creates babies without womb to save energy for parent
    # bug,this way more babies can be created during one turn by one bug
    # babies are created with a photogland so they will gain the remaining power needed passively next turn

    def have_sex(self, blocks, no_go=None):
        for block in blocks:
            if block.block == Plant and block.direction is not no_go:
                #gmable that the plant block will give enough energy to the baby to make up for missing energy
                if (self.bug.strength() - Propagator.USE_COST - 1) > self.minimum_baby_strength/2:
                    self.bug.womb.give_birth(self.minimum_baby_strength / 2, block.direction)
        for block in blocks:
            if block.block == Soil and block.direction is not no_go:
                if (self.bug.strength() - Propagator.USE_COST - 1) > self.minimum_baby_strength*2:
                    self.bug.womb.give_birth(self.minimum_baby_strength*2, block.direction)

#less food now so it moves less randomly to conserve energy and only has sex on plant tiles when there is a confirmed
# abundance of food, otherwise food goes to the adults
class MidGame:
    def __init__(self, bug):
        self.bug = bug

    # VALUES------------------------------------------------------------------------------------------------------------

    #now born fully grown to ensure survival in food scares areas
    minimum_baby_strength = Cilia.CREATION_COST + CreatureTypeSensor.CREATION_COST + Propagator.CREATION_COST + EnergySensor.CREATION_COST + PhotoGland.CREATION_COST + 1

    # TURN--------------------------------------------------------------------------------------------------------------

    def do_turn(self):
        if not (self.bug.powerhouse and self.bug.type_sensor and self.bug.womb and self.bug.energy_sensor and self.bug.cilia):
            self.bug.create_base_organs()
        else:
            if self.bug.survive_turn():
                vision = self.bug.look_around()
                if not self.bug.eat_enemy_if_possible(vision):
                    if not self.bug.find_food(vision):
                        chance=random.randint(0,9)
                        #less food, so less movement to save energy
                        if chance<7:
                            self.bug.move_rand(vision)

                # If we have energy left over after a turn
                self.bug.use_extra_energy(vision)
        self.bug.check_game_state()

    # ACTIONS-----------------------------------------------------------------------------------------------------------

    def have_sex(self,blocks,no_go=None):
        plant=0
        for block in blocks:
            if block.block == Plant and block.direction is not no_go:
                plant+=1
        if plant >2:
            for block in blocks:
                if block.block == Plant and block.direction is not no_go:
                    if (self.bug.strength() - Propagator.USE_COST - 1) > self.minimum_baby_strength:
                        self.bug.womb.give_birth(self.minimum_baby_strength, block.direction)
        for block in blocks:
            if block.block == Soil and block.direction is not no_go:
                if (self.bug.strength() - Propagator.USE_COST - 1) > self.minimum_baby_strength*2:
                    self.bug.womb.give_birth(self.minimum_baby_strength*2, block.direction)


#4000 bugs is basically dominating so we just need to sweep the battlefield, instead of going random when it finds nothing, it just goes SW.
class LateGame:
    def __init__(self, bug):
        self.bug = bug

    # VALUES------------------------------------------------------------------------------------------------------------

    minimum_baby_strength = Cilia.CREATION_COST + CreatureTypeSensor.CREATION_COST + Propagator.CREATION_COST + EnergySensor.CREATION_COST + PhotoGland.CREATION_COST + 1

    # TURN--------------------------------------------------------------------------------------------------------------

    def do_turn(self):
        if not (self.bug.powerhouse and self.bug.type_sensor and self.bug.womb and self.bug.energy_sensor and self.bug.cilia):
            self.bug.create_base_organs()
        else:
            if self.bug.survive_turn():
                print("hello")
                vision = self.bug.look_around()

                if not self.bug.eat_enemy_if_possible(vision):
                    if not self.bug.find_food(vision):
                        if self.bug.strength() >= Creature.MAX_STRENGTH*0.9:
                            for block in vision:
                                if block.direction == Direction.SW:
                                    if block.block is not Hatsune_Miku:
                                        self.bug.cilia.move_in_direction(Direction.SW)

                self.bug.use_extra_energy(vision)
    # ACTIONS-----------------------------------------------------------------------------------------------------------

    #Whatever plant blocks exist will be gobbled up by parents so we prioritise soil instead
    def have_sex(self,blocks,no_go=None):
        for block in blocks:
            if block.block == Soil and block.direction is not no_go:
                if self.bug.strength() >= 0.9 * Creature.MAX_STRENGTH:
                    self.bug.womb.give_birth(self.minimum_baby_strength*2, block.direction)

# SUBCLASS--------------------------------------------------------------------------------------------------------------

#just gives birth
class Birther(Propagator):
    def make_child(self):
        return Hatsune_Miku()

# OTHERS----------------------------------------------------------------------------------------------------------------
#object that contains block type and its direction relative to the cell
class Block:
    def __init__(self,direction,block):
        self.direction = direction
        self.block = block