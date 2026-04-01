import pygame
import math
from sys import exit
from helper import *

fps = 120
clock = pygame.time.Clock()

pygame.init()

#COLORS
BLACK = (0,0,0)
WHITE = (255,255,255)

#screen
screenSize = screenWidth, screenHeight = (1400,800)
screen = pygame.display.set_mode(screenSize)

# SETTINGS
Settings = {
	"Camera" :{
		"Zoom" : 100,
		"Max Zoom" : 800,
		"Min Zoom" : 10,
		"Zoom Diff": 12.5,
		"Center" : [0,0],
		"Size" : (screenWidth, screenHeight)
	},

	"Drawing" : {
		"Thickness" : 5,
		"Auto Smoothing" : False,
		"Smoothness" : 60,
		"Color" : (255,255,255),
		"Main Colors": [(244,67,54), (255, 152, 0), (76, 175, 80), (33, 150, 243), (135, 84, 167), (255,255,255), (0,0,0)]
	},

	"Board" : {
		"Color" : (17,17,17),
		"Dots" : True,
		"Dot Color" : (26,26,26),
		"Dot Distance" : 100,
		"Dot Radius" : 5,
	}
}

# Main variables
Objects = [{}]
OccupiedSpaces = {}


# FUNCTTIONS
def GetDotAt(mx,my):
	PlaceX = int(math.floor((mx - (screenWidth/2))/(max(0.1, Settings["Camera"]["Zoom"]/100)))) + Settings["Camera"]["Center"][0]
	PlaceY = int(math.floor((my - (screenHeight/2))/(max(0.1, Settings["Camera"]["Zoom"]/100)))) + Settings["Camera"]["Center"][1]
	return {
		"radius" : Settings["Drawing"]["Thickness"],
		"pos" : (PlaceX,PlaceY),
		"color" : Settings["Drawing"]["Color"]}

def DotOccupied(x,y):
	if y in OccupiedSpaces:
		if x in OccupiedSpaces[y]:
			return True
	return False

def SafelyRemoveLastObject():
	if(len(Objects) == 1): return

	Objects.pop()
	LastN = len(Objects)-1

	for y in Objects[LastN]:
		for x in Objects[LastN][y]:
			if y not in OccupiedSpaces: continue
			if x not in OccupiedSpaces[y]: continue

			del OccupiedSpaces[y][x]

		if y not in OccupiedSpaces: continue;

		if len(OccupiedSpaces[y]) == 0:
			del OccupiedSpaces[y]

	Objects.pop()
	Objects.append({})
#
running = True
Tick = 0
old_mouse_state = [[0,0],[False,False,False]]
AddingObject = False

RenderingPage = "Home"
hoveringOverGui = False
clickedGUI = False
while running:
	Tick+=1
	mx, my = pygame.mouse.get_pos()
	mouse_buttons = pygame.mouse.get_pressed()
	mouse_state = [[mx,my], mouse_buttons]

	GUI.allGUI = {}

	# GUIS
	Pos = GUI.UIVE(30,0,30,0)
	Size= GUI.UIVE(0, 0.02, 0, 1)
	Frame = GUI.Frame(Pos, Size, Settings["Drawing"]["Color"], name = "ColorFrame")
	GUI.UIConstraint("x", Frame)
	GUI.UICorner(0,1,Frame)
	GUI.UIBorder((100,100,100), 0, 0.2, Frame)


#	Pos = GUI.UIVE(0,1-0.03,0,0.05)
#	Size= GUI.UIVE(0, 0.03, 0, 1)
#	Frame = GUI.Frame(Pos, Size, (255,255,255), name = "SettingsFrame")
#	GUI.UIConstraint("x", Frame)
#	GUI.UICorner(0,0.2,Frame)
#	GUI.UIBorder((100,100,100), 0, 0.2, Frame)


	Pages = {"Home" : ["ColorFrame"]}

	#pre-calc
	if (not mouse_buttons[0]) and (not mouse_buttons[1]) and mouse_buttons[2] and (not hoveringOverGui):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_LCTRL]:
			if(old_mouse_state[1][2]):
				vector = (mouse_state[0][0] - old_mouse_state[0][0], mouse_state[0][1] - old_mouse_state[0][1])
				Settings["Camera"]["Center"][0] -= vector[0]*(int(math.ceil(100/Settings["Camera"]["Zoom"])))
				Settings["Camera"]["Center"][1] -= vector[1]*(int(math.ceil(100/Settings["Camera"]["Zoom"])))

	if mouse_buttons[0] and (not mouse_buttons[1]) and (not mouse_buttons[2]) and (not hoveringOverGui):
		if(old_mouse_state[1][0]):
			AddingObject = True
			smoothness = int(math.ceil(Settings["Drawing"]["Smoothness"]/(max(0.1, Settings["Camera"]["Zoom"]/100))))

			StructIndex = len(Objects)-1

			startpos = (old_mouse_state[0][0], old_mouse_state[0][1])
			vector = (mouse_state[0][0] - old_mouse_state[0][0], mouse_state[0][1] - old_mouse_state[0][1])
			devvector = (vector[0]/smoothness, vector[1]/smoothness)

			if Settings["Drawing"]["Auto Smoothing"]:
				distance = math.hypot(vector[0], vector[1])
				smoothness = max(8, min(100, int(distance *3)))

			visited = set()
			for step in range(smoothness):
				x = math.ceil(startpos[0] + (devvector[0]*step))
				y = math.ceil(startpos[1] + (devvector[1]*step))
				PlacingDot = GetDotAt(x,y)

				rx, ry = PlacingDot["pos"]

				if (rx, ry) in visited: continue
				visited.add((rx,ry))

				if DotOccupied(rx, ry):
					OccupiedObjN = OccupiedSpaces[ry][rx]

					if (OccupiedObjN in Objects and ry in Objects[OccupiedObjN] and rx in Objects[OccupiedObjN][ry]):
						del Objects[OccupiedObjN][ry][rx]

					if ry in Objects[OccupiedObjN] and len(Objects[OccupiedObjN][ry]) == 0:
						del Objects[OccupiedObjN][ry]

					del OccupiedSpaces[ry][rx]
					if len(OccupiedSpaces[ry]) == 0:
						del OccupiedSpaces[ry]

				if ry not in OccupiedSpaces: OccupiedSpaces[ry] = {}
				if rx not in OccupiedSpaces[ry]: OccupiedSpaces[ry][rx] = StructIndex

				if ry not in Objects[StructIndex]: Objects[StructIndex][ry] = {}
				Objects[StructIndex][ry][rx] = PlacingDot



	else:
		if AddingObject: Objects.append({})
		AddingObject = False

	#events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		if event.type == pygame.KEYDOWN:
			if (not AddingObject) and (not hoveringOverGui):
				if event.key == pygame.K_z:
					keys = pygame.key.get_pressed()
					if keys[pygame.K_LCTRL]:
						SafelyRemoveLastObject()
				if pygame.K_1 <= event.key <= pygame.K_7:
					index = event.key-pygame.K_1
					Settings["Drawing"]["Color"] = Settings["Drawing"]["Main Colors"][index]

		if event.type == pygame.MOUSEWHEEL:
			if (not AddingObject) and (not hoveringOverGui):
				keys = pygame.key.get_pressed()
				if keys[pygame.K_LCTRL]:
					if event.y > 0:
						Settings["Camera"]["Zoom"] = min(Settings["Camera"]["Max Zoom"], Settings["Camera"]["Zoom"]+Settings["Camera"]["Zoom Diff"])
					elif event.y < 0:
						Settings["Camera"]["Zoom"] = max(Settings["Camera"]["Min Zoom"], Settings["Camera"]["Zoom"]-Settings["Camera"]["Zoom Diff"])

	#display
	screen.fill(BLACK)

	draw_board(screen, Settings["Camera"], Settings["Board"])

	for obj in Objects:
		for y in obj:
			for x in obj[y]:
				dotinfo = obj[y][x]

				radius = dotinfo["radius"]
				pos = dotinfo["pos"]
				color = dotinfo["color"]
				Dot(radius, pos, color).render(screen, Settings["Camera"])


	GUI.renderGUIS(screen, Pages[RenderingPage])

	hoveringOverGui = GUI.hoveringGUI(Pages[RenderingPage])
	clickedGUI = GUI.clickedGUI(Pages[RenderingPage])

	pygame.display.flip()
	clock.tick(fps)
	#
	old_mouse_state = [mouse_state[0][:], mouse_state[1]]

pygame.quit()
exit()
