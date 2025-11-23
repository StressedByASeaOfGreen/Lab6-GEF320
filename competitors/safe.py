from shared import Creature, Propagator, PhotoGland, Direction


class SafeBug(Creature):
    """
    A minimal creature that never spends strength unless it can afford the cost.
    Designed not to die immediately.
    """

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
        # Only act if we have *positive* usable strength
        s = self.strength()
        if s <= 0:
            return

        # Build womb only when affordable
        if not self.womb and s > Propagator.CREATION_COST:
            self.womb = SafeProp(self)
            return

        # Build leaves one at a time only when safe
        if self.leaves < Creature.MAX_ORGANS - 1 and s > PhotoGland.CREATION_COST:
            PhotoGland(self)
            self.leaves += 1
            return

        # Only try to reproduce when clearly safe
        if self.womb:
            baby_cost = SafeProp.min_baby_cost
            if s > baby_cost + Propagator.USE_COST:
                self.womb.give_birth(baby_cost, Direction.random())
class SafeProp(Propagator):
    min_baby_cost = Propagator.CREATION_COST + PhotoGland.CREATION_COST + 1

    def make_child(self):
        return SafeBug()
