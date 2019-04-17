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
    mesh = trimesh.load(objFile,process=None,vertex_normal=True)
    mesh.remove_degenerate_faces()
    print(len(mesh.vertex_normals))
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

    # OBJECT = r"RealObject-pig2"
    # OBJECT = r"RealObject-penrack3"
    # OBJECT = r"RealObject-pig2"
    # OBJECT = r"RealObject-oatmeal"
    OBJECT = r"RealObject-cookies"
    # OBJECT = r"RealObject-cookies2"
    # OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object', OBJECT)
    OBJECT_ROOT = os.path.join(DATA_ROOT_E, r'Object', OBJECT)
    OBJECT_ViewDir = os.path.join(OBJECT_ROOT, "Views","View_%04d")
    OBJECT_CalibPrismDir = os.path.join(OBJECT_ROOT, "CalibPrism")

    # Log setting
    LOG_ROOT = os.path.join(DATA_ROOT, r"Object/LOG")
    if not os.path.exists(LOG_ROOT):
        os.mkdir(LOG_ROOT)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logFileName = r'LogAutoDownloadRMVS{:%Y-%m-%d}'.format(datetime.now())
    fileHandler = logging.FileHandler("{0}/{1}.log".format(LOG_ROOT,logFileName))
    fileHandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(fileHandler)
    consoleHander = logging.StreamHandler()
    logger.addHandler(consoleHander)

    v_size = 184
    u_size = 224
    nTotal = 409

    # Setup setting: camera, panel pose
    panelConfig = os.path.join(CONFIG_ROOT, "Setup" + OBJECT, "panelConfig.txt")
    cameraConfig = os.path.join(CONFIG_ROOT, "Setup" + OBJECT, "cameraConfig.txt")
    poseConfig = os.path.join(CONFIG_ROOT, "Setup" + OBJECT, "poseConfig.txt")

    # Option Setting
    # positionStr = r"0.1982,-0.0921,0"
    positionStr = r"0.1988,-0.09269,0"
    nViewsCount = 36
    nViews = "36"
    # Bases Setting
    generics = "20"
    genericStart = "0.01"
    genericEnd = "0.60"
    # genericRoughnesses = "0.01,0.02,0.04,0.07,0.09,0.11,0.13,0.16,0.20,0.25,0.40"
    # genericRoughnesses = "0.01,0.02,0.03,0.05,0.07,0.09,0.11,0.13,0.16,0.20,0.25"
    genericRoughnesses = "0.01,0.02,0.04,0.07,0.09,0.11,0.13,0.16,0.20,0.25"

    # Downsampled lights
    rowScanWidth = "7"
    rowScanHeight = "1"
    colScanWidth = "1"
    colScanHeight = "23"

    # Camera extrinsic, scale setting
    viewScale = "0.009"
    cameraExtrinDirectory = os.path.join(OBJECT_ROOT, "CalibPrism", "Extrinsic")

    # nrmRefine Model : recoverDirName
    # nrmRefRecDirName = "refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=10_dptWeight=10_fDistTH=1_nDptIters=1"
    nrmRefRecDirName = "refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.5_nDptIters=1"

    # Option setting
    UndistOpt = 1

    if UndistOpt:
        logger.info("Third Part: refine nrm ")
        BackUpOpt = 1

        _environ = dict(os.environ)
        try:
            if 'PATH' in _environ:
                os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT
            else:
                os.environ['PATH'] = BUILD_ROOT

            startView = 0
            for v in range(startView, nViewsCount):

                logger.info("Dealing view: {0}th".format(v))


                viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
                framesDirectory = os.path.join(viewDirectory, "Frames")

                nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                nrmRefineIterFinalDir = os.path.join(nrmRefineDirectory, "Iter", "Iter_final")

                viewRecNrmDir = os.path.join(nrmRefineDirectory, nrmRefRecDirName)
                viewDistImgFile = os.path.join(viewRecNrmDir, "distR.pfm")
                viewNrmImgFile = os.path.join(viewRecNrmDir, "nrmObj.pfm")
                refineNrmDiffWeight = os.path.join(nrmRefineIterFinalDir, r"Base_diffuse/weight.pfm")

                CopyLastIter = 1
                if CopyLastIter:
                    # copy diff weight from last iteration
                    nrmRefineIterLastDir = os.path.join(nrmRefineDirectory, "Iter", "Iter_0002")
                    refineNrmDiffLastWeight = os.path.join(nrmRefineIterLastDir, r"Base_diffuse/weight.pfm")
                    shutil.copy(refineNrmDiffLastWeight, refineNrmDiffWeight)

                if BackUpOpt:
                    viewNrmImgFileBackup = os.path.join(viewRecNrmDir, "nrmObjBackup.pfm")
                    shutil.copy(viewNrmImgFile,viewNrmImgFileBackup)

                    refineNrmDiffWeightBackup = os.path.join(nrmRefineIterFinalDir, r"Base_diffuse/weightBackup.pfm")
                    shutil.copy(refineNrmDiffWeight,refineNrmDiffWeightBackup)

                re = subprocess.run(
                    ["ImgUndistort", "-cameraConfig=" + cameraConfig, "-in=" + viewNrmImgFile, "-out=" + viewNrmImgFile],
                    stdout=True, stderr=True, check=True)

                re = subprocess.run(
                    ["ImgUndistort", "-cameraConfig=" + cameraConfig, "-in=" + refineNrmDiffWeight, "-out=" + refineNrmDiffWeight],
                    stdout=True, stderr=True, check=True)



        finally:
            os.environ.clear()
            os.environ.update(_environ)

