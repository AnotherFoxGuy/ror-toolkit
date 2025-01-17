#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import wx, os, os.path
import ogre.renderer.OGRE as ogre
from ror.truckparser import *

from ror.logger import log
from ror.settingsManager import rorSettings

from ror.rorcommon import *
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *

import ogre.renderer.OGRE as Ogre
#import ogre.physics.OgreNewt as OgreNewt
import ogre.io.OIS as OIS

IMGSCALE = 20

class RoRTruckUVOgreWindow(wxOgreWindow):
	def __init__(self, parent, ID, size = wx.Size(200,200), **kwargs):
		self.parent = parent
		self.rordir = rorSettings().rorFolder
		self.sceneManager = None
		self.trucktree = None
		self.clearlist = {'entity':[]}
		self.initScene()
		wxOgreWindow.__init__(self, parent, ID, "truckUV", size = size, **kwargs)

	def initScene(self):
		if not self.sceneManager is None:
			self.sceneManager.clearScene()
		self.EntityCount = 0
		self.bodies=[]
		self.trucktree = None
		self.clearlist = {'entity':[]}
# Lepes comment it
#		# try to clear things up
#		try:
#			if self.nodes != {}:
#				for n in self.nodes:
#					n[0].detachAllObjects()
#					self.sceneManager.destroySceneNode(n[0].getName())
#		except:
#			pass
#		try:
#			for e in self.clearlist['entity']:
#				print e
#				self.sceneManager.destroyEntity(e)
#		except:
#			pass

		self.nodes = {}
		self.beams = {}
		self.shocks = {}
		self.submeshs = {}
		self.selection = None
		self.enablephysics = False


	def __del__ (self):
		# delete the world when we're done.
		self.sceneManager.destroyEntity('groundent')
		#ogre.ResourceGroupManager.getSingleton().undeclareResource("UVGroundPlane", "General")

		del self.bodies


	def OnFrameStarted(self):
		pass

	def OnFrameEnded(self):
		pass

	def SceneInitialisation(self):
		initResources()
	
		#get the scenemanager
		self.sceneManager = getOgreManager().createSceneManager(ogre.ST_GENERIC)

		# create a camera
		self.camera = self.sceneManager.createCamera('Camera')
		self.camera.setAutoAspectRatio(True)
		self.camera.setProjectionType(Ogre.ProjectionType.PT_ORTHOGRAPHIC)
		self.camera.setFarClipDistance(9999)
		self.camera.setNearClipDistance(30)
		self.camera.setPosition(Ogre.Vector3(0,100,-0.1))
		self.camera.lookAt(Ogre.Vector3(0,0,0))

		# create the Viewport"
		self.viewport = self.renderWindow.addViewport(self.camera, 0, 0.0, 0.0, 1.0, 1.0)
		self.viewport.backgroundColour = ogre.ColourValue(0, 0, 0)

		#set some default values
		self.sceneDetailIndex = 0
		self.filtering = ogre.TFO_BILINEAR

		# bind mouse and keyboard
		self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)

		#create objects
		self.populateScene()


	def populateScene(self):
		self.sceneManager.AmbientLight = ogre.ColourValue(0.7, 0.7, 0.7 )

		fadeColour = (0.8, 0.8, 0.8)
#		self.sceneManager.setFog(ogre.FOG_EXP, ogre.ColourValue.White, 0.0002)
		#self.sceneManager.setFog(ogre.FOG_LINEAR, fadeColour, 0.001, 5000.0, 10000.0)
		self.renderWindow.getViewport(0).BackgroundColour = fadeColour

		self.sceneManager.AmbientLight = ogre.ColourValue(0.7, 0.7, 0.7 )
		self.sceneManager.setShadowTechnique(ogre.ShadowTechnique.SHADOWTYPE_STENCIL_ADDITIVE);
		self.sceneManager.setSkyDome(True, 'mysimple/truckEditorSky', 4.0, 8.0)

		self.MainLight = self.sceneManager.createLight('MainLight')
		self.MainLight.setPosition (ogre.Vector3(20, 80, 130))

		self.createUVGroundPlane()


	def setTree(self, tree):
		self.trucktree = tree
		self.createUVPlane()
		self.createUVIslands()

	def createUVGroundPlane(self):
		plane = ogre.Plane()
		plane.normal = ogre.Vector3(0, 1, 0)
		plane.d = 100
		# see http://www.ogre3d.org/docs/api/html/classOgre_1_1MeshManager.html#Ogre_1_1MeshManagera5
		uuid = randomID()
		ogre.MeshManager.getSingleton().createPlane(uuid+'UVGroundPlane', "General", plane, 2000, 2000,
												20, 20, True, 1, 200.0, 200.0, ogre.Vector3(0, 0, 1),
												ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY,
												ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY,
												True, True)
		entity = self.sceneManager.createEntity(uuid+'groundent', uuid+'UVGroundPlane')

		entity.setMaterialName('TruckEditor/UVBackground')
		self.groundplanenode = self.sceneManager.getRootSceneNode().createChildSceneNode()
		self.groundplanenode.attachObject(entity)

	def createUVIsland(self, smg, smgid):
		#print smg
		# read in nodes
		nodes = {}
		print "nodes"
		for nodeobj in self.trucktree['nodes']:
			if nodeobj.has_key('type'):
				continue
			node = nodeobj['data']
			print node
			nodes[int(node[0])] = ogre.Vector3(float(node[1]),float(node[2]),float(node[3]))

		# read in UVs then
		uv = {}
		print "uv"
		for data in smg['texcoords']:
			tex = data['data']
			print tex
			uv[int(tex[0])] = [float(tex[1]), float(tex[2])]

		# and create the triangles
		print "triangles"
		print self.trucktree['globals'][0]['data'][2]
		matname = self.trucktree['globals'][0]['data'][2]

		idstr = str(smgid)
		uuid = randomID()
		sm = self.sceneManager.createManualObject(uuid+"manualsmg"+idstr)
		sm.begin(matname, ogre.RenderOperation.OT_TRIANGLE_LIST)

		uvcounter = smgid * 100
		print "cab"
		for data in smg['cab']:
			cab = data['data']
			print cab
			if len(cab) == 0:
				continue

			idstr = str(smg)+str(uvcounter)
			uvcounter += 1
			line = self.sceneManager.createManualObject(uuid+"manualuv_" + idstr)
			mat = "TruckEditor/UVBeam"
			line.begin(mat, ogre.RenderOperation.OT_LINE_LIST)

			depth = 10

			uv1 = uv[int(cab[0])]
			pos1 = Ogre.Vector3((1-uv1[0]) * self.imgwidth/IMGSCALE - self.imgwidth/IMGSCALE/2, depth, (1-uv1[1]) * self.imgheight/IMGSCALE - self.imgheight/IMGSCALE/2)
			line.position(pos1)

			uv2 = uv[int(cab[1])]
			pos2 = Ogre.Vector3((1-uv2[0]) * self.imgwidth/IMGSCALE - self.imgwidth/IMGSCALE/2, depth, (1-uv2[1]) * self.imgheight/IMGSCALE - self.imgheight/IMGSCALE/2)
			line.position(pos2)

			uv3 = uv[int(cab[2])]
			pos3 = Ogre.Vector3((1-uv3[0]) * self.imgwidth/IMGSCALE - self.imgwidth/IMGSCALE/2, depth, (1-uv3[1]) * self.imgheight/IMGSCALE - self.imgheight/IMGSCALE/2)
			line.position(pos3)
			line.position(pos1)

			line.end()
			line.setCastShadows(False)
			linenode = self.sceneManager.getRootSceneNode().createChildSceneNode()
			linenode.attachObject(line)
			linenode.showBoundingBox(True)


	def createUVIslands(self):
		smgcounter = 0
		if self.trucktree:
			for smg in self.trucktree['submeshgroups']:
				self.createUVIsland(smg, smgcounter)
				smgcounter += 1

	def createUVPlane(self):
		self.imgwidth = 600
		self.imgheight = 480
		matname = None
		if self.trucktree:
			log().info("truck editor len(trucktree) = " +str(len(self.trucktree) ))
			matname = self.trucktree['globals'][0]['data'][2]
			mat = ogre.MaterialManager.getSingleton().getByName(matname)
			if mat is not None:
				texturename = mat.getTechnique(0).getPass(0).getTextureUnitState(0).getTextureName()
				pair = mat.getTechnique(0).getPass(0).getTextureUnitState(0).getTextureDimensions()
				texture = Ogre.TextureManager.getSingleton().getByName(texturename)
				self.imgwidth = texture.getSrcWidth()
				self.imgheight = texture.getSrcHeight()
				log().debug("texture name %s, image Width %d, image Height %d " %( texturename, int(self.imgwidth), int(self.imgheight)))


		plane = ogre.Plane()
		plane.normal = ogre.Vector3(0, 1, 0)
		plane.d = 20
		# see http://www.ogre3d.org/docs/api/html/classOgre_1_1MeshManager.html#Ogre_1_1MeshManagera5
		uuid = randomID()
		mesh = ogre.MeshManager.getSingleton().createPlane(uuid + 'UVPlane', "General", plane, self.imgwidth/IMGSCALE, self.imgheight/IMGSCALE,
													1, 1, True, 1, 1, 1, ogre.Vector3(0, 0, 1),
													ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY,
													ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY,
													True, True)
		entity = self.sceneManager.createEntity(uuid+'uvent', uuid+'UVPlane')

		#it = ogre.ResourceGroupManager.getSingleton().getResourceManagerIterator()
		#rm = it.getNext()
		#print rm
		#texture = rm.getByName(texturename)
		#print "texture: ", texturename, texture.getWidth(), texture.getHeight()

		if matname:
			entity.setMaterialName(matname)
		self.uvplanenode = self.sceneManager.getRootSceneNode().createChildSceneNode()
		self.uvplanenode.attachObject(entity)

	def onMouseEvent(self,event):
		width = self.renderWindow.getWidth()
		height = self.renderWindow.getHeight()
		if event.GetWheelRotation() != 0:
			zfactor = 0.01
			if event.ShiftDown():
				zfactor = 0.1
			zoom = zfactor * -event.GetWheelRotation()
			newclip = self.camera.getNearClipDistance() + zoom
			if newclip > 5 and newclip < 98:
				#print newclip
				self.camera.setNearClipDistance(newclip)

		if event.RightDown():
			self.StartDragX, self.StartDragY = event.GetPosition()
		if event.Dragging() and event.RightIsDown():
			x,y = event.GetPosition()
			dx = self.StartDragX - x
			dy = self.StartDragY - y
			self.StartDragX, self.StartDragY = x, y
			if event.ShiftDown():
				dx = float(dx)
				dy = float(dy)
			else:
				dx = float(dx) / 2
				dy = float(dy) / 2
			newPos = self.camera.getPosition() + ogre.Vector3(-dx, 0, -dy)
			self.camera.setPosition(newPos)
			# todo : restrict movement
		event.Skip()

	def onKeyDown(self,event):
		d = 2
		if event.ShiftDown():
			d = 5
		if event.m_keyCode == 65: # A, wx.WXK_LEFT:
			self.camera.moveRelative(ogre.Vector3(d,0,0))
		elif event.m_keyCode == 68: # D, wx.WXK_RIGHT:
			self.camera.moveRelative(ogre.Vector3(-d,0,0))
		elif event.m_keyCode == 87: # W ,wx.WXK_UP:
			self.camera.moveRelative(ogre.Vector3(0,-d,0))
		elif event.m_keyCode == 83: # S, wx.WXK_DOWN:
			self.camera.moveRelative(ogre.Vector3(0,d,0))

		event.Skip()