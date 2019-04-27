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
    # OBJECT = r"RealObject-oatmeal2"
    OBJECT = r"RealObject-cookies"
    # OBJECT = r"RealObject-cookies2"
    # OBJECT = r"RealObject-gift1"
    # OBJECT = r"RealObject-gift2"
    # OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object', OBJECT)
    OBJECT_ROOT = os.path.join(DATA_ROOT_E, r'Object', OBJECT)
    # OBJECT_ROOT = r"C:\v-jiazha\RealObject-penrack3"
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

    # Download source setting
    SourceOBJECT = OBJECT
    SourcePath = r"\\msr-ig-server13\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object"
    SourceDir = os.path.join(SourcePath,SourceOBJECT)
    SourceViewDir = os.path.join(SourceDir,"Views","View_%04d")
    SourceViewLastFile = os.path.join(SourceViewDir,"Frames", "result_c0223.pfm")
    SourceCalibPrismDir = os.path.join(SourceDir,"CalibPrism")
    SourceCalibPrismLastFile = os.path.join(SourceCalibPrismDir,"Extrinsic","view_0035.txt")

    v_size = 184
    u_size = 224
    nTotal = 409
    sleepTime = 60
    miniutesAgo = 60 * (15 + 24*8)
    timerBarrier = (time.time() - 60 * miniutesAgo) #if file is created after timeBarrier, it's new

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
    # genericRoughnesses = "0.01,0.02,0.04,0.07,0.09,0.11,0.13,0.16,0.20,0.25"

    # Downsampled lights
    rowScanWidth = "7"
    rowScanHeight = "1"
    colScanWidth = "1"
    colScanHeight = "23"

    # Camera extrinsic, scale setting
    viewScale = "0.009"
    cameraExtrinDirectory = os.path.join(OBJECT_ROOT, "CalibPrism", "Extrinsic")

    # nrmRefine Model : recoverDirName
    # nrmRefRecDirName = "refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.5_nDptIters=1"
    # nrmRefRecDirName = "refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.1_nDptIters=1"
    nrmRefRecDirName = "refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=10_dptWeight=10_fDistTH=1_nDptIters=2"

    # Option setting
    SecondRefineNrmOption = 1


    logger.info("Start dealing object: {0}".format(OBJECT))

    if SecondRefineNrmOption:
        logger.info("Third Part: refine nrm ")
        CapSimOption = 0
        CapDilateMaskOption = 0
        CapRefineNrBasesOption = 1
        # parse curves from projected mask.
        CapParseCurOption = 0
        CapSpecPeakMask = 0

        modelName = "Recover"
        meshComReconTrimFObj = os.path.join(OBJECT_ROOT, r"Recover\Model\Combine", "{0}.obj".format(modelName))

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
                # FramesCombine: projected images from the recovered model using combined normal maps
                nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesCombine")
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

                if CapDilateMaskOption:
                    # dilate masks
                    nDil = "50"
                    inputFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")
                    outputFile = os.path.join(nrmRefineFramesDirectory, "mask_dil.pfm")
                    re = subprocess.run(
                        ["ImgDilator", "-in=" + inputFile, "-out=" + outputFile, "-n=" + nDil], stdout=True,
                        stderr=True,
                        check=True)

                    inputFile = os.path.join(nrmRefineFramesDirectory, "pos.pfm")
                    outputFile = os.path.join(nrmRefineFramesDirectory, "pos_dil.pfm")
                    re = subprocess.run(
                        ["ImgDilator", "-in=" + inputFile, "-out=" + outputFile, "-n=" + nDil], stdout=True,
                        stderr=True,
                        check=True)

                inputFramesCol = os.path.join(framesDirectory, r"result_c%04d.pfm")
                inputFramesRow = os.path.join(framesDirectory, r"result_r%04d.pfm")

                combIterFinal = os.path.join(viewDirectory, "Recover/Combine/Iter/Iter_final")
                combRouWeight = os.path.join(combIterFinal, "Base_r_%.5f/weight.pfm")
                combDiffWeight = os.path.join(combIterFinal, "Base_diffuse/weight.pfm")
                combNrm = os.path.join(combIterFinal, "nrmR.pfm")
                combErr = os.path.join(combIterFinal, "errorR.pfm")
                combSpecMsk = os.path.join(combIterFinal, "specMsk.pfm")
                combDiffMsk = os.path.join(combIterFinal, "diffMsk.pfm")

                nrmRefineItersDirectory = os.path.join(nrmRefineDirectory, "IterSam", "Iter_%04d")
                nrmRefineIterFinalDir = os.path.join(nrmRefineDirectory, "IterSam", "Iter_final")

                recPos = os.path.join(nrmRefineFramesDirectory, "pos.pfm")
                recPosDil = os.path.join(nrmRefineFramesDirectory, "pos_dil.pfm")
                refineNrmR = os.path.join(nrmRefineIterFinalDir, "nrmR.pfm")
                refineErrR = os.path.join(nrmRefineIterFinalDir, "errorR.pfm")
                refineNrmD = os.path.join(nrmRefineIterFinalDir, "nrmD.pfm")
                refineNrmS = os.path.join(nrmRefineIterFinalDir, "nrmS.pfm")
                refineNrmDMsk = os.path.join(nrmRefineIterFinalDir, "nrmDMsk.pfm")


                threshold = "5.0"

                viewDepTruthImgFile = os.path.join(framesDirectory, "depth.pfm")
                # viewMaskImgFile = os.path.join(framesDirectory, "mask.pfm")
                viewMaskImgFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")
                viewMaskDilImgFile  = os.path.join(nrmRefineFramesDirectory, "mask_dil.pfm")

                thetaStep = "1"
                phiSize = "4"
                nIter = "2"
                thetaSize = "6"

                numUniform = "10"
                numImportance = "10"

                # output refinement weight files
                refineNrmRouWeight = os.path.join(nrmRefineIterFinalDir, r"Base_r_%.5f/weight.pfm")
                refineNrmDiffWeight = os.path.join(nrmRefineIterFinalDir, r"Base_diffuse/weight.pfm")
                if CapRefineNrBasesOption:
                    logger.info("CapRefineNrBasesSamping view: {0}th".format(v))
                    re = subprocess.run(
                        ["CapRefineNrBasesSampling", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                         "-specRouWeightFile=" + refineNrmRouWeight,
                         "-diffWeightFile=" + refineNrmDiffWeight,
                         "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                         "-iterDirectory=" + nrmRefineItersDirectory,
                         "-iterFinalDirectory=" + nrmRefineIterFinalDir,
                         "-nrmFile=" + combNrm, "-posFile=" + recPosDil, "-maskFile=" + viewMaskDilImgFile,
                         "-nrmRFile=" + refineNrmR, "-errRFile=" + refineErrR, "-nrmDFile=" + refineNrmD,
                         "-nrmSFile=" + refineNrmS, "-nrmDMskFile=" + refineNrmDMsk,
                         "-generics=" + generics, "-genericStart=" + genericStart,
                         "-genericEnd=" + genericEnd,
                         "-genericRoughnesses=" + genericRoughnesses,
                         "-threshold=" + threshold, "-rowScanWidth=" + rowScanWidth,
                         "-rowScanHeight=" + rowScanHeight,
                         "-colScanWidth=" + colScanWidth, "-colScanHeight=" + colScanHeight,
                         "-thetaStep=" + thetaStep, "-phiSize=" + phiSize, "-nIter=" + nIter,
                         "-thetaSize=" + thetaSize,
                         "-numUniform=" + numUniform,"-numImportance=" + numImportance,
                         "--recordIter"],
                        stdout=True, stderr=True, check=True)

                refineInputFramesCol = os.path.join(nrmRefineFramesDirectory, r"result_c%04d.pfm")
                refineInputFramesRow = os.path.join(nrmRefineFramesDirectory, r"result_r%04d.pfm")

                # CapParseCur
                if CapParseCurOption:
                    curveFileCol = os.path.join(framesDirectory, r"curveColProjMsk.cur")
                    curveFileRow = os.path.join(framesDirectory, "curveRowProjMsk.cur")

                    maskFile = viewMaskDilImgFile
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
                    # viewMaskImgFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")
                    # viewMaskDilImgFile
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
                         "-maskFile=" + viewMaskDilImgFile,
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

