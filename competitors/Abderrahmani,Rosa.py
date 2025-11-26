from shared import Creature, Propagator, PhotoGland, Direction


class SafeBug(Creature):
    """
    A bug that plays safe, and reproduces and keeps it strength up.
    this hope that either the enemy is to smart and doesn't attack bugs with higher strength,
    or that the enemy is dumb and attack us and die.
    this bug doesn't have any movement so it cant attack. depending on the bug, this can be really disadvantageous
    """

    min_baby_cost = Propagator.CREATION_COST + PhotoGland.CREATION_COST + 1
    __count = 0

    def __init__(self):
        super().__init__()
        SafeBug.__count += 1
        self.womb = None
        self.leaves = 0

    @classmethod
    def instance_count(cls):
        return SafeBug.__count

    @classmethod
    def destroyed(cls):
        SafeBug.__count -= 1

    def do_turn(self): #make organs, then focus on giving birth
        if not (self.womb and self.leaves < Creature.MAX_ORGANS-1):
            self.make_organ()

        else:
            while self.strength() > (self.min_baby_cost + Propagator.USE_COST)*4: #the 4 can be change but >1
                self.womb.give_birth(self.min_baby_cost, Direction.random())


    def make_organ(self): #one womb and all photogland
        if not self.womb and self.strength() > Propagator.CREATION_COST:
            self.womb = SafeProp(self)

        # Build leaves one at a time, checking strength each iteration
        while self.leaves < Creature.MAX_ORGANS - 1 and self.strength() > PhotoGland.CREATION_COST:
            PhotoGland(self)
            self.leaves += 1

class SafeProp(Propagator):
    def make_child(self):
        return SafeBug()
