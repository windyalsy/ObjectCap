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
    TOOL_LCT_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool\LCT"
    COMMON_ROOT = os.path.join(DATA_ROOT, r'RealCommon')
    CONFIG_ROOT = os.path.join(COMMON_ROOT,r"Config0301")

    # OBJECT = r"RealObject-pig2"
    # OBJECT = r"RealObject-penrack3"
    # OBJECT = r"RealObject-pig2"
    # OBJECT = r"RealObject-oatmeal"
    OBJECT = r"RealObject-cookies"
    OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object', OBJECT)
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
    nrmRefRecDirName = "refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.1_nDptIters=0"

    # Option setting
    FinalBRDFOpt = 1

    if FinalBRDFOpt:
        logger.info("Third Part: refine nrm ")
        CapSimOption = 1

        CapRefineNrBasesOption = 1
        # parse curves from projected mask.
        CapParseCurOption = 1
        CapSpecPeakMask = 1

        BRDFOptDirName = "FinalOpt2"
        modelName = "Recover"
        meshComReconTrimFObj = os.path.join(OBJECT_ROOT, r"Recover\Model\Combine", "{0}.obj".format(modelName))
        meshComReconTrimFObj = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-cookies\Recover\Model\FinalOpt\RecoverUpdate.obj"
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
                modelFile = meshComReconTrimFObj

                viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
                framesDirectory = os.path.join(viewDirectory, "Frames")

                nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "Frames"+BRDFOptDirName)
                # nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "Frames")

                cameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt" % v)
                renderOption = "2"
                if CapSimOption:
                    logger.info("CapSim view: {0}th".format(v))
                    re = subprocess.run(
                        ["CapSim", "-framesDirectory=" + nrmRefineFramesDirectory, "-modelFile=" + modelFile,
                         "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                         "-viewScale=" + viewScale, "-flipZ",
                         "-renderOption=" + renderOption],
                        stdout=True, stderr=True, check=True)

                inputFramesCol = os.path.join(framesDirectory, r"result_c%04d.pfm")
                inputFramesRow = os.path.join(framesDirectory, r"result_r%04d.pfm")

                nrmRefineItersDirectory = os.path.join(nrmRefineDirectory, "Iter" + BRDFOptDirName, "Iter_%04d")
                nrmRefineIterFinalDir = os.path.join(nrmRefineDirectory, "Iter" + BRDFOptDirName, "Iter_final")

                recPos = os.path.join(nrmRefineFramesDirectory, "pos.pfm")
                viewImgNrm = os.path.join(nrmRefineFramesDirectory, "nrm.pfm")
                viewMaskImgFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")
                refineNrmR = os.path.join(nrmRefineIterFinalDir, "nrmR.pfm")
                refineErrR = os.path.join(nrmRefineIterFinalDir, "errorR.pfm")

                thetaStep = "1"
                phiSize = "4"
                nIter = "0"
                thetaSize = "6"

                # output refinement weight files
                refineNrmRouWeight = os.path.join(nrmRefineIterFinalDir, r"Base_r_%.5f/weight.pfm")
                refineNrmDiffWeight = os.path.join(nrmRefineIterFinalDir, r"Base_diffuse/weight.pfm")
                if CapRefineNrBasesOption:
                    logger.info("CapRefineNrBases view: {0}th".format(v))
                    #fix normal and solve weights: nIter:0
                    re = subprocess.run(
                        ["CapRefineNrBases", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                         "-specRouWeightFile=" + refineNrmRouWeight,
                         "-diffWeightFile=" + refineNrmDiffWeight,
                         "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                         "-iterDirectory=" + nrmRefineItersDirectory,
                         "-iterFinalDirectory=" + nrmRefineIterFinalDir,
                         "-nrmFile=" + viewImgNrm, "-posFile=" + recPos, "-maskFile=" + viewMaskImgFile,
                         "-nrmRFile=" + refineNrmR, "-errRFile=" + refineErrR,
                         "-generics=" + generics, "-genericStart=" + genericStart,
                         "-genericEnd=" + genericEnd,
                         "-genericRoughnesses=" + genericRoughnesses,
                         "-rowScanWidth=" + rowScanWidth,
                         "-rowScanHeight=" + rowScanHeight,
                         "-colScanWidth=" + colScanWidth, "-colScanHeight=" + colScanHeight,
                         "-thetaStep=" + thetaStep, "-phiSize=" + phiSize, "-nIter=" + nIter,
                         "-thetaSize=" + thetaSize,
                         "-recordIter"],
                        stdout=True, stderr=True, check=True)

                refineInputFramesCol = os.path.join(nrmRefineFramesDirectory, r"result_c%04d.pfm")
                refineInputFramesRow = os.path.join(nrmRefineFramesDirectory, r"result_r%04d.pfm")

                # CapParseCur
                if CapParseCurOption:
                    curveFileCol = os.path.join(framesDirectory, r"curveColProjMskFinalOpt2.cur")
                    curveFileRow = os.path.join(framesDirectory, "curveRowProjMskFinalOpt2.cur")

                    maskFile = viewMaskImgFile
                    # smooth parameters
                    sigma = "2"
                    hWidth = "0"
                    # scale light intensity
                    scale = "1"
                    logger.info("CapParseCur projected mask view: {0}th".format(v))
                    re = subprocess.run(
                        ["CapParseCur", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                         "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                         "-curveFileRow=" + curveFileRow, "-curveFileCol=" + curveFileCol,
                         "-sigma=" + sigma,
                         "-hWidth=" + hWidth, "-positionStr=" + positionStr, "-saveCurve", "--saveCSV",
                         "--useLightAVG", "-scale=" + scale, "-maskFile=" + maskFile,
                         "-rowScanWidth=" + rowScanWidth, "-rowScanHeight=" + rowScanHeight,
                         "-colScanWidth=" + colScanWidth, "-colScanHeight=" + colScanHeight],
                        stdout=True, stderr=True, check=True)

                # CapSpecPeakMask
                if CapSpecPeakMask:
                    # viewMaskImgFile = os.path.join(framesDirectory, "mask.pfm")
                    viewMaskImgFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")
                    viewMeasPeakImgFile = os.path.join(nrmRefineIterFinalDir, "peakMeas.pfm")
                    viewSpecPeakImgFile = os.path.join(nrmRefineIterFinalDir, "peakSpec.pfm")
                    viewDiffPeakImgFile = os.path.join(nrmRefineIterFinalDir, "peakDiff.pfm")

                    # output refinement weight files
                    refineNrmRouWeight = os.path.join(nrmRefineIterFinalDir, r"Base_r_%.5f/weight.pfm")
                    refineNrmDiffWeight = os.path.join(nrmRefineIterFinalDir, r"Base_diffuse/weight.pfm")
                    peakPosTh = "2"
                    re = subprocess.run(
                        ["CapSpecPeakMask", "-panelConfig=" + panelConfig,
                         "-specRouWeightFile=" + refineNrmRouWeight,
                         "-diffWeightFile=" + refineNrmDiffWeight,
                         "-iterFinalDirectory=" + nrmRefineIterFinalDir,
                         "-maskFile=" + viewMaskImgFile,
                         "-measPeakFile=" + viewMeasPeakImgFile,
                         "-specPeakFile=" + viewSpecPeakImgFile,
                         "-diffPeakFile=" + viewDiffPeakImgFile,
                         "-generics=" + generics, "-genericStart=" + genericStart,
                         "-genericEnd=" + genericEnd,
                         "-genericRoughnesses=" + genericRoughnesses,
                         "-peakPosTh=" + peakPosTh],
                        stdout=True, stderr=True, check=True)
        finally:
            os.environ.clear()
            os.environ.update(_environ)

