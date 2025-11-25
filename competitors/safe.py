from shared import Creature, Propagator, PhotoGland, Direction


class SafeBug(Creature):
    """
    A minimal creature that never spends strength unless it can afford the cost.
    Designed not to die immediately.
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

    def do_turn(self):
        if not (self.womb and self.leaves < Creature.MAX_ORGANS-1):
            self.make_organ()


        # Reproduce only when clearly safe
        else:
            while self.strength() > (self.min_baby_cost + Propagator.USE_COST)*4:
                self.womb.give_birth(self.min_baby_cost, Direction.random())


    def make_organ(self):
        # Build womb if affordable and not already created
        if not self.womb and self.strength() > Propagator.CREATION_COST:
            self.womb = SafeProp(self)

        # Build leaves one at a time, checking strength each iteration
        while self.leaves < Creature.MAX_ORGANS - 1 and self.strength() > PhotoGland.CREATION_COST:
            PhotoGland(self)
            self.leaves += 1

class SafeProp(Propagator):
    def make_child(self):
        return SafeBug()
