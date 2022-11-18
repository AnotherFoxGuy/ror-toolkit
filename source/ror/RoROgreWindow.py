#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import wx 
import Ogre
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *
from random import random

class RoROgreWindow(wxOgreWindow): 
    def __init__(self, parent, ID, size = wx.Size(200,200), renderSystem = "OpenGL", **kwargs): 
        self.rand = str(random())
        wxOgreWindow.__init__(self, parent, ID, size = size, renderSystem = renderSystem, **kwargs) 
        self.parent = parent

    def SceneInitialisation(self):
        # only init things in the main window, not in shared ones!
        # setup resources 
        Ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/main", "FileSystem", "OgreInternal", False)
        Ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/packs/OgreCore.zip", "Zip", "Bootstrap", False)
        Ogre.ResourceGroupManager.getSingleton().addResourceLocation("media", "FileSystem", "General", False)
        Ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/fonts", "FileSystem", "General", False)
        Ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/materials/programs", "FileSystem", "General", False)
        Ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/materials/scripts", "FileSystem", "General", False)
        Ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/materials/textures", "FileSystem", "General", False)
        Ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/models", "FileSystem", "General", False)
        Ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/overlays", "FileSystem", "General", False)
        Ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/particle", "FileSystem", "General", False)
        Ogre.ResourceGroupManager.getSingleton().initialiseAllResourceGroups() 

        #get the scenemanager
        self.sceneManager = getOgreManager().createSceneManager() #Ogre.SceneManager.ST_GENERIC

        # create a camera
        self.camera = self.sceneManager.createCamera(str(randomID()) + 'Camera')
        self.camera_sn = self.sceneManager.getRootSceneNode().createChildSceneNode()
        self.camera_sn.attachObject(self.camera)
        self.camera_sn.lookAt(Ogre.Vector3(0, 0, 0), Ogre.Node.TS_WORLD)
        self.camera_sn.setPosition(Ogre.Vector3(0, 0, 100))
        self.camera.nearClipDistance = 1
        self.camera.setAutoAspectRatio(True)

        # create the Viewport"
        self.viewport = self.renderWindow.addViewport(self.camera, 0, 0.0, 0.0, 1.0, 1.0)
        self.viewport.backgroundColour = Ogre.ColourValue(0, 0, 0)
        self.viewport.setOverlaysEnabled(False)  # disable terrain Editor overlays on this viewport

        # bind mouse and keyboard
        d=10.0 #displacement for key strokes 
        self.ControlKeyDict={wx.WXK_LEFT:Ogre.Vector3(-d,0.0,0.0), 
                             wx.WXK_RIGHT:Ogre.Vector3(d,0.0,0.0), 
                             wx.WXK_UP:Ogre.Vector3(0.0,0.0,-d), 
                             wx.WXK_DOWN:Ogre.Vector3(0.0,0.0,d), 
                             wx.WXK_PAGEUP:Ogre.Vector3(0.0,d,0.0), 
                             wx.WXK_PAGEDOWN:Ogre.Vector3(0.0,-d,0.0)} 
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown) 
        self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)
        
        #create objects
        self.populateScene()
    
    def populateScene(self):
        self.sceneManager.AmbientLight = Ogre.ColourValue(0.7, 0.7, 0.7 )
        self.sceneManager.setShadowTechnique(Ogre.ShadowTechnique.SHADOWTYPE_STENCIL_ADDITIVE);
        self.sceneManager.setSkyDome(True, 'Examples/CloudySky', 4.0, 8.0) 

        self.MainLight = self.sceneManager.createLight('MainLight') 
        self.MainLight.setPosition (Ogre.Vector3(20, 80, 130))

        # add some fog 
#        self.sceneManager.setFog(Ogre.FOG_EXP, Ogre.ColourValue.White, 0.0002) 

        # create a floor Mesh
        plane = Ogre.Plane() 
        plane.normal = Ogre.Vector3(0, 1, 0) 
        plane.d = 200 
        
        Ogre.MeshManager.getSingleton().createPlane('FloorPlane' + self.rand, "General", plane, 200000.0, 200000.0, 
                                                    20, 20, True, 1, 50.0, 50.0,Ogre.Vector3(0, 0, 1),
                                                    Ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY, 
                                                    Ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY, 
                                                    True, True)

        # create floor entity 
        entity = self.sceneManager.createEntity('floor', 'FloorPlane' + self.rand)
        entity.setMaterialName('Examples/RustySteel')
        self.sceneManager.getRootSceneNode().createChildSceneNode().attachObject(entity)

        # create a mesh
        fishNode = self.sceneManager.getRootSceneNode().createChildSceneNode("fishNode" + self.rand)
        entity = self.sceneManager.createEntity('fishEnt' + self.rand, 'fish.mesh')
        fishNode.attachObject(entity)
        fishNode.setScale(10.0, 10.0, 10.0)
        entity.setCastShadows(True)

    def onKeyDown(self, event):
        validMove = self.ControlKeyDict.get(event.m_keyCode, False)
        if validMove:
            pos = self.camera.getPosition()
            pos += validMove
            self.camera.setPosition(pos)
        event.Skip()

    def onMouseEvent(self, event):
        self.SetFocus()  # Gives Keyboard focus to the window

        if event.RightDown():  # Precedes dragging
            self.StartDragX, self.StartDragY = event.GetPosition()  # saves position of initial click

        if event.Dragging() and event.RightIsDown():  # Dragging with RMB
            x, y = event.GetPosition()
            dx = self.StartDragX - x
            dy = self.StartDragY - y
            self.StartDragX, self.StartDragY = x, y

            self.camera.yaw(Ogre.Degree(dx / 3.0))
            self.camera.pitch(Ogre.Degree(dy / 3.0))
        event.Skip()
