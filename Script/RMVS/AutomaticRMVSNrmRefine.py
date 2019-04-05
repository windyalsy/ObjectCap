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
import trimesh.io.export as ex
from datetime import datetime

def obj2ply(objFile, plyFile):
    mesh = trimesh.load(objFile)
    ex.export_mesh(mesh,plyFile,encoding='ascii',vertex_normal=True)
    return

def ply2obj(plyFile, objFile):
    mesh = trimesh.load(plyFile)
    ex.export_mesh(mesh,objFile,include_normals=True,
                     include_texture=True)
    return

# args[0] src file, arg[1] target file, args[2] working folder
def CallMagick(args):
    re = subprocess.run(["magick", args[0], "-sample", "20%", args[1]], stdout=False, stderr=True, check=True, cwd=args[2])

# args[0] target file, args[1] working folder
def CallDNGConverter(args):
    re = subprocess.run(["dngconvert","-c","1760,300-2560,1100", args[0]], stdout=False, stderr=True, check=True, cwd=args[1])

# args[0] target files, args[1] working folder
def CallADobeDNGConverter(args):
    re = subprocess.run(["AdobeDNGConverter", "-c"] + args[0], stdout=False, stderr=True, check=True, cwd=args[1])

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

    OBJECT = r"RealObject-pig2"
    OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object', OBJECT)
    OBJECT_ViewDir = os.path.join(OBJECT_ROOT, "Views","View_%04d")

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

    v_size = 184
    u_size = 224
    nTotal = 409
    sleepTime = 60
    miniutesAgo = 60 * 9
    timerBarrier = (time.time() - 60 * miniutesAgo) #if file is created after timeBarrier, it's new

    # Setup setting: camera, panel pose
    panelConfig = os.path.join(CONFIG_ROOT, "Setup", "panelConfig.txt")
    cameraConfig = os.path.join(CONFIG_ROOT, "Setup", "cameraConfig.txt")
    poseConfig = os.path.join(CONFIG_ROOT, "Setup", "poseConfig.txt")

    # Option Setting
    # positionStr = r"0.1982,-0.0921,0"
    positionStr = r"0.1988,-0.09269,0"
    nViewsCount = 36
    nViews = "36"
    # Bases Setting
    generics = "20"
    genericStart = "0.01"
    genericEnd = "0.60"
    genericRoughnesses = "0.01,0.02,0.03,0.05,0.07,0.09,0.11,0.13,0.16,0.20,0.25"

    # Downsampled lights
    rowScanWidth = "7"
    rowScanHeight = "1"
    colScanWidth = "1"
    colScanHeight = "23"

    # Camera extrinsic, scale setting
    viewScale = "0.009"
    cameraExtrinDirectory = os.path.join(OBJECT_ROOT, "CalibPrism", "Extrinsic")

    # Option setting
    DownloadOption = 0

    logger.info("Start dealing object: {0}".format(OBJECT))
    for v in range(nViewsCount):
        logger.info("Start check view: {0}".format(v))
        if DownloadOption:
            signFile = SourceViewLastFile % v
            while True:
                if os.path.isfile(signFile):
                    createTime = os.path.getctime(signFile)
                    if createTime > timerBarrier:
                        logger.info("View {0} captured finished".format(v))
                        break
                time.sleep(sleepTime)
            logger.info("Download view: {0}".format(v))
            srcDir = SourceViewDir % v
            tarDir = OBJECT_ViewDir % v
            # if tar dir exists, delete it.
            if os.path.exists(tarDir):
                shutil.rmtree(tarDir,ignore_errors=True)
                time.sleep(10)
            # copy directory
            shutil.copytree(srcDir, tarDir,ignore=_logpath)
        #----------------------------------------------------------------------------------------
        _environ = dict(os.environ)
        try:
            if 'PATH' in _environ:
                os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT
            else:
                os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT
            logger.info("Dealing view: {0}th".format(v))

            viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
            framesDirectory = os.path.join(viewDirectory, "Frames")

            inputFramesCol = os.path.join(framesDirectory, r"result_c%04d.pfm")
            inputFramesRow = os.path.join(framesDirectory, r"result_r%04d.pfm")
            curveFileCol = os.path.join(framesDirectory, r"curveCol.cur")
            curveFileRow = os.path.join(framesDirectory, "curveRow.cur")
            curveCSVCol = os.path.join(framesDirectory, "curveCol.csv")
            curveCSVRow = os.path.join(framesDirectory, "curveRow.csv")

            curveFileColAVG = os.path.join(framesDirectory, r"curveColAVG.cur")
            curveFileRowAVG = os.path.join(framesDirectory, "curveRowAVG.cur")
            curveCSVColAVG = os.path.join(framesDirectory, "curveColAVG.csv")
            curveCSVRowAVG = os.path.join(framesDirectory, "curveRowAVG.csv")

            maskFile = os.path.join(framesDirectory, "mask.pfm")
            # smooth parameters
            sigma = "2"
            hWidth = "0"
            # scale light intensity
            scale = "1"

            # # CapParse curves non AVG
            # logger.info("CapParseCur view: {0}th".format(v))
            # re = subprocess.run(["CapParseCur", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
            #                      "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
            #                      "-curveFileRow=" + curveFileRow, "-curveFileCol=" + curveFileCol,
            #                      "-curveCSVRow=" + curveCSVRow, "-curveCSVCol=" + curveCSVCol, "-sigma=" + sigma,
            #                      "-hWidth=" + hWidth, "-positionStr=" + positionStr, "-saveCurve", "--saveCSV",
            #                      "--useLightAVG", "-scale=" + scale,
            #                      "-rowScanWidth=" + rowScanWidth, "-rowScanHeight=" + rowScanHeight,
            #                      "-colScanWidth=" + colScanWidth, "-colScanHeight=" + colScanHeight],
            #                     stdout=True, stderr=True, check=True)
            #
            # BALL_TYPE = r"Diffuse"
            # recoverDirectory = os.path.join(viewDirectory, "Recover", BALL_TYPE)
            # tableFile = os.path.join(CONFIG_ROOT, BALL_TYPE, "Recover", BALL_TYPE, "nrmTab.pfm")
            # nrmRFile = os.path.join(recoverDirectory, "nrmR.pfm")
            # thMaskFile = os.path.join(recoverDirectory, "thMsk.pfm")
            # peakPosTh = "2"
            #
            # # CapNr diffuse
            # logger.info("CapNr diffuse view: {0}th".format(v))
            # re = subprocess.run(["CapNr", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
            #                      "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
            #                      "-curveFileRow=" + curveFileRowAVG, "-curveFileCol=" + curveFileColAVG,
            #                      "-curveCSVRow=" + curveCSVRowAVG, "-curveCSVCol=" + curveCSVColAVG,
            #                      "-thMaskFile=" + thMaskFile, "-peakPosTh=" + peakPosTh,
            #                      "-tableFile=" + tableFile, "-nrmRFile=" + nrmRFile, "-sigma=" + sigma,
            #                      "-hWidth=" + hWidth, "-positionStr=" + positionStr, "-saveCurve", "--saveCSV",
            #                      "-useLightAVG", "-scale=" + scale, "-maskFile=" + maskFile,
            #                      "-downsample", "-rowScanWidth=" + rowScanWidth, "-rowScanHeight=" + rowScanHeight,
            #                      "-colScanWidth=" + colScanWidth, "-colScanHeight=" + colScanHeight],
            #                     stdout=True, stderr=True, check=True)
            #
            # iterDirectory = os.path.join(recoverDirectory, "Iter")
            # iterRecordDirectory = os.path.join(iterDirectory, "Iter_%04d")
            # iterFinalDirectory = os.path.join(iterDirectory, "Iter_final")
            # refineNrmRouWeight = os.path.join(iterFinalDirectory, r"Base_r_%.5f/weight.pfm")
            # refineNrmDiffWeight = os.path.join(iterFinalDirectory, r"Base_diffuse/weight.pfm")
            # refineNrmR = os.path.join(iterFinalDirectory, "nrmR.pfm")
            # refineErrR = os.path.join(iterFinalDirectory, "errorR.pfm")
            # nrmFindInTableFile = os.path.join(recoverDirectory, "nrmR.pfm")
            #
            # thetaStep = "1"
            # phiSize = "36"
            # nIter = "2"
            # thetaSize = "10"
            # threshold = "5.0"
            # # CapRefineNrBases using diffuse normal table initialization
            #
            # logger.info("CapRefineNrBases diffuse view: {0}th".format(v))
            # re = subprocess.run(
            #     ["CapRefineNrBases", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
            #      "-specRouWeightFile=" + refineNrmRouWeight, "-diffWeightFile=" + refineNrmDiffWeight,
            #      "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
            #      "-iterDirectory=" + iterRecordDirectory,
            #      "-nrmFile=" + nrmFindInTableFile, "-maskFile=" + maskFile,
            #      "-nrmRFile=" + refineNrmR, "-errRFile=" + refineErrR,
            #      "-generics=" + generics, "-genericStart=" + genericStart, "-genericEnd=" + genericEnd,
            #      "-genericRoughnesses=" + genericRoughnesses,
            #      "-threshold=" + threshold, "-rowScanWidth=" + rowScanWidth, "-rowScanHeight=" + rowScanHeight,
            #      "-colScanWidth=" + colScanWidth, "-colScanHeight=" + colScanHeight,
            #      "-thetaStep=" + thetaStep, "-phiSize=" + phiSize, "-nIter=" + nIter, "-thetaSize=" + thetaSize,
            #      "-positionStr=" + positionStr, "-nonLocal",
            #      "-recordIter"],
            #     stdout=True, stderr=True, check=True)

            BALL_TYPE = "Mirror"
            recoverDirectory = os.path.join(viewDirectory, "Recover", BALL_TYPE)
            tableFile = os.path.join(CONFIG_ROOT, BALL_TYPE, "Recover", BALL_TYPE, "nrmTab.pfm")
            nrmRFile = os.path.join(recoverDirectory, "nrmR.pfm")
            thMaskFile = os.path.join(recoverDirectory, "thMsk.pfm")
            peakPosTh = "1"

            # CapNr specular
            logger.info("CapNr spec view: {0}th".format(v))
            re = subprocess.run(["CapNr", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                 "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                                 "-curveFileRow=" + curveFileRowAVG, "-curveFileCol=" + curveFileColAVG,
                                 "-curveCSVRow=" + curveCSVRowAVG, "-curveCSVCol=" + curveCSVColAVG,
                                 "-nrmRFile=" + nrmRFile,
                                 "-thMaskFile=" + thMaskFile, "-peakPosTh=" + peakPosTh,
                                 "-tableFile=" + tableFile,  "-sigma=" + sigma,
                                 "-hWidth=" + hWidth, "-positionStr=" + positionStr, "--saveCurve", "--saveCSV",
                                 "-useLightAVG", "-scale=" + scale, "-maskFile=" + maskFile],
                                stdout=True, stderr=True, check=True)

            nrmFile = os.path.join(recoverDirectory, "nrmR.pfm")
            diffErrorFile = os.path.join(viewDirectory, "Recover/Diffuse/Iter/Iter_final/errorR.pfm")
            nrmDiffFile = os.path.join(viewDirectory, "Recover/Diffuse/Iter/Iter_final/nrmR.pfm")

            iterDirectory = os.path.join(recoverDirectory, "Iter")
            iterRecordDirectory = os.path.join(iterDirectory, "Iter_%04d")
            iterFinalDirectory = os.path.join(iterDirectory, "Iter_final")
            refineNrmRouWeight = os.path.join(iterFinalDirectory, r"Base_r_%.5f/weight.pfm")
            refineNrmDiffWeight = os.path.join(iterFinalDirectory, r"Base_diffuse/weight.pfm")
            refineNrmR = os.path.join(iterFinalDirectory, "nrmR.pfm")
            refineErrR = os.path.join(iterFinalDirectory, "errorR.pfm")
            nrmFindInTableFile = os.path.join(recoverDirectory, "nrmR.pfm")

            thetaStep = "1"
            phiSize = "36"
            nIter = "2"
            thetaSize = "5"
            threshold = "5.0"
            # CapRefineNrBases using specular normal table initialization
            logger.info("CapRefineNrBases specular view: {0}th".format(v))
            re = subprocess.run(
                ["CapRefineNrBases", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                 "-specRouWeightFile=" + refineNrmRouWeight, "-diffWeightFile=" + refineNrmDiffWeight,
                 "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                 "-iterDirectory=" + iterRecordDirectory,
                 "-nrmFile=" + nrmFindInTableFile, "-maskFile=" + maskFile,
                 "-nrmRFile=" + refineNrmR, "-errRFile=" + refineErrR,
                 "-generics=" + generics, "-genericStart=" + genericStart, "-genericEnd=" + genericEnd,
                 "-genericRoughnesses=" + genericRoughnesses,
                 "-threshold=" + threshold, "-rowScanWidth=" + rowScanWidth, "-rowScanHeight=" + rowScanHeight,
                 "-colScanWidth=" + colScanWidth, "-colScanHeight=" + colScanHeight,
                 "-thetaStep=" + thetaStep, "-phiSize=" + phiSize, "-nIter=" + nIter, "-thetaSize=" + thetaSize,
                 "-positionStr=" + positionStr, "-nonLocal",
                 "-recordIter"],
                stdout=True, stderr=True, check=True)

            specIterFinal = os.path.join(viewDirectory, "Recover/Mirror/Iter/Iter_final")
            specRouWeight = os.path.join(specIterFinal, "Base_r_%.5f/weight.pfm")
            specDiffWeight = os.path.join(specIterFinal, "Base_diffuse/weight.pfm")
            specNrm = os.path.join(specIterFinal, "nrmR.pfm")
            specErr = os.path.join(specIterFinal, "errorR.pfm")

            diffIterFinal = os.path.join(viewDirectory, "Recover/Diffuse/Iter/Iter_final")
            diffRouWeight = os.path.join(diffIterFinal, "Base_r_%.5f/weight.pfm")
            diffDiffWeight = os.path.join(diffIterFinal, "Base_diffuse/weight.pfm")
            diffNrm = os.path.join(diffIterFinal, "nrmR.pfm")
            diffErr = os.path.join(diffIterFinal, "errorR.pfm")

            combIterFinal = os.path.join(viewDirectory, "Recover/Combine/Iter/Iter_final")
            combRouWeight = os.path.join(combIterFinal, "Base_r_%.5f/weight.pfm")
            combDiffWeight = os.path.join(combIterFinal, "Base_diffuse/weight.pfm")
            combNrm = os.path.join(combIterFinal, "nrmR.pfm")
            combErr = os.path.join(combIterFinal, "errorR.pfm")
            combSpecMsk = os.path.join(combIterFinal, "specMsk.pfm")
            combDiffMsk = os.path.join(combIterFinal, "diffMsk.pfm")
            combNrmDMsk = os.path.join(combIterFinal, "nrmDMsk.pfm")
            threshold = "5.0"

            logger.info("CapCombine view: {0}th".format(v))
            re = subprocess.run(
                ["CapFitCombine", "-specRouWeight=" + specRouWeight, "-specDiffWeight=" + specDiffWeight,
                 "-specNrm=" + specNrm, "-specErr=" + specErr, "-diffRouWeight=" + diffRouWeight,
                 "-diffDiffWeight=" + diffDiffWeight,
                 "-diffNrm=" + diffNrm, "-diffErr=" + diffErr, "-combRouWeight=" + combRouWeight,
                 "-combDiffWeight=" + combDiffWeight,
                 "-combNrm=" + combNrm, "-combErr=" + combErr, "-combSpecMsk=" + combSpecMsk,
                 "-combDiffMsk=" + combDiffMsk,
                 "-maskFile=" + maskFile, "-cameraConfig=" + cameraConfig,
                 "-generics=" + generics, "-genericStart=" + genericStart, "-genericEnd=" + genericEnd,
                 "-genericRoughnesses=" + genericRoughnesses,
                 "-combNrmDMsk=" + combNrmDMsk, "-threshold=" + threshold],
                stdout=True, stderr=True, check=True)

        finally:
            os.environ.clear()
            os.environ.update(_environ)
