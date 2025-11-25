"""


Spreading Poisonous Fungi
By: Kyslenko, V


"""



from shared import Creature, Propagator, PhotoGland, Direction, PoisonGland, LifeSensor


class PhunGuy(Creature):
    """
    Grows one womb (Propagator) and the maximum number of leaves(PhotoGlands).
    On each turn, if it has enough strength, gives birth to as many new SuperPlants
    as possible, in random directions.
    """

    minimum_baby_strength = Propagator.CREATION_COST + PhotoGland.CREATION_COST + 1
    __instance_count = 0

    def __init__(self):
        super().__init__()
        PhunGuy.__instance_count += 1
        self.womb = None
        self.gland = None
        self.sensor = None
        self.leaf_count = 0
        self.all_leaves_grown = False

    def do_turn(self):
        if not (self.womb and self.all_leaves_grown):
            self.grow_organs()

        if self.instance_count() > 100:
            if not self.gland:
                self.grow_poison()
            else: 
                #self.gland.remove_poison(100)
                self.make_babies()
                self.gland.add_poison(500)
                # self.gland.drop_poison(Direction.N, 100)
                # self.gland.drop_poison(Direction.E, 100)
                # self.gland.drop_poison(Direction.S, 100)
                # self.gland.drop_poison(Direction.W, 100)

            
        else:
            self.make_babies()


    @classmethod
    def instance_count(cls):
        return PhunGuy.__instance_count

    @classmethod
    def destroyed(cls):
        PhunGuy.__instance_count -= 1

    def grow_poison(self):
        if not self.gland and self.strength() > PoisonGland.CREATION_COST:
            self.gland = PoisonGland(self)
    
    def grow_organs(self):
        if not self.womb and self.strength() > Propagator.CREATION_COST:
            self.womb = PhunGuyPropagator(self)
        # if not self.sensor and self.strength() > LifeSensor.CREATION_COST:
        #     self.sensor = LifeSensor(self)
        while self.leaf_count < Creature.MAX_ORGANS - 2 and self.strength() > PhotoGland.CREATION_COST:
            PhotoGland(self)
            self.leaf_count += 1
        if self.leaf_count == Creature.MAX_ORGANS - 2:
            self.all_leaves_grown = True

    def make_babies(self):
        while self.strength() > (self.minimum_baby_strength + Propagator.USE_COST)*4:
            self.womb.give_birth(self.minimum_baby_strength, Direction.random())
            # self.womb.give_birth(self.minimum_baby_strength, Direction.N)
            # self.womb.give_birth(self.minimum_baby_strength, Direction.E)
            # self.womb.give_birth(self.minimum_baby_strength, Direction.S)
            # self.womb.give_birth(self.minimum_baby_strength, Direction.W)


class PhunGuyPropagator(Propagator):

    def make_child(self):
        return PhunGuy()