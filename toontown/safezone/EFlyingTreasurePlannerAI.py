from toontown.safezone import DistributedEFlyingTreasureAI
from toontown.safezone import TreasurePlannerAI
import random

class EFlyingTreasurePlannerAI(TreasurePlannerAI.TreasurePlannerAI):
    def __init__(self, zoneId, callback=None):
        self.healAmount = 9
        self.spawnPoints = []
        TreasurePlannerAI.TreasurePlannerAI.__init__(self, zoneId, DistributedEFlyingTreasureAI.DistributedEFlyingTreasureAI, callback)

    def initSpawnPoints(self):
        z = 35
        self.spawnPoints = [(random.randint(100, 300) - 200,
                             random.randint(100, 300) - 200,
                             z) for _ in range(20)]
        return self.spawnPoints
