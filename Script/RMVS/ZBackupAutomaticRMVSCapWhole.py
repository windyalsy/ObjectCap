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
    ex.export_mesh(mesh,objFile)
    return

def rmBadFace(objFile,objRFile):
    mesh = trimesh.load(objFile)
    mesh.remove_degenerate_faces()
    ex.export_mesh(mesh,objRFile)

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
    # OBJECT = r"RealObject-penrack"
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
    miniutesAgo = 60 * 100
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
    DownloadViewsOption = 0
    DownloadCalibPrismOption = 0
    FirstCapNrmOption = 0
    FirstMVSOption = 0
    SecondRefineNrmOption = 0
    SecondMVSOption = 1
    FinalMeshOpt = 1

    logger.info("Start dealing object: {0}".format(OBJECT))
    startView = 0
    for v in range(startView,nViewsCount):
        if DownloadViewsOption:
            logger.info("Start check view: {0}".format(v))
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
        if FirstCapNrmOption:
            CapParseCurOption = 0
            CapNrDiffOption = 0
            CapNrSpecOption = 1
            CapRefineNrBasesDiffOption = 0
            CapRefineNrBasesSpecOption = 0
            CapCombineOption = 0
            logger.info("First part: CapSim CapParseCur CapNr CapRefineNrBases CapCombine")
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

                if CapParseCurOption:
                    # CapParse curves non AVG
                    logger.info("CapParseCur view: {0}th".format(v))
                    re = subprocess.run(["CapParseCur", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                         "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                                         "-curveFileRow=" + curveFileRow, "-curveFileCol=" + curveFileCol,
                                         "-curveCSVRow=" + curveCSVRow, "-curveCSVCol=" + curveCSVCol, "-sigma=" + sigma,
                                         "-hWidth=" + hWidth, "-positionStr=" + positionStr, "-saveCurve", "--saveCSV",
                                         "--useLightAVG", "-scale=" + scale,
                                         "-rowScanWidth=" + rowScanWidth, "-rowScanHeight=" + rowScanHeight,
                                         "-colScanWidth=" + colScanWidth, "-colScanHeight=" + colScanHeight],
                                        stdout=True, stderr=True, check=True)

                BALL_TYPE = r"Diffuse"
                recoverDirectory = os.path.join(viewDirectory, "Recover", BALL_TYPE)
                tableFile = os.path.join(CONFIG_ROOT, BALL_TYPE, "Recover", BALL_TYPE, "nrmTab.pfm")
                nrmRFile = os.path.join(recoverDirectory, "nrmR.pfm")
                thMaskFile = os.path.join(recoverDirectory, "thMsk.pfm")
                peakPosTh = "2"

                if CapNrDiffOption:
                    # CapNr diffuse
                    logger.info("CapNr diffuse view: {0}th".format(v))
                    re = subprocess.run(["CapNr", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                         "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                                         "-curveFileRow=" + curveFileRowAVG, "-curveFileCol=" + curveFileColAVG,
                                         "-curveCSVRow=" + curveCSVRowAVG, "-curveCSVCol=" + curveCSVColAVG,
                                         "-thMaskFile=" + thMaskFile, "-peakPosTh=" + peakPosTh,
                                         "-tableFile=" + tableFile, "-nrmRFile=" + nrmRFile, "-sigma=" + sigma,
                                         "-hWidth=" + hWidth, "-positionStr=" + positionStr, "-saveCurve", "--saveCSV",
                                         "-useLightAVG", "-scale=" + scale, "-maskFile=" + maskFile,
                                         "-downsample", "-rowScanWidth=" + rowScanWidth, "-rowScanHeight=" + rowScanHeight,
                                         "-colScanWidth=" + colScanWidth, "-colScanHeight=" + colScanHeight],
                                        stdout=True, stderr=True, check=True)

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
                nIter = "1"
                thetaSize = "10"
                threshold = "5.0"
                # CapRefineNrBases using diffuse normal table initialization

                if CapRefineNrBasesDiffOption:
                    logger.info("CapRefineNrBases diffuse view: {0}th".format(v))
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

                BALL_TYPE = "Mirror"
                recoverDirectory = os.path.join(viewDirectory, "Recover", BALL_TYPE)
                tableFile = os.path.join(CONFIG_ROOT, BALL_TYPE, "Recover", BALL_TYPE, "nrmTab.pfm")
                nrmRFile = os.path.join(recoverDirectory, "nrmR.pfm")
                thMaskFile = os.path.join(recoverDirectory, "thMsk.pfm")
                peakPosTh = "2"

                if CapNrSpecOption:
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
                nIter = "1"
                thetaSize = "5"
                threshold = "5.0"
                if CapRefineNrBasesSpecOption:
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

                if CapCombineOption:
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

    #---------------------------------------------------------------------------------------
    if DownloadCalibPrismOption:
        logger.info("Start check calib prism")
        signFile = SourceCalibPrismLastFile
        while True:
            if os.path.isfile(signFile):
                createTime = os.path.getctime(signFile)
                if createTime > timerBarrier:
                    logger.info("Camera extrinsic ready")
                    break
            time.sleep(sleepTime)
        logger.info("Download calib prism")
        srcDir = SourceCalibPrismDir
        tarDir = OBJECT_CalibPrismDir
        # if tar dir exists, delete it.
        if os.path.exists(tarDir):
            shutil.rmtree(tarDir, ignore_errors=True)
            time.sleep(10)
        # copy directory
        shutil.copytree(srcDir, tarDir, ignore=_logpath)

    if FirstMVSOption:
        RGBNPlaneSweepMVSOption = 1
        CombineAllViewOption = 1
        PoissonEachViewOption = 0

        logger.info("Second Part: MVS ")
        if not os.path.exists(OBJECT_ROOT):
            os.makedirs(OBJECT_ROOT)
        _environ = dict(os.environ)
        try:
            if 'PATH' in _environ:
                os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT  + ";" + TOOL_ROOT
            else:
                os.environ['PATH'] = BUILD_ROOT  + ";" + TOOL_ROOT


            viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
            framesDirectory = os.path.join(viewDirectory, "Frames")
            viewCameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt")

            combIterFinal = os.path.join(viewDirectory, "Recover/Combine/Iter/Iter_final")
            combDiffWeight = os.path.join(combIterFinal, "Base_diffuse/weight.pfm")
            combNrm = os.path.join(combIterFinal, "nrmR.pfm")

            viewRGBImgFile = combDiffWeight
            viewNrmImgFile = combNrm
            modelName = "re_" + OBJECT
            recoverDirName = "re_Th_"

            rgbWeight = "10"
            nrmWeight = "1"
            dptWeight = "1"
            minDepth = "1.1"
            maxDepth = "1.3"
            nNeighbors = "2"
            nSteps = "1001"
            nRefineIters = "3"
            nRefineSteps = "9"
            nDptIters = "1"
            nFirstKNeighborsForCost = "2"

            fDistTH = "0.001"
            nMetricLabel = "1"

            recoverDirName = recoverDirName + "rgbWeight=" + rgbWeight + "_nrmWeight=" + nrmWeight + "_dptWeight=" \
                             + dptWeight + "_fDistTH=" + fDistTH + "_nDptIters=" + nDptIters

            outputDir = os.path.join(combIterFinal, recoverDirName)
            viewDistImgFile = os.path.join(outputDir, "distR.pfm")
            viewDepthImgFile = os.path.join(outputDir, "depthR.pfm")

            viewMaskImgFile = os.path.join(framesDirectory, "mask.pfm")
            # test mask
            viewThMaskImgFile = os.path.join(viewDirectory, "Recover/Mirror/thMsk.pfm")

            # Sweep
            if RGBNPlaneSweepMVSOption:
                logger.info("RGBNPlaneSweepMVS")
                re = subprocess.run(["RGBNPlaneSweepMVS", "-cameraConfig=" + cameraConfig, "-poseConfig=" + poseConfig,
                                     "-cameraExtrin=" + viewCameraExtrinsic,
                                     "-viewFramesDirectory=" + outputDir, "-viewRGBImgFile=" + viewRGBImgFile,
                                     "-viewNrmImgFile=" + viewNrmImgFile, "-viewDistImgFile=" + viewDistImgFile,
                                     "-viewDepthImgFile=" + viewDepthImgFile,
                                     "-viewMaskImgFile=" + viewMaskImgFile,
                                     # "-viewMaskImgFile=" + viewThMaskImgFile,
                                     # "-viewThMaskImgFile=" + viewThMaskImgFile,
                                     "-modelName=" + modelName, "-rgbWeight=" + rgbWeight, "-nrmWeight=" + nrmWeight,
                                     "-dptWeight=" + dptWeight, "-nDptIters=" + nDptIters,
                                     "-minDepth=" + minDepth, "-maxDepth=" + maxDepth, "-nNeighbors=" + nNeighbors,
                                     "-nSteps=" + nSteps, "-nRefineIters=" + nRefineIters,
                                     "-nRefineSteps=" + nRefineSteps,
                                     "-nFirstKNeighborsForCost=" + nFirstKNeighborsForCost, "-nViews=" + nViews,
                                     "-bDistTHLabel",
                                     "-fDistTH=" + fDistTH, "-nMetricLabel=" + nMetricLabel, "-flipZ", "-GPUOption",
                                     "-viewScale=" + viewScale, "-realOption"],
                                    stdout=True, stderr=True, check=True)

            meshCom = trimesh.base.Trimesh()  # combine all views's meshes.
            meshComF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName, "Comb_{0}.txt".format(modelName))
            meshComObjF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName, "Comb_{0}.obj".format(modelName))
            meshComReconF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName, "Recon_{0}.ply".format(modelName))
            meshComReconTrimF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName,
                                             "Trim_{0}.ply".format(modelName))
            meshComReconTrimFObj = os.path.join(OBJECT_ROOT, r"Recover\Model\Recover.obj".format(modelName))

            meshComFDir = os.path.dirname(meshComF)
            logger.info("Start combine all views' mesh")
            if not os.path.exists(meshComFDir):
                os.makedirs(meshComFDir)
            _environ = dict(os.environ)

            if CombineAllViewOption:
                for v in range(nViewsCount):
                    viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
                    combIterFinal = os.path.join(viewDirectory, "Recover", "Combine", "Iter", "Iter_final")
                    outputDir = os.path.join(combIterFinal, recoverDirName)

                    modelObjF = os.path.join(outputDir, "{0}.obj".format(modelName))
                    modelPlyF = os.path.join(outputDir, "{0}_%04d.ply".format(modelName) % v)
                    modelReconF = os.path.join(outputDir, "{0}Recon_%04d.ply".format(modelName) % v)
                    modelReconTrimF = os.path.join(outputDir, "{0}ReconTrim_%04d.ply".format(modelName) % v)
                    logger.info("PossionRecon view: {0}th".format(v))
                    if PoissonEachViewOption:
                        obj2ply(modelObjF, modelPlyF)
                        # Poisson reconstruction
                        re = subprocess.run(["PoissonRecon.exe", "--in", modelPlyF, "--out", modelReconF,
                                             "--density", "--verbose", "--threads", "8"], stdout=True, stderr=True,
                                            check=True)
                        # Trim surface
                        re = subprocess.run(
                            ["SurfaceTrimmer.exe", "--in", modelReconF, "--out", modelReconTrimF, "--trim", "7"],
                            stdout=True, stderr=True, check=True)
                        # mesh = trimesh.load(modelReconTrimF)
                    # mesh = trimesh.load(modelPlyF)
                    mesh = trimesh.load(modelObjF)
                    if v == 0:
                        vertices = mesh.vertices
                        vertexNrms = mesh.vertex_normals
                    else:
                        vertices = np.concatenate((vertices, mesh.vertices), axis=0)
                        vertexNrms = np.concatenate((vertexNrms, mesh.vertex_normals), axis=0)
                    meshCom = trimesh.util.concatenate(meshCom, mesh)
                # save combined mesh
                # meshCom.vertices = vertices
                # meshCom.vertex_normals = vertexNrms
                pointCloud = np.concatenate((vertices, vertexNrms), axis=1)
                np.savetxt(meshComF, pointCloud, delimiter=" ")
                # meshCom = trimesh.base.Trimesh(vertices = vertices)
                ex.export_mesh(meshCom, meshComObjF, include_normals=True)
                # obj2ply(meshComObjF,meshComF)
                # ex.export_mesh(meshCom, meshComF, encoding='ascii', vertex_normal=True)

            # poisson reconstruct combined mesh
            re = subprocess.run(
                ["PoissonRecon.exe", "--in", meshComF, "--out", meshComReconF, "--normals", "--depth", "12",
                 "--pointWeight", "0",
                 "--density", "--threads", "2"], stdout=True, stderr=True, check=True)
            # trim combined mesh
            re = subprocess.run(
                ["SurfaceTrimmer.exe", "--in", meshComReconF, "--out", meshComReconTrimF, "--trim", "7"],
                stdout=True, stderr=True, check=True)
            ply2obj(meshComReconTrimF, meshComReconTrimFObj)
        finally:
            os.environ.clear()
            os.environ.update(_environ)

    if SecondRefineNrmOption:
        logger.info("Third Part: refine nrm ")
        CapSimOption = 1

        CapRefineNrBasesOption = 0
        # parse curves from projected mask.
        CapParseCurOption = 0

        if SecondRefineNrmOption:
            modelName = "Recover"
            meshComReconTrimFObj = os.path.join(OBJECT_ROOT, r"Recover\Model", "{0}.obj".format(modelName))

            if not os.path.exists(OBJECT_ROOT):
                os.makedirs(OBJECT_ROOT)
            _environ = dict(os.environ)
            try:
                if 'PATH' in _environ:
                    os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT
                else:
                    os.environ['PATH'] = BUILD_ROOT

                for v in range(startView,nViewsCount):

                    logger.info("Dealing view: {0}th".format(v))
                    modelFile = meshComReconTrimFObj

                    viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
                    framesDirectory = os.path.join(viewDirectory, "Frames")

                    nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                    nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesBase")
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

                    combIterFinal = os.path.join(viewDirectory, "Recover/Combine/Iter/Iter_final")
                    combRouWeight = os.path.join(combIterFinal, "Base_r_%.5f/weight.pfm")
                    combDiffWeight = os.path.join(combIterFinal, "Base_diffuse/weight.pfm")
                    combNrm = os.path.join(combIterFinal, "nrmR.pfm")
                    combErr = os.path.join(combIterFinal, "errorR.pfm")
                    combSpecMsk = os.path.join(combIterFinal, "specMsk.pfm")
                    combDiffMsk = os.path.join(combIterFinal, "diffMsk.pfm")

                    recPos = os.path.join(nrmRefineFramesDirectory, "pos.pfm")
                    refineNrmR = os.path.join(nrmRefineFramesDirectory, "nrmR.pfm")
                    refineErrR = os.path.join(nrmRefineFramesDirectory, "errorR.pfm")
                    refineNrmD = os.path.join(nrmRefineFramesDirectory, "nrmD.pfm")
                    refineNrmS = os.path.join(nrmRefineFramesDirectory, "nrmS.pfm")
                    refineNrmDMsk = os.path.join(nrmRefineFramesDirectory, "nrmDMsk.pfm")
                    nrmRefineItersDirectory = os.path.join(nrmRefineFramesDirectory, "Iter", "Iter_%04d")

                    threshold = "5.0"

                    modelName = "re" + "RecWithDepthConstraintO2NCC"
                    recoverDirName = "re_RGBN_DptCon"

                    outputDir = os.path.join(combIterFinal, recoverDirName)
                    viewPosImgFile = os.path.join(outputDir, "pos.pfm")
                    viewDistImgFile = os.path.join(outputDir, "distR.pfm")
                    viewDepthImgFile = os.path.join(outputDir, "depthR.pfm")
                    viewDepTruthImgFile = os.path.join(framesDirectory, "depth.pfm")
                    # viewMaskImgFile = os.path.join(framesDirectory, "mask.pfm")
                    viewMaskImgFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")

                    thetaStep = "0.5"
                    phiSize = "36"
                    nIter = "2"
                    thetaSize = "10"

                    # output refinement weight files
                    refineNrmRouWeight = os.path.join(nrmRefineFramesDirectory, r"Base_r_%.5f/weight.pfm")
                    refineNrmDiffWeight = os.path.join(nrmRefineFramesDirectory, r"Base_diffuse/weight.pfm")
                    if CapRefineNrBasesOption:
                        logger.info("CapRefineNrBases view: {0}th".format(v))
                        re = subprocess.run(
                            ["CapRefineNrBases", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                             "-specRouWeightFile=" + refineNrmRouWeight,
                             "-diffWeightFile=" + refineNrmDiffWeight,
                             "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                             "-iterDirectory=" + nrmRefineItersDirectory,
                             "-nrmFile=" + combNrm, "-posFile=" + recPos, "-maskFile=" + viewMaskImgFile,
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
                             "-recordIter"],
                            stdout=True, stderr=True, check=True)

                    refineInputFramesCol = os.path.join(nrmRefineFramesDirectory, r"result_c%04d.pfm")
                    refineInputFramesRow = os.path.join(nrmRefineFramesDirectory, r"result_r%04d.pfm")

                    # CapParseCur
                    if CapParseCurOption:
                        curveFileCol = os.path.join(framesDirectory, r"curveColProjMsk.cur")
                        curveFileRow = os.path.join(framesDirectory, "curveRowProjMsk.cur")

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

            finally:
                os.environ.clear()
                os.environ.update(_environ)

    if SecondMVSOption:
        # Forth part RefineNrBases
        logger.info("Forth Part: MVS ")
        if SecondMVSOption:
            MVSSweepOption = 5
            RGBNPlaneSweepMVSOption = 0

            if not os.path.exists(OBJECT_ROOT):
                os.makedirs(OBJECT_ROOT)
            _environ = dict(os.environ)
            try:
                if 'PATH' in _environ:
                    os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT
                else:
                    os.environ['PATH'] = BUILD_ROOT

                viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
                framesDirectory = os.path.join(viewDirectory, "Frames")
                viewCameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt")

                combIterFinal = os.path.join(viewDirectory, "Recover/Combine/Iter/Iter_final")
                combDiffWeight = os.path.join(combIterFinal, "Base_diffuse/weight.pfm")
                combNrm = os.path.join(combIterFinal, "nrmR.pfm")
                combNrmDMsk = os.path.join(combIterFinal, "nrmDMsk.pfm")

                nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesBase")
                refineNrmR = os.path.join(nrmRefineFramesDirectory, "nrmR.pfm")
                refineDiffWeight = os.path.join(nrmRefineFramesDirectory, "Base_diffuse/weight.pfm")

                if MVSSweepOption == 2:
                    viewRGBImgFile = os.path.join(framesDirectory, "diff.pfm")
                    viewNrmImgFile = os.path.join(framesDirectory, "nrm.pfm")
                    modelName = "gt_"
                    recoverDirName = "gt_"

                if MVSSweepOption == 1:
                    viewRGBImgFile = combDiffWeight
                    viewNrmImgFile = combNrm
                    modelName = "re_"
                    recoverDirName = "re_"

                if MVSSweepOption == 3:
                    viewRGBImgFile = combDiffWeight
                    viewNrmImgFile = combNrm
                    modelName = "re_"
                    recoverDirName = "re_"

                if MVSSweepOption == 4:
                    viewRGBImgFile = combDiffWeight
                    viewNrmImgFile = refineNrmR
                    modelName = "refine_"
                    recoverDirName = "refine_"

                if MVSSweepOption == 5:
                    viewRGBImgFile = combDiffWeight
                    viewNrmImgFile = refineNrmR
                    modelName = "refine_"
                    recoverDirName = "refineNrBasesIter(WithTH)_"

                rgbWeight = "1"
                nrmWeight = "1"
                dptWeight = "1"
                minDepth = "1.1"
                maxDepth = "1.3"
                nNeighbors = "6"
                nSteps = "1001"
                nRefineIters = "2"
                nRefineSteps = "9"
                nDptIters = "1"
                nFirstKNeighborsForCost = "2"
                fDistTH = "0.01"
                nMetricLabel = "1"
                checkW = "172"
                checkH = "283"

                # modelName = modelName + "rgbWeight="+rgbWeight+"_nrmWeight="+nrmWeight+"_dptWeight="\
                #                  +dptWeight+"_fDistTH="+fDistTH + "_nDptIters="+nDptIters
                recoverDirName = recoverDirName + "rgbWeight=" + rgbWeight + "_nrmWeight=" + nrmWeight + "_dptWeight=" \
                                 + dptWeight + "_fDistTH=" + fDistTH + "_nDptIters=" + nDptIters

                outputDir = os.path.join(combIterFinal, recoverDirName)
                viewDistImgFile = os.path.join(outputDir, "distR.pfm")
                viewDepthImgFile = os.path.join(outputDir, "depthR.pfm")

                viewMaskImgFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")
                viewThMaskImgFile = os.path.join(viewDirectory, "Recover/Mirror/thMsk.pfm")
                # viewMaskImgFile = os.path.join(combIterFinal, "nrmDMsk.pfm")
                # viewMaskImgFile = os.path.join(combIterFinal, "specMsk.pfm")
                # viewMaskImgFile=$combIterFinal/nrmDMsk.pfm
                # modelName = "model" + "RecWithoutDepthConstraintO2NCC"

                # Sweep
                if RGBNPlaneSweepMVSOption:
                    logger.info("RGBNPlaneSweepMVS")
                    re = subprocess.run(
                        ["RGBNPlaneSweepMVS", "-cameraConfig=" + cameraConfig, "-poseConfig=" + poseConfig,
                         "-cameraExtrin=" + viewCameraExtrinsic,
                         "-viewFramesDirectory=" + outputDir, "-viewRGBImgFile=" + viewRGBImgFile,
                         "-viewNrmImgFile=" + viewNrmImgFile, "-viewDistImgFile=" + viewDistImgFile,
                         "-viewDepthImgFile=" + viewDepthImgFile,
                         "-viewMaskImgFile=" + viewMaskImgFile,
                         # "-viewMaskImgFile=" + viewThMaskImgFile,
                         "-viewThMaskImgFile=" + viewThMaskImgFile,
                         "-modelName=" + modelName, "-rgbWeight=" + rgbWeight, "-nrmWeight=" + nrmWeight,
                         "-dptWeight=" + dptWeight, "-nDptIters=" + nDptIters,
                         "-minDepth=" + minDepth, "-maxDepth=" + maxDepth, "-nNeighbors=" + nNeighbors,
                         "-nSteps=" + nSteps, "-nRefineIters=" + nRefineIters, "-nRefineSteps=" + nRefineSteps,
                         "-nFirstKNeighborsForCost=" + nFirstKNeighborsForCost, "-nViews=" + nViews,
                         "-checkW=" + checkW, "-checkH=" + checkH, "-checkOption",
                         "-bDistTHLabel",
                         "-fDistTH=" + fDistTH, "-nMetricLabel=" + nMetricLabel, "-flipZ", "-GPUOption",
                         "-viewScale=" + viewScale, "-realOption"], stdout=True, stderr=True, check=True)

            finally:
                os.environ.clear()
                os.environ.update(_environ)

            CombineAllViewOption = 0
            PoissonEachViewOption = 0

            meshCom = trimesh.base.Trimesh()  # combine all views's meshes.
            meshComF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName, "Comb_{0}.txt".format(modelName))
            meshComObjF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName, "Comb_{0}.obj".format(modelName))
            meshComReconF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName,
                                         "Recon_{0}.ply".format(modelName))
            meshComReconTrimF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName,
                                             "Trim_{0}.ply".format(modelName))
            meshComReconTrimFObj = os.path.join(OBJECT_ROOT, r"Recover\Model", "Final",
                                                "Recover.obj")

            meshComFDir = os.path.dirname(meshComF)
            logger.info("Start")
            if not os.path.exists(meshComFDir):
                os.makedirs(meshComFDir)
            if not os.path.exists(meshComReconTrimFObj):
                os.makedirs(meshComReconTrimFObj)
            _environ = dict(os.environ)
            try:
                if 'PATH' in _environ:
                    os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT
                else:
                    os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT
                if CombineAllViewOption:
                    for v in range(nViewsCount):
                        viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
                        combIterFinal = os.path.join(viewDirectory, "Recover", "Combine", "Iter", "Iter_final")
                        outputDir = os.path.join(combIterFinal, recoverDirName)

                        modelObjF = os.path.join(outputDir, "{0}.obj".format(modelName))
                        modelPlyF = os.path.join(outputDir, "{0}_%04d.ply".format(modelName) % v)
                        modelReconF = os.path.join(outputDir, "{0}Recon_%04d.ply".format(modelName) % v)
                        modelReconTrimF = os.path.join(outputDir, "{0}ReconTrim_%04d.ply".format(modelName) % v)
                        logger.info("PossionRecon view: {0}th".format(v))
                        if PoissonEachViewOption:
                            obj2ply(modelObjF, modelPlyF)
                            # Poisson reconstruction
                            re = subprocess.run(["PoissonRecon.exe", "--in", modelPlyF, "--out", modelReconF,
                                                 "--density"], stdout=True, stderr=True, check=True)
                            # Trim surface
                            re = subprocess.run(
                                ["SurfaceTrimmer.exe", "--in", modelReconF, "--out", modelReconTrimF, "--trim", "7"],
                                stdout=True, stderr=True, check=True)
                            # mesh = trimesh.load(modelReconTrimF)
                            # mesh = trimesh.load(modelPlyF)
                        mesh = trimesh.load(modelObjF)
                        if v == 0:
                            vertices = mesh.vertices
                            vertexNrms = mesh.vertex_normals
                        else:
                            vertices = np.concatenate((vertices, mesh.vertices), axis=0)
                            vertexNrms = np.concatenate((vertexNrms, mesh.vertex_normals), axis=0)
                        meshCom = trimesh.util.concatenate(meshCom, mesh)
                        # save combined mesh
                        # meshCom.vertices = vertices
                        # meshCom.vertex_normals = vertexNrms
                    pointCloud = np.concatenate((vertices, vertexNrms), axis=1)
                    np.savetxt(meshComF, pointCloud, delimiter=" ")
                    # meshCom = trimesh.base.Trimesh(vertices=vertices)
                    ex.export_mesh(meshCom, meshComObjF, include_normals=True)
                    # obj2ply(meshComObjF,meshComF)
                    # ex.export_mesh(meshCom, meshComF, encoding='ascii', vertex_normal=True)

                    # poisson reconstruct combined mesh
                re = subprocess.run(
                    ["PoissonRecon.exe", "--in", meshComF, "--out", meshComReconF, "--normals", "--pointWeight", "0",
                     "--depth",
                     "11", "--density", "--threads", "2","--samplesPerNode", "5"], stdout=True, stderr=True, check=True)
                # trim combined mesh
                re = subprocess.run(
                    ["SurfaceTrimmer.exe", "--in", meshComReconF, "--out", meshComReconTrimF, "--trim", "6"],
                    stdout=True, stderr=True, check=True)
                ply2obj(meshComReconTrimF, meshComReconTrimFObj)
            finally:
                os.environ.clear()
                os.environ.update(_environ)

    if FinalMeshOpt:
        CapSimOption = 1
        CapNrmCombine = 1

        texWidth="1024"
        texHeight="1024"

        _environ = dict(os.environ)
        try:
            if 'PATH' in _environ:
                os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT
            else:
                os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT

            reModel = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "Recover.obj")
            reModelR = os.path.join(OBJECT_ROOT, r"Recover\Model\FInal", "RecoverR.obj")
            reModelUV = os.path.join(OBJECT_ROOT, r"Recover\Model\FInal", "RecoverUV.obj")

            # remove degenerated faces
            rmBadFace(reModel, reModelR)
            # UVAtlas parameterization
            re = subprocess.run(
                ["UVAtlas","-y","-o",reModelUV,reModelR],
                stdout=True, stderr=True, check=True)

            if CapSimOption:
                logger.info("Project recovered model into each view:")
                for v in range(startView, nViewsCount):
                    logger.info("Dealing view: {0}th".format(v))
                    modelFile = reModelUV

                    viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
                    framesDirectory = os.path.join(viewDirectory, "Frames")

                    nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                    nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesMeshOpt")

                    cameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt" % v)
                    renderOption = "2"
                    re = subprocess.run(
                        ["CapSim", "-framesDirectory=" + nrmRefineFramesDirectory, "-modelFile=" + modelFile,
                         "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                         "-viewScale=" + viewScale, "-flipZ",
                         "-renderOption=" + renderOption],
                        stdout=True, stderr=True, check=True)

            if CapNrmCombine:
                # combine all views' nrm into uv texture
                logger.info("CapNrmCombine: combine into texture space ")
                viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")

                framesDirectory = os.path.join(viewDirectory, "Frames")
                nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesMeshOpt")

                viewRecNrmDir = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-pig2\Views\View_%04d\Recover\Combine\Iter\Iter_final\refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.005_nDptIters=1"
                viewDistImgFile = os.path.join(viewRecNrmDir, "distR.pfm")
                viewNrmImgFile = os.path.join(viewRecNrmDir, "nrmObj.pfm")
                viewMaskImgFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")
                viewTexCoordImgFile = os.path.join(nrmRefineFramesDirectory, "tex.pfm")

                textureImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "NrmTex.pfm")

                reModelUpt = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverUpdate.obj")
                reModelUptPly = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverUpdate.ply")
                reModelFinal = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverFinal.ply")

                re = subprocess.run(
                    ["CapNrmCombine",
                     "-viewNrmImgFile=" + viewNrmImgFile, "-viewDistImgFile=" + viewDistImgFile,
                     "-viewTexCoordImgFile=" + viewTexCoordImgFile, "-textureImgFile=" + textureImgFile,
                     "-viewMaskImgFile=" + viewMaskImgFile, "-nViews=" + nViews, "-width=" + texWidth,
                     "-height=" + texHeight,
                     "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ"
                     ], stdout=True, stderr=True, check=True)

                obj2ply(reModelUpt, reModelUptPly)

                re = subprocess.run(
                    ["mesh_opt",
                     reModelUptPly, reModelFinal], stdout=True, stderr=True, check=True)
        finally:
            os.environ.clear()
            os.environ.update(_environ)
