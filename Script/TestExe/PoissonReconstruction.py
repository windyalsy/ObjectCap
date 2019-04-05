# CapNrmCombine: combine all views' textures together.
# V0: Origin
import os
import subprocess
import shutil
import logging
import trimesh
import trimesh.io.export as ex

def obj2ply(objFile, plyFile):
    mesh = trimesh.load(objFile)
    ex.export_mesh(mesh,plyFile,encoding='ascii',vertex_normal=True)
    return

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    BUILD_ROOT = r"D:\v-jiazha\2-workspaces\Source\ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    TOOL_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool"
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')
    CONFIG_ROOT = os.path.join(COMMON_ROOT,r"Config0301")

    # OBJECT = r"RealObject-pig2"
    OBJECT = r"RealObject-penrack3"
    OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object', OBJECT)
    OBJECT_ViewDir = os.path.join(OBJECT_ROOT, "Views", "View_%04d")

    panelConfig = os.path.join(CONFIG_ROOT, "Setup", "panelConfig.txt")
    cameraConfig = os.path.join(CONFIG_ROOT, "Setup", "cameraConfig.txt")
    poseConfig = os.path.join(CONFIG_ROOT, "Setup", "poseConfig.txt")

    # MODEL_NAME = r"Pig/Pig_160608.obj"
    # MODEL_NAME = r"Kitty_160420.obj"
    MODEL_NAME = r"sphere_20k.obj"
    positionStr = r"0.1988,-0.09269,0"
    # positionStr = r"0.199,-0.126,0"
    generics = "10"
    genericStart = "0.01"
    genericEnd = "0.40"
    # genericRoughnesses = "0.13,0.16,0.20,0.25,0.30,0.4,0.5,0.6,0.7"
    resolution = "256"
    faceID = "5"
    nViews = "36"
    texWidth = "1024"
    texHeight = "1024"

    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT

        # refine geometry based on vertex's apparent normal
        logger.info("Mesh_opt: refine geometry ")

        reModel = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "Recover.obj")
        reModelUpt = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverUpdate.obj")
        reModelUptPly = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverUpdate.ply")
        reModelPoisson = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverPoisson.ply")

        # Test remove degenerated faces
        # objFile = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverTest.obj")
        # objRepairedFile = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverRepaired.obj")
        # mesh = trimesh.load(objFile)
        # mesh.remove_degenerate_faces()
        # ex.export_mesh(mesh, objRepairedFile)

        # obj2ply(reModelUpt,reModelUptPly)

        # poisson reconstruct combined mesh
        re = subprocess.run(
            ["PoissonRecon.exe", "--in", reModelUptPly, "--out", reModelPoisson, "--normals", "--pointWeight", "3",
             "--depth",
             "12", "--density", "--threads", "2"], stdout=True, stderr=True, check=True)
        # # trim combined mesh
        # re = subprocess.run(
        #     ["SurfaceTrimmer.exe", "--in", meshComReconF, "--out", meshComReconTrimF, "--trim", "7"],
        #     stdout=True, stderr=True, check=True)
        #
        # re = subprocess.run(
        #     ["mesh_opt",
        #      reModelUptPly,reModelFinal], stdout=True, stderr=True, check=True)
        print(re.args)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
