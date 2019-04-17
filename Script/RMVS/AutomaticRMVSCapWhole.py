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
    nrmRefRecDirName = "refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.1_nDptIters=1"

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
                    createTime = os.path.getmtime(signFile)
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
            CapParseCurOption = 1
            CapNrDiffOption = 1
            CapNrSpecOption = 1
            CapRefineNrBasesDiffOption = 1
            CapRefineNrBasesSpecOption = 1
            CapCombineOption = 1
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
                                         "-hWidth=" + hWidth, "-positionStr=" + positionStr, "--saveCurve", "--saveCSV",
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
                phiSize = "4"
                nIter = "2"
                thetaSize = "6"
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
                phiSize = "4"
                nIter = "2"
                thetaSize = "6"
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
                         "--recordIter"],
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
                createTime = os.path.getmtime(signFile)
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
        CleanPointCloudOption = 0

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

            combDir = os.path.join(viewDirectory, "Recover/Combine")
            combIterFinal = os.path.join(viewDirectory, "Recover/Combine/Iter/Iter_final")
            combDiffWeight = os.path.join(combIterFinal, "Base_diffuse/weight.pfm")
            combNrm = os.path.join(combIterFinal, "nrmR.pfm")

            viewRGBImgFile = combDiffWeight
            viewNrmImgFile = combNrm
            modelName = "re_" + OBJECT
            recoverDirName = "re_Th_"

            rgbWeight = "0.1"
            nrmWeight = "1"
            dptWeight = "1"
            minDepth = "1.1"
            maxDepth = "1.3"
            nNeighbors = "4"
            nSteps = "1001"
            nRefineIters = "3"
            nRefineSteps = "9"
            nDptIters = "1"
            nFirstKNeighborsForCost = "2"

            fDistTH = "0.5"
            nMetricLabel = "1"

            recoverDirName = recoverDirName + "rgbWeight=" + rgbWeight + "_nrmWeight=" + nrmWeight + "_dptWeight=" \
                             + dptWeight + "_fDistTH=" + fDistTH + "_nDptIters=" + nDptIters

            outputDir = os.path.join(combDir, recoverDirName)
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
            recoverDir = os.path.join(OBJECT_ROOT, r"Recover\Model\Combine", recoverDirName)
            meshComF = os.path.join(OBJECT_ROOT, recoverDir, "Comb_{0}.txt".format(modelName))
            meshComObjF = os.path.join(OBJECT_ROOT, recoverDir, "Comb_{0}.obj".format(modelName))
            meshComReconF = os.path.join(OBJECT_ROOT, recoverDir, "Recon_{0}.ply".format(modelName))
            meshComReconTrimF = os.path.join(OBJECT_ROOT, recoverDir,"Trim_{0}.ply".format(modelName))
            meshComReconTrimFUp = os.path.join(OBJECT_ROOT, r"Recover\Model\Combine", recoverDirName,
                                             "Trim_{0}Upt.ply".format(modelName))
            meshComReconTrimFObj = os.path.join(OBJECT_ROOT, recoverDir, "Recover.obj")
            meshCombineDir = os.path.join(OBJECT_ROOT, r"Recover\Model", "Combine")
            meshCombineDirObj = os.path.join(OBJECT_ROOT, r"Recover\Model", "Combine","Recover.obj")

            meshComFDir = os.path.dirname(meshComF)
            logger.info("Start combine all views' mesh")
            if not os.path.exists(meshComFDir):
                os.makedirs(meshComFDir)
            _environ = dict(os.environ)

            if CombineAllViewOption:
                for v in range(nViewsCount):
                    viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
                    combDir = os.path.join(viewDirectory, "Recover", "Combine")
                    outputDir = os.path.join(combDir, recoverDirName)

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
                    # Trimesh util bug for concatenate
                    # if v==0:
                    #     meshCom = trimesh.util.concatenate(mesh)
                    # else:
                    #     meshCom = trimesh.util.concatenate(meshCom, mesh)
                pointCloud = np.concatenate((vertices, vertexNrms), axis=1)
                np.savetxt(meshComF, pointCloud, delimiter=" ")
                # meshCom = trimesh.base.Trimesh(vertices = vertices)
                # meshCom = trimesh.Trimesh(vertices,None,None,vertexNrms)
                # meshCom.export(meshComObjF, include_normals=True)
                # obj2ply(meshComObjF,meshComF)
                # ex.export_mesh(meshCom, meshComF, encoding='ascii', vertex_normal=True)

                # combine all point
                viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
                nrmCombDirectory = os.path.join(viewDirectory, "Recover/Combine")
                outputDir = os.path.join(nrmCombDirectory, recoverDirName)
                modelObjVF = os.path.join(outputDir, "{0}.obj".format(modelName))
                re = subprocess.run(
                    ["ModelComb", "-srcModelFile=" + modelObjVF, "-tarModelFile=" + meshComObjF, "-nViews=" + nViews],
                    stdout=True, stderr=True, check=True)

                # poisson reconstruct combined mesh
                re = subprocess.run(
                    ["PoissonRecon.exe", "--in", meshComF, "--out", meshComReconF, "--normals", "--depth", "10",
                     "--samplesPerNode", "15" ,"--pointWeight", "0",
                     "--density", "--threads", "2"], stdout=True, stderr=True, check=True)
                # trim combined mesh
                re = subprocess.run(
                    ["SurfaceTrimmer.exe", "--in", meshComReconF, "--out", meshComReconTrimF, "--trim", "6"],
                    stdout=True, stderr=True, check=True)

                re = subprocess.run(
                    ["mesh_opt", meshComReconTrimF, "norm:"+ meshComReconTrimFUp], stdout=True, stderr=True, check=True)
                ply2obj(meshComReconTrimFUp, meshComReconTrimFObj)
                ply2obj(meshComReconTrimFUp, meshCombineDirObj)

            if CleanPointCloudOption:
                logger.info("Clean point cloud ")

                CapMultiSimOption = 1
                CapDilateMaskOption = 1
                CapCleanOption = 1
                clean_nIters = 1
                firstRecModel = meshComReconTrimFObj
                firstCombModel = meshComObjF
                # each view: format string
                viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
                nrmCombDirectory = os.path.join(viewDirectory, "Recover/Combine")
                outputDir = os.path.join(nrmCombDirectory, recoverDirName)
                # combined
                for iter in range(clean_nIters):
                    logger.info("Iter: {} ".format(iter) )
                    viewIterDir = os.path.join(outputDir,"Iter_Clean","Iter_%04d" % iter)
                    viewIterFramesDir = os.path.join(viewIterDir, "Frames")
                    iterDir = os.path.join(recoverDir,"Iter_Clean")
                    cleanModel = os.path.join(iterDir,"Iter_%04d_clean.obj")
                    cleanModelPly = os.path.join(iterDir, "Iter_%04d_clean.ply")
                    poissonModel = os.path.join(iterDir,"Iter_%04d_poi.ply")
                    trimModel = os.path.join(iterDir,"Iter_%04d_trim.ply")
                    recModel = os.path.join(iterDir,"Iter_%04d_rec.obj")
                    preModel = recModel % (iter-1)
                    preComModel = cleanModel % (iter -1)
                    if iter == 0:
                        preModel = firstRecModel
                        preComModel = firstCombModel
                    logger.info("CapMultiSim ")
                    if CapMultiSimOption:
                        cameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt")
                        renderOption = "2"
                        re = subprocess.run(
                            ["CapMultiSim", "-framesDirectory=" + viewIterFramesDir, "-modelFile=" + preModel,
                             "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                             "-viewScale=" + viewScale, "-flipZ",
                             "-renderOption=" + renderOption,"-nViews="+nViews],
                            stdout=True, stderr=True, check=True)
                    logger.info("Dilate mask ")
                    if CapDilateMaskOption:
                        # dilate masks
                        for v in range(nViewsCount):
                            nDil = "30"
                            inputFile = os.path.join(viewIterFramesDir % v, "mask.pfm")
                            outputFile = os.path.join(viewIterFramesDir % v, "mask_dil.pfm")
                            re = subprocess.run(
                                ["ImgDilator", "-in=" + inputFile, "-out=" + outputFile, "-n="+nDil], stdout=True, stderr=True,
                                check=True)
                    logger.info("Clean outliers ")
                    if CapCleanOption:
                        cameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt")
                        viewMaskImgFile = os.path.join(viewIterFramesDir, "mask_dil.pfm")
                        srcModel = preComModel
                        tarModel = cleanModel % iter
                        re = subprocess.run(
                            ["CapCleanPointCloud", "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                             "-viewMaskImgFile=" + viewMaskImgFile,
                             "-srcModelFile=" + srcModel, "-tarModelFile=" + tarModel,
                             "-viewScale=" + viewScale, "-flipZ", "-nViews=" + nViews],
                            stdout=True, stderr=True, check=True)
                        # poisson reconstruct combined mesh

                    modelInP = cleanModelPly % iter
                    modelOutP = poissonModel % iter
                    obj2ply(cleanModel % iter,modelInP)
                    re = subprocess.run(
                        ["PoissonRecon.exe", "--in", modelInP, "--out", modelOutP, "--normals",
                         "--pointWeight", "0",
                         "--depth",
                         "11", "--density", "--threads", "2", "--samplesPerNode", "5"], stdout=True,
                        stderr=True, check=True)
                    # trim combined mesh
                    modelInT = modelOutP
                    modelOutT = trimModel % iter
                    re = subprocess.run(
                        ["SurfaceTrimmer.exe", "--in", modelInT, "--out", modelOutT, "--trim",
                         "4"],
                        stdout=True, stderr=True, check=True)
                    ply2obj(modelOutT, recModel % iter)
                shutil.move(recModel % (clean_nIters - 1), meshCombineDirObj)

        finally:
            os.environ.clear()
            os.environ.update(_environ)

    if SecondRefineNrmOption:
        logger.info("Third Part: refine nrm ")
        CapSimOption = 1
        CapDilateMaskOption = 1
        CapRefineNrBasesOption = 1
        # parse curves from projected mask.
        CapParseCurOption = 1
        CapSpecPeakMask = 1

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

                nrmRefineItersDirectory = os.path.join(nrmRefineDirectory, "Iter", "Iter_%04d")
                nrmRefineIterFinalDir = os.path.join(nrmRefineDirectory, "Iter", "Iter_final")

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

                # output refinement weight files
                refineNrmRouWeight = os.path.join(nrmRefineIterFinalDir, r"Base_r_%.5f/weight.pfm")
                refineNrmDiffWeight = os.path.join(nrmRefineIterFinalDir, r"Base_diffuse/weight.pfm")
                if CapRefineNrBasesOption:
                    logger.info("CapRefineNrBases view: {0}th".format(v))
                    re = subprocess.run(
                        ["CapRefineNrBases", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
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

    if SecondMVSOption:
        # Forth part RefineNrBases
        logger.info("Forth Part: MVS ")

        MVSSweepOption = 5
        RGBNPlaneSweepMVSOption = 1

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

            nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
            nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesCombine")
            nrmRefineIterFinalDir = os.path.join(nrmRefineDirectory, "Iter", "Iter_final")
            refineNrmR = os.path.join(nrmRefineIterFinalDir, "nrmR.pfm")
            refineDiffWeight = os.path.join(nrmRefineIterFinalDir, "Base_diffuse/weight.pfm")

            if MVSSweepOption == 5:
                viewRGBImgFile = refineDiffWeight
                viewNrmImgFile = refineNrmR
                modelName = "refine_"
                recoverDirName = "refineNrBasesIter(WithTH)_"

            rgbWeight = "1"
            nrmWeight = "10"
            dptWeight = "10"
            minDepth = "1.1"
            maxDepth = "1.3"
            nNeighbors = "8"
            nSteps = "200"
            nRefineIters = "1"
            nRefineSteps = "10"
            nDptIters = "2"
            nFirstKNeighborsForCost = "3"
            fDistTH = "1"
            nMetricLabel = "1"
            checkW = "174"
            checkH = "18"

            # modelName = modelName + "rgbWeight="+rgbWeight+"_nrmWeight="+nrmWeight+"_dptWeight="\
            #                  +dptWeight+"_fDistTH="+fDistTH + "_nDptIters="+nDptIters
            recoverDirName = recoverDirName + "rgbWeight=" + rgbWeight + "_nrmWeight=" + nrmWeight + "_dptWeight=" \
                             + dptWeight + "_fDistTH=" + fDistTH + "_nDptIters=" + nDptIters
            nrmRefRecDirName = recoverDirName

            outputDir = os.path.join(nrmRefineDirectory, recoverDirName)
            viewDistImgFile = os.path.join(outputDir, "distR.pfm")
            viewDepthImgFile = os.path.join(outputDir, "depthR.pfm")

            viewMaskImgFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")
            viewMaskDilImgFile = os.path.join(nrmRefineFramesDirectory, "mask_dil.pfm")
            viewMaskSpecPeakImgFile = os.path.join(nrmRefineIterFinalDir, "specNicePeakMask.pfm")
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
                     # "-viewMaskImgFile=" + viewMaskImgFile,
                     "-viewMaskImgFile=" + viewMaskDilImgFile,
                     # "-viewMaskImgFile=" + viewMaskSpecPeakImgFile,
                     # "-viewMaskImgFile=" + viewThMaskImgFile,
                     # "-viewThMaskImgFile=" + viewMaskSpecPeakImgFile,
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

        CombineAllViewOption = 1
        PoissonEachViewOption = 0
        CleanPointCloudOption = 1

        meshCom = trimesh.base.Trimesh()  # combine all views's meshes.
        recoverDir = os.path.join(OBJECT_ROOT, r"Recover\Model\NrmRefine", recoverDirName)
        meshComF = os.path.join(recoverDir, "Comb_{0}.txt".format(modelName))
        meshComObjF = os.path.join(recoverDir, "Comb_{0}.obj".format(modelName))
        meshComReconF = os.path.join(recoverDir,"Recon_{0}.ply".format(modelName))
        meshComReconTrimF = os.path.join(recoverDir,"Trim_{0}.ply".format(modelName))
        meshComReconTrimFObj = os.path.join(OBJECT_ROOT, recoverDir,"Recover.obj")

        meshFinalDir = os.path.join(OBJECT_ROOT, r"Recover\Model", "Final")
        meshFinalDirObj = os.path.join(OBJECT_ROOT, r"Recover\Model", "Final",
                                            "Recover.obj")
        # shutil.move(meshComReconTrimFObj,meshFinalDirObj)

        meshComFDir = os.path.dirname(meshComF)
        logger.info("Start")
        if not os.path.exists(meshComFDir):
            os.makedirs(meshComFDir)
        if not os.path.exists(meshFinalDir):
            os.makedirs(meshFinalDir)
        _environ = dict(os.environ)
        try:
            if 'PATH' in _environ:
                os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT
            else:
                os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT
            if CombineAllViewOption:
                meshCom = trimesh.Trimesh()
                for v in range(nViewsCount):
                    viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
                    nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                    outputDir = os.path.join(nrmRefineDirectory, recoverDirName)

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
                # meshCom = trimesh.Trimesh(vertices,None,None,vertexNrms)
                # meshCom.export(meshComObjF, include_normals=True)
                # obj2ply(meshComObjF,meshComF)
                # ex.export_mesh(meshCom, meshComF, encoding='ascii', vertex_normal=True)

                # combine all point
                viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
                nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                outputDir = os.path.join(nrmRefineDirectory, recoverDirName)
                modelObjVF = os.path.join(outputDir, "{0}.obj".format(modelName))
                re = subprocess.run(
                    ["ModelComb", "-srcModelFile=" + modelObjVF, "-tarModelFile=" + meshComObjF, "-nViews=" + nViews],
                    stdout=True, stderr=True, check=True)

                # poisson reconstruct combined mesh

                re = subprocess.run(
                    ["PoissonRecon.exe", "--in", meshComF, "--out", meshComReconF, "--normals", "--pointWeight", "0",
                     "--depth",
                     "10", "--density", "--threads", "2","--samplesPerNode", "15"], stdout=True, stderr=True, check=True)
                # trim combined mesh
                re = subprocess.run(
                    ["SurfaceTrimmer.exe", "--in", meshComReconF, "--out", meshComReconTrimF, "--trim", "6"],
                    stdout=True, stderr=True, check=True)
                ply2obj(meshComReconTrimF, meshComReconTrimFObj)

            if CleanPointCloudOption:
                logger.info("Clean point cloud ")

                CapMultiSimOption = 1
                CapDilateMaskOption = 1
                CapCleanOption = 1
                clean_nIters = 2
                firstRecModel = meshComReconTrimFObj
                firstCombModel = meshComObjF
                # each view: format string
                viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
                nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                outputDir = os.path.join(nrmRefineDirectory, recoverDirName)
                # combined
                for iter in range(clean_nIters):
                    logger.info("Iter: {} ".format(iter) )
                    viewIterDir = os.path.join(outputDir,"Iter_Clean","Iter_%04d" % iter)
                    viewIterFramesDir = os.path.join(viewIterDir, "Frames")
                    iterDir = os.path.join(recoverDir,"Iter_Clean")
                    cleanModel = os.path.join(iterDir,"Iter_%04d_clean.obj")
                    cleanModelPly = os.path.join(iterDir, "Iter_%04d_clean.ply")
                    poissonModel = os.path.join(iterDir,"Iter_%04d_poi.ply")
                    trimModel = os.path.join(iterDir,"Iter_%04d_trim.ply")
                    recModel = os.path.join(iterDir,"Iter_%04d_rec.obj")
                    preModel = recModel % (iter-1)
                    preComModel = cleanModel % (iter -1)
                    if iter == 0:
                        preModel = firstRecModel
                        preComModel = firstCombModel
                    logger.info("CapMultiSim ")
                    if CapMultiSimOption:
                        cameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt")
                        renderOption = "2"
                        re = subprocess.run(
                            ["CapMultiSim", "-framesDirectory=" + viewIterFramesDir, "-modelFile=" + preModel,
                             "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                             "-viewScale=" + viewScale, "-flipZ",
                             "-renderOption=" + renderOption,"-nViews="+nViews],
                            stdout=True, stderr=True, check=True)
                    logger.info("Dilate mask ")
                    if CapDilateMaskOption:
                        # dilate masks
                        for v in range(nViewsCount):
                            nDil = "10"
                            inputFile = os.path.join(viewIterFramesDir % v, "mask.pfm")
                            outputFile = os.path.join(viewIterFramesDir % v, "mask_dil.pfm")
                            re = subprocess.run(
                                ["ImgDilator", "-in=" + inputFile, "-out=" + outputFile, "-n="+nDil], stdout=True, stderr=True,
                                check=True)
                    logger.info("Clean outliers ")
                    if CapCleanOption:
                        cameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt")
                        viewMaskImgFile = os.path.join(viewIterFramesDir, "mask_dil.pfm")
                        srcModel = preComModel
                        tarModel = cleanModel % iter
                        re = subprocess.run(
                            ["CapCleanPointCloud", "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                             "-viewMaskImgFile=" + viewMaskImgFile,
                             "-srcModelFile=" + srcModel, "-tarModelFile=" + tarModel,
                             "-viewScale=" + viewScale, "-flipZ", "-nViews=" + nViews],
                            stdout=True, stderr=True, check=True)
                        # poisson reconstruct combined mesh

                    modelInP = cleanModelPly % iter
                    modelOutP = poissonModel % iter
                    obj2ply(cleanModel % iter,modelInP)
                    re = subprocess.run(
                        ["PoissonRecon.exe", "--in", modelInP, "--out", modelOutP, "--normals",
                         "--pointWeight","0",
                         "--depth",
                         "10", "--density", "--threads", "2", "--samplesPerNode", "5"], stdout=True,
                        stderr=True, check=True)
                    # trim combined mesh
                    modelInT = modelOutP
                    modelOutT = trimModel % iter
                    re = subprocess.run(
                        ["SurfaceTrimmer.exe", "--in", modelInT, "--out", modelOutT, "--trim",
                         "4"],
                        stdout=True, stderr=True, check=True)
                    ply2obj(modelOutT, recModel % iter)


                shutil.move(recModel  % (clean_nIters - 1), meshFinalDirObj)

        finally:
            os.environ.clear()
            os.environ.update(_environ)

    if FinalMeshOpt:
        MeshOpt = 1
        MeshOptPreprocess = 1
        MeshOptCapNrmCombine = 1
        MeshOptSecond = 1
        MeshOptSecondPreprocess = 1
        MeshOptSecondCapNrmCombine = 1
        FitRouOption = 1
        texWidth="1024"
        texHeight="1024"
        edgeLength = "0.0005"
        meshOpt_nIter = 2

        # MODEL_ROOT = os.path.join(OBJECT_ROOT, r"Recover\Model")
        # MeshOptIter = os.path.join(OBJECT_ROOT, r"Recover\Model","MeshOpt")
        _environ = dict(os.environ)
        try:
            if 'PATH' in _environ:
                os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT +";" + TOOL_LCT_ROOT
            else:
                os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT + ";" + TOOL_LCT_ROOT

            if MeshOpt:
                logger.info("Meah opt:")

                # each view: format string
                viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
                nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                viewMeshOptDir = os.path.join(nrmRefineDirectory, "FramesMeshOpt")

                # recovered model dir:
                meshFinalDir = os.path.join(OBJECT_ROOT, r"Recover\Model\Final")
                iterDir = os.path.join(meshFinalDir, "Iter_MeshOpt")
                firstModel = os.path.join(meshFinalDir, "Recover.obj")
                finalIterModel = os.path.join(meshFinalDir, "RecoverFinal.obj")
                lastIterModel = os.path.join(iterDir, "Iter_%04d_RecoverFinal.obj" % (meshOpt_nIter - 1))

                if not os.path.exists(iterDir):
                    os.makedirs(iterDir)

                for iter in range(meshOpt_nIter):
                    logger.info("Mesh opt iter {}".format(iter))
                    viewIterDir = os.path.join(viewMeshOptDir, "Iter_%04d" % iter)
                    viewIterFramesDir = os.path.join(viewIterDir, "Frames")

                    reModel = os.path.join(iterDir,"Iter_%04d_RecoverFinal.obj" % (iter - 1))
                    reModelR = os.path.join(iterDir, "Iter_%04d_RecoverR.obj"% iter)
                    reModelUV = os.path.join(iterDir, "Iter_%04d_RecoverUV.obj"% iter)
                    reModelUVR = os.path.join(iterDir, "Iter_%04d_RecoverUVR.obj"% iter)
                    reModelUpt = os.path.join(iterDir, "Iter_%04d_RecoverUpdate.obj"% iter)
                    reModelUptPly = os.path.join(iterDir, "Iter_%04d_RecoverUpdate.ply"% iter)
                    reModelFinal = os.path.join(iterDir, "Iter_%04d_RecoverFinal.ply"% iter)
                    reModelFinalObj = os.path.join(iterDir, "Iter_%04d_RecoverFinal.obj"% iter)
                    reModelFinalPoission = os.path.join(iterDir, "Iter_%04d_RecoverFinalPoission.ply"% iter)
                    reModelFinalTrim = os.path.join(iterDir, r"Iter_%04d_RecoverFinalTrim.ply"% iter)
                    reModelFinalPost = os.path.join(iterDir, "Iter_%04d_RecoverPostProcess.obj"% iter)
                    if(iter == 0):
                        reModel = firstModel
                    if MeshOptPreprocess:
                        logger.info("Preprocess model ")
                        # remove degenerated faces
                        # rmBadFace(reModel, reModelR)
                        mesh = trimesh.load(reModel)
                        mesh.remove_degenerate_faces()
                        # mesh = mesh.subdivide()
                        mesh.export(reModelR)

                        logger.info("Remesh model ")
                        re = subprocess.run(
                                ["LCT", "-i" , reModelR, "-o" , reModelR,"-l",edgeLength],
                                stdout=True, stderr=True, check=True)

                        logger.info("UVAtlas ")
                        # UVAtlas parameterization
                        re = subprocess.run(
                            ["UVAtlas", "-iv","TEXCOORD","-w",texWidth,"-h",texHeight,"-y", "-o", reModelUV, reModelR],
                            stdout=True, stderr=True, check=True)

                        logger.info("Project recovered model into each view:")

                        logger.info("CapMultiSim ")
                        CapMultiSimOption = 1
                        if CapMultiSimOption:
                            cameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt")
                            renderOption = "2"
                            re = subprocess.run(
                                ["CapMultiSim", "-framesDirectory=" + viewIterFramesDir, "-modelFile=" + reModelUV,
                                 "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                                 "-viewScale=" + viewScale, "-flipZ",
                                 "-renderOption=" + renderOption, "-nViews=" + nViews],
                                stdout=True, stderr=True, check=True)

                        # for v in range(startView, nViewsCount):
                        #     logger.info("Dealing view: {0}th".format(v))
                        #     modelFile = reModelUV
                        #
                        #     viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
                        #     framesDirectory = os.path.join(viewDirectory, "Frames")
                        #
                        #     nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                        #     nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesMeshOpt")
                        #
                        #     cameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt" % v)
                        #     renderOption = "2"
                        #     re = subprocess.run(
                        #         ["CapSim", "-framesDirectory=" + nrmRefineFramesDirectory, "-modelFile=" + modelFile,
                        #          "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                        #          "-viewScale=" + viewScale, "-flipZ",
                        #          "-renderOption=" + renderOption],
                        #         stdout=True, stderr=True, check=True)

                    if MeshOptCapNrmCombine:
                        # combine all views' nrm into uv texture
                        logger.info("CapTexCombine: combine into texture space ")
                        viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")

                        framesDirectory = os.path.join(viewDirectory, "Frames")
                        nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                        nrmRefineIterFinalDir = os.path.join(nrmRefineDirectory, "Iter", "Iter_final")
                        cameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt")

                        # viewRecNrmDir = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-pig2\Views\View_%04d\Recover\Combine\Iter\Iter_final\refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.01_nDptIters=1"
                        viewNrmRefineImgFile = os.path.join(nrmRefineIterFinalDir,r"nrmR.pfm") #in world space where nrm is estimated
                        # need to be changed
                        viewRecNrmDir = os.path.join(nrmRefineDirectory,nrmRefRecDirName)
                        viewDistImgFile = os.path.join(viewRecNrmDir, "distR.pfm")
                        viewNrmImgFile = os.path.join(viewRecNrmDir, "nrmObj.pfm")
                        viewMaskImgFile = os.path.join(viewIterFramesDir, "mask.pfm")
                        viewGeoNrmImgFile = os.path.join(viewIterFramesDir, "nrmObj.pfm")
                        viewTexCoordImgFile = os.path.join(viewIterFramesDir, "tex.pfm")
                        # viewMaskImgFile = os.path.join(nrmRefineIterFinalDir, "specNicePeakMask.pfm")

                        refineNrmRouWeight = os.path.join(nrmRefineIterFinalDir, r"Base_r_%.5f/weight.pfm")
                        refineNrmDiffWeight = os.path.join(nrmRefineIterFinalDir, r"Base_diffuse/weight.pfm")

                        texNrmImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "TexNrm.pfm")
                        texPosImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "TexPos.pfm")
                        texDiffImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", r"Base_diffuse/weight.pfm")
                        texSpecRouImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", r"Base_r_%.5f/weight.pfm")
                        texSpecFitImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "result_specular.pfm")
                        texRouFitImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "result_roughness_fitted.pfm")

                        re = subprocess.run(
                            ["CapTexCombine",
                             "-viewFramesDirectory=" + viewRecNrmDir,
                             "-viewNrmImgFile=" + viewNrmImgFile, "-viewGeoNrmImgFile=" + viewGeoNrmImgFile,"-viewDistImgFile=" + viewDistImgFile,
                             "-viewTexCoordImgFile=" + viewTexCoordImgFile,
                             "-viewDiffWeightFile=" + refineNrmDiffWeight, "-viewSpecRouWeightFile=" + refineNrmRouWeight,
                             "-genericRoughnesses=" + genericRoughnesses,
                             "-texNrmImgFile=" + texNrmImgFile,
                             "-texPosImgFile=" + texPosImgFile,
                             "-texDiffImgFile=" + texDiffImgFile,
                             "-texSpecRouImgFile=" + texSpecRouImgFile,
                             "-viewMaskImgFile=" + viewMaskImgFile, "-nViews=" + nViews, "-uvWidth=" + texWidth,
                             "-uvHeight=" + texHeight,
                             "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ", "--solveRou",
                             "-texSpecFitImgFile=" + texSpecFitImgFile, "-texRouFitImgFile=" + texRouFitImgFile,
                             "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                             "-viewScale=" + viewScale
                             ], stdout=True, stderr=True, check=True)

                        logger.info("Update normal")
                        re = subprocess.run(
                            ["CapUpdateNrm",
                             "-texNrmImgFile=" + texNrmImgFile,
                             "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ", "-merge"
                             ], stdout=True, stderr=True, check=True)

                        logger.info("Change obj into ply")
                        # mesh.export(plyFile, "ply", encoding='ascii', vertex_normal=True)
                        obj2ply(reModelUpt, reModelUptPly)

                        re = subprocess.run(
                            ["mesh_opt", reModelUptPly,"-lambda", "0.1", "norm:"+ reModelFinal], stdout=True, stderr=True, check=True)
                        ply2obj(reModelFinal,reModelFinalObj)

                        # re = subprocess.run(
                        #     ["PoissonRecon.exe", "--in", reModelFinal, "--out", reModelFinalPoission, "--normals", "--pointWeight",
                        #      "0",
                        #      "--depth",
                        #      "10", "--density", "--threads", "2"], stdout=True, stderr=True,
                        #     check=True)
                        # # trim combined mesh
                        # re = subprocess.run(
                        #     ["SurfaceTrimmer.exe", "--in", reModelFinalPoission, "--out", reModelFinalTrim, "--trim", "6"],
                        #     stdout=True, stderr=True, check=True)

                shutil.move(lastIterModel,finalIterModel)

            if MeshOptSecond:
                meshFinalOptDir = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt")
                if not os.path.exists(meshFinalOptDir):
                    os.makedirs(meshFinalOptDir)
                # when mesh_opt finished, combine all textures together using new uv
                reModel = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverFinal.obj")
                reModelR = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "RecoverR.obj")
                reModelUV = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "RecoverUV.obj")
                reModelUpt = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "RecoverUpdate.obj")
                reModelFinalObjFlip = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt\Object",
                                                   "RecoverFinalFlip.obj")

                texDiffImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", r"Base_diffuse/weight.pfm")
                texSpecRouImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", r"Base_r_%.5f/weight.pfm")
                texSpecFitImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "result_specular.pfm")
                texRouFitImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "result_roughness_fitted.pfm")

                if MeshOptSecondPreprocess:
                    logger.info("Preprocess model ")
                    # remove degenerated faces
                    rmBadFace(reModel, reModelR)

                    logger.info("Remesh model ")
                    re = subprocess.run(
                            ["LCT", "-i" , reModelR, "-o" , reModelR,"-l",edgeLength],
                            stdout=True, stderr=True, check=True)

                    logger.info("UVAtlas ")
                    # UVAtlas parameterization
                    re = subprocess.run(
                        ["UVAtlas", "-iv", "TEXCOORD", "-w", texWidth, "-h", texHeight, "-y", "-o", reModelUV,
                         reModelR],
                        stdout=True, stderr=True, check=True)

                    logger.info("Project recovered model into each view:")
                    CapMultiSimOption = 1
                    if CapMultiSimOption:
                        viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
                        nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                        nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesFinal")
                        cameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt")
                        renderOption = "2"
                        re = subprocess.run(
                            ["CapMultiSim", "-framesDirectory=" + nrmRefineFramesDirectory, "-modelFile=" + reModelUV,
                             "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                             "-viewScale=" + viewScale, "-flipZ",
                             "-renderOption=" + renderOption, "-nViews=" + nViews],
                            stdout=True, stderr=True, check=True)

                    # startView = 0
                    # for v in range(startView, nViewsCount):
                    #     logger.info("Dealing view: {0}th".format(v))
                    #     modelFile = reModelUV
                    #     viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
                    #     framesDirectory = os.path.join(viewDirectory, "Frames")
                    #
                    #     nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                    #     nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesFinal")
                    #
                    #     cameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt" % v)
                    #     renderOption = "2"
                    #     re = subprocess.run(
                    #         ["CapSim", "-framesDirectory=" + nrmRefineFramesDirectory, "-modelFile=" + modelFile,
                    #          "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                    #          "-viewScale=" + viewScale, "-flipZ",
                    #          "-renderOption=" + renderOption],
                    #         stdout=True, stderr=True, check=True)

                if MeshOptSecondCapNrmCombine:
                    # combine all views' nrm into uv texture
                    logger.info("CapTexCombine: combine into texture space ")
                    viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")

                    framesDirectory = os.path.join(viewDirectory, "Frames")
                    nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                    nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesFinal")
                    nrmRefineIterFinalDir = os.path.join(nrmRefineDirectory, "Iter", "Iter_final")
                    cameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt")

                    # viewRecNrmDir = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-pig2\Views\View_%04d\Recover\Combine\Iter\Iter_final\refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.01_nDptIters=1"
                    viewNrmRefineImgFile = os.path.join(nrmRefineIterFinalDir,r"nrmR.pfm")
                    viewRecNrmDir = os.path.join(nrmRefineDirectory, nrmRefRecDirName)
                    viewDistImgFile = os.path.join(viewRecNrmDir, "distR.pfm")
                    viewNrmImgFile = os.path.join(viewRecNrmDir, "nrmObj.pfm")
                    # viewMaskImgFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")
                    viewMaskImgFile = os.path.join(viewRecNrmDir, "maskR.pfm")
                    viewTexCoordImgFile = os.path.join(nrmRefineFramesDirectory, "tex.pfm")
                    viewGeoNrmImgFile = os.path.join(nrmRefineFramesDirectory, "nrmObj.pfm")
                    # viewMaskImgFile = os.path.join(nrmRefineIterFinalDir, "specNicePeakMask.pfm")

                    refineNrmRouWeight = os.path.join(nrmRefineIterFinalDir, r"Base_r_%.5f/weight.pfm")
                    refineNrmDiffWeight = os.path.join(nrmRefineIterFinalDir, r"Base_diffuse/weight.pfm")

                    texNrmImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "TexNrm.pfm")
                    texPosImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "TexPos.pfm")
                    texDiffImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", r"Base_diffuse/weight.pfm")
                    texSpecRouImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", r"Base_r_%.5f/weight.pfm")
                    texSpecFitImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "result_specular.pfm")
                    texRouFitImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "result_roughness_fitted.pfm")

                    reModelUpt = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "RecoverUpdate.obj")
                    reModelUptPly = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "RecoverUpdate.ply")
                    reModelFinal = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "RecoverFinal.ply")
                    reModelFinalObj = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "RecoverFinal.obj")


                    re = subprocess.run(
                        ["CapTexCombine",
                         "-viewFramesDirectory=" + viewRecNrmDir,
                         "-viewNrmImgFile=" + viewNrmImgFile,"-viewGeoNrmImgFile=" + viewGeoNrmImgFile,
                         "-viewDistImgFile=" + viewDistImgFile,
                         "-viewTexCoordImgFile=" + viewTexCoordImgFile,
                         "-viewDiffWeightFile=" + refineNrmDiffWeight, "-viewSpecRouWeightFile=" + refineNrmRouWeight,
                         "-genericRoughnesses=" + genericRoughnesses,
                         "-texNrmImgFile=" + texNrmImgFile,
                         "-texPosImgFile=" + texPosImgFile,
                         "-texDiffImgFile=" + texDiffImgFile,
                         "-texSpecRouImgFile=" + texSpecRouImgFile,
                         "-viewMaskImgFile=" + viewMaskImgFile, "-nViews=" + nViews, "-uvWidth=" + texWidth,
                         "-uvHeight=" + texHeight,
                         "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ", "--solveRou",
                         "-texSpecFitImgFile=" + texSpecFitImgFile, "-texRouFitImgFile=" + texRouFitImgFile,
                         "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                         "-viewScale=" + viewScale
                         ], stdout=True, stderr=True, check=True)

                    logger.info("Update normal")
                    re = subprocess.run(
                        ["CapUpdateNrm",
                         "-texNrmImgFile=" + texNrmImgFile,
                         "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ","--merge"
                         ], stdout=True, stderr=True, check=True)

                    # logger.info("Change obj into ply")
                    # # mesh.export(plyFile, "ply", encoding='ascii', vertex_normal=True)
                    # obj2ply(reModelUpt, reModelUptPly)
                    #
                    # re = subprocess.run(
                    #     ["mesh_opt", reModelUptPly, "norm:"+ reModelFinal], stdout=True, stderr=True, check=True)
                    # ply2obj(reModelFinal,reModelFinalObj)

                    # re = subprocess.run(
                    #     ["CapNrmCombine",
                    #      "-viewNrmImgFile=" + viewNrmImgFile, "-viewDistImgFile=" + viewDistImgFile,
                    #      "-viewTexCoordImgFile=" + viewTexCoordImgFile,
                    #      "-viewDiffWeightFile=" + refineNrmDiffWeight, "-viewSpecRouWeightFile=" + refineNrmRouWeight,
                    #      "-genericRoughnesses=" + genericRoughnesses,
                    #      "-texNrmImgFile=" + texNrmImgFile,
                    #      "-texDiffImgFile=" + texDiffImgFile,
                    #      "-texSpecRouImgFile=" + texSpecRouImgFile,
                    #      "-viewMaskImgFile=" + viewMaskImgFile, "-nViews=" + nViews, "-width=" + texWidth,
                    #      "-height=" + texHeight,
                    #      "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ", "-solveRou",
                    #      "-texSpecFitImgFile=" + texSpecFitImgFile, "-texRouFitImgFile=" + texRouFitImgFile
                    #      ], stdout=True, stderr=True, check=True)

                    re = subprocess.run(
                        ["CapBRDFCombine",
                         "-viewFramesDirectory=" + viewRecNrmDir,
                         "-viewNrmImgFile=" + viewGeoNrmImgFile, "-viewDistImgFile=" + viewDistImgFile,
                         "-viewTexCoordImgFile=" + viewTexCoordImgFile,
                         "-viewDiffWeightFile=" + refineNrmDiffWeight, "-viewSpecRouWeightFile=" + refineNrmRouWeight,
                         "-genericRoughnesses=" + genericRoughnesses,
                         "-texNrmImgFile=" + texNrmImgFile,
                         "-texPosImgFile=" + texPosImgFile,
                         "-texDiffImgFile=" + texDiffImgFile,
                         "-texSpecRouImgFile=" + texSpecRouImgFile,
                         "-viewMaskImgFile=" + viewMaskImgFile, "-nViews=" + nViews, "-uvWidth=" + texWidth,
                         "-uvHeight=" + texHeight,
                         "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ", "-solveRou",
                         "-texSpecFitImgFile=" + texSpecFitImgFile, "-texRouFitImgFile=" + texRouFitImgFile,
                         "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                         "-viewScale=" + viewScale
                         ], stdout=True, stderr=True, check=True)

                    if not os.path.exists(os.path.dirname(reModelFinalObjFlip)):
                        os.makedirs(os.path.dirname(reModelFinalObjFlip))

                if FitRouOption:
                    logger.info("Create model: ")
                    re = subprocess.run(
                        ["ModelTool",
                         "-srcModelFile=" + reModelUpt, "-tarModelFile=" + reModelFinalObjFlip, "-flipZ","--flipVC","-tarTex",
                         "-tarTexDiffFile=" + texDiffImgFile, "-tarTexSpecFile=" + texSpecFitImgFile, "-tarTexRouFile="+texRouFitImgFile
                         ], stdout=True, stderr=True, check=True)
                    logger.info("Dilate textures: ")
                    CapDilateTextureOption = 1
                    if CapDilateTextureOption:
                        # dilate texture
                        inputDir= os.path.dirname(reModelFinalObjFlip)
                        nDil = "2"
                        inputFile = os.path.join(inputDir, "result_diff.pfm")
                        outputFile = os.path.join(inputDir, "result_diff.pfm")
                        re = subprocess.run(
                            ["ImgDilator", "-in=" + inputFile, "-out=" + outputFile], stdout=True, stderr=True,
                            check=True)

                        inputFile = os.path.join(inputDir, "result_spec.pfm")
                        outputFile = os.path.join(inputDir, "result_spec.pfm")
                        re = subprocess.run(
                            ["ImgDilator", "-in=" + inputFile, "-out=" + outputFile], stdout=True, stderr=True,
                            check=True)

                        inputFile = os.path.join(inputDir, "result_roughness.pfm")
                        outputFile = os.path.join(inputDir, "result_roughness.pfm")
                        re = subprocess.run(
                            ["ImgDilator", "-in=" + inputFile, "-out=" + outputFile], stdout=True, stderr=True,
                            check=True)


        finally:
            os.environ.clear()
            os.environ.update(_environ)

    FinalBRDFOpt = 0
    if FinalBRDFOpt:
        CapSimOption = 0
        CapNrmCombine = 0
        FitRouOption = 0
        texWidth="1024"
        texHeight="1024"

        _environ = dict(os.environ)
        try:
            if 'PATH' in _environ:
                os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT +";" + TOOL_LCT_ROOT
            else:
                os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT + ";" + TOOL_LCT_ROOT

            FinalBRDFOptDirName = "FinalOpt2"
            if MeshOpt:
                reModel = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "Recover.obj")
                reModelR = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverR.obj")
                reModelUV = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverUV.obj")
                reModelUVR = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverUVR.obj")
                if MeshOptPreprocess:
                    logger.info("Preprocess model ")
                    # remove degenerated faces
                    # rmBadFace(reModel, reModelR)
                    mesh = trimesh.load(reModel)
                    mesh.remove_degenerate_faces()
                    # mesh = mesh.subdivide()
                    mesh.export(reModelR)

                    logger.info("Remesh model ")
                    edgeLength = "0.0001"
                    re = subprocess.run(
                            ["LCT", "-i" , reModelR, "-o" , reModelR,"-l",edgeLength],
                            stdout=True, stderr=True, check=True)
                    print(re)

                    # logger.info("UVAtlas ")
                    # # UVAtlas parameterization
                    # re = subprocess.run(
                    #     ["UVAtlas", "-iv","TEXCOORD","-w",texWidth,"-h",texHeight,"-t","-y", "-o", reModelUV, reModelR],
                    #     stdout=True, stderr=True, check=True)
                    # #
                    # # logger.info("Merge vertices separated by UVAtlas ")
                    # # # remove degenerated faces
                    # # # rmBadFace(reModel, reModelR)
                    #
                    # # mesh = trimesh.load(reModelUV,file_type="ply",resolver=None,include_texture=True)
                    # # mesh.merge_vertices()
                    # # mesh.remove_degenerate_faces()
                    # # # mesh = mesh.subdivide()
                    # # print(mesh.vertex_normals)
                    # # mesh.export(reModelUVR,encoding='ascii')
                    #
                    # logger.info("Project recovered model into each view:")
                    # for v in range(startView, nViewsCount):
                    #     logger.info("Dealing view: {0}th".format(v))
                    #     modelFile = reModelUV
                    #
                    #     viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
                    #     framesDirectory = os.path.join(viewDirectory, "Frames")
                    #
                    #     nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                    #     nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesMeshOpt")
                    #
                    #     cameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt" % v)
                    #     renderOption = "2"
                    #     re = subprocess.run(
                    #         ["CapSim", "-framesDirectory=" + nrmRefineFramesDirectory, "-modelFile=" + modelFile,
                    #          "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                    #          "-viewScale=" + viewScale, "-flipZ",
                    #          "-renderOption=" + renderOption],
                    #         stdout=True, stderr=True, check=True)

                if MeshOptCapNrmCombine:
                    # combine all views' nrm into uv texture
                    logger.info("CapTexCombine: combine into texture space ")
                    viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")

                    framesDirectory = os.path.join(viewDirectory, "Frames")
                    nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                    nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesMeshOpt")
                    nrmRefineIterFinalDir = os.path.join(nrmRefineDirectory, "Iter", "Iter_final")
                    cameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt")

                    # viewRecNrmDir = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-pig2\Views\View_%04d\Recover\Combine\Iter\Iter_final\refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.01_nDptIters=1"
                    viewNrmRefineImgFile = os.path.join(nrmRefineIterFinalDir,r"nrmR.pfm") #in world space where nrm is estimated
                    viewRecNrmDir = os.path.join(nrmRefineDirectory,nrmRefRecDirName)
                    viewDistImgFile = os.path.join(viewRecNrmDir, "distR.pfm")
                    viewNrmImgFile = os.path.join(viewRecNrmDir, "nrmObj.pfm")
                    viewMaskImgFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")
                    viewMaskImgFile = os.path.join(nrmRefineIterFinalDir, "specNicePeakMask.pfm")
                    viewTexCoordImgFile = os.path.join(nrmRefineFramesDirectory, "tex.pfm")

                    refineNrmRouWeight = os.path.join(nrmRefineIterFinalDir, r"Base_r_%.5f/weight.pfm")
                    refineNrmDiffWeight = os.path.join(nrmRefineIterFinalDir, r"Base_diffuse/weight.pfm")

                    texNrmImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "TexNrm.pfm")
                    texPosImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "TexPos.pfm")
                    texDiffImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", r"Base_diffuse/weight.pfm")
                    texSpecRouImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", r"Base_r_%.5f/weight.pfm")
                    texSpecFitImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "result_specular.pfm")
                    texRouFitImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "result_roughness_fitted.pfm")

                    reModelUpt = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverUpdate.obj")
                    reModelUptPly = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverUpdate.ply")
                    reModelFinal = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverFinal.ply")
                    reModelFinalObj = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverFinal.obj")
                    reModelFinalPost = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverPostProcess.obj")

                    # re = subprocess.run(
                    #     ["CapNrmCombine",
                    #      "-viewNrmImgFile=" + viewNrmImgFile, "-viewDistImgFile=" + viewDistImgFile,
                    #      "-viewTexCoordImgFile=" + viewTexCoordImgFile,
                    #      "-viewDiffWeightFile=" + refineNrmDiffWeight, "-viewSpecRouWeightFile=" + refineNrmRouWeight,
                    #      "-genericRoughnesses=" + genericRoughnesses,
                    #      "-texNrmImgFile=" + texNrmImgFile,
                    #      "-texDiffImgFile=" + texDiffImgFile,
                    #      "-texSpecRouImgFile=" + texSpecRouImgFile,
                    #      "-viewMaskImgFile=" + viewMaskImgFile, "-nViews=" + nViews, "-width=" + texWidth,
                    #      "-height=" + texHeight,
                    #      "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ","--solveRou",
                    #      "-texSpecFitImgFile=" + texSpecFitImgFile, "-texRouFitImgFile=" + texRouFitImgFile
                    #      ], stdout=True, stderr=True, check=True)

                    re = subprocess.run(
                        ["CapTexCombine",
                         "-viewFramesDirectory=" + viewRecNrmDir,
                         "-viewNrmImgFile=" + viewNrmImgFile, "-viewDistImgFile=" + viewDistImgFile,
                         "-viewTexCoordImgFile=" + viewTexCoordImgFile,
                         "-viewDiffWeightFile=" + refineNrmDiffWeight, "-viewSpecRouWeightFile=" + refineNrmRouWeight,
                         "-genericRoughnesses=" + genericRoughnesses,
                         "-texNrmImgFile=" + texNrmImgFile,
                         "-texPosImgFile=" + texPosImgFile,
                         "-texDiffImgFile=" + texDiffImgFile,
                         "-texSpecRouImgFile=" + texSpecRouImgFile,
                         "-viewMaskImgFile=" + viewMaskImgFile, "-nViews=" + nViews, "-uvWidth=" + texWidth,
                         "-uvHeight=" + texHeight,
                         "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ", "--solveRou",
                         "-texSpecFitImgFile=" + texSpecFitImgFile, "-texRouFitImgFile=" + texRouFitImgFile,
                         "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                         "-viewScale=" + viewScale
                         ], stdout=True, stderr=True, check=True)

                    logger.info("Change obj into ply")
                    # mesh.export(plyFile, "ply", encoding='ascii', vertex_normal=True)
                    obj2ply(reModelUpt, reModelUptPly)

                    re = subprocess.run(
                        ["mesh_opt", reModelUptPly, "norm:"+ reModelFinal], stdout=True, stderr=True, check=True)
                    ply2obj(reModelFinal,reModelFinalObj)

                    reModelFinalPoission = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverFinalPoission.ply")
                    reModelFinalTrim = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverFinalTrim.ply")

                    re = subprocess.run(
                        ["PoissonRecon.exe", "--in", reModelFinal, "--out", reModelFinalPoission, "--normals", "--pointWeight",
                         "0",
                         "--depth",
                         "10", "--density", "--threads", "2"], stdout=True, stderr=True,
                        check=True)
                    # trim combined mesh
                    re = subprocess.run(
                        ["SurfaceTrimmer.exe", "--in", reModelFinalPoission, "--out", reModelFinalTrim, "--trim", "7"],
                        stdout=True, stderr=True, check=True)

                    # mesh = trimesh.Trimesh()
                    mesh = trimesh.load(reModelFinalTrim)
                    # mesh = trimesh.load(reModelFinalObj)
                    print(len(mesh.vertices))
                    mesh.merge_vertices()
                    print(len(mesh.vertices))
                    mesh.remove_degenerate_faces()
                    # mesh = mesh.subdivide()
                    mesh.export(reModelFinalPost)

            if MeshOptSecond:
                meshFinalOptDir = reModel = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt")
                if not os.path.exists(meshFinalOptDir):
                    os.makedirs(meshFinalOptDir)
                # when mesh_opt finished, combine all textures together using new uv
                reModel = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverPostProcess.obj")
                reModelR = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "RecoverR.obj")
                reModelUV = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "RecoverUV.obj")

                if MeshOptSecondPreprocess:
                    logger.info("Preprocess model ")
                    # remove degenerated faces
                    rmBadFace(reModel, reModelR)

                    logger.info("UVAtlas ")
                    # UVAtlas parameterization
                    re = subprocess.run(
                        ["UVAtlas", "-iv", "TEXCOORD", "-w", texWidth, "-h", texHeight, "-t", "-y", "-o", reModelUV,
                         reModelR],
                        stdout=True, stderr=True, check=True)

                    logger.info("Project recovered model into each view:")
                    startView = 0
                    for v in range(startView, nViewsCount):
                        logger.info("Dealing view: {0}th".format(v))
                        modelFile = reModelUV
                        viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
                        framesDirectory = os.path.join(viewDirectory, "Frames")

                        nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                        nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesFinal")

                        cameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt" % v)
                        renderOption = "2"
                        re = subprocess.run(
                            ["CapSim", "-framesDirectory=" + nrmRefineFramesDirectory, "-modelFile=" + modelFile,
                             "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                             "-viewScale=" + viewScale, "-flipZ",
                             "-renderOption=" + renderOption],
                            stdout=True, stderr=True, check=True)

                if MeshOptCapNrmCombine:
                    # combine all views' nrm into uv texture
                    logger.info("CapTexCombine: combine into texture space ")
                    viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")

                    framesDirectory = os.path.join(viewDirectory, "Frames")
                    nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                    nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesFinal")
                    nrmRefineIterFinalDir = os.path.join(nrmRefineDirectory, "Iter", "Iter_final")
                    cameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt")

                    # viewRecNrmDir = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-pig2\Views\View_%04d\Recover\Combine\Iter\Iter_final\refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.01_nDptIters=1"
                    viewNrmRefineImgFile = os.path.join(nrmRefineIterFinalDir,r"nrmR.pfm")
                    viewRecNrmDir = os.path.join(nrmRefineDirectory, nrmRefRecDirName)
                    viewDistImgFile = os.path.join(viewRecNrmDir, "distR.pfm")
                    viewNrmImgFile = os.path.join(viewRecNrmDir, "nrmObj.pfm")
                    viewMaskImgFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")
                    viewTexCoordImgFile = os.path.join(nrmRefineFramesDirectory, "tex.pfm")
                    viewMaskImgFile = os.path.join(nrmRefineIterFinalDir, "specNicePeakMask.pfm")

                    refineNrmRouWeight = os.path.join(nrmRefineIterFinalDir, r"Base_r_%.5f/weight.pfm")
                    refineNrmDiffWeight = os.path.join(nrmRefineIterFinalDir, r"Base_diffuse/weight.pfm")

                    texNrmImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "TexNrm.pfm")
                    texPosImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "TexPos.pfm")
                    texDiffImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", r"Base_diffuse/weight.pfm")
                    texSpecRouImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", r"Base_r_%.5f/weight.pfm")
                    texSpecFitImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "result_specular.pfm")
                    texRouFitImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "result_roughness_fitted.pfm")

                    reModelUpt = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "RecoverUpdate.obj")
                    reModelUptPly = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "RecoverUpdate.ply")
                    reModelFinal = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "RecoverFinal.ply")
                    reModelFinalObj = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt", "RecoverFinal.obj")
                    reModelFinalObjFlip = os.path.join(OBJECT_ROOT, r"Recover\Model\FinalOpt\Object","RecoverFinalFlip.obj")

                    re = subprocess.run(
                        ["CapTexCombine",
                         "-viewFramesDirectory=" + viewRecNrmDir,
                         "-viewNrmImgFile=" + viewNrmImgFile, "-viewDistImgFile=" + viewDistImgFile,
                         "-viewTexCoordImgFile=" + viewTexCoordImgFile,
                         "-viewDiffWeightFile=" + refineNrmDiffWeight, "-viewSpecRouWeightFile=" + refineNrmRouWeight,
                         "-genericRoughnesses=" + genericRoughnesses,
                         "-texNrmImgFile=" + texNrmImgFile,
                         "-texPosImgFile=" + texPosImgFile,
                         "-texDiffImgFile=" + texDiffImgFile,
                         "-texSpecRouImgFile=" + texSpecRouImgFile,
                         "-viewMaskImgFile=" + viewMaskImgFile, "-nViews=" + nViews, "-uvWidth=" + texWidth,
                         "-uvHeight=" + texHeight,
                         "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ", "--solveRou",
                         "-texSpecFitImgFile=" + texSpecFitImgFile, "-texRouFitImgFile=" + texRouFitImgFile,
                         "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                         "-viewScale=" + viewScale
                         ], stdout=True, stderr=True, check=True)

                    logger.info("Change obj into ply")
                    # mesh.export(plyFile, "ply", encoding='ascii', vertex_normal=True)
                    obj2ply(reModelUpt, reModelUptPly)

                    re = subprocess.run(
                        ["mesh_opt", reModelUptPly, "norm:"+ reModelFinal], stdout=True, stderr=True, check=True)
                    ply2obj(reModelFinal,reModelFinalObj)

                    re = subprocess.run(
                        ["CapNrmCombine",
                         "-viewNrmImgFile=" + viewNrmImgFile, "-viewDistImgFile=" + viewDistImgFile,
                         "-viewTexCoordImgFile=" + viewTexCoordImgFile,
                         "-viewDiffWeightFile=" + refineNrmDiffWeight, "-viewSpecRouWeightFile=" + refineNrmRouWeight,
                         "-genericRoughnesses=" + genericRoughnesses,
                         "-texNrmImgFile=" + texNrmImgFile,
                         "-texDiffImgFile=" + texDiffImgFile,
                         "-texSpecRouImgFile=" + texSpecRouImgFile,
                         "-viewMaskImgFile=" + viewMaskImgFile, "-nViews=" + nViews, "-width=" + texWidth,
                         "-height=" + texHeight,
                         "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ", "-solveRou",
                         "-texSpecFitImgFile=" + texSpecFitImgFile, "-texRouFitImgFile=" + texRouFitImgFile
                         ], stdout=True, stderr=True, check=True)

                    re = subprocess.run(
                        ["CapBRDFCombine",
                         "-viewFramesDirectory=" + viewRecNrmDir,
                         "-viewNrmImgFile=" + viewNrmImgFile, "-viewDistImgFile=" + viewDistImgFile,
                         "-viewTexCoordImgFile=" + viewTexCoordImgFile,
                         "-viewDiffWeightFile=" + refineNrmDiffWeight, "-viewSpecRouWeightFile=" + refineNrmRouWeight,
                         "-genericRoughnesses=" + genericRoughnesses,
                         "-texNrmImgFile=" + texNrmImgFile,
                         "-texPosImgFile=" + texPosImgFile,
                         "-texDiffImgFile=" + texDiffImgFile,
                         "-texSpecRouImgFile=" + texSpecRouImgFile,
                         "-viewMaskImgFile=" + viewMaskImgFile, "-nViews=" + nViews, "-uvWidth=" + texWidth,
                         "-uvHeight=" + texHeight,
                         "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ", "-solveRou",
                         "-texSpecFitImgFile=" + texSpecFitImgFile, "-texRouFitImgFile=" + texRouFitImgFile,
                         "-cameraConfig=" + cameraConfig, "-cameraExtrin=" + cameraExtrinsic,
                         "-viewScale=" + viewScale
                         ], stdout=True, stderr=True, check=True)

                    if not os.path.exists(os.path.dirname(reModelFinalObjFlip)):
                        os.makedirs(os.path.dirname(reModelFinalObjFlip))

                    FitRouOption = 1
                    if FitRouOption:
                        # meshUpt = trimesh.load(reModelUpt)
                        # meshRefined = trimesh.load(reModelFinal)
                        # meshUpt.vertices = meshRefined.vertices
                        # #after UVAtlas, vertices size is not consistent with vertex_texture
                        # A = meshUpt.metadata['vertex_texture'][0:len(meshUpt.vertices)]
                        # meshUpt.metadata['vertex_texture'] = A
                        # print(meshUpt.vertex_normals)
                        # ex.export_mesh(meshUpt,reModelFinalObj,file_type="obj",include_normals=True,include_texture=True)
                        logger.info("Create model: ")
                        re = subprocess.run(
                            ["ModelTool",
                             "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelFinalObjFlip, "-flipZ","--flipVC","-tarTex",
                             "-tarTexDiffFile=" + texDiffImgFile, "-tarTexSpecFile=" + texSpecFitImgFile, "-tarTexRouFile="+texRouFitImgFile
                             ], stdout=True, stderr=True, check=True)

        finally:
            os.environ.clear()
            os.environ.update(_environ)
