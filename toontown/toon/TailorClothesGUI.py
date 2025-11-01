from toontown.makeatoon import ClothesGUI
from . import ToonDNA
from direct.gui.DirectGui import *

class TailorClothesGUI(ClothesGUI.ClothesGUI):
    notify = directNotify.newCategory('MakeClothesGUI')

    def __init__(self, doneEvent, swapEvent, tailorId):
        ClothesGUI.ClothesGUI.__init__(self, ClothesGUI.CLOTHES_TAILOR, doneEvent, swapEvent)
        self.tailorId = tailorId

    def setupScrollInterface(self):
        self.dna = self.toon.getStyle()
        gender = self.dna.getGender()
        if self.swapEvent != None:
            self.tops = ToonDNA.getTops(gender, tailorId=self.tailorId)
            self.bottoms = ToonDNA.getBottoms(gender, tailorId=self.tailorId)
            self.hats = ToonDNA.getHats(gender, tailorId=self.tailorId)
            self.glasses = ToonDNA.getGlasses(gender, tailorId=self.tailorId)
            self.backpacks = ToonDNA.getBackpacks(gender, tailorId=self.tailorId)
            self.shoes = ToonDNA.getShoes(gender, tailorId=self.tailorId)
            self.gender = gender
            self.topChoice = -1
            self.bottomChoice = -1
            self.hatChoice = -1
            self.glassesChoice = -1
            self.backpackChoice = -1
            self.shoesChoice = -1
            # The 'none' choice is always present, which is why those checks
            # are like this.
            if len(self.hats) <= 1:
                self.hatLButton['state'] = DGG.DISABLED
                self.hatRButton['state'] = DGG.DISABLED
            if len(self.glasses) <= 1:
                self.glassesLButton['state'] = DGG.DISABLED
                self.glassesRButton['state'] = DGG.DISABLED
            if len(self.backpacks) <= 1:
                self.backpackLButton['state'] = DGG.DISABLED
                self.backpackRButton['state'] = DGG.DISABLED
            if len(self.shoes) <= 1:
                self.shoesLButton['state'] = DGG.DISABLED
                self.shoesRButton['state'] = DGG.DISABLED

        self.setupButtons()
        return
