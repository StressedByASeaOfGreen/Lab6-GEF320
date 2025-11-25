from shared import Creature, PhotoGland, Cilia, CreatureTypeSensor, Propagator, Direction


class StarveBomb(Creature):
    __count = 0

    def __init__(self):
        super().__init__()
        StarveBomb.__count += 1

        # reserved organs
        self.womb = None
        self.move = None
        self.food_sensor = None
        self.enemy_sensor = None

        # internal state
        self.mode = "early"   # early -> mid
        self.leaf_count = 0

    @classmethod
    def instance_count(cls):
        return StarveBomb.__count

    @classmethod
    def destroyed(cls):
        StarveBomb.__count -= 1

    def do_turn(self):
        # mode switch
        if self.mode == "early" and self.strength() > 300:
            self.mode = "mid"

        if self.mode == "early":
            self.do_early()
        else:
            self.do_mid()

    def do_early(self):
        s = self.strength()
        if s <= 0:
            return

        # always build food production first
        if self.leaf_count < 3 and s > PhotoGland.CREATION_COST:
            PhotoGland(self)
            self.leaf_count += 1
            return

        # build movement once we have enough leaves
        if not self.move and s > Cilia.CREATION_COST + 30:
            self.move = Cilia(self)
            return

        # create womb only when very safe
        if not self.womb and s > Propagator.CREATION_COST + 50:
            self.womb = StarterProp(self)
            return

        # reproduce very conservatively to avoid dying
        if self.womb and s > StarterProp.min_baby + 120:
            self.womb.give_birth(StarterProp.min_baby, Direction.random())

    def do_mid(self):
        s = self.strength()
        if s <= 0:
            return

        # late game: activate sensors
        if not self.food_sensor and s > CreatureTypeSensor.CREATION_COST + 20:
            self.food_sensor = CreatureTypeSensor(self)
            return

        # enemy sensor comes even later
        if not self.enemy_sensor and s > CreatureTypeSensor.CREATION_COST + 80:
            self.enemy_sensor = CreatureTypeSensor(self)
            return

        # give babies aggressively now
        if self.womb and s > StarterProp.min_baby + 50:
            self.womb.give_birth(StarterProp.min_baby, Direction.random())

        # move toward anything interesting if sensors exist
        if self.food_sensor and self.move:
            for d in Direction:
                t = self.food_sensor.sense(d)
                if t is not None:
                    self.move.move_in_direction(d)
                    return
            self.move.move_in_direction(Direction.random())


class StarterProp(Propagator):
    # minimal safe baby cost
    min_baby = Propagator.CREATION_COST + PhotoGland.CREATION_COST + 1

    def make_child(self):
        return StarveBomb()
