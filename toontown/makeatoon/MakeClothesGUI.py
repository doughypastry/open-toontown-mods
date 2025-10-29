from . import ClothesGUI
from toontown.toon import ToonDNA

class MakeClothesGUI(ClothesGUI.ClothesGUI):
    notify = directNotify.newCategory('MakeClothesGUI')

    def __init__(self, doneEvent):
        ClothesGUI.ClothesGUI.__init__(self, ClothesGUI.CLOTHES_MAKETOON, doneEvent)

    def setupScrollInterface(self):
        self.dna = self.toon.getStyle()
        self.tops = ToonDNA.getRandomizedTops(tailorId=ToonDNA.MAKE_A_TOON)
        self.bottoms = ToonDNA.getRandomizedBottoms(tailorId=ToonDNA.MAKE_A_TOON)
        self.topChoice = 0
        self.bottomChoice = 0
        self.setupButtons()

    def setupButtons(self):
        ClothesGUI.ClothesGUI.setupButtons(self)
        # This handles a naked Toon, which isn't possible, so this can be
        # removed safely. I removed just the gender-specific bits.
        if len(self.dna.torso) == 1:
            torsoStyle = 's'
            self.toon.swapToonTorso(self.dna.torso[0] + torsoStyle)
            self.toon.loop('neutral', 0)
            self.toon.swapToonColor(self.dna)
            self.swapTop(0)
            self.swapBottom(0)
        return None
