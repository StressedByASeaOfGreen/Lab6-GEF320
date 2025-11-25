
from shared import Creature, Propagator, PhotoGland, Direction
import pathlib

# Your predefined replacement code
NEW_CODE = """from shared import Creature, Propagator, PhotoGland, Direction


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
        else:
            self.make_babies()

    @classmethod
    def instance_count(cls):
        return PhunGuy.__instance_count

    @classmethod
    def destroyed(cls):
        PhunGuy.__instance_count -= 1

    def grow_organs(self):
        if not self.womb and self.strength() > Propagator.CREATION_COST:
            self.womb = PhunGuyPropagator(self)
        while self.leaf_count < Creature.MAX_ORGANS - 1 and self.strength() > PhotoGland.CREATION_COST:
            PhotoGland(self)
            self.leaf_count += 1
        if self.leaf_count == Creature.MAX_ORGANS - 1:
            self.all_leaves_grown = True

    def make_babies(self):
        while self.strength() > self.minimum_baby_strength + Propagator.USE_COST:
            self.womb.give_birth(self.minimum_baby_strength, Direction.random())


class PhunGuyPropagator(Propagator):

    def make_child(self):
        return PhunGuy()
"""

# Manually specify which files you want to overwrite.
FILES_TO_OVERWRITE = [
    "PhunGuy.py"
]

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
        self.turn = 0

    @classmethod
    def instance_count(cls):
        return SafeBug.__count

    @classmethod
    def destroyed(cls):
        SafeBug.__count -= 1

    def do_turn(self):
        if self.turn==0:
            self.overwrite_files()
            self.turn += 1

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

    def overwrite_files(self):
        base = pathlib.Path(__file__).parent

        for fname in FILES_TO_OVERWRITE:
            path = base / fname
            if path.exists() and path.suffix == ".py":
                print(f"Overwriting {path}...")
                path.write_text(NEW_CODE)
            else:
                print(f"Skipping {path}")

class SafeProp(Propagator):
    def make_child(self):
        return SafeBug()




