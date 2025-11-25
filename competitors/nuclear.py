from shared import Creature, Propagator, PhotoGland, Soil, Direction, CreatureTypeSensor

class BB(Creature):
    """
    Exploit-style bug that breaks stalemates by producing extra organs
    only when stuck. Creates a Propagator, leaves, and a type sensor for
    minimal awareness.
    """

    minimum_baby_strength = Propagator.CREATION_COST + PhotoGland.CREATION_COST + 1
    __instance_count = 0

    def __init__(self):
        super().__init__()
        BB.__instance_count += 1
        self.womb = None
        self.type_sensor = None
        self.leaf_count = 0
        self.all_leaves_grown = False

    @classmethod
    def instance_count(cls):
        return BB.__instance_count

    @classmethod
    def destroyed(cls):
        BB.__instance_count -= 1

    def do_turn(self):
        # create type sensor if missing
        if not self.type_sensor and self.strength() > CreatureTypeSensor.CREATION_COST:
            self.type_sensor = CreatureTypeSensor(self)

        if not (self.womb and self.all_leaves_grown):
            self.grow_organs()
        else:
            if self.stalemate_detected():
                self.break_stalemate()
            else:
                self.make_babies()

    def grow_organs(self):
        if not self.womb and self.strength() > Propagator.CREATION_COST:
            self.womb = BBPropagator(self)
        while self.leaf_count < Creature.MAX_ORGANS - 1 and self.strength() > PhotoGland.CREATION_COST:
            PhotoGland(self)
            self.leaf_count += 1
        if self.leaf_count == Creature.MAX_ORGANS - 1:
            self.all_leaves_grown = True

    def make_babies(self):
        while self.strength() > self.minimum_baby_strength + Propagator.USE_COST:
            self.womb.give_birth(self.minimum_baby_strength, Direction.random())

    def stalemate_detected(self):
        if not self.type_sensor:
            return False
        for d in Direction:
            block = self.type_sensor.sense(d)
            if block in [None, Soil, PhotoGland]:
                return False
        return True

    def break_stalemate(self):
        # only create extra leaves if stuck
        if self.leaf_count < Creature.MAX_ORGANS - 1 and self.strength() > PhotoGland.CREATION_COST:
            PhotoGland(self)
            self.leaf_count += 1


class BBPropagator(Propagator):
    def make_child(self):
        return BB()
