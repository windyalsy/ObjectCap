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
    COMMON_ROOT = os.path.join(DATA_ROOT, r'RealCommon')
    CONFIG_ROOT = os.path.join(COMMON_ROOT,r"Config0301")

    # OBJECT = r"RealObject-pig2"
    # OBJECT = r"RealObject-penrack3"
    # OBJECT = r"RealObject-pig2"
    OBJECT = r"RealObject-oatmeal"
    # OBJECT = r"RealObject-cookies"
    OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object', OBJECT)
    OBJECT_ViewDir = os.path.join(OBJECT_ROOT, "Views","View_%04d")
    OBJECT_CalibPrismDir = os.path.join(OBJECT_ROOT, "CalibPrism")


    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

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
    genericRoughnesses = "0.01,0.02,0.04,0.07,0.09,0.11,0.13,0.16,0.20,0.25,0.40"
    # genericRoughnesses = "0.01,0.02,0.03,0.05,0.07,0.09,0.11,0.13,0.16,0.20,0.25"

    # Downsampled lights
    rowScanWidth = "7"
    rowScanHeight = "1"
    colScanWidth = "1"
    colScanHeight = "23"

    # Camera extrinsic, scale setting
    viewScale = "0.009"
    cameraExtrinDirectory = os.path.join(OBJECT_ROOT, "CalibPrism", "Extrinsic")

    # nrmRefine Model : recoverDirName
    nrmRefRecDirName = "refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.5_nDptIters=1"

    # Option setting

    logger.info("Start dealing object: {0}".format(OBJECT))
    if not os.path.exists(OBJECT_ROOT):
        os.makedirs(OBJECT_ROOT)
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
            # FramesCombine: projected images from the recovered model using combined normal maps
            nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesCombine")
            nrmRefineIterFinalDir = os.path.join(nrmRefineDirectory, "Iter", "Iter_final")

            # viewMaskImgFile = os.path.join(framesDirectory, "mask.pfm")
            viewMaskImgFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")
            viewMeasPeakImgFile = os.path.join(nrmRefineIterFinalDir, "peakMeas.pfm")
            viewSpecPeakImgFile = os.path.join(nrmRefineIterFinalDir, "peakSpec.pfm")
            viewDiffPeakImgFile = os.path.join(nrmRefineIterFinalDir, "peakDiff.pfm")

            # output refinement weight files
            refineNrmRouWeight = os.path.join(nrmRefineIterFinalDir, r"Base_r_%.5f/weight.pfm")
            refineNrmDiffWeight = os.path.join(nrmRefineIterFinalDir, r"Base_diffuse/weight.pfm")
            peakPosTh = "2"

            nrmRefineItersDirectory = os.path.join(nrmRefineDirectory, "Iter", "Iter_%04d" % 2)
            src = os.path.join(nrmRefineItersDirectory, r"errorUpdateWeights.pfm")
            dst = os.path.join(nrmRefineIterFinalDir, r"errorR.pfm")
            shutil.move(src,dst)

    finally:
        os.environ.clear()
        os.environ.update(_environ)


