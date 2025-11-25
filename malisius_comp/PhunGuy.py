
from shared import Creature, Propagator, PhotoGland, Direction


class PhunGuy(Creature):

    minimum_baby_strength = Propagator.CREATION_COST + PhotoGland.CREATION_COST + 1
    __instance_count = 0

    def __init__(self):
        super().__init__()
        PhunGuy.__instance_count += 1
        self.womb = None
        self.leaf_count = 0
        self.all_leaves_grown = False

    def do_turn(self):
        if not (self.womb and self.all_leaves_grown):
            self.grow_organs()


    @classmethod
    def instance_count(cls):
        return PhunGuy.__instance_count

    @classmethod
    def destroyed(cls):
        PhunGuy.__instance_count -= 1

    def grow_organs(self):

        while self.leaf_count < Creature.MAX_ORGANS - 1 and self.strength() > PhotoGland.CREATION_COST:
            PhotoGland(self)
            self.leaf_count += 1
        if self.leaf_count == Creature.MAX_ORGANS - 1:
            self.all_leaves_grown = True



class PhunGuyPropagator(Propagator):

    def make_child(self):
        return PhunGuy()
