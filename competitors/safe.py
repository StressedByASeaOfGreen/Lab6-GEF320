from shared import *


class SafeBug(Creature):

    min_baby_cost = Propagator.CREATION_COST + PhotoGland.CREATION_COST + 1
    __count = 0

    def __init__(self):
        super().__init__()
        SafeBug.__count += 1
        self.womb = None
        self.type_sensor= None
        self.cilia = None
        self.leaves = 0

    @classmethod
    def instance_count(cls):
        return SafeBug.__count

    @classmethod
    def destroyed(cls):
        SafeBug.__count -= 1

    def do_turn(self): #make organs, then focus on giving birth
        if not (self.womb and self.leaves < Creature.MAX_ORGANS-1 and self.type_sensor and self.cilia):
            self.make_organ()

        elif self.strength() > (self.min_baby_cost + Propagator.USE_COST)*4:
            target = self.find_target()
            if target == None: return
            elif target.type == Plant:#only reproduce on plants
                self.womb.give_birth(self.min_baby_cost,target.direction)
            elif target.type not in [Soil, SafeBug, SafeProp, PoisonDrop]:
                self.cilia.move_in_direction(target.direction)
            elif target.type== Soil:
                self.cilia.move_in_direction(target.direction)


    def make_organ(self):
        if self.leaves < Creature.MAX_ORGANS - 3:
            while self.leaves < Creature.MAX_ORGANS - 2 and self.strength() > PhotoGland.CREATION_COST:
                PhotoGland(self)
                self.leaves += 1

        if not self.womb and self.strength() > Propagator.CREATION_COST:
            self.womb = SafeProp(self)

        if not self.type_sensor and self.strength() > CreatureTypeSensor.CREATION_COST:
            self.type_sensor = CreatureTypeSensor(self)

        if not self.cilia and self.strength() > Cilia.CREATION_COST:
            self.cilia = Cilia(self)


    def find_target(self):
        blocks= []
        if self.type_sensor:
            for d in Direction:
                blocks.append(Block(d, self.type_sensor.sense(d)))
            for block in blocks:
                if block.type == Plant and not block.type is None:
                    return block
            for block in blocks:
                if block.type not in [Soil, SafeBug, SafeProp, PoisonDrop] and not block.type is None:
                    return block
            for block in blocks:
                if block.type == Soil and not block.type is None:
                    return block
        return None



class SafeProp(Propagator):
    def make_child(self):
        return SafeBug()

class Block:
    def __init__(self,direction,block):
        self.direction = direction
        self.type = block
