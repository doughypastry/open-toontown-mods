from direct.directnotify import DirectNotifyGlobal
from toontown.building import DistributedDoorAI

class DistributedHouseDoorAI(DistributedDoorAI.DistributedDoorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedHouseDoorAI')
