#parallel preprocess scan data
#automatically download image data and preprocess them

import os
import subprocess
import logging
import shutil
import time

import numpy as np
import logging
import trimesh
from datetime import datetime

def obj2ply(objFile, plyFile):
    mesh = trimesh.load(objFile,process=None)
    mesh.export(plyFile,"ply",encoding='ascii',vertex_normal=True)
    # mesh = pymesh.load_mesh(objFile)
    # pymesh.save_mesh(plyFile, mesh, ascii=True)
    return

def ply2obj(plyFile, objFile):
    mesh = trimesh.load(plyFile,process=None,vertex_normal=True)
    print(len(mesh.vertex_normals))
    mesh.export(objFile)
    return

def rmBadFace(objFile,objRFile):
    mesh = trimesh.load(objFile)
    mesh.remove_degenerate_faces()
    mesh.export(objRFile)

def _logpath(path, names):
    print('Working in %s' % path)
    return []   # nothing will be ignored

if __name__ == "__main__":

    ImageMagicPath = r"C:/Program Files/ImageMagick-7.0.8-Q16-HDRI"
    BUILD_ROOT = r"D:\v-jiazha\2-workspaces\Source\ObjectCap\x64\Release"
    TOOL_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    # DATA_ROOT_E = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    TOOL_LCT_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool\LCT"
    COMMON_ROOT = os.path.join(DATA_ROOT, r'RealCommon')
    CONFIG_ROOT = os.path.join(COMMON_ROOT,r"Config0301")


    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    v_size = 184
    u_size = 224
    nTotal = 409

    # Option Setting
    # positionStr = r"0.1982,-0.0921,0"
    positionStr = r"0.1988,-0.09269,0"
    nViewsCount = 36
    nViews = "36"
    # Bases Setting
    generics = "20"
    genericStart = "0.01"
    genericEnd = "0.60"
    genericRoughnesses = "0.01,0.02,0.04,0.07,0.09,0.11,0.13,0.16,0.20,0.25,0.40"
    # genericRoughnesses = "0.01,0.02,0.03,0.05,0.07,0.09,0.11,0.13,0.16,0.20,0.25"

    # Downsampled lights
    rowScanWidth = "7"
    rowScanHeight = "1"
    colScanWidth = "1"
    colScanHeight = "23"

    OBJECT_MERGE = r"RealObject-cookiesMerge"
    OBJECT_ROOT_MERGE = os.path.join(DATA_ROOT, r'Object',OBJECT_MERGE)
    OBJECT_ROOT_MERGE_SFM = os.path.join(OBJECT_ROOT_MERGE, r'SfM')
    OBJECT_ROOT_MERGE_SFM_CONFIG = os.path.join(OBJECT_ROOT_MERGE_SFM,'SfMConfig')
    OBJECT_Model_Dir_MERGE = os.path.join(OBJECT_ROOT_MERGE, "Recover", "Model","Final")

    # nCount = "2"
    # OBJECT_LIST = "RealObject-cookies,RealObject-cookies2"

    nCount = "1"
    nObjCount = 1
    OBJECTS = ["RealObject-cookies"]
    OBJECT_LIST = ','.join(OBJECTS)
    print(OBJECT_LIST)

    OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object',"%s")
    OBJECT_ViewDir = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
    OBJECT_Model_Dir = os.path.join(OBJECT_ROOT, "Recover", "Model","FinalOpt")

    panelConfig = os.path.join(CONFIG_ROOT, "Setup" + "%s", "panelConfig.txt")
    cameraConfig = os.path.join(CONFIG_ROOT, "Setup" + "%s", "cameraConfig.txt")
    poseConfig = os.path.join(CONFIG_ROOT, "Setup" + "%s", "poseConfig.txt")

    # panelConfig = os.path.join(CONFIG_ROOT, "SetupOrigin", "panelConfig.txt")
    # cameraConfig = os.path.join(CONFIG_ROOT, "SetupDownsample30", "cameraConfig.txt")
    # poseConfig = os.path.join(CONFIG_ROOT, "SetupOrigin", "poseConfig.txt")

    # Camera extrinsic, scale setting
    # viewScale = "0.009"
    viewScale= "1"
    cameraExtrinDirectory = os.path.join(OBJECT_ROOT, "ColmapSfM", "Extrinsic")


    alignModel = os.path.join(OBJECT_Model_Dir_MERGE,"AlignPoindCloud.obj")
    modelOrigin = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-cookiesMerge\SfM\denseRecon\fused.obj"
    modelFlip = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-cookiesMerge\SfM\denseRecon\fusedFlip.obj"

    # Option setting
    CapLoadSfMCameraOpt = 1
    CapCreateKeyPointsOpt = 1
    CapAlignPointCloudOpt = 1
    CapRefinePointCloudOpt = 1
    CleanPointCloudOption = 1
    logger.info("Start merging objects:")
    if not os.path.exists( OBJECT_Model_Dir_MERGE):
        os.makedirs( OBJECT_Model_Dir_MERGE)
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT + ";" + TOOL_LCT_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT + ";" + TOOL_LCT_ROOT

        re = subprocess.run(
            ["ModelConvert.exe", "-srcModelFile=" + modelOrigin, "-tarModelFile=" + modelFlip, "-flipZ", "-flipY"],
            stdout=True, stderr=True, check=True)

        CapMultiSimOption = 1
        if CapMultiSimOption:
            for i in range(nObjCount):
                logger.info("CapMultiSim  object : {} ".format(i))
                cameraConfigObj = cameraConfig % OBJECTS[i]
                # cameraConfigObj = cameraConfig
                cameraExtrinsic = os.path.join(cameraExtrinDirectory % OBJECTS[i], "view_%04d.txt")
                viewDirectory = os.path.join(OBJECT_ROOT % OBJECTS[i], "Views", "View_%04d")
                nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                viewExpFramesDir = os.path.join(nrmRefineDirectory, "Experiment/Frames")
                renderOption = "2"
                re = subprocess.run(
                    ["CapMultiSim", "-framesDirectory=" + viewExpFramesDir,
                     "-modelFile=" + modelFlip,
                     "-cameraConfig=" + cameraConfigObj, "-cameraExtrin=" + cameraExtrinsic,
                     "-viewScale=" + viewScale, "-flipZ","--flipY",
                     "-renderOption=" + renderOption, "-nViews=" + nViews],
                    stdout=True, stderr=True, check=True)

    finally:
        os.environ.clear()
        os.environ.update(_environ)


