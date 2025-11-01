from panda3d.core import *
from toontown.toon import Toon
from toontown.toon import ToonDNA
from direct.fsm import StateData
from direct.gui.DirectGui import *
from panda3d.core import *
from .MakeAToonGlobals import *
from toontown.toonbase import TTLocalizer
from direct.directnotify import DirectNotifyGlobal
from . import ShuffleButton
import random
CLOTHES_MAKETOON = 0
CLOTHES_TAILOR = 1
CLOTHES_CLOSET = 2

class ClothesGUI(StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('ClothesGUI')

    def __init__(self, type, doneEvent, swapEvent = None):
        StateData.StateData.__init__(self, doneEvent)
        self.type = type
        self.toon = None
        self.swapEvent = swapEvent
        self.gender = '?'
        self.girlInShorts = 0
        self.swappedTorso = 0
        return

    def load(self):
        self.gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
        guiRArrowUp = self.gui.find('**/tt_t_gui_mat_arrowUp')
        guiRArrowRollover = self.gui.find('**/tt_t_gui_mat_arrowUp')
        guiRArrowDown = self.gui.find('**/tt_t_gui_mat_arrowDown')
        guiRArrowDisabled = self.gui.find('**/tt_t_gui_mat_arrowDisabled')
        shuffleFrame = self.gui.find('**/tt_t_gui_mat_shuffleFrame')
        shuffleArrowUp = self.gui.find('**/tt_t_gui_mat_shuffleArrowUp')
        shuffleArrowDown = self.gui.find('**/tt_t_gui_mat_shuffleArrowDown')
        shuffleArrowRollover = self.gui.find('**/tt_t_gui_mat_shuffleArrowUp')
        shuffleArrowDisabled = self.gui.find('**/tt_t_gui_mat_shuffleArrowDisabled')
        self.parentFrame = DirectFrame(relief=DGG.RAISED, pos=(0.98, 0, 0.416), frameColor=(1, 0, 0, 0))

        if self.type == CLOTHES_CLOSET:
            # Closet doesn't let you choose accessories
            top = -0.4
        elif self.type == CLOTHES_MAKETOON:
            # Make-A-Toon doesn't let you choose glasses or backpacks
            top = 0.1
        else:
            top = 0.3

        self.shirtFrame = DirectFrame(parent=self.parentFrame, image=shuffleFrame, image_scale=halfButtonInvertScale, relief=None, pos=(0, 0, top), hpr=(0, 0, 3), scale=1.2, frameColor=(1, 1, 1, 1), text=TTLocalizer.ClothesShopShirt, text_scale=0.0575, text_pos=(-0.001, -0.015), text_fg=(1, 1, 1, 1))
        self.topLButton = DirectButton(parent=self.shirtFrame, relief=None, image=(shuffleArrowUp,
         shuffleArrowDown,
         shuffleArrowRollover,
         shuffleArrowDisabled), image_scale=halfButtonScale, image1_scale=halfButtonHoverScale, image2_scale=halfButtonHoverScale, pos=(-0.2, 0, 0), command=self.swapTop, extraArgs=[-1])
        self.topRButton = DirectButton(parent=self.shirtFrame, relief=None, image=(shuffleArrowUp,
         shuffleArrowDown,
         shuffleArrowRollover,
         shuffleArrowDisabled), image_scale=halfButtonInvertScale, image1_scale=halfButtonInvertHoverScale, image2_scale=halfButtonInvertHoverScale, pos=(0.2, 0, 0), command=self.swapTop, extraArgs=[1])

        self.bottomFrame = DirectFrame(parent=self.parentFrame, image=shuffleFrame, image_scale=halfButtonInvertScale, relief=None, pos=(0, 0, top - 0.25), hpr=(0, 0, -2), scale=1.2, frameColor=(1, 1, 1, 1), text=TTLocalizer.ColorShopToon, text_scale=0.0575, text_pos=(-0.001, -0.015), text_fg=(1, 1, 1, 1))
        self.bottomLButton = DirectButton(parent=self.bottomFrame, relief=None, image=(shuffleArrowUp,
         shuffleArrowDown,
         shuffleArrowRollover,
         shuffleArrowDisabled), image_scale=halfButtonScale, image1_scale=halfButtonHoverScale, image2_scale=halfButtonHoverScale, pos=(-0.2, 0, 0), command=self.swapBottom, extraArgs=[-1])
        self.bottomRButton = DirectButton(parent=self.bottomFrame, relief=None, image=(shuffleArrowUp,
         shuffleArrowDown,
         shuffleArrowRollover,
         shuffleArrowDisabled), image_scale=halfButtonInvertScale, image1_scale=halfButtonInvertHoverScale, image2_scale=halfButtonInvertHoverScale, pos=(0.2, 0, 0), command=self.swapBottom, extraArgs=[1])

        shuffleButtonPos = (0, 0, -1)

        self.hatFrame = None
        self.glassesFrame = None
        self.backpackFrame = None
        self.shoesFrame = None

        if not self.type == CLOTHES_CLOSET:
            self.hatFrame = DirectFrame(parent=self.parentFrame, image=shuffleFrame, image_scale=halfButtonInvertScale, relief=None, pos=(0, 0, top - 0.53), hpr=(0, 0, 3), scale=1.2, frameColor=(1, 1, 1, 1), text=TTLocalizer.ClothesShopHats, text_scale=0.0575, text_pos=(-0.001, -0.015), text_fg=(1, 1, 1, 1))
            self.hatLButton = DirectButton(parent=self.hatFrame, relief=None, image=(shuffleArrowUp,
             shuffleArrowDown,
             shuffleArrowRollover,
             shuffleArrowDisabled), image_scale=halfButtonScale, image1_scale=halfButtonHoverScale, image2_scale=halfButtonHoverScale, pos=(-0.2, 0, 0), command=self.swapHat, extraArgs=[-1])
            self.hatRButton = DirectButton(parent=self.hatFrame, relief=None, image=(shuffleArrowUp,
             shuffleArrowDown,
             shuffleArrowRollover,
             shuffleArrowDisabled), image_scale=halfButtonInvertScale, image1_scale=halfButtonInvertHoverScale, image2_scale=halfButtonInvertHoverScale, pos=(0.2, 0, 0), command=self.swapHat, extraArgs=[1])

            if not self.type == CLOTHES_MAKETOON:
                self.glassesFrame = DirectFrame(parent=self.parentFrame, image=shuffleFrame, image_scale=halfButtonInvertScale, relief=None, pos=(0, 0, top - 0.77), hpr=(0, 0, -2), scale=1.2, frameColor=(1, 1, 1, 1), text=TTLocalizer.ClothesShopGlasses, text_scale=0.0575, text_pos=(-0.001, -0.015), text_fg=(1, 1, 1, 1))
                self.glassesLButton = DirectButton(parent=self.glassesFrame, relief=None, image=(shuffleArrowUp,
                 shuffleArrowDown,
                 shuffleArrowRollover,
                 shuffleArrowDisabled), image_scale=halfButtonScale, image1_scale=halfButtonHoverScale, image2_scale=halfButtonHoverScale, pos=(-0.2, 0, 0), command=self.swapGlasses, extraArgs=[-1])
                self.glassesRButton = DirectButton(parent=self.glassesFrame, relief=None, image=(shuffleArrowUp,
                 shuffleArrowDown,
                 shuffleArrowRollover,
                 shuffleArrowDisabled), image_scale=halfButtonInvertScale, image1_scale=halfButtonInvertHoverScale, image2_scale=halfButtonInvertHoverScale, pos=(0.2, 0, 0), command=self.swapGlasses, extraArgs=[1])

                self.backpackFrame = DirectFrame(parent=self.parentFrame, image=shuffleFrame, image_scale=halfButtonInvertScale, relief=None, pos=(0, 0, top - 1.05), hpr=(0, 0, 3), scale=1.2, frameColor=(1, 1, 1, 1), text=TTLocalizer.ClothesShopBackpacks, text_scale=0.0575, text_pos=(-0.001, -0.015), text_fg=(1, 1, 1, 1))
                self.backpackLButton = DirectButton(parent=self.backpackFrame, relief=None, image=(shuffleArrowUp,
                 shuffleArrowDown,
                 shuffleArrowRollover,
                 shuffleArrowDisabled), image_scale=halfButtonScale, image1_scale=halfButtonHoverScale, image2_scale=halfButtonHoverScale, pos=(-0.2, 0, 0), command=self.swapBackpack, extraArgs=[-1])
                self.backpackRButton = DirectButton(parent=self.backpackFrame, relief=None, image=(shuffleArrowUp,
                 shuffleArrowDown,
                 shuffleArrowRollover,
                 shuffleArrowDisabled), image_scale=halfButtonInvertScale, image1_scale=halfButtonInvertHoverScale, image2_scale=halfButtonInvertHoverScale, pos=(0.2, 0, 0), command=self.swapBackpack, extraArgs=[1])

                shuffleButtonPos = (0, 0, -1.25)
                top -= 0.52

            self.shoesFrame = DirectFrame(parent=self.parentFrame, image=shuffleFrame, image_scale=halfButtonInvertScale, relief=None, pos=(0, 0, top - 0.77), hpr=(0, 0, -2), scale=1.2, frameColor=(1, 1, 1, 1), text=TTLocalizer.ClothesShopShoes, text_scale=0.0575, text_pos=(-0.001, -0.015), text_fg=(1, 1, 1, 1))
            self.shoesLButton = DirectButton(parent=self.shoesFrame, relief=None, image=(shuffleArrowUp,
             shuffleArrowDown,
             shuffleArrowRollover,
             shuffleArrowDisabled), image_scale=halfButtonScale, image1_scale=halfButtonHoverScale, image2_scale=halfButtonHoverScale, pos=(-0.2, 0, 0), command=self.swapShoes, extraArgs=[-1])
            self.shoesRButton = DirectButton(parent=self.shoesFrame, relief=None, image=(shuffleArrowUp,
             shuffleArrowDown,
             shuffleArrowRollover,
             shuffleArrowDisabled), image_scale=halfButtonInvertScale, image1_scale=halfButtonInvertHoverScale, image2_scale=halfButtonInvertHoverScale, pos=(0.2, 0, 0), command=self.swapShoes, extraArgs=[1])

        self.parentFrame.hide()
        self.shuffleFetchMsg = 'ClothesShopShuffle'
        self.shuffleButton = ShuffleButton.ShuffleButton(self, self.shuffleFetchMsg, pos=shuffleButtonPos)
        return

    def unload(self):
        self.gui.removeNode()
        del self.gui
        self.parentFrame.destroy()
        self.shirtFrame.destroy()
        self.topLButton.destroy()
        self.topRButton.destroy()
        self.bottomFrame.destroy()
        self.bottomLButton.destroy()
        self.bottomRButton.destroy()
        if self.hatFrame:
            self.hatFrame.destroy()
            self.hatLButton.destroy()
            self.hatRButton.destroy()
        if self.glassesFrame:
            self.glassesFrame.destroy()
            self.glassesLButton.destroy()
            self.glassesRButton.destroy()
        if self.backpackFrame:
            self.backpackFrame.destroy()
            self.backpackLButton.destroy()
            self.backpackRButton.destroy()
        if self.shoesFrame:
            self.shoesFrame.destroy()
            self.shoesLButton.destroy()
            self.shoesRButton.destroy()
        del self.parentFrame
        del self.shirtFrame
        del self.topLButton
        del self.topRButton
        del self.bottomFrame
        del self.bottomLButton
        del self.bottomRButton
        if self.hatFrame:
            del self.hatFrame
            del self.hatLButton
            del self.hatRButton
        if self.glassesFrame:
            del self.glassesFrame
            del self.glassesLButton
            del self.glassesRButton
        if self.backpackFrame:
            del self.backpackFrame
            del self.backpackLButton
            del self.backpackRButton
        if self.shoesFrame:
            del self.shoesFrame
            del self.shoesLButton
            del self.shoesRButton
        self.shuffleButton.unload()
        self.ignore('MAT-newToonCreated')

    def showButtons(self):
        self.parentFrame.show()

    def hideButtons(self):
        self.parentFrame.hide()

    def enter(self, toon):
        self.notify.debug('enter')
        base.disableMouse()
        self.toon = toon
        self.setupScrollInterface()
        if not self.type == CLOTHES_TAILOR:
            currTop = (self.toon.style.topTex,
             self.toon.style.topTexColor,
             self.toon.style.sleeveTex,
             self.toon.style.sleeveTexColor)
            currTopIndex = self.tops.index(currTop)
            self.swapTop(currTopIndex - self.topChoice)
            currBottom = (self.toon.style.botTex, self.toon.style.botTexColor)
            currBottomIndex = self.bottoms.index(currBottom)
            self.swapBottom(currBottomIndex - self.bottomChoice)
            if not self.type == CLOTHES_CLOSET:
                currHatIndex = self.hats.index(self.toon.hat)
                self.swapHat(currHatIndex - self.hatChoice)
                currShoesIndex = self.shoes.index(self.toon.shoes)
                self.swapShoes(currShoesIndex - self.shoesChoice)
                if not self.type == CLOTHES_MAKETOON:
                    currGlassesIndex = self.glasses.index(self.toon.glasses)
                    self.swapGlasses(currGlassesIndex - self.glassesChoice)
                    currBackpackIndex = self.backpacks.index(self.toon.backpack)
                    self.swapBackpack(currBackpackIndex - self.backpackChoice)
        choicePool = [self.tops, self.bottoms, self.hats, self.glasses, self.backpacks, self.shoes]
        self.shuffleButton.setChoicePool(choicePool)
        self.accept(self.shuffleFetchMsg, self.changeClothes)
        self.acceptOnce('MAT-newToonCreated', self.shuffleButton.cleanHistory)

    def exit(self):
        try:
            del self.toon
        except:
            self.notify.warning('ClothesGUI: toon not found')

        self.hideButtons()
        self.ignore('enter')
        self.ignore('next')
        self.ignore('last')
        self.ignore(self.shuffleFetchMsg)

    def setupButtons(self):
        self.girlInShorts = 0
        if self.gender == 'f':
            if self.bottomChoice == -1:
                botTex = self.bottoms[0][0]
            else:
                botTex = self.bottoms[self.bottomChoice][0]
            if ToonDNA.GirlBottoms[botTex][1] == ToonDNA.SHORTS:
                self.girlInShorts = 1
        if self.toon.style.getGender() == 'm':
            self.bottomFrame['text'] = TTLocalizer.ClothesShopShorts
        else:
            self.bottomFrame['text'] = TTLocalizer.ClothesShopBottoms
        self.acceptOnce('last', self.__handleBackward)
        self.acceptOnce('next', self.__handleForward)
        return None

    def swapTop(self, offset):
        length = len(self.tops)
        self.topChoice += offset
        if self.topChoice <= 0:
            self.topChoice = 0
        self.updateScrollButtons(self.topChoice, length, 0, self.topLButton, self.topRButton)
        if self.topChoice < 0 or self.topChoice >= len(self.tops) or len(self.tops[self.topChoice]) != 4:
            self.notify.warning('topChoice index is out of range!')
            return None
        self.toon.style.topTex = self.tops[self.topChoice][0]
        self.toon.style.topTexColor = self.tops[self.topChoice][1]
        self.toon.style.sleeveTex = self.tops[self.topChoice][2]
        self.toon.style.sleeveTexColor = self.tops[self.topChoice][3]
        self.toon.generateToonClothes()
        if self.swapEvent != None:
            messenger.send(self.swapEvent)
        messenger.send('wakeup')

    def swapBottom(self, offset):
        length = len(self.bottoms)
        self.bottomChoice += offset
        if self.bottomChoice <= 0:
            self.bottomChoice = 0
        self.updateScrollButtons(self.bottomChoice, length, 0, self.bottomLButton, self.bottomRButton)
        if self.bottomChoice < 0 or self.bottomChoice >= len(self.bottoms) or len(self.bottoms[self.bottomChoice]) != 2:
            self.notify.warning('bottomChoice index is out of range!')
            return None
        self.toon.style.botTex = self.bottoms[self.bottomChoice][0]
        self.toon.style.botTexColor = self.bottoms[self.bottomChoice][1]
        if self.toon.generateToonClothes() == 1:
            self.toon.loop('neutral', 0)
            self.swappedTorso = 1
        if self.swapEvent != None:
            messenger.send(self.swapEvent)
        messenger.send('wakeup')

    def swapHat(self, offset):
        if self.type == CLOTHES_CLOSET:
            return
        if self.hatChoice < 0:
            # Don't choose the 'none' selection initially
            self.hatChoice = 1

            # Skip this hat if we are already wearing it
            if self.toon.getHat() == self.hats[self.hatChoice]:
                if offset > 0 and len(self.hats) > 2:
                    self.hatChoice += 1
                else:
                    # Nevermind, choose 'none'
                    self.hatChoice = 0
        else:
            self.hatChoice += offset
            if self.hatChoice < 0:
                self.hatChoice = 0
        self.updateScrollButtons(self.hatChoice, len(self.hats), 0, self.hatLButton, self.hatRButton)
        if self.hatChoice < 0 or self.hatChoice >= len(self.hats) or len(self.hats[self.hatChoice]) != 3:
            self.notify.warning('hatChoice index is out of range!')
            return None
        self.toon.setHat(*self.hats[self.hatChoice])
        if self.swapEvent != None:
            messenger.send(self.swapEvent)
        messenger.send('wakeup')

    def swapGlasses(self, offset):
        if self.type != CLOTHES_TAILOR:
            return
        if self.glassesChoice < 0:
            # Don't choose the 'none' selection initially
            self.glassesChoice = 1

            # Skip these glasses if we are already wearing them
            if self.toon.getGlasses() == self.glasses[self.glassesChoice]:
                if offset > 0 and len(self.glasses) > 2:
                    self.glassesChoice += 1
                else:
                    # Nevermind, choose 'none'
                    self.glassesChoice = 0
        else:
            self.glassesChoice += offset
            if self.glassesChoice < 0:
                self.glassesChoice = 0
        self.updateScrollButtons(self.glassesChoice, len(self.glasses), 0, self.glassesLButton, self.glassesRButton)
        if self.glassesChoice < 0 or self.glassesChoice >= len(self.glasses) or len(self.glasses[self.glassesChoice]) != 3:
            self.notify.warning('glassesChoice index is out of range!')
            return None
        self.toon.setGlasses(*self.glasses[self.glassesChoice])
        if self.swapEvent != None:
            messenger.send(self.swapEvent)
        messenger.send('wakeup')

    def swapBackpack(self, offset):
        if self.type != CLOTHES_TAILOR:
            return
        if self.backpackChoice < 0:
            # Don't choose the 'none' selection initially
            self.backpackChoice = 1

            # Skip this backpack if we are already wearing it
            if self.toon.getBackpack() == self.backpacks[self.backpackChoice]:
                if offset > 0 and len(self.backpacks) > 2:
                    self.backpackChoice += 1
                else:
                    # Nevermind, choose 'none'
                    self.backpackChoice = 0
        else:
            self.backpackChoice += offset
            if self.backpackChoice < 0:
                self.backpackChoice = 0
        self.updateScrollButtons(self.backpackChoice, len(self.backpacks), 0, self.backpackLButton, self.backpackRButton)
        if self.backpackChoice < 0 or self.backpackChoice >= len(self.backpacks) or len(self.backpacks[self.backpackChoice]) != 3:
            self.notify.warning('backpackChoice index is out of range!')
            return None
        self.toon.setBackpack(*self.backpacks[self.backpackChoice])
        if self.swapEvent != None:
            messenger.send(self.swapEvent)
        messenger.send('wakeup')

    def swapShoes(self, offset):
        if self.type == CLOTHES_CLOSET:
            return
        if self.shoesChoice < 0:
            # Don't choose the 'none' selection initially
            self.shoesChoice = 1

            # Skip these shoes if we are already wearing them
            if self.toon.getShoes() == self.shoes[self.shoesChoice]:
                if offset > 0 and len(self.shoes) > 2:
                    self.shoesChoice += 1
                else:
                    # Nevermind, choose 'none'
                    self.shoesChoice = 0
        else:
            self.shoesChoice += offset
            if self.shoesChoice < 0:
                self.shoesChoice = 0
        self.updateScrollButtons(self.shoesChoice, len(self.shoes), 0, self.shoesLButton, self.shoesRButton)
        if self.shoesChoice < 0 or self.shoesChoice >= len(self.shoes) or len(self.shoes[self.shoesChoice]) != 3:
            self.notify.warning('shoesChoice index is out of range!')
            return None
        self.toon.setShoes(*self.shoes[self.shoesChoice])
        if self.swapEvent != None:
            messenger.send(self.swapEvent)
        messenger.send('wakeup')

    def updateScrollButtons(self, choice, length, startTex, lButton, rButton):
        if choice >= length - 1:
            rButton['state'] = DGG.DISABLED
        else:
            rButton['state'] = DGG.NORMAL
        if choice <= 0:
            lButton['state'] = DGG.DISABLED
        else:
            lButton['state'] = DGG.NORMAL

    def __handleForward(self):
        self.doneStatus = 'next'
        messenger.send(self.doneEvent)

    def __handleBackward(self):
        self.doneStatus = 'last'
        messenger.send(self.doneEvent)

    def resetClothes(self, style, accessories=None):
        if self.toon:
            self.toon.style.makeFromNetString(style.makeNetString())
            if accessories:
                self.toon.setAccessoriesFromNetString(Toon.makeAccessoryNetString(*accessories))
            if self.swapEvent != None and self.swappedTorso == 1:
                self.toon.swapToonTorso(self.toon.style.torso, genClothes=0)
                self.toon.generateToonClothes()
                self.toon.loop('neutral', 0)
        return

    def changeClothes(self):
        self.notify.debug('Entering changeClothes')
        newChoice = self.shuffleButton.getCurrChoice()
        if newChoice[0] in self.tops:
            newTopIndex = self.tops.index(newChoice[0])
        else:
            newTopIndex = self.topChoice
        if newChoice[1] in self.bottoms:
            newBottomIndex = self.bottoms.index(newChoice[1])
        else:
            newBottomIndex = self.bottomChoice
        if newChoice[2] in self.hats:
            newHatIndex = self.hats.index(newChoice[2])
        else:
            newHatIndex = self.hatChoice
        if newChoice[3] in self.glasses:
            newGlassesIndex = self.glasses.index(newChoice[3])
        else:
            newGlassesIndex = self.glassesChoice
        if newChoice[4] in self.backpacks:
            newBackpackIndex = self.backpacks.index(newChoice[4])
        else:
            newBackpackIndex = self.backpackChoice
        if newChoice[5] in self.shoes:
            newShoesIndex = self.shoes.index(newChoice[5])
        else:
            newShoesIndex = self.shoesChoice
        oldTopIndex = self.topChoice
        oldBottomIndex = self.bottomChoice
        oldHatIndex = self.hatChoice
        oldGlassesIndex = self.glassesChoice
        oldBackpackIndex = self.backpackChoice
        oldShoesIndex = self.shoesChoice
        self.swapTop(newTopIndex - oldTopIndex)
        self.swapBottom(newBottomIndex - oldBottomIndex)
        if len(self.hats) > 1:
            self.swapHat(newHatIndex - oldHatIndex)
        if len(self.glasses) > 1:
            self.swapGlasses(newGlassesIndex - oldGlassesIndex)
        if len(self.backpacks) > 1:
            self.swapBackpack(newBackpackIndex - oldBackpackIndex)
        if len(self.shoes) > 1:
            self.swapShoes(newShoesIndex - oldShoesIndex)

    def getCurrToonSetting(self):
        return [self.tops[self.topChoice], self.bottoms[self.bottomChoice], self.hats[self.hatChoice], self.shoes[self.shoesChoice]]
