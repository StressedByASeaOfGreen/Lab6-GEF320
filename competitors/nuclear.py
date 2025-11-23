from shared import Creature, Propagator, PhotoGland, Direction, Soil, Plant, Cilia, CreatureTypeSensor, EnergySensor
import random

class AdaptivePlant(Creature):
    """
    A fully adaptive, rapid-reproducing plant bug inspired by previous designs.
    - Fast early reproduction on safe tiles
    - Organ growth is energy-aware
    - Avoids oscillation and gets unstuck
    - Progressive strategy: EarlyGame, MidGame, LateGame
    """

    __instance_count = 0

    def __init__(self):
        super().__init__()
        AdaptivePlant.__instance_count += 1
        # Base organs
        self.powerhouse = None
        self.womb = None
        self.type_sensor = None
        self.energy_sensor = None
        self.cilia = None
        self.previous_move = None
        self.organs = []
        # Game state control
        self.game_state = EarlyGame(self)

    @classmethod
    def instance_count(cls):
        return AdaptivePlant.__instance_count

    @classmethod
    def destroyed(cls):
        AdaptivePlant.__instance_count -= 1

    # ---------------------- Core Turn ----------------------
    def do_turn(self):
        self.game_state.do_turn()

    # ---------------------- Organ Management ----------------------
    def create_base_organs(self):
        """
        Creates minimal organs first to survive and reproduce.
        """
        if not self.powerhouse and self.strength() > PhotoGland.CREATION_COST:
            self.powerhouse = PhotoGland(self)
            self.organs.append(self.powerhouse)
        if not self.cilia and self.strength() > Cilia.CREATION_COST:
            self.cilia = Cilia(self)
            self.organs.append(self.cilia)
        if not self.type_sensor and self.strength() > CreatureTypeSensor.CREATION_COST:
            self.type_sensor = CreatureTypeSensor(self)
            self.organs.append(self.type_sensor)
        if not self.energy_sensor and self.strength() > EnergySensor.CREATION_COST:
            self.energy_sensor = EnergySensor(self)
            self.organs.append(self.energy_sensor)
        if not self.womb and self.strength() > Propagator.CREATION_COST:
            self.womb = PlantPropagator(self)
            self.organs.append(self.womb)

    # ---------------------- Movement ----------------------
    def move_safely(self, blocks):
        """
        Chooses a safe move (soil or plant) avoiding oscillation.
        """
        safe_moves = [b.direction for b in blocks if b.block in [Soil, Plant]]
        if self.previous_move:
            safe_moves = [d for d in safe_moves if d != self.previous_move.opposite]
        if safe_moves:
            chosen = random.choice(safe_moves)
            self.cilia.move_in_direction(chosen)
            self.previous_move = chosen

    # ---------------------- Vision ----------------------
    def look_around(self, blocks_to_view=8):
        if not self.type_sensor:
            return []
        directions = Direction if blocks_to_view == 8 else [Direction.N, Direction.E, Direction.S, Direction.W]
        return [Block(d, self.type_sensor.sense(d)) for d in directions]

    # ---------------------- Eating & Attacking ----------------------
    def find_enemy(self, blocks):
        return any(b.block not in [Soil, Plant, AdaptivePlant, Propagator] for b in blocks)

    def find_weak_enemy(self, blocks):
        weakest_direction = None
        weakest_energy = 0
        for b in blocks:
            if b.block not in [Soil, Plant, AdaptivePlant, Propagator]:
                energy = self.energy_sensor.sense(b.direction)
                if self.strength() - Cilia.USE_COST - 50 > energy and energy > weakest_energy:
                    weakest_energy = energy
                    weakest_direction = b.direction
        return weakest_direction

    def attack_enemy_if_possible(self, blocks):
        if self.find_enemy(blocks):
            d = self.find_weak_enemy(blocks)
            if d is not None:
                self.cilia.move_in_direction(d)
                return True
        return False

    # ---------------------- Reproduction ----------------------
    def minimum_baby_strength(self):
        return (PhotoGland.CREATION_COST + Cilia.CREATION_COST +
                CreatureTypeSensor.CREATION_COST + Propagator.CREATION_COST +
                EnergySensor.CREATION_COST + 1)

    def spread_babies(self, blocks):
        if not self.womb:
            return
        for b in blocks:
            if b.block in [Plant, Soil]:
                while self.strength() > self.minimum_baby_strength() + Propagator.USE_COST:
                    self.womb.give_birth(self.minimum_baby_strength(), b.direction)

    # ---------------------- Energy & Survival ----------------------
    def cost_of_life(self):
        cost = sum(o.maintenance_cost() for o in self.organs if o != PhotoGland)
        return cost + 20

    def cost_of_turn(self):
        return Cilia.USE_COST + CreatureTypeSensor.USE_COST + EnergySensor.USE_COST

    def survive_turn(self):
        return self.strength() > (self.cost_of_life() + self.cost_of_turn())

    def use_extra_energy(self, blocks):
        """
        Builds extra PhotoGlands or produces babies when fully grown.
        """
        if self.strength() > PhotoGland.CREATION_COST + self.cost_of_life() and len(self.organs) < Creature.MAX_ORGANS:
            self.organs.append(PhotoGland(self))
        elif len(self.organs) >= Creature.MAX_ORGANS:
            self.spread_babies(blocks)

# ---------------------- Propagator ----------------------
class PlantPropagator(Propagator):
    def make_child(self):
        return AdaptivePlant()

# ---------------------- Block Container ----------------------
class Block:
    def __init__(self, direction, block):
        self.direction = direction
        self.block = block

# ---------------------- Game States ----------------------
class EarlyGame:
    """
    Focus on rapid reproduction and survival. Moves safely.
    """
    def __init__(self, bug):
        self.bug = bug

    def do_turn(self):
        self.bug.create_base_organs()
        if not self.bug.survive_turn():
            return

        vision = self.bug.look_around()
        if not self.bug.attack_enemy_if_possible(vision):
            if not self.bug.spread_babies(vision):
                self.bug.move_safely(vision)
        self.bug.use_extra_energy(vision)

class MidGame(EarlyGame):
    """
    Conservative movement, more focus on resource collection and selective reproduction.
    """
    pass

class LateGame(EarlyGame):
    """
    Aggressive movement, produces babies mainly on Soil to expand quickly.
    """
    def do_turn(self):
        self.bug.create_base_organs()
        if not self.bug.survive_turn():
            return

        vision = self.bug.look_around()
        self.bug.spread_babies([b for b in vision if b.block == Soil])
        self.bug.use_extra_energy(vision)
