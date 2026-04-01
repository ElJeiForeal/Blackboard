import pygame
import math

def draw_dot(screen, radius, actualPos, color, CameraConf):
	#
	zoom = CameraConf["Zoom"]
	camWidth, camHeight = CameraConf["Size"]
	cameraCenter = CameraConf["Center"]

	#main
	multiplier = max(0.1, zoom/100)


	zeroedAPos = (actualPos[0]-cameraCenter[0], actualPos[1] - cameraCenter[1])
	displayPos = (math.floor(zeroedAPos[0]*multiplier) + camWidth/2, math.floor(zeroedAPos[1]*multiplier) + camHeight/2)

	displayRadius = math.ceil(radius*multiplier)

	pygame.draw.circle(screen, color, displayPos, displayRadius)

def draw_board(screen, CameraConf, BoardConf):
	camWidth, camHeight = CameraConf["Size"]
	center = CameraConf["Center"]
	zoom = CameraConf["Zoom"]

	dot_spacing = BoardConf["Dot Distance"]
	dot_radius = BoardConf["Dot Radius"]
	background_color = BoardConf["Color"]
	dot_color = BoardConf["Dot Color"]

	#main

	multiplier = max(0.1, zoom/100)

	#fill the screen
	screen.fill(background_color)

	if not  BoardConf["Dots"]: return
	#drawing dots
	lefttopX = center[0] - (camWidth/(2*multiplier))
	lefttopY = center[1] - (camHeight/(2*multiplier))

	dotRows = int((camHeight/multiplier)//dot_spacing) + 3
	dotCols = int((camWidth/multiplier)//dot_spacing) + 3

	startCol = lefttopX//dot_spacing
	startRow = lefttopY//dot_spacing

	sy = startRow*dot_spacing
	sx = startCol*dot_spacing

	for yi in range(dotRows):
		dy = yi*dot_spacing
		y = sy+dy
		for xi in range(dotCols):
			dx = xi*dot_spacing
			x = sx+dx

			draw_dot(screen, dot_radius, (x,y), dot_color, CameraConf)


class Dot:
	def __init__(self, radius, position, color):
		self.position = position
		self.radius = radius
		self.color = color

	def render(self, screen, CameraConf):
		draw_dot(screen, self.radius, self.position, self.color, CameraConf)



class GUI:
	effectOrder = {
		"UIConstraint" : 0,
		"UICorner" : 1,
		"UIBorder": 2
	}

	allGUI = {}

	@staticmethod
	def renderGUIS(screen, names):
		for name in names:
			GUI.allGUI[name].render(screen)

	@staticmethod
	def hoveringGUI(names):
		pos = pygame.mouse.get_pos()
		for name in names:
			rect = GUI.allGUI[name].BaseRect
			if rect == None: continue

			if(rect.collidepoint(pos)): return GUI.allGUI[name]

		return False

	@staticmethod
	def clickedGUI(names, mousebutton = 0):
		pos = pygame.mouse.get_pos()
		if not pygame.mouse.get_pressed()[mousebutton]: return False;

		hoveringGui = GUI.hoveringGUI(names)
		if not hoveringGui: return False;

		return hoveringGui

	class UIVE():
		def __init__(self, xOffset, xScale, yOffset, yScale):
			self.X = (xOffset, xScale)
			self.Y = (yOffset, yScale)
	# effects

	class UIConstraint():
		def __init__(self, type, parent, name = "UIConstraint"):
			self.name = name
			self.ID = "UIConstraint"
			self.Class = "effect"

			self.type = type

			self.parent = parent
			parent.children.append(self)

	class UICorner():
		def __init__(self, radiusOffset, radiusScale, parent, name = "UICorner"):
			self.name = name
			self.ID = "UICorner"
			self.Class = "effect"

			self.radius = (radiusOffset, radiusScale)

			self.parent = parent
			parent.children.append(self)

	class UIBorder():
		def __init__(self, color, thicknessOffset, thicknessScale, parent, name = "UIBorder"):
			self.name = name
			self.ID = "UIBorder"
			self.Class = "effect"

			self.thickness = (thicknessOffset, thicknessScale)
			self.color = color

			self.parent = parent
			parent.children.append(self)

	# GUI

	class Frame:
		def __init__(self, position, size, color, name):
			self.name = name
			self.Class = "UI"
			self.ID = "Frame"

			self.position = position
			self.size = size
			self.color = color

			GUI.allGUI[name] = self

			self.children = []

		def render(self, screen):
			width, height = screen.get_size()

			original_x = int(math.ceil((width*self.position.X[1]) + (self.position.X[0])))
			original_y = int(math.ceil((height*self.position.Y[1]) + (self.position.Y[0])))

			original_sizex = int(math.ceil((width*self.size.X[1]) + (self.size.X[0])))
			original_sizey = int(math.ceil((height*self.size.Y[1]) + (self.size.Y[0])))

			#sorting effects
			x = original_x
			y = original_y
			sizex = original_sizex
			sizey = original_sizey

			appliedEffects = []
			applyEffects = {}

			for child in self.children:
				if child.Class != "effect": continue
				if child.ID in appliedEffects: continue

				appliedEffects.append(child.ID)

				applyEffects[GUI.effectOrder[child.ID]] = child


			#Needed variables
			cornerRadius = 0
			beforeRects = []

			#applying effects
			for i in sorted(applyEffects):
				effect = applyEffects[i]

				if effect.ID == "UIConstraint":
					if effect.type == "x":
						sizey = sizex
					else:
						sizex = sizey

				if effect.ID == "UICorner":
					cornerRadius = int(math.ceil(((sizex*effect.radius[1]) + effect.radius[0])))

				if effect.ID == "UIBorder":
					thick = int(math.ceil( (sizex*effect.thickness[1]) + effect.thickness[0] ))
					rect = pygame.Rect(0,0,sizex+thick,sizey+thick)
					rect.center = (x,y)
					beforeRects.append({"rect": rect, "color" : effect.color})
			#
			self.BaseRect = pygame.Rect(x,y,sizex,sizey)
			self.BaseRect.center = (x,y)

			for rectinfo in beforeRects:
				pygame.draw.rect(screen, rectinfo["color"], rectinfo["rect"], border_radius = cornerRadius)
			pygame.draw.rect(screen, self.color, self.BaseRect, border_radius = cornerRadius)
