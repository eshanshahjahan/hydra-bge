import bge
import GameLogic
import mathutils
import PySixense

print('starting up')

# Set globals for camera, gun, and initial positions and rotations
camera = GameLogic.getCurrentScene().cameras['Camera']
initial_camera_rot = camera.orientation.copy()
initial_camera_pos = camera.position.copy()

gun = GameLogic.getCurrentScene().objects['Gun']
initial_gun_rot = gun.orientation.copy()
initial_gun_pos = gun.position.copy()

if PySixense.Init() != PySixense.Constants.Success:
    print("Error initializing Sixense SDK")

offset = mathutils.Vector([0,0,0])

def recenter():
    global offset
    left = PySixense.GetNewestData(0)[1]
    offset = mathutils.Vector([left.pos[0]/100, left.pos[2]/-100, left.pos[1]/100])

recenter()
    
# Create an object whose destructor will exit PySixense
class Shutdown:
    def __del__(self):
        print('shutting down')
        assert(PySixense.Exit() == PySixense.Constants.Success)

GameLogic.shutdown = Shutdown()

def main(cont):
    left = PySixense.GetNewestData(0)[1]
    
    mat = mathutils.Matrix(left.rot_mat)
    mat.transpose()
    camera.orientation = initial_camera_rot * mat
    camera.position = initial_camera_pos + (mathutils.Vector([left.pos[0]/100, left.pos[2]/-100, left.pos[1]/100]) - offset)
 
    right = PySixense.GetNewestData(1)[1]
    arr = right.rot_mat
    mat = mathutils.Matrix([[arr[0][0], -1 * arr[2][0], arr[1][0]], [-1 * arr[0][2], arr[2][2], -1 * arr[1][2]], [arr[0][1], -1 * arr[2][1], arr[1][1]]])
    gun.orientation = initial_gun_rot * mat
    gun.position = initial_gun_pos + (mathutils.Vector([right.pos[0]/100, right.pos[2]/-100, right.pos[1]/100]) - offset)

    target = gun.sensors['Ray'].hitObject
    laser = GameLogic.getCurrentScene().objects['Laser']
    if target is not None and target != laser:
        laser = GameLogic.getCurrentScene().objects['Laser']
        laser.position = gun.sensors['Ray'].hitPosition
        if right.trigger > 0.5:
            target.color = [0.25,0.,0.,1.]