from otp.ai.AIBaseGlobal import *
from panda3d.core import *
from .DistributedNPCToonBaseAI import *
from . import ToonDNA
from direct.task.Task import Task
from toontown.ai import DatabaseObject
from toontown.estate import ClosetGlobals
from toontown.toon import Toon

class DistributedNPCTailorAI(DistributedNPCToonBaseAI):
    freeClothes = simbase.config.GetBool('free-clothes', 0)
    housingEnabled = simbase.config.GetBool('want-housing', 1)

    def __init__(self, air, npcId):
        DistributedNPCToonBaseAI.__init__(self, air, npcId)
        self.timedOut = 0
        self.givesQuests = 0
        self.customerDNA = None
        self.customerAccessories = None
        self.customerId = None
        return

    def getTailor(self):
        return 1

    def delete(self):
        taskMgr.remove(self.uniqueName('clearMovie'))
        self.ignoreAll()
        self.customerDNA = None
        self.customerAccessories = None
        self.customerId = None
        DistributedNPCToonBaseAI.delete(self)
        return

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.air.doId2do:
            self.notify.warning('Avatar: %s not found' % avId)
            return
        if self.isBusy():
            self.freeAvatar(avId)
            return
        av = self.air.doId2do[avId]
        self.customerDNA = ToonDNA.ToonDNA()
        self.customerDNA.makeFromNetString(av.getDNAString())
        self.customerAccessories = av.getAccessoryNetString()
        self.customerId = avId
        # Iunno why they did this
        # This would already be the avatar's current setting
        av.b_setDNAString(self.customerDNA.makeNetString())
        av.b_setAccessoriesString(self.customerAccessories)
        self.acceptOnce(self.air.getAvatarExitEvent(avId), self.__handleUnexpectedExit, extraArgs=[avId])
        flag = NPCToons.PURCHASE_MOVIE_START_BROWSE
        if self.freeClothes or self.air.questManager.hasTailorClothingTicket(av, self) == 1 or self.air.questManager.hasTailorClothingTicket(av, self) == 2:
            flag = self.getPurchasableMovieMode(av)
        self.sendShoppingMovie(avId, flag)
        DistributedNPCToonBaseAI.avatarEnter(self)

    def getPurchasableMovieMode(self, av):
        mode = NPCToons.PURCHASE_MOVIE_START
        if self.housingEnabled:
            if self.isClosetAlmostFull(av) and self.isTrunkAlmostFull(av):
                mode = NPCToons.PURCHASE_MOVIE_START_NOROOM
            elif self.isClosetAlmostFull(av):
                mode = NPCToons.PURCHASE_MOVIE_START_NOROOM_CLOSET
            elif self.isTrunkAlmostFull(av):
                mode = NPCToons.PURCHASE_MOVIE_START_NOROOM_TRUNK
        return mode

    def isClosetAlmostFull(self, av):
        numClothes = len(av.clothesTopsList) / 4 + len(av.clothesBottomsList) / 2
        if numClothes >= av.maxClothes - 1:
            return 1
        return 0

    def isTrunkAlmostFull(self, av):
        numAccessories = (len(av.hatList) + len(av.glassesList) + len(av.backpackList) + len(av.shoesList)) / 3
        if numAccessories >= av.maxAccessories - 1:
            return 1
        return 0

    def sendShoppingMovie(self, avId, flag):
        self.busy = avId
        self.sendUpdate('setMovie', [flag,
         self.npcId,
         avId,
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        taskMgr.doMethodLater(NPCToons.TAILOR_COUNTDOWN_TIME, self.sendTimeoutMovie, self.uniqueName('clearMovie'))

    def rejectAvatar(self, avId):
        self.notify.warning('rejectAvatar: should not be called by a Tailor!')

    def sendTimeoutMovie(self, task):
        toon = self.air.doId2do.get(self.customerId)
        if toon != None:
            self.revertAvatarLook(toon)
        self.timedOut = 1
        self.sendUpdate('setMovie', [NPCToons.PURCHASE_MOVIE_TIMEOUT,
         self.npcId,
         self.busy,
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        self.sendClearMovie(None)
        return Task.done

    def sendClearMovie(self, task):
        self.ignore(self.air.getAvatarExitEvent(self.busy))
        self.customerDNA = None
        self.customerAccessories = None
        self.customerId = None
        self.busy = 0
        self.timedOut = 0
        self.sendUpdate('setMovie', [NPCToons.PURCHASE_MOVIE_CLEAR,
         self.npcId,
         0,
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        self.sendUpdate('setCustomerStyleAndAccessories', [0, '', ''])
        return Task.done

    def completePurchase(self, avId):
        self.busy = avId
        self.sendUpdate('setMovie', [NPCToons.PURCHASE_MOVIE_COMPLETE,
         self.npcId,
         avId,
         ClockDelta.globalClockDelta.getRealNetworkTime()])
        self.sendClearMovie(None)
        return

    def setStyleAndAccessories(self, dnaBlob, accessoriesBlob, finished, which):
        avId = self.air.getAvatarIdFromSender()
        if avId != self.customerId:
            if self.customerId:
                self.air.writeServerEvent('suspicious', avId, 'DistributedNPCTailorAI.setStyleAndAccessories customer is %s' % self.customerId)
                self.notify.warning('customerId: %s, but got setStyleAndAccessories for: %s' % (self.customerId, avId))
            return
        testDNA = ToonDNA.ToonDNA()
        if not testDNA.isValidNetString(dnaBlob):
            self.air.writeServerEvent('suspicious', avId, 'DistributedNPCTailorAI.setStyleAndAccessories: invalid dna: %s' % dnaBlob)
            return
        if not Toon.isValidAccessoryNetString(accessoriesBlob):
            self.air.writeServerEvent('suspicious', avId, 'DistributedNPCTailorAI.setStyleAndAccessories: invalid accessories: %s' % accessoriesBlob)
            return
        if avId in self.air.doId2do:
            av = self.air.doId2do[avId]
            if finished == 2 and which > 0:
                if self.air.questManager.removeClothingTicket(av, self) == 1 or self.freeClothes:
                    self.confirmNewAvatarLook(av, dnaBlob, accessoriesBlob, which)
                    self.air.writeServerEvent('boughtTailorClothes', avId, '%s|%s|%s' % (self.doId, which, self.customerDNA.asTuple()))
                else:
                    self.air.writeServerEvent('suspicious', avId, 'DistributedNPCTailorAI.setStyleAndAccessories bogus clothing ticket')
                    self.notify.warning('NPCTailor: setStyleAndAccessories() - client tried to purchase with bogus clothing ticket!')
                    self.revertAvatarLook(av)
            elif finished == 1:
                self.revertAvatarLook(av)
            else:
                self.sendUpdate('setCustomerStyleAndAccessories', [avId, dnaBlob, accessoriesBlob])
        else:
            self.notify.warning('no av for avId: %d' % avId)
        if self.timedOut == 1 or finished == 0:
            return
        if self.busy == avId:
            taskMgr.remove(self.uniqueName('clearMovie'))
            self.completePurchase(avId)
        elif self.busy:
            self.air.writeServerEvent('suspicious', avId, 'DistributedNPCTailorAI.setStyleAndAccessories busy with %s' % self.busy)
            self.notify.warning('setStyleAndAccessories from unknown avId: %s busy: %s' % (avId, self.busy))

    def confirmNewAvatarLook(self, av, dnaBlob, accessoriesBlob, which):
        av.b_setDNAString(dnaBlob)
        av.b_setAccessoriesString(accessoriesBlob)
        if which & ClosetGlobals.SHIRT:
            if av.addToClothesTopsList(self.customerDNA.topTex, self.customerDNA.topTexColor, self.customerDNA.sleeveTex, self.customerDNA.sleeveTexColor) == 1:
                av.b_setClothesTopsList(av.getClothesTopsList())
            else:
                self.notify.warning('NPCTailor: setStyleAndAccessories() - unable to save old tops - we exceeded the tops list length')
        if which & ClosetGlobals.SHORTS:
            if av.addToClothesBottomsList(self.customerDNA.botTex, self.customerDNA.botTexColor) == 1:
                av.b_setClothesBottomsList(av.getClothesBottomsList())
            else:
                self.notify.warning('NPCTailor: setStyleAndAccessories() - unable to save old bottoms - we exceeded the bottoms list length')
        accessories = Toon.makeAccessoriesFromNetString(accessoriesBlob)
        if which & ClosetGlobals.HAT:
            hat = accessories['hat']
            if hat[0] != 0:
                if av.addToAccessoriesList(ToonDNA.HAT, hat[0], hat[1], hat[2]):
                    av.b_setHatList(av.getHatList())
                else:
                    self.notify.warning('NPCTailor: setStyleAndAccessories() - unable to save old hat - we exceeded the hat list length')
        if which & ClosetGlobals.GLASSES:
            glasses = accessories['glasses']
            if glasses[0] != 0:
                if av.addToAccessoriesList(ToonDNA.GLASSES, glasses[0], glasses[1], glasses[2]):
                    av.b_setGlassesList(av.getGlassesList())
                else:
                    self.notify.warning('NPCTailor: setStyleAndAccessories() - unable to save old glasses - we exceeded the glasses list length')
        if which & ClosetGlobals.BACKPACK:
            backpack = accessories['backpack']
            if backpack[0] != 0:
                if av.addToAccessoriesList(ToonDNA.BACKPACK, backpack[0], backpack[1], backpack[2]):
                    av.b_setBackpackList(av.getBackpackList())
                else:
                    self.notify.warning('NPCTailor: setStyleAndAccessories() - unable to save old backpack - we exceeded the backpack list length')
        if which & ClosetGlobals.SHOES:
            shoes = accessories['shoes']
            if shoes[0] != 0:
                if av.addToAccessoriesList(ToonDNA.SHOES, shoes[0], shoes[1], shoes[2]):
                    av.b_setShoesList(av.getShoesList())
                else:
                    self.notify.warning('NPCTailor: setStyleAndAccessories() - unable to save old shoes - we exceeded the shoes list length')

    def revertAvatarLook(self, av):
        if self.customerDNA:
            av.b_setDNAString(self.customerDNA.makeNetString())
        if self.customerAccessories:
            av.b_setAccessoriesString(self.customerAccessories)

    def __handleUnexpectedExit(self, avId):
        self.notify.warning('avatar:' + str(avId) + ' has exited unexpectedly')
        if self.customerId == avId:
            toon = self.air.doId2do.get(avId)
            if toon == None:
                toon = DistributedToonAI.DistributedToonAI(self.air)
                toon.doId = avId
            if self.customerDNA or self.customerAccessories:
                self.revertAvatarLook(toon)
                # FIXME: Doesn't seem to be working right now...
                # db = DatabaseObject.DatabaseObject(self.air, avId)
                # db.storeObject(toon, ['setDNAString'])
        else:
            self.notify.warning('invalid customer avId: %s, customerId: %s ' % (avId, self.customerId))
        if self.busy == avId:
            self.sendClearMovie(None)
        else:
            self.notify.warning('not busy with avId: %s, busy: %s ' % (avId, self.busy))
        return
