import utils
import copy
import math

# path for the base nuke effect
base_path = "/pa/units/land/nuke_launcher/nuke_launcher_ammo_explosion.pfx"

out_path = "pa/units/land/nuke_launcher/nuke_launcher_ammo_explosion.pfx"
# out_path = "pa/effects/specs/ping.pfx"

# this is the base nuke effect, it comes from the game
base_nuke = utils.load_base_json(base_path)
# base_nuke = {"emitters": []}


############################################### configuration
scale = 2.0
# dots per scale unit
dps = 19.0


############################################### set scale of the flag
# http://en.wikipedia.org/wiki/Flag_of_the_United_States#Design


flag = {}

flag['height'] = float(scale)
flag['width'] = flag['height'] * 1.9

flag['canton_height'] = flag['height'] * 7.0 / 13.0
flag['canton_width'] = flag['width'] * 2.0 / 5.0

flag['star_vsep'] = flag['canton_height'] / 10.0
flag['star_hsep'] = flag['canton_width'] / 12.0

flag['stripe_width'] = flag['height'] / 13.0
flag['star_size'] = flag['stripe_width'] * 4.0 / 5.0

flag['white'] = [1.000, 1.000, 1.000]
flag['red']   = [0.698, 0.132, 0.203]
flag['blue']  = [0.234, 0.233, 0.430]

###############################################




# create beam particle to be our 'field' of data points
base_beam = {
    "spec": {
        "shader": "particle_transparent",
        "shape": "beam",
        "sizeX": 1.0 / dps / 2 / 3,
        "alpha": 0,
        "baseTexture": "/pa/effects/textures/particles/flat.papa"
    },
    "lifetime": 10,
    "emitterLifetime": 10,
    "maxParticles": 0,
    # "sizeX": [[0, 1],[1, 0]],
    "emissionBursts": 1,
    "bLoop": False,
    "endDistance": -1,
    "delay": 2
}

base_particle = {
	"spec": {
        "shader": "particle_add",
        "facing": "emitterZ",
        "sizeX": 1.0,
        "alpha": [[0, 4], [0.9, 1], [1, 0]],
        "dataChannelFormat": "PositionAndColor",
        "baseTexture": "/pa/effects/textures/particles/flat.papa"
    },
    "rotationRange" : 3.14,
    "lifetime": 6,
    "lifetimeRange": 0.8,
    "type": "EMITTER",
    "useRadialVelocityDir" : True,
    "velocity": 120,
    "gravity": 0,
    "drag": 0.989,
    "offsetRangeX": 0.01,
    "offsetRangeY": 0.01,
    "offsetRangeZ": 0.01,
    "emissionBursts": 1,
    "maxParticles": 1,
    "emitterLifetime": 10,
    "endDistance": -1,
    # "useWorldSpace": True,
    "bLoop": False,
    "delay": 2
}

def get_color(x, y, flag):
	# first invert the x coord
	x = flag['width'] - x

	# bounds check
	if (x < 0 or x > flag['width']): return
	if (y < 0 or y > flag['height']): return

	# color to return

	# assume red, then specialise based on test
	color = flag['red']

	# check if we are on an odd stripe -> make point white instead
	if (int(y / flag['stripe_width'] - 0.001) % 2): color = flag['white']

	# check for the canton -> inside canton so must be blue
	if (x < flag['canton_width'] and y < flag['canton_height']): color = flag['blue']

	# finally, check if we are inside a star
	G = flag['star_hsep']
	E = flag['star_vsep']

	# if we are too far
	# if (x >= G / 2 and x <= flag['canton_width'] - G / 2):

	i = int(round((x) / G))
	j = int(round((y) / E))

	if (i % 2 == j % 2):
		if (i >= 1 and i <= 11):
			if (j >= 1 and j <= 9):
				dx = x - float(G) * i
				dy = y - float(E) * j

				if (math.sqrt(dx * dx + dy * dy) <= flag['star_size'] / 2):
					color = flag['white']



	return color


#################################################### create beam effects
def create_flag():
	# make red part
	# dots per scale unit
	w = int(flag['width'] * dps)
	# dots per scale unit
	h = int(flag['height'] * dps)

	base_beam['offsetX'] = []
	base_beam['offsetY'] = []
	base_beam['offsetZ'] = 4.0

	base_white = copy.deepcopy(base_beam)
	base_red = copy.deepcopy(base_beam)
	base_blue = copy.deepcopy(base_beam)

	base_white['red'], base_white['green'], base_white['blue'] = flag['white']
	base_red['red'], base_red['green'], base_red['blue'] = flag['red']
	base_blue['red'], base_blue['green'], base_blue['blue'] = flag['blue']

	points = w * h

	for j in xrange(h+1):
		for i in xrange(w+1):
			# dots per scale unit
			x = i / dps
			y = j / dps

			color = get_color(x, y, flag)

			# get the color
			if (color == flag['red']):
				base = base_red
			elif (color == flag['blue']):
				base = base_blue
			elif(color == flag['white']):
				base = base_white

			# append to that color beam
			base['offsetX'].append([0, x - flag['width'] / 2])
			base['offsetY'].append([0, y - flag['height'] / 2])
			base['maxParticles'] = base['maxParticles'] + 1 

	totalParticles = 0
	for base in [base_white, base_red, base_blue]:
		totalParticles += base['maxParticles']
		print 'maxParticles :', base['maxParticles']
		for i in xrange(base['maxParticles']):
			t = float(i) / (base['maxParticles'] - 1)
			base['offsetX'][i][0] = t
			base['offsetY'][i][0] = t

		# add the beams to the effect
		beam_index = len(base_nuke['emitters'])
		base_nuke['emitters'].append(base)

		################################################# add slave particles ('MERICA)
		particle = copy.deepcopy(base_particle)
		
		# inherit color from beam particle
		particle['red'] = base['red']
		particle['green'] = base['green']
		particle['blue'] = base['blue']

		particle['linkIndex'] = beam_index
		particle['maxParticles'] = base['maxParticles']

		base_nuke['emitters'].append(particle)

	print 'totalParticles :', totalParticles
	



create_flag()

utils.save_local_json(base_nuke, out_path)
