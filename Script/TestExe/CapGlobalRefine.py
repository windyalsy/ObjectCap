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
    DATA_ROOT_E = r"E:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
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

    # nCount = "2"
    # # OBJECTS = ["RealObject-cookies","RealObject-cookies2"]
    # OBJECTS = ["RealObject-oatmeal", "RealObject-oatmeal2"]
    nCount = "1"
    # OBJECTS = ["RealObject-cookies","RealObject-cookies2"]
    # OBJECTS = ["RealObject-cookies2"]
    # OBJECTS = ["RealObject-cookies"]
    # OBJECTS = ["RealObject-penrack3"]
    # OBJECTS = ["RealObject-gift2"]
    OBJECTS = ["RealObject-gift1"]
    OBJECT_LIST = ','.join(OBJECTS)

    # OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object',"%s")
    OBJECT_ROOT = os.path.join(DATA_ROOT_E, r'Object',"%s")
    # OBJECT_ViewDir = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
    OBJECT_Model_Dir = os.path.join(OBJECT_ROOT, "Recover", "Model","FinalOpt")
    OBJECT_CalibPrism_Dir = os.path.join(OBJECT_ROOT,"CalibPrism")
    OBJECT_ColmapSfM_Dir = os.path.join(OBJECT_ROOT,"ColmapSfM")

    # OBJECT_MERGE = r"RealObject-cookies2"
    # OBJECT_MERGE = r"RealObject-oatmealMerge"
    # OBJECT_MERGE = r"RealObject-giftMerge"
    OBJECT_MERGE = OBJECTS[0]
    OBJECT_ROOT_MERGE = os.path.join(DATA_ROOT_E, r'Object', OBJECT_MERGE)
    # OBJECT_ROOT_MERGE = os.path.join(DATA_ROOT, r'Object', OBJECT_MERGE)
    OBJECT_ROOT_MERGE_SFM = os.path.join(OBJECT_ROOT_MERGE, r'SfMFromPrismMultiSeq')
    OBJECT_ROOT_MERGE_SFM_CONFIG = os.path.join(OBJECT_ROOT_MERGE_SFM, 'SfMConfig')
    OBJECT_Model_Dir_MERGE = os.path.join(OBJECT_ROOT_MERGE, "Recover", "Model", "Final")

    # Setup setting: camera,
    cameraConfig = os.path.join(CONFIG_ROOT, "Setup%s", "cameraConfig.txt")
    panelConfig = os.path.join(CONFIG_ROOT, "Setup" + OBJECTS[0], "panelConfig.txt") #panelConfig common

    # Camera extrinsic, scale setting
    viewScale = "0.009"
    cameraExtrinDirectory = os.path.join(OBJECT_ROOT, "CalibPrism", "Extrinsic")
    cameraExtrin =  os.path.join(OBJECT_ROOT, "CalibPrism", "Extrinsic","view_%04d.txt")

    # Frames directory setting:
    viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
    framesDirectory = os.path.join(viewDirectory, "Frames")
    nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
    viewFramesCapDir = framesDirectory
    viewFramesProjDir = os.path.join(nrmRefineDirectory,"FramesFinal")

    # Importance sampling setting
    numUniform = "10"
    numImportance = "10"
    # numUniform = "5"
    # numImportance = "5"
    nCombViews = "5"

    # Refine normal setting
    thetaStep = "1"
    phiSize = "4"
    nIter = "2"
    thetaSize = "8"

    # UV setting
    texWidth = "1024"
    texHeight = "1024"
    # texWidth = "512"
    # texHeight = "512"
    divSize = "256"

    # Record iteration option
    recordIterOption = "1"

    meshFinalOptDir = os.path.join(OBJECT_ROOT_MERGE, r"Recover\Model\FinalOpt")
    if not os.path.exists(meshFinalOptDir):
        os.makedirs(meshFinalOptDir)
    # when mesh_opt finished, combine all textures together using new uv
    reModelUpt = os.path.join(OBJECT_ROOT_MERGE, r"Recover\Model\FinalOpt", "RecoverUpdate.obj")
    texNrmImgFile = os.path.join(meshFinalOptDir, "TexNrm.pfm")

    meshGlobalRefineDir = os.path.join(meshFinalOptDir, r"GlobalRefine")
    if not os.path.exists(meshGlobalRefineDir):
        os.makedirs(meshGlobalRefineDir)

    # Option setting
    CapGlobalRefineOpt = 1

    logger.info("Start globally solve BRDF weights:")
    if not os.path.exists( OBJECT_ROOT_MERGE_SFM_CONFIG):
        os.makedirs( OBJECT_ROOT_MERGE_SFM_CONFIG)
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT + ";" + TOOL_LCT_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT + ";" + TOOL_LCT_ROOT

        if CapGlobalRefineOpt:
            # modelFile = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-gift2\Recover\Model\FinalOpt\RecoverUpdate.obj"
            # modelFile = r"E:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-penrack3\Recover\Model\FinalOpt\RecoverUpdate.obj"
            # modelFile = r"E:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-penrack3\Recover\Model\FinalOpt\RecoverR.obj"
            modelFile = reModelUpt
            # output refinement weight files

            re = subprocess.run(
                ["CapGlobalRefine", "-modelFile=" + modelFile,
                 "-objectListString=" + OBJECT_LIST,
                 "-cameraConfig=" + cameraConfig,
                 "-panelConfig=" + panelConfig,
                 "-cameraExtrin=" + cameraExtrin,
                 "-viewFramesCapDir=" + viewFramesCapDir,
                 "-viewFramesProjDir=" + viewFramesProjDir,
                 "-texNrmImgFile=" + texNrmImgFile,
                 "-uvWidth=" + texWidth,"-uvHeight=" + texHeight,"-divSize=" + divSize,
                 "-numUniform=" + numUniform, "-numImportance=" + numImportance,
                 "-nCombViews=" + nCombViews,
                 "-thetaStep=" + thetaStep, "-phiSize=" + phiSize, "-nIter=" + nIter,
                 "-thetaSize=" + thetaSize,
                 "-nCount=" + nCount, "-nViews=" + nViews,"-viewScale=" + viewScale,
                 "-flipZ",
                 "-generics=" + generics, "-genericStart=" + genericStart,"-genericEnd=" + genericEnd,
                 "-genericRoughnesses=" + genericRoughnesses,
                 "-rowScanWidth=" + rowScanWidth, "-rowScanHeight=" + rowScanHeight, "-colScanWidth=" + colScanWidth, "-colScanHeight=" + colScanHeight,
                 "-workingSpaceDir=" + meshGlobalRefineDir,"-recordIter="+recordIterOption
                 ],
                stdout=True, stderr=True, check=True)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
