from toontown.estate import DistributedStatuary
from toontown.estate import DistributedLawnDecor
from direct.directnotify import DirectNotifyGlobal
from direct.showbase.ShowBase import *
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from panda3d.core import *
from toontown.toon import Toon
from toontown.toon import ToonDNA
from . import GardenGlobals
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from panda3d.core import NodePath
from panda3d.core import Point3

def appearanceFromToon(toon):
    def findItemNumInList(wantItem, wantList):
        i = 0
        for item in wantList:
            if item == wantItem:
                break
            i += 1

        return i

    dna = toon.style
    if dna.gender == 'f':
        genderTypeNum = 0
    else:
        genderTypeNum = 1
    legTypeNum = findItemNumInList(dna.legs, ToonDNA.toonLegTypes)
    torsoTypeNum = findItemNumInList(dna.torso, ToonDNA.toonTorsoTypes)
    headTypeNum = findItemNumInList(dna.head, ToonDNA.toonHeadTypes)

    dg = PyDatagram()
    dg.addUint8(legTypeNum)
    dg.addUint8(torsoTypeNum)
    dg.addUint8(headTypeNum)
    dg.addUint8(genderTypeNum)

    # Store the accessories.
    # We only need the model and the texture.
    hat = toon.getHat()
    glasses = toon.getGlasses()
    backpack = toon.getBackpack()
    shoes = toon.getShoes()

    dg.addUint8(hat[0])
    dg.addUint8(hat[1])
    dg.addUint8(glasses[0])
    dg.addUint8(glasses[1])
    dg.addUint8(backpack[0])
    dg.addUint8(backpack[1])
    dg.addUint8(shoes[0])
    dg.addUint8(shoes[1])

    return dg.getMessage()


class DistributedToonStatuary(DistributedStatuary.DistributedStatuary):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedToonStatuary')

    def __init__(self, cr):
        self.notify.debug('constructing DistributedToonStatuary')
        DistributedStatuary.DistributedStatuary.__init__(self, cr)
        self.toon = None
        return

    def loadModel(self):
        DistributedStatuary.DistributedStatuary.loadModel(self)
        self.model.setScale(self.worldScale * 1.5, self.worldScale * 1.5, self.worldScale)
        self.getToonPropertiesFromOptional()
        dna = ToonDNA.ToonDNA()
        dna.newToonFromProperties(self.headType, self.torsoType, self.legType, self.gender, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.setupStoneToon(dna)
        self.poseToonFromTypeIndex(self.typeIndex)
        self.toon.reparentTo(self.model)

    def delete(self):
        self.deleteToon()
        DistributedStatuary.DistributedStatuary.delete(self)

    def setupStoneToon(self, dna):
        self.toon = Toon.Toon()
        self.toon.setPos(0, 0, 0)
        self.toon.setDNA(dna)
        self.toon.setHat(self.hatType, self.hatTexture, 0)
        self.toon.setGlasses(self.glassesType, self.glassesTexture, 0)
        self.toon.setBackpack(self.backpackType, self.backpackTexture, 0)
        self.toon.setShoes(self.shoesType, self.shoesTexture, 0)
        self.toon.initializeBodyCollisions('toonStatue')
        self.toon.stopBlink()
        self.toon.stopLookAround()
        self.gender = self.toon.style.gender
        self.speciesType = self.toon.style.getAnimal()
        self.headType = self.toon.style.head
        self.removeTextures()
        self.setStoneTexture()
        self.toon.dropShadow.hide()
        self.toon.setZ(70)
        self.toon.setScale(20 / 1.5, 20 / 1.5, 20)

    def deleteToon(self):
        self.notify.debug('entering deleteToon')
        self.toon.delete()
        self.toon = None
        return

    # This is unused.
    def copyLocalAvatarToon(self):
        self.toon = Toon.Toon()
        self.toon.reparentTo(render)
        self.toon.copyLook(base.localAvatar)
        self.toon.setPos(base.localAvatar, 0, 0, 0)
        self.toon.pose('victory', 30)
        self.toon.setH(180)
        self.speciesType = self.toon.style.getAnimal()
        self.gender = self.toon.style.gender

    def setupCollision(self):
        DistributedStatuary.DistributedStatuary.setupCollision(self)
        self.colSphereNode.setScale(self.colSphereNode.getScale() * 1.5)

    def setupShadow(self):
        pass

    def removeTextures(self):
        for node in self.toon.findAllMatches('**/*'):
            node.setState(RenderState.makeEmpty())

        desatShirtTex = loader.loadTexture('phase_3/maps/desat_shirt_1.png')
        desatSleeveTex = loader.loadTexture('phase_3/maps/desat_sleeve_1.png')
        desatShortsTex = loader.loadTexture('phase_3/maps/desat_shorts_1.png')
        desatSkirtTex = loader.loadTexture('phase_3/maps/desat_skirt_1.png')
        if self.toon.hasLOD():
            for lodName in self.toon.getLODNames():
                torso = self.toon.getPart('torso', lodName)
                torsoTop = torso.find('**/torso-top')
                if torsoTop:
                    torsoTop.setTexture(desatShirtTex, 1)
                sleeves = torso.find('**/sleeves')
                if sleeves:
                    sleeves.setTexture(desatSleeveTex, 1)
                bottoms = torso.findAllMatches('**/torso-bot*')
                for bottomNum in range(0, bottoms.getNumPaths()):
                    bottom = bottoms.getPath(bottomNum)
                    if bottom:
                        if self.toon.style.torso[1] == 's':
                            bottom.setTexture(desatShortsTex, 1)
                        else:
                            bottom.setTexture(desatSkirtTex, 1)

    def setStoneTexture(self):
        gray = VBase4(1.6, 1.6, 1.6, 1)
        self.toon.setColor(gray, 10)
        stoneTex = loader.loadTexture('phase_5.5/maps/smoothwall_1.png')
        ts = TextureStage('ts')
        ts.setPriority(1)
        self.toon.setTexture(ts, stoneTex)
        tsDetail = TextureStage('tsDetail')
        tsDetail.setPriority(2)
        tsDetail.setSort(10)
        tsDetail.setCombineRgb(tsDetail.CMInterpolate, tsDetail.CSTexture, tsDetail.COSrcColor, tsDetail.CSPrevious, tsDetail.COSrcColor, tsDetail.CSConstant, tsDetail.COSrcColor)
        tsDetail.setColor(VBase4(0.5, 0.5, 0.5, 1))
        if self.toon.hasLOD():
            for lodName in self.toon.getLODNames():
                head = self.toon.getPart('head', lodName)
                eyes = head.find('**/eye*')
                if not eyes.isEmpty():
                    eyes.setColor(Vec4(1.4, 1.4, 1.4, 0.3), 10)
                ears = head.find('**/ears*')
                animal = self.toon.style.getAnimal()
                if animal != 'dog':
                    muzzle = head.find('**/muzzle*neutral')
                else:
                    muzzle = head.find('**/muzzle*')
                if ears != ears.notFound():
                    if self.speciesType == 'cat':
                        ears.setTexture(tsDetail, stoneTex)
                    elif self.speciesType == 'horse':
                        pass
                    elif self.speciesType == 'rabbit':
                        ears.setTexture(tsDetail, stoneTex)
                    elif self.speciesType == 'monkey':
                        ears.setTexture(tsDetail, stoneTex)
                        ears.setColor(VBase4(0.6, 0.9, 1, 1), 10)
                if muzzle != muzzle.notFound():
                    muzzle.setTexture(tsDetail, stoneTex)
                if self.speciesType == 'dog':
                    nose = head.find('**/nose')
                    if nose != nose.notFound():
                        nose.setTexture(tsDetail, stoneTex)

        tsLashes = TextureStage('tsLashes')
        tsLashes.setPriority(2)
        tsLashes.setMode(tsLashes.MDecal)
        if self.gender == 'f':
            if self.toon.hasLOD():
                head = self.toon.getPart('head', '1000')
            else:
                head = self.toon.getPart('head', 'lodRoot')
            if self.headType[1] == 'l':
                openString = 'open-long'
                closedString = 'closed-long'
            else:
                openString = 'open-short'
                closedString = 'closed-short'
            lashesOpen = head.find('**/' + openString)
            lashesClosed = head.find('**/' + closedString)
            if lashesOpen != lashesOpen.notFound():
                lashesOpen.setTexture(tsLashes, stoneTex)
                lashesOpen.setColor(VBase4(1, 1, 1, 0.4), 10)
            if lashesClosed != lashesClosed.notFound():
                lashesClosed.setTexture(tsLashes, stoneTex)
                lashesClosed.setColor(VBase4(1, 1, 1, 0.4), 10)

        def makeAccessoryGrayscale(node, texturePath):
            geomState = node.getGeomState(0)
            texAttrib = geomState.getAttrib(TextureAttrib.getClassType())
            if not texAttrib:
                return

            # Load the actual texture of the accessory, if it has one defined
            if texturePath:
                sourceTex = loader.loadTexture(texturePath, okMissing=True)
            else:
                sourceTex = None

            # Make a copy of the texture it already has
            stage = texAttrib.getOnStage(0)
            texture = texAttrib.getOnTexture(stage)
            if not texture:
                return
            texture = texture.makeCopy()

            # Store the source texture into a PNMImage, make it grayscale, then
            # load it into the target texture
            pnm = PNMImage()
            if sourceTex:
                sourceTex.store(pnm)
            else:
                texture.store(pnm)
            pnm.makeGrayscale()
            texture.load(pnm)

            # Re-add the texture
            attrib = texAttrib.addOnStage(stage, texture)
            node.setGeomState(0, geomState.setAttrib(attrib))

        def makeAccessoryPathGrayscale(node, texturePath):
            for np in node.findAllMatches('**/+GeomNode'):
                makeAccessoryGrayscale(np.node(), texturePath)

        # Give the stone appearance to the accessories
        for node in self.toon.hatNodes:
            makeAccessoryPathGrayscale(node, ToonDNA.HatTextures[self.hatTexture])
        for node in self.toon.glassesNodes:
            makeAccessoryPathGrayscale(node, ToonDNA.GlassesTextures[self.glassesTexture])
        for node in self.toon.backpackNodes:
            makeAccessoryPathGrayscale(node, ToonDNA.BackpackTextures[self.backpackTexture])
        for geom in self.toon.findAllMatches('**/%s;+s' % ToonDNA.ShoesModels[self.shoesType]):
            makeAccessoryGrayscale(geom.node(), ToonDNA.ShoesTextures[self.shoesTexture])

    def setOptional(self, optional):
        self.optional = optional

    def getToonPropertiesFromOptional(self):
        dg = PyDatagram(self.optional)
        dgi = PyDatagramIterator(dg)

        legTypeNum = dgi.getUint8()
        torsoTypeNum = dgi.getUint8()
        headTypeNum = dgi.getUint8()
        genderTypeNum = dgi.getUint8()
        if genderTypeNum == 0:
            self.gender = 'f'
        else:
            self.gender = 'm'
        if legTypeNum <= len(ToonDNA.toonLegTypes):
            self.legType = ToonDNA.toonLegTypes[legTypeNum]
        if torsoTypeNum <= len(ToonDNA.toonTorsoTypes):
            self.torsoType = ToonDNA.toonTorsoTypes[torsoTypeNum]
        if headTypeNum <= len(ToonDNA.toonHeadTypes):
            self.headType = ToonDNA.toonHeadTypes[headTypeNum]

        self.hatType = dgi.getUint8()
        self.hatTexture = dgi.getUint8()
        self.glassesType = dgi.getUint8()
        self.glassesTexture = dgi.getUint8()
        self.backpackType = dgi.getUint8()
        self.backpackTexture = dgi.getUint8()
        self.shoesType = dgi.getUint8()
        self.shoesTexture = dgi.getUint8()

    def poseToonFromTypeIndex(self, typeIndex):
        if typeIndex == 205:
            self.toon.pose('wave', 18)
        elif typeIndex == 206:
            self.toon.pose('victory', 116)
        elif typeIndex == 207:
            self.toon.pose('bored', 96)
        elif typeIndex == 208:
            self.toon.pose('think', 59)

    def poseToonFromSpecialsIndex(self, specialsIndex):
        if specialsIndex == 105:
            self.toon.pose('wave', 18)
        elif specialsIndex == 106:
            self.toon.pose('victory', 116)
        elif specialsIndex == 107:
            self.toon.pose('bored', 96)
        elif specialsIndex == 108:
            self.toon.pose('think', 59)
