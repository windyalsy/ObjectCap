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
    OBJECT_Model_Dir_MERGE = os.path.join(OBJECT_ROOT_MERGE, "Recover", "Model","Final")

    OBJECT1 = r"RealObject-cookies"
    OBJECT_ROOT1 = os.path.join(DATA_ROOT, r'Object',OBJECT1)
    OBJECT_ViewDir1 = os.path.join(OBJECT_ROOT1, "Views", "View_%04d")
    OBJECT_Model_Dir1 = os.path.join(OBJECT_ROOT1, "Recover", "Model","FinalOpt")

    OBJECT2 = r"RealObject-cookies2"
    OBJECT_ROOT2 = os.path.join(DATA_ROOT, r'Object',OBJECT2)
    OBJECT_ViewDir2 = os.path.join(OBJECT_ROOT2, "Views", "View_%04d")
    OBJECT_Model_Dir2 = os.path.join(OBJECT_ROOT2, "Recover", "Model","FinalOpt")

    # Setup setting: camera,
    cameraConfig1 = os.path.join(CONFIG_ROOT, "Setup" + OBJECT1, "cameraConfig.txt")
    cameraConfig2 = os.path.join(CONFIG_ROOT, "Setup" + OBJECT2, "cameraConfig.txt")

    # Camera extrinsic, scale setting
    viewScale = "0.009"
    cameraExtrinDirectory1 = os.path.join(OBJECT_ROOT1, "CalibPrism", "Extrinsic")
    cameraExtrinDirectory2 = os.path.join(OBJECT_ROOT2, "CalibPrism", "Extrinsic")

    # keyPointsUVFile1 = os.path.join(OBJECT_Model_Dir_MERGE,"keyPointsUV1.txt")
    # keyPointsUVFile2 = os.path.join(OBJECT_Model_Dir_MERGE,"keyPointsUV2.txt")
    keyPointsUVFile1 = os.path.join(OBJECT_Model_Dir1,"keyPointsUV.txt")
    keyPointsUVFile2 = os.path.join(OBJECT_Model_Dir2,"keyPointsUV.txt")
    keyPointsPosFile1 = os.path.join(OBJECT_Model_Dir_MERGE,"keyPointsPos1.txt")
    keyPointsPosFile2 = os.path.join(OBJECT_Model_Dir_MERGE,"keyPointsPos2.txt")

    # tranform second point cloud into the first one
    transExtrinFile = os.path.join(OBJECT_Model_Dir_MERGE,"transExtrin.txt")

    src1Model = os.path.join(OBJECT_Model_Dir1,"RecoverUpdate.obj")
    src2Model = os.path.join(OBJECT_Model_Dir2,"RecoverUpdate.obj")
    alignModel = os.path.join(OBJECT_Model_Dir_MERGE,"AlignPoindCloud.obj")
    alignModelPly = os.path.join(OBJECT_Model_Dir_MERGE,"AlignPoindCloud.ply")
    alignModelPoi = os.path.join(OBJECT_Model_Dir_MERGE,"Align_Poi.ply")
    alignModelTrim = os.path.join(OBJECT_Model_Dir_MERGE,"Align_Trim.ply")
    alignModelRec = os.path.join(OBJECT_Model_Dir_MERGE,"Recover.obj")

    # Option setting
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

        if CapCreateKeyPointsOpt:
            texPosImgFile1 = os.path.join(OBJECT_Model_Dir1,"TexPos.pfm")
            re = subprocess.run(
                ["CapCreateKeyPointsList", "-keyPointsUVFile=" + keyPointsUVFile1,
                 "-keyPointsPosFile=" + keyPointsPosFile1,
                 "-flipZ", "-texPosImgFile=" + texPosImgFile1],
                stdout=True, stderr=True, check=True)

            texPosImgFile2 = os.path.join(OBJECT_Model_Dir2,"TexPos.pfm")
            re = subprocess.run(
                ["CapCreateKeyPointsList", "-keyPointsUVFile=" + keyPointsUVFile2,
                 "-keyPointsPosFile=" + keyPointsPosFile2,
                 "-flipZ", "-texPosImgFile=" + texPosImgFile2],
                stdout=True, stderr=True, check=True)

        if CapAlignPointCloudOpt:

            re = subprocess.run(
                ["CapAlignPointCloud", "-src1ModelFile=" + src1Model, "-src2ModelFile=" + src2Model,
                 "-keyPointsFile1=" + keyPointsPosFile1,
                 "-keyPointsFile2=" + keyPointsPosFile2, "-tarModelFile=" + alignModel, "-transExtrin=" + transExtrinFile,
                 "-viewScale=" + viewScale, "-flipZ", "-nViews=" + nViews],
                stdout=True, stderr=True, check=True)

            obj2ply(alignModel, alignModelPly)

            re = subprocess.run(
                ["PoissonRecon.exe", "--in", alignModelPly, "--out", alignModelPoi, "--normals", "--pointWeight",
                 "0",
                 "--depth",
                 "10", "--density", "--threads", "1"], stdout=True, stderr=True,
                check=True)
            # trim combined mesh
            re = subprocess.run(
                ["SurfaceTrimmer.exe", "--in", alignModelPoi, "--out", alignModelTrim, "--trim", "2"],
                stdout=True, stderr=True, check=True)
            ply2obj(alignModelTrim,alignModelRec)

    finally:
        os.environ.clear()
        os.environ.update(_environ)


