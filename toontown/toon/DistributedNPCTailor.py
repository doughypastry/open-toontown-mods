from panda3d.core import *
from .DistributedNPCToonBase import *
from direct.gui.DirectGui import *
from panda3d.core import *
from . import Toon
from . import NPCToons
from direct.task.Task import Task
from . import TailorClothesGUI
from toontown.toonbase import TTLocalizer
from . import ToonDNA
from toontown.estate import ClosetGlobals

ROOM_AVAILABLE_CLOSET = 1
ROOM_AVAILABLE_TRUNK = 2

class DistributedNPCTailor(DistributedNPCToonBase):

    def __init__(self, cr):
        DistributedNPCToonBase.__init__(self, cr)
        self.isLocalToon = 0
        self.clothesGUI = None
        self.av = None
        self.oldStyle = None
        self.oldAccessories = None
        self.browsing = 0
        self.roomAvailable = 0
        self.button = None
        self.popupInfo = None
        self.lerpCameraSeq = None
        return

    def disable(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupPurchaseGUI'))
        if self.lerpCameraSeq:
            self.lerpCameraSeq.finish()
            self.lerpCameraSeq = None
        if self.clothesGUI:
            self.clothesGUI.exit()
            self.clothesGUI.unload()
            self.clothesGUI = None
            if self.button != None:
                self.button.destroy()
                del self.button
            self.cancelButton.destroy()
            del self.cancelButton
            del self.gui
            self.counter.show()
            del self.counter
        if self.popupInfo:
            self.popupInfo.destroy()
            self.popupInfo = None
        self.av = None
        self.oldStyle = None
        self.oldAccessories = None
        base.localAvatar.posCamera(0, 0)
        DistributedNPCToonBase.disable(self)
        return

    def handleCollisionSphereEnter(self, collEntry):
        base.cr.playGame.getPlace().fsm.request('purchase')
        self.sendUpdate('avatarEnter', [])

    def __handleUnexpectedExit(self):
        self.notify.warning('unexpected exit')
        self.av = None
        self.oldStyle = None
        self.oldAccessories = None
        return

    def resetTailor(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('popupPurchaseGUI'))
        if self.lerpCameraSeq:
            self.lerpCameraSeq.finish()
            self.lerpCameraSeq = None
        if self.clothesGUI:
            self.clothesGUI.hideButtons()
            self.clothesGUI.exit()
            self.clothesGUI.unload()
            self.clothesGUI = None
            if self.button != None:
                self.button.destroy()
                del self.button
            self.cancelButton.destroy()
            del self.cancelButton
            del self.gui
            self.counter.show()
            del self.counter
            self.show()
        self.startLookAround()
        self.detectAvatars()
        self.clearMat()
        if self.isLocalToon:
            self.freeAvatar()
        return Task.done

    def canStartTailorInteraction(self, mode):
        if mode == NPCToons.PURCHASE_MOVIE_START or mode == NPCToons.PURCHASE_MOVIE_START_BROWSE:
            return True
        if mode == NPCToons.PURCHASE_MOVIE_START_NOROOM or mode == NPCToons.PURCHASE_MOVIE_START_NOROOM_CLOSET or mode == NPCToons.PURCHASE_MOVIE_START_NOROOM_TRUNK:
            return True
        return False

    def setMovie(self, mode, npcId, avId, timestamp):
        timeStamp = ClockDelta.globalClockDelta.localElapsedTime(timestamp)
        self.remain = NPCToons.CLERK_COUNTDOWN_TIME - timeStamp
        self.npcId = npcId
        self.isLocalToon = avId == base.localAvatar.doId
        if mode == NPCToons.PURCHASE_MOVIE_CLEAR:
            return
        if mode == NPCToons.PURCHASE_MOVIE_TIMEOUT:
            if self.lerpCameraSeq:
                self.lerpCameraSeq.finish()
                self.lerpCameraSeq = None
            if self.isLocalToon:
                self.ignore(self.purchaseDoneEvent)
                self.ignore(self.swapEvent)
                if self.popupInfo:
                    self.popupInfo.reparentTo(hidden)
            if self.clothesGUI:
                self.clothesGUI.resetClothes(self.oldStyle, accessories=self.oldAccessories)
                self.__handlePurchaseDone(timeout=1)
            self.setChatAbsolute(TTLocalizer.STOREOWNER_TOOKTOOLONG, CFSpeech | CFTimeout)
            self.resetTailor()
        elif self.canStartTailorInteraction(mode):
            if mode == NPCToons.PURCHASE_MOVIE_START:
                self.browsing = 0
                self.roomAvailable = ROOM_AVAILABLE_CLOSET | ROOM_AVAILABLE_TRUNK
            elif mode == NPCToons.PURCHASE_MOVIE_START_BROWSE:
                self.browsing = 1
                self.roomAvailable = ROOM_AVAILABLE_CLOSET | ROOM_AVAILABLE_TRUNK
            elif mode == NPCToons.PURCHASE_MOVIE_START_NOROOM:
                self.browsing = 0
                self.roomAvailable = 0
            elif mode == NPCToons.PURCHASE_MOVIE_START_NOROOM_CLOSET:
                self.browsing = 0
                self.roomAvailable = ROOM_AVAILABLE_TRUNK
            elif mode == NPCToons.PURCHASE_MOVIE_START_NOROOM_TRUNK:
                self.browsing = 0
                self.roomAvailable = ROOM_AVAILABLE_CLOSET
            self.av = base.cr.doId2do.get(avId)
            if self.av is None:
                self.notify.warning('Avatar %d not found in doId' % avId)
                return
            else:
                self.accept(self.av.uniqueName('disable'), self.__handleUnexpectedExit)
            style = self.av.getStyle()
            self.oldStyle = ToonDNA.ToonDNA()
            self.oldStyle.makeFromNetString(style.makeNetString())
            self.oldAccessories = [self.av.getHat(), self.av.getGlasses(), self.av.getBackpack(), self.av.getShoes()]
            self.setupAvatars(self.av)
            if self.isLocalToon:
                camera.wrtReparentTo(render)
                self.lerpCameraSeq = camera.posQuatInterval(1, Point3(-5, 9, self.getHeight() - 0.5), Point3(-150, -2, 0), other=self, blendType='easeOut', name=self.uniqueName('lerpCamera'))
                self.lerpCameraSeq.start()
            if self.browsing == 0:
                if self.roomAvailable == 0:
                    # No room in either closet or trunk
                    self.setChatAbsolute(TTLocalizer.STOREOWNER_NOROOM, CFSpeech | CFTimeout)
                elif self.roomAvailable == ROOM_AVAILABLE_CLOSET:
                    # The avatar doesn't have a trunk.
                    # We show the regular greeting message, but warn them later
                    # that they will lose their accessories.
                    if self.av.maxAccessories == 0:
                        self.setChatAbsolute(TTLocalizer.STOREOWNER_GREETING, CFSpeech | CFTimeout)
                    else:
                        # No room in trunk
                        self.setChatAbsolute(TTLocalizer.STOREOWNER_NOROOM_TRUNK, CFSpeech | CFTimeout)
                elif self.roomAvailable == ROOM_AVAILABLE_TRUNK:
                    # No room in closet
                    self.setChatAbsolute(TTLocalizer.STOREOWNER_NOROOM_CLOSET, CFSpeech | CFTimeout)
                else:
                    self.setChatAbsolute(TTLocalizer.STOREOWNER_GREETING, CFSpeech | CFTimeout)
            else:
                self.setChatAbsolute(TTLocalizer.STOREOWNER_BROWSING, CFSpeech | CFTimeout)
            if self.isLocalToon:
                taskMgr.doMethodLater(3.0, self.popupPurchaseGUI, self.uniqueName('popupPurchaseGUI'))
                print('-----------Starting tailor interaction-----------')
                print('avid: %s, gender: %s' % (self.av.doId, self.av.style.gender))
                print('current top = %s,%s,%s,%s and  bot = %s,%s,' % (self.av.style.topTex,
                 self.av.style.topTexColor,
                 self.av.style.sleeveTex,
                 self.av.style.sleeveTexColor,
                 self.av.style.botTex,
                 self.av.style.botTexColor))
                print('current hat = %s, glasses = %s, backpack = %s, shoes = %s' % (str(self.av.hat),
                 str(self.av.glasses),
                 str(self.av.backpack),
                 str(self.av.shoes)))
                print('topsList = %s' % self.av.getClothesTopsList())
                print('bottomsList = %s' % self.av.getClothesBottomsList())
                print('hatList = %s' % self.av.getHatList())
                print('glassesList = %s' % self.av.getGlassesList())
                print('backpackList = %s' % self.av.getBackpackList())
                print('shoesList = %s' % self.av.getShoesList())
                print('-------------------------------------------------')
        elif mode == NPCToons.PURCHASE_MOVIE_COMPLETE:
            self.setChatAbsolute(TTLocalizer.STOREOWNER_GOODBYE, CFSpeech | CFTimeout)
            if self.av and self.isLocalToon:
                print('-----------ending tailor interaction-----------')
                print('avid: %s, gender: %s' % (self.av.doId, self.av.style.gender))
                print('current top = %s,%s,%s,%s and  bot = %s,%s,' % (self.av.style.topTex,
                 self.av.style.topTexColor,
                 self.av.style.sleeveTex,
                 self.av.style.sleeveTexColor,
                 self.av.style.botTex,
                 self.av.style.botTexColor))
                print('current hat = %s, glasses = %s, backpack = %s, shoes = %s' % (str(self.av.hat),
                 str(self.av.glasses),
                 str(self.av.backpack),
                 str(self.av.shoes)))
                print('topsList = %s' % self.av.getClothesTopsList())
                print('bottomsList = %s' % self.av.getClothesBottomsList())
                print('hatList = %s' % self.av.getHatList())
                print('glassesList = %s' % self.av.getGlassesList())
                print('backpackList = %s' % self.av.getBackpackList())
                print('shoesList = %s' % self.av.getShoesList())
                print('-------------------------------------------------')
            self.resetTailor()
        elif mode == NPCToons.PURCHASE_MOVIE_NO_MONEY:
            self.notify.warning('PURCHASE_MOVIE_NO_MONEY should not be called')
            self.resetTailor()
        return

    def popupPurchaseGUI(self, task):
        self.setChatAbsolute('', CFSpeech)
        self.purchaseDoneEvent = 'purchaseDone'
        self.swapEvent = 'swap'
        self.acceptOnce(self.purchaseDoneEvent, self.__handlePurchaseDone)
        self.accept(self.swapEvent, self.__handleSwap)
        self.clothesGUI = TailorClothesGUI.TailorClothesGUI(self.purchaseDoneEvent, self.swapEvent, self.npcId)
        self.clothesGUI.load()
        self.clothesGUI.enter(self.av)
        self.clothesGUI.showButtons()
        self.gui = loader.loadModel('phase_3/models/gui/create_a_toon_gui')
        if self.browsing == 0:
            self.button = DirectButton(relief=None, image=(self.gui.find('**/CrtAtoon_Btn1_UP'), self.gui.find('**/CrtAtoon_Btn1_DOWN'), self.gui.find('**/CrtAtoon_Btn1_RLLVR')), pos=(-0.15, 0, -0.85), command=self.__handleButton, text=('', TTLocalizer.MakeAToonDone, TTLocalizer.MakeAToonDone), text_font=ToontownGlobals.getInterfaceFont(), text_scale=0.08, text_pos=(0, -0.03), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1))
        else:
            self.button = None
        self.cancelButton = DirectButton(relief=None, image=(self.gui.find('**/CrtAtoon_Btn2_UP'), self.gui.find('**/CrtAtoon_Btn2_DOWN'), self.gui.find('**/CrtAtoon_Btn2_RLLVR')), pos=(0.15, 0, -0.85), command=self.__handleCancel, text=('', TTLocalizer.MakeAToonCancel, TTLocalizer.MakeAToonCancel), text_font=ToontownGlobals.getInterfaceFont(), text_scale=0.08, text_pos=(0, -0.03), text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1))
        camera.setPosHpr(base.localAvatar, -4.16, 8.25, 2.47, -152.89, 0.0, 0.0)
        self.counter = render.find('**/*mo1_TI_counter')
        self.counter.hide()
        self.hide()
        return Task.done

    def __handleButton(self):
        messenger.send('next')

    def __handleCancel(self):
        self.clothesGUI.resetClothes(self.oldStyle, accessories=self.oldAccessories)
        messenger.send('last')

    def __handleSwap(self):
        self.d_setStyleAndAccessories(self.av.getStyle().makeNetString(), self.av.getAccessoryNetString(), 0)

    def __handlePurchaseDone(self, timeout = 0):
        if self.clothesGUI.doneStatus == 'last' or timeout == 1:
            self.d_setStyleAndAccessories(self.oldStyle.makeNetString(), Toon.makeAccessoryNetString(*self.oldAccessories), 1)
        else:
            which = 0
            if self.clothesGUI.topChoice != -1:
                which = which | ClosetGlobals.SHIRT
            if self.clothesGUI.bottomChoice != -1:
                which = which | ClosetGlobals.SHORTS
            if self.clothesGUI.hatChoice != -1:
                which = which | ClosetGlobals.HAT
            if self.clothesGUI.shoesChoice != -1:
                which = which | ClosetGlobals.SHOES
            print('setStyleAndAccessories: which = %d, top = %d, bot = %d, hat = %d, shoes = %d' % (which, self.clothesGUI.topChoice, self.clothesGUI.bottomChoice, self.clothesGUI.hatChoice, self.clothesGUI.shoesChoice))
            if self.roomAvailable != ROOM_AVAILABLE_CLOSET | ROOM_AVAILABLE_TRUNK:
                if self.isLocalToon:
                    # If the closet is already full
                    willFillCloset = self.av.isClosetFull()

                    # If the closet has space for one more item, but we want to buy two
                    if which & ClosetGlobals.SHIRT and which & ClosetGlobals.SHORTS:
                        willFillCloset = True

                    # Check if we are actually buying any accessories
                    mightLoseAccessory = False
                    if self.clothesGUI.hatChoice != -1 and self.av.getHat() != self.oldAccessories[0]:
                        if self.oldAccessories[0][0] != 0:
                            mightLoseAccessory = True
                    else:
                        which = which & ~ClosetGlobals.HAT
                    if self.clothesGUI.glassesChoice != -1 and self.av.getGlasses() != self.oldAccessories[1]:
                        if self.oldAccessories[1][0] != 0:
                            mightLoseAccessory = True
                    else:
                        which = which & ~ClosetGlobals.GLASSES
                    if self.clothesGUI.backpackChoice != -1 and self.av.getBackpack() != self.oldAccessories[2]:
                        if self.oldAccessories[2][0] != 0:
                            mightLoseAccessory = True
                    else:
                        which = which & ~ClosetGlobals.BACKPACK
                    if self.clothesGUI.shoesChoice != -1 and self.av.getShoes() != self.oldAccessories[3]:
                        if self.oldAccessories[3][0] != 0:
                            mightLoseAccessory = True
                    else:
                        which = which & ~ClosetGlobals.SHOES

                    if self.av.maxAccessories > 0:
                        # If the trunk is already full, or the trunk has room
                        # for one more item, but we want to buy more than one
                        whichAccessories = which >> 2
                        buyingAtLeastTwoAccessories = bin(whichAccessories).count('1') > 1

                        willFillTrunk = False
                        if whichAccessories != 0 and self.av.isTrunkFull():
                            willFillTrunk = True
                        if buyingAtLeastTwoAccessories:
                            willFillTrunk = True

                        hasTrunk = True
                    else:
                        # Special case: The avatar has no trunk, so we display
                        # a different message. We don't need to show it if we
                        # weren't wearing accessories already, but if we did
                        # make a selection, and it's different from what we
                        # are wearing, AND we would lose our old accessories,
                        # we display it.
                        willFillTrunk = mightLoseAccessory
                        hasTrunk = False

                    # Now decide which message to show if you will lose clothing or accessories
                    if willFillCloset or willFillTrunk:
                        if willFillCloset and willFillTrunk:
                            if hasTrunk:
                                # "Your closet and trunk are full."
                                textToUse = TTLocalizer.STOREOWNER_CONFIRM_LOSS
                            else:
                                # "Your closet is full."
                                # You don't have a trunk, after all
                                textToUse = TTLocalizer.STOREOWNER_CONFIRM_LOSS_CLOSET
                        elif willFillTrunk and hasTrunk:
                            textToUse = TTLocalizer.STOREOWNER_CONFIRM_LOSS_TRUNK
                        elif willFillTrunk and not hasTrunk:
                            textToUse = TTLocalizer.STOREOWNER_CONFIRM_LOSS_NOTRUNK
                        else:
                            textToUse = TTLocalizer.STOREOWNER_CONFIRM_LOSS_CLOSET
                        self.__enterConfirmLoss(textToUse, 2, which)
                        self.clothesGUI.hideButtons()
                        self.button.hide()
                        self.cancelButton.hide()
                    else:
                        self.d_setStyleAndAccessories(self.av.getStyle().makeNetString(), self.av.getAccessoryNetString(), 2, which)
            else:
                self.d_setStyleAndAccessories(self.av.getStyle().makeNetString(), self.av.getAccessoryNetString(), 2, which)

    def __enterConfirmLoss(self, text, finished, which):
        if self.popupInfo == None:
            buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
            okButtonImage = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'), buttons.find('**/ChtBx_OKBtn_Rllvr'))
            cancelButtonImage = (buttons.find('**/CloseBtn_UP'), buttons.find('**/CloseBtn_DN'), buttons.find('**/CloseBtn_Rllvr'))

            if text == TTLocalizer.STOREOWNER_CONFIRM_LOSS_CLOSET:
                text_pos = (0, -0.05)
                geom_scale = (0.88, 1, 0.55)
                button_z = -0.31
            else:
                text_pos = (0, 0)
                geom_scale = (0.88, 1, 0.65)
                button_z = -0.35

            self.popupInfo = DirectFrame(
                parent=hidden,
                relief=None,
                state='normal',
                text=text,
                text_wordwrap=10,
                textMayChange=0,
                frameSize=(-1, 1, -1, 1),
                text_pos=text_pos,
                geom=DGG.getDefaultDialogGeom(),
                geom_color=ToontownGlobals.GlobalDialogColor,
                geom_scale=geom_scale,
                geom_pos=(0, 0, -.18),
                text_scale=0.08)

            DirectButton(
                self.popupInfo,
                image=okButtonImage,
                relief=None,
                text=TTLocalizer.STOREOWNER_OK,
                text_scale=0.05,
                text_pos=(0.0, -0.1),
                textMayChange=0,
                pos=(-0.08, 0.0, button_z),
                command=self.__handleConfirmLossOK,
                extraArgs=[finished, which])

            DirectButton(
                self.popupInfo,
                image=cancelButtonImage,
                relief=None,
                text=TTLocalizer.STOREOWNER_CANCEL,
                text_scale=0.05,
                text_pos=(0.0, -0.1),
                textMayChange=0,
                pos=(0.08, 0.0, button_z),
                command=self.__handleConfirmLossCancel)

            buttons.removeNode()

        self.popupInfo.reparentTo(aspect2d)

    def __handleConfirmLossOK(self, finished, which):
        self.d_setStyleAndAccessories(self.av.getStyle().makeNetString(), self.av.getAccessoryNetString(), finished, which)
        self.popupInfo.reparentTo(hidden)

    def __handleConfirmLossCancel(self):
        self.d_setStyleAndAccessories(self.oldStyle.makeNetString(), Toon.makeAccessoryNetString(*self.oldAccessories), 1)
        self.popupInfo.reparentTo(hidden)

    def d_setStyleAndAccessories(self, dnaString, accessoriesString, finished, whichItems = ClosetGlobals.SHIRT | ClosetGlobals.SHORTS | ClosetGlobals.HAT | ClosetGlobals.GLASSES | ClosetGlobals.BACKPACK | ClosetGlobals.SHOES):
        self.sendUpdate('setStyleAndAccessories', [dnaString, accessoriesString, finished, whichItems])

    def setCustomerStyleAndAccessoriesDNA(self, avId, dnaString, accessoriesString):
        if avId != base.localAvatar.doId:
            av = base.cr.doId2do.get(avId, None)
            if av:
                if self.av == av:
                    oldTorso = self.av.style.torso
                    self.av.style.makeFromNetString(dnaString)
                    self.av.setAccessoriesFromNetString(accessoriesString)
                    if len(oldTorso) == 2 and len(self.av.style.torso) == 2 and self.av.style.torso[1] != oldTorso[1]:
                        self.av.swapToonTorso(self.av.style.torso, genClothes=0)
                        self.av.loop('neutral', 0)
                    self.av.generateToonClothes()
        return
