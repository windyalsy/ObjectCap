#Real capture
# V0: Origin
import os
import subprocess
import numpy as np
import logging
import trimesh
import trimesh.io.export as ex
from datetime import  datetime

def obj2ply(objFile, plyFile):
    mesh = trimesh.load(objFile)
    ex.export_mesh(mesh,plyFile,encoding='ascii',vertex_normal=True)
    return

def ply2obj(plyFile, objFile):
    mesh = trimesh.load(plyFile)
    ex.export_mesh(mesh,objFile,include_normals=True,
                     include_texture=True)
    return

if __name__ == "__main__":

    FirstCapNrmOption = 1
    FirstMVSOption = 0
    SecondRefineNrmOption = 0
    SecondMVSOption = 0

    # BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    BUILD_ROOT = r"D:\v-jiazha\2-workspaces\Source\ObjectCap\x64\Release"
    TOOL_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    COMMON_ROOT = os.path.join(DATA_ROOT, r'RealCommon')
    COMMON_SINGLE_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\RealCommon"
    LOG_ROOT = os.path.join(DATA_ROOT,r"Object/LOG")
    COMMON_ROOT = os.path.join(DATA_ROOT, r'RealCommon')
    CONFIG_ROOT = os.path.join(COMMON_ROOT,r"Config0301")

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    fileName = r'{:%Y-%m-%d}'.format(datetime.now())
    fileHandler = logging.FileHandler("{0}/{1}.log".format(LOG_ROOT, fileName))
    fileHandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    logger.addHandler(consoleHandler)

    # Setup setting: camera, panel pose
    panelConfig = os.path.join(CONFIG_ROOT, "Setup", "panelConfig.txt")
    cameraConfig = os.path.join(CONFIG_ROOT, "Setup", "cameraConfig.txt")
    poseConfig = os.path.join(CONFIG_ROOT, "Setup", "poseConfig.txt")

    # OBJECT_LIST = [r"Object-testgallon",r"Object-testspray",r"Object-testpig",r"Object-testkight"]
    # MODEL_NAME_LIST = [r"Gallon/Gallon_Metal_Drum_55.obj", r"Spray/spray_can_dirt.obj",r"Pig/Pig_160608.obj",r"Knight/Knight.obj"]
    # OBJECT_LIST = [r"Object-testgallon", r"Object-testspray"]
    # MODEL_NAME_LIST = [r"Gallon/Gallon_Metal_Drum_55.obj", r"Spray/spray_can_dirt.obj"]
    # OBJECT_LIST = [r"Object-testknight"]
    # MODEL_NAME_LIST = [r"Knight/Knight.obj"]
    # OBJECT_LIST = [r"Object-testhamburger"]
    # MODEL_NAME_LIST = [r"Hamburger/hamburger_130.obj"]
    OBJECT_LIST = [r"RealObject-pig3"]
    MODEL_NAME_LIST = [r"Pig/Pig_160608.obj"]
    # OBJECT_LIST = [r"Object-testhat"]
    # MODEL_NAME_LIST = [r"Hat/basic_fedora_hat_1302.obj"]
    # OBJECT_LIST = [r"Object-testducks"]
    # MODEL_NAME_LIST = [r"DuckS/duck_130122.obj"]

    for index in range(len(OBJECT_LIST)):
        # OBJECT = r"Object-testkitty"
        # OBJECT = r"Object-testpig"
        # OBJECT = r"Object-testduck"
        # OBJECT = r"Object-testmuck"
        # OBJECT = r"Object-testgallon"
        # OBJECT = r"Object-testspray"
        # MODEL_NAME = r"Pig/Pig_160608.obj"
        # MODEL_NAME = r"Kitty_160420.obj"
        # MODEL_NAME = r"Duck/duck_160415.obj"
        # MODEL_NAME = r"Muck/travel_mug_STNL8LC.obj"
        # MODEL_NAME = r"Gallon/Gallon_Metal_Drum_55.obj"
        # MODEL_NAME = r"Spray/spray_can_dirt.obj"
        OBJECT = OBJECT_LIST[index]
        MODEL_NAME = MODEL_NAME_LIST[index]
        logger.info("Start {0}th object: {1} ".format(index,OBJECT))

        OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object', OBJECT)

        # positionStr = r"0.1982,-0.0921,0"
        positionStr = r"0.1982,-0.0921,0"
        nViewsCount = 36
        nViews = "36"
        # bases
        generics = "20"
        genericStart = "0.01"
        genericEnd = "0.60"
        genericRoughnesses = "0.01,0.02,0.03,0.05,0.07,0.09,0.11,0.13,0.16,0.20,0.25"

        # downsampled lights
        rowScanWidth = "7"
        rowScanHeight = "1"
        colScanWidth = "1"
        colScanHeight = "23"

        # camera extrinsic scale
        viewScale = "0.009"
        cameraExtrinDirectory = os.path.join(OBJECT_ROOT, "CalibPrism", "Extrinsic")
        #-------------------------------------------------------------------------------------------------------------------
        #First part
        if FirstCapNrmOption:
            CapSimOption = 0
            CapParseCurOption = 0
            CapNrDiffOption = 1
            CapNrSpecOption = 0
            CapRefineNrBasesDiffOption = 0
            CapRefineNrBasesSpecOption = 0
            CapCombineOption = 0

            logger.info("First part: CapSim CapParseCur CapNr CapRefineNrBases CapCombine")
            if not os.path.exists(OBJECT_ROOT):
                os.makedirs(OBJECT_ROOT)
            _environ = dict(os.environ)
            try:
                if 'PATH' in _environ:
                    os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT
                else:
                    os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT

                for v in range(nViewsCount):
                    logger.info("Dealing view: {0}th".format(v))
                    modelDirectory =os.path.join(COMMON_ROOT, "Model")
                    modelFile = os.path.join(modelDirectory, MODEL_NAME)

                    viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
                    framesDirectory =os.path.join(viewDirectory,"Frames")

                    # just test gl rendering
                    # panelConfig = os.path.join(COMMON_ROOT, "Setups", "SetupNoLight", "Config", "panelConfig.txt")

                    # CapSim synthetic
                    if CapSimOption:
                        logger.info("CapSim view: {0}th".format(v))
                        re = subprocess.run(["CapSim", "-framesDirectory="+framesDirectory, "-modelFile=" + modelFile,
                                         "-panelConfig="+panelConfig, "-cameraConfig="+cameraConfig, "-poseConfig="+poseConfig,
                                         "-bounding", "-boundingRadius=1","--nonLocal","-positionStr="+positionStr,
                                         "-downsample","-rowScanWidth="+rowScanWidth, "-rowScanHeight=" + rowScanHeight,
                                         "-colScanWidth=" + colScanWidth, "-colScanHeight="+ colScanHeight],
                                        stdout = True, stderr=True, check=True)

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

                    posFile = os.path.join(framesDirectory, "pos.pfm")
                    nrmFile = os.path.join(framesDirectory,  "nrm.pfm")
                    maskFile =os.path.join(framesDirectory, "mask.pfm")
                    nrmTruthFile =os.path.join(framesDirectory, "nrm.pfm")
                    # smooth parameters
                    sigma = "2"
                    hWidth = "0"
                    # scale light intensity
                    scale = "1"
                    # fitting parameters
                    interval = "1"
                    iterMax = "6"
                    resolution = "256"
                    faceID = "5"
                    kernelSize = "5"

                    # CapParse curves non AVG
                    if CapParseCurOption:
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
                    tableFile = os.path.join(COMMON_SINGLE_ROOT, BALL_TYPE, "Recover" ,BALL_TYPE, "nrmTab.pfm")
                    nrmRFile =os.path.join(recoverDirectory, "nrmR.pfm")
                    nrmSFile =os.path.join(recoverDirectory, "nrmS.pfm")
                    nrmDFile =os.path.join(recoverDirectory, "nrmD.pfm")
                    loggingFile =os.path.join(recoverDirectory,"logging.txt")
                    thMaskFile = os.path.join(recoverDirectory, "thMsk.pfm")
                    peakPosTh = "2"

                    # CapNr diffuse
                    if CapNrDiffOption:
                        logger.info("CapNr diffuse view: {0}th".format(v))
                        re = subprocess.run(["CapNr", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                             "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                                             "-curveFileRow=" + curveFileRowAVG, "-curveFileCol=" + curveFileColAVG,
                                             "-curveCSVRow=" + curveCSVRowAVG, "-curveCSVCol=" + curveCSVColAVG,
                                             "-posFile=" + posFile,
                                             "-thMaskFile="+thMaskFile,"-peakPosTh="+peakPosTh,
                                             "-tableFile=" + tableFile, "-nrmRFile=" + nrmRFile, "-nrmSFile=" + nrmSFile,
                                             "-nrmDFile=" + nrmDFile, "-loggingFile=" + loggingFile, "-sigma=" + sigma,
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
                    refineNrmD = os.path.join(iterFinalDirectory, "nrmD.pfm")
                    refineNrmS = os.path.join(iterFinalDirectory, "nrmS.pfm")
                    refineNrmDMsk = os.path.join(iterFinalDirectory, "nrmDMsk.pfm")
                    nrmFindInTableFile = os.path.join(recoverDirectory, "nrmR.pfm")

                    thetaStep = "1"
                    phiSize = "18"
                    nIter = "2"
                    thetaSize = "5"
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
                             "-nrmRFile=" + refineNrmR, "-errRFile=" + refineErrR, "-nrmDFile=" + refineNrmD,
                             "-nrmSFile=" + refineNrmS, "-nrmDMskFile=" + refineNrmDMsk,
                             "-generics=" + generics, "-genericStart=" + genericStart, "-genericEnd=" + genericEnd,
                             "-genericRoughnesses="+genericRoughnesses,
                             "-threshold=" + threshold, "-rowScanWidth=" + rowScanWidth, "-rowScanHeight=" + rowScanHeight,
                             "-colScanWidth=" + colScanWidth, "-colScanHeight=" + colScanHeight,
                             "-thetaStep=" + thetaStep, "-phiSize=" + phiSize, "-nIter=" + nIter, "-thetaSize=" + thetaSize,
                             "-positionStr=" + positionStr, "-nonLocal",
                             "-recordIter"],
                            stdout=True, stderr=True, check=True)

                    BALL_TYPE = "Mirror"
                    recoverDirectory = os.path.join(viewDirectory, "Recover", BALL_TYPE)
                    tableFile = os.path.join(COMMON_SINGLE_ROOT, BALL_TYPE, "Recover", BALL_TYPE, "nrmTab.pfm")
                    nrmRFile = os.path.join(recoverDirectory, "nrmR.pfm")
                    nrmSFile = os.path.join(recoverDirectory, "nrmS.pfm")
                    nrmDFile = os.path.join(recoverDirectory, "nrmD.pfm")
                    loggingFile = os.path.join(recoverDirectory, "logging.txt")
                    thMaskFile = os.path.join(recoverDirectory, "thMsk.pfm")
                    peakPosTh = "10"

                    # CapNr specular
                    if CapNrSpecOption:
                        logger.info("CapNr spec view: {0}th".format(v))
                        re = subprocess.run(["CapNr", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                             "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                                             "-curveFileRow="+curveFileRowAVG, "-curveFileCol="+curveFileColAVG,
                                             "-curveCSVRow="+curveCSVRowAVG, "-curveCSVCol="+curveCSVColAVG, "-posFile="+posFile,
                                             "-thMaskFile=" + thMaskFile,"-peakPosTh=" + peakPosTh,
                                             "-tableFile=" + tableFile, "-nrmRFile=" + nrmRFile, "-nrmSFile=" + nrmSFile,
                                             "-nrmDFile=" + nrmDFile, "-loggingFile=" + loggingFile, "-sigma=" + sigma,
                                             "-hWidth=" + hWidth, "-positionStr=" + positionStr, "--saveCurve", "--saveCSV",
                                             "-useLightAVG", "-scale=" + scale,"-maskFile="+maskFile],
                                            stdout=True, stderr=True, check=True)

                    iterDirectory = os.path.join(recoverDirectory, "Iter")
                    basesDirectory = os.path.join(COMMON_SINGLE_ROOT, BALL_TYPE, "Recover", BALL_TYPE, "Iter/Bases")
                    nrmFile = os.path.join(recoverDirectory, "nrmR.pfm")
                    diffErrorFile = os.path.join(viewDirectory, "Recover/Diffuse/Iter/Iter_final/errorR.pfm")
                    nrmDiffFile = os.path.join(viewDirectory,"Recover/Diffuse/Iter/Iter_final/nrmR.pfm")

                    iterDirectory = os.path.join(recoverDirectory, "Iter")
                    iterRecordDirectory = os.path.join(iterDirectory, "Iter_%04d")
                    iterFinalDirectory = os.path.join(iterDirectory, "Iter_final")
                    refineNrmRouWeight = os.path.join(iterFinalDirectory, r"Base_r_%.5f/weight.pfm")
                    refineNrmDiffWeight = os.path.join(iterFinalDirectory, r"Base_diffuse/weight.pfm")
                    refineNrmR = os.path.join(iterFinalDirectory, "nrmR.pfm")
                    refineErrR = os.path.join(iterFinalDirectory, "errorR.pfm")
                    refineNrmD = os.path.join(iterFinalDirectory, "nrmD.pfm")
                    refineNrmS = os.path.join(iterFinalDirectory, "nrmS.pfm")
                    refineNrmDMsk = os.path.join(iterFinalDirectory, "nrmDMsk.pfm")
                    nrmFindInTableFile = os.path.join(recoverDirectory, "nrmR.pfm")

                    thetaStep = "1"
                    phiSize = "18"
                    nIter = "2"
                    thetaSize = "5"
                    threshold = "5.0"
                    # CapRefineNrBases using specular normal table initialization
                    if CapRefineNrBasesSpecOption:
                        logger.info("CapRefineNrBases specular view: {0}th".format(v))
                        re = subprocess.run(
                            ["CapRefineNrBases", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                             "-specRouWeightFile=" + refineNrmRouWeight, "-diffWeightFile=" + refineNrmDiffWeight,
                             "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                             "-iterDirectory=" + iterRecordDirectory,
                             "-nrmFile=" + nrmFindInTableFile, "-maskFile=" + maskFile,
                             "-nrmRFile=" + refineNrmR, "-errRFile=" + refineErrR, "-nrmDFile=" + refineNrmD,
                             "-nrmSFile=" + refineNrmS, "-nrmDMskFile=" + refineNrmDMsk,
                             "-generics=" + generics, "-genericStart=" + genericStart, "-genericEnd=" + genericEnd,
                             "-genericRoughnesses=" + genericRoughnesses,
                             "-threshold=" + threshold, "-rowScanWidth=" + rowScanWidth, "-rowScanHeight=" + rowScanHeight,
                             "-colScanWidth=" + colScanWidth, "-colScanHeight=" + colScanHeight,
                             "-thetaStep=" + thetaStep, "-phiSize=" + phiSize, "-nIter=" + nIter, "-thetaSize=" + thetaSize,
                             "-positionStr=" + positionStr, "-nonLocal",
                             "-recordIter"],
                            stdout=True, stderr=True, check=True)

                    specIterFinal =os.path.join(viewDirectory,"Recover/Mirror/Iter/Iter_final")
                    specRouWeight =os.path.join(specIterFinal,"Base_r_%.5f/weight.pfm")
                    specDiffWeight =os.path.join(specIterFinal,"Base_diffuse/weight.pfm")
                    specNrm =os.path.join(specIterFinal,"nrmR.pfm")
                    specErr =os.path.join(specIterFinal,"errorR.pfm")

                    diffIterFinal = os.path.join(viewDirectory, "Recover/Diffuse/Iter/Iter_final")
                    diffRouWeight = os.path.join(diffIterFinal, "Base_r_%.5f/weight.pfm")
                    diffDiffWeight = os.path.join(diffIterFinal, "Base_diffuse/weight.pfm")
                    diffNrm = os.path.join(diffIterFinal, "nrmR.pfm")
                    diffErr = os.path.join(diffIterFinal, "errorR.pfm")

                    combIterFinal =os.path.join(viewDirectory, "Recover/Combine/Iter/Iter_final")
                    combRouWeight =os.path.join(combIterFinal, "Base_r_%.5f/weight.pfm")
                    combDiffWeight =os.path.join(combIterFinal, "Base_diffuse/weight.pfm")
                    combNrm =os.path.join(combIterFinal,"nrmR.pfm")
                    combErr =os.path.join(combIterFinal,"errorR.pfm")
                    combSpecMsk =os.path.join(combIterFinal,"specMsk.pfm")
                    combDiffMsk =os.path.join(combIterFinal,"diffMsk.pfm")
                    combNrmD =os.path.join(combIterFinal ,"nrmD.pfm")
                    combNrmS =os.path.join(combIterFinal , "nrmS.pfm")
                    combNrmDMsk =os.path.join(combIterFinal,"nrmDMsk.pfm")
                    threshold = "5.0"

                    if CapCombineOption:
                        logger.info("CapCombine view: {0}th".format(v))
                        re = subprocess.run(["CapFitCombine", "-specRouWeight=" + specRouWeight, "-specDiffWeight=" + specDiffWeight,
                                             "-specNrm=" + specNrm, "-specErr=" + specErr,"-diffRouWeight=" + diffRouWeight, "-diffDiffWeight=" + diffDiffWeight,
                                             "-diffNrm=" + diffNrm, "-diffErr=" + diffErr,"-combRouWeight=" + combRouWeight, "-combDiffWeight=" + combDiffWeight,
                                             "-combNrm=" + combNrm, "-combErr=" + combErr,"-combSpecMsk="+combSpecMsk, "-combDiffMsk="+combDiffMsk,
                                             "-maskFile="+maskFile, "-cameraConfig=" + cameraConfig,
                                             "-generics=" + generics,"-genericStart=" + genericStart,"-genericEnd=" + genericEnd,
                                             "-genericRoughnesses=" + genericRoughnesses,
                                             "-combNrmD=" + combNrmD, "-combNrmS=" + combNrmS,
                                             "-combNrmDMsk=" + combNrmDMsk, "-threshold="+threshold],
                                            stdout=True, stderr=True, check=True)

            finally:
                os.environ.clear()
                os.environ.update(_environ)

        #-------------------------------------------------------------------------------------------------------------------
        #Second part
        if FirstMVSOption:
            MVSSweepOption = 3
            RGBNPlaneSweepMVSOption = 1
            logger.info("Second Part: MVS ")
            if not os.path.exists(OBJECT_ROOT):
                os.makedirs(OBJECT_ROOT)
            _environ = dict(os.environ)
            try:
                if 'PATH' in _environ:
                    os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT
                else:
                    os.environ['PATH'] = BUILD_ROOT

                modelDirectory = os.path.join(COMMON_ROOT, "Model")
                modelFile = os.path.join(modelDirectory, MODEL_NAME)
                # viewConfigDirectory=$COMMON_ROOT/Setups/Setup_%04d/Config

                viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
                # framesDirectory =os.path.join(viewDirectory,"Frames")
                framesDirectory = os.path.join(viewDirectory, "Frames")
                configDirectory = os.path.join(COMMON_SINGLE_ROOT, "Setup", "Config")
                viewCameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt")
                # panelConfig = os.path.join(configDirectory, "panelConfig.txt")
                # just test gl rendering
                # panelConfig = os.path.join(COMMON_ROOT, "Setups", "SetupNoLight", "Config", "panelConfig.txt")
                # common camera
                cameraConfig = os.path.join(configDirectory, "cameraConfig.txt")
                poseConfig = os.path.join(configDirectory, "poseConfig.txt")

                combIterFinal = os.path.join(viewDirectory, "Recover/Combine/Iter/Iter_final")
                combDiffWeight = os.path.join(combIterFinal, "Base_diffuse/weight.pfm")
                combNrm = os.path.join(combIterFinal, "nrmR.pfm")
                combNrmDMsk = os.path.join(combIterFinal, "nrmDMsk.pfm")

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
                    recoverDirName = "re_TestTh"

                rgbWeight = "1"
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
                checkW = "385"
                checkH = "275"
                positionStr = "0.1982,-0.0921,0"
                fDistTH = "0.001"
                nMetricLabel = "0"

                modelName = modelName + "_"
                # modelName = modelName + "rgbWeight=" + rgbWeight + "_nrmWeight=" + nrmWeight + "_dptWeight=" \
                #             + dptWeight + "_fDistTH=" + fDistTH + "_nDptIters=" + nDptIters
                recoverDirName = recoverDirName + "rgbWeight=" + rgbWeight + "_nrmWeight=" + nrmWeight + "_dptWeight=" \
                                 + dptWeight + "_fDistTH=" + fDistTH + "_nDptIters=" + nDptIters

                outputDir = os.path.join(combIterFinal, recoverDirName)
                viewDistImgFile = os.path.join(outputDir, "distR.pfm")
                viewDepthImgFile = os.path.join(outputDir, "depthR.pfm")

                viewDepTruthImgFile = os.path.join(framesDirectory, "depth.pfm")
                viewMaskImgFile = os.path.join(framesDirectory, "mask.pfm")
                # test mask
                viewMaskImgFile = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-penrack\Views\View_%04d\Recover\NrmRefine\FramesBase\mask.pfm"
                viewThMaskImgFile = os.path.join(viewDirectory, "Recover/Mirror/thMsk.pfm")

                # viewMaskImgFile = os.path.join(combIterFinal, "specMsk.pfm")
                # viewMaskImgFile=$combIterFinal/nrmDMsk.pfm
                # modelName = "model" + "RecWithoutDepthConstraintO2NCC"

                # Sweep
                if RGBNPlaneSweepMVSOption:
                    logger.info("RGBNPlaneSweepMVS")
                    re = subprocess.run(["RGBNPlaneSweepMVS", "-cameraConfig=" + cameraConfig,  "-poseConfig=" + poseConfig,
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
                                         "-nSteps=" + nSteps, "-nRefineIters=" + nRefineIters, "-nRefineSteps=" + nRefineSteps,
                                         "-nFirstKNeighborsForCost=" + nFirstKNeighborsForCost, "-nViews=" + nViews,
                                         "-checkW=" + checkW, "-checkH=" + checkH, "--checkOption", "-bDistTHLabel",
                                         "-fDistTH=" + fDistTH, "-nMetricLabel=" + nMetricLabel, "-flipZ", "-GPUOption",
                                         "-viewScale=" + viewScale,"-realOption"],
                                        stdout=True, stderr=True, check=True)

            finally:
                os.environ.clear()
                os.environ.update(_environ)

            CombineAllViewOption = 1
            PoissonEachViewOption = 0

            meshCom = trimesh.base.Trimesh()  # combine all views's meshes.
            meshComF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName,"Comb_{0}.txt".format(modelName))
            meshComObjF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName, "Comb_{0}.obj".format(modelName))
            meshComReconF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName,"Recon_{0}.ply".format(modelName))
            meshComReconTrimF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName,"Trim_{0}.ply".format(modelName))
            meshComReconTrimFObj = os.path.join(OBJECT_ROOT, r"Recover\Model\Recover.obj".format(modelName))

            meshComFDir = os.path.dirname(meshComF)
            logger.info("Start")
            if not os.path.exists(meshComFDir):
                os.makedirs(meshComFDir)
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
                                                 "--density", "--verbose", "--threads", "8"], stdout=True, stderr=True, check=True)
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
                            vertices = np.concatenate((vertices, mesh.vertices),axis=0)
                            vertexNrms = np.concatenate((vertexNrms, mesh.vertex_normals), axis=0)
                        meshCom = trimesh.util.concatenate(meshCom, mesh)
                    # save combined mesh
                    # meshCom.vertices = vertices
                    # meshCom.vertex_normals = vertexNrms
                    pointCloud = np.concatenate((vertices,vertexNrms),axis=1)
                    np.savetxt(meshComF,pointCloud, delimiter=" ")
                    # meshCom = trimesh.base.Trimesh(vertices = vertices)
                    ex.export_mesh(meshCom, meshComObjF,include_normals=True)
                    # obj2ply(meshComObjF,meshComF)
                    # ex.export_mesh(meshCom, meshComF, encoding='ascii', vertex_normal=True)

                # poisson reconstruct combined mesh
                re = subprocess.run(
                    ["PoissonRecon.exe", "--in", meshComF, "--out", meshComReconF, "--normals", "--depth", "12", "--pointWeight", "0",
                     "--density", "--threads", "2"], stdout=True, stderr=True, check=True)
                # trim combined mesh
                re = subprocess.run(["SurfaceTrimmer.exe", "--in", meshComReconF, "--out", meshComReconTrimF, "--trim", "7"],
                                    stdout=True, stderr=True, check=True)
                ply2obj(meshComReconTrimF, meshComReconTrimFObj)

            finally:
                os.environ.clear()
                os.environ.update(_environ)

        #-------------------------------------------------------------------------------------------------------------------
        #Third part RefineNrBases
        CapSimOption = 1

        if SecondRefineNrmOption:
            CapRefineNrBasesOption = 1
            # render based on refine normal outcome.
            CapSimRefineNrOption = 0
            # parse curves from rendered outcome.
            CapParseCurOption = 0

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

                for v in range(nViewsCount):

                    logger.info("Dealing view: {0}th".format(v))
                    modelFile = meshComReconTrimFObj

                    viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
                    framesDirectory = os.path.join(viewDirectory, "Frames")
                    configDirectory = os.path.join(COMMON_SINGLE_ROOT, "Setup", "Config")
                    panelConfig = os.path.join(configDirectory, "panelConfig.txt")
                    # just test gl rendering
                    # panelConfig = os.path.join(COMMON_ROOT, "Setups", "SetupNoLight", "Config", "panelConfig.txt")
                    cameraConfig = os.path.join(configDirectory, "cameraConfig.txt")
                    poseConfig = os.path.join(configDirectory, "poseConfig.txt")

                    nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                    # nrmRefineFramesDirectory =os.path.join(nrmRefineDirectory,"FramesTestScope")
                    # nrmRefineFramesDirectory =os.path.join(nrmRefineDirectory,"FramesTestValuePeak")
                    nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesBase")
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

                    gtNrm = os.path.join(framesDirectory, "nrm.pfm")
                    gtPos = os.path.join(framesDirectory, "pos.pfm")
                    constantPos = os.path.join(framesDirectory, "posConstant.pfm")

                    combIterFinal = os.path.join(viewDirectory, "Recover/Combine/Iter/Iter_final")
                    combRouWeight = os.path.join(combIterFinal, "Base_r_%.5f/weight.pfm")
                    combDiffWeight = os.path.join(combIterFinal, "Base_diffuse/weight.pfm")
                    combNrm = os.path.join(combIterFinal, "nrmR.pfm")
                    combErr = os.path.join(combIterFinal, "errorR.pfm")
                    combSpecMsk = os.path.join(combIterFinal, "specMsk.pfm")
                    combDiffMsk = os.path.join(combIterFinal, "diffMsk.pfm")
                    combNrmD = os.path.join(combIterFinal, "nrmD.pfm")
                    combNrmS = os.path.join(combIterFinal, "nrmS.pfm")
                    combNrmDMsk = os.path.join(combIterFinal, "nrmDMsk.pfm")

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
                    phiSize = "45"
                    nIter = "2"
                    thetaSize = "10"
                    # tempDir =os.path.join(r"D:\Nrm_refine\Nrm_0025")
                    # combRouWeight =os.path.join(tempDir, "Base_r_%.5f/weight.pfm")
                    # combDiffWeight =os.path.join(tempDir, "Base_diffuse/weight.pfm")

                    # output refinement weight files
                    refineNrmRouWeight = os.path.join(nrmRefineFramesDirectory, r"Base_r_%.5f/weight.pfm")
                    refineNrmDiffWeight = os.path.join(nrmRefineFramesDirectory, r"Base_diffuse/weight.pfm")
                    if CapRefineNrBasesOption:
                        logger.info("CapRefineNrBases view: {0}th".format(v))
                        re = subprocess.run(["CapRefineNrBases", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
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

                    if CapSimRefineNrOption:
                        logger.info("CapSimBasesComb view: {0}th".format(v))
                        re = subprocess.run(["CapSimBasesComb", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                             "-specRouWeightFile=" + refineNrmRouWeight,
                                             "-diffWeightFile=" + refineNrmDiffWeight,
                                             "-inputFramesRow=" + refineInputFramesRow,
                                             "-inputFramesCol=" + refineInputFramesCol,
                                             "-nrmFile=" + refineNrmR, "-posFile=" + recPos, "-maskFile=" + viewMaskImgFile,
                                             "-generics=" + generics, "-genericStart=" + genericStart,
                                             "-genericEnd=" + genericEnd,
                                             "-genericRoughnesses=" + genericRoughnesses,
                                             "-rowScanWidth=" + rowScanWidth, "-rowScanHeight=" + rowScanHeight,
                                             "-colScanWidth=" + colScanWidth, "-colScanHeight=" + colScanHeight],
                                            stdout=True, stderr=True, check=True)

                    refineCurveFileCol = os.path.join(nrmRefineFramesDirectory, r"curveCol.cur")
                    refineCurveFileRow = os.path.join(nrmRefineFramesDirectory, "curveRow.cur")
                    refineCurveCSVCol = os.path.join(nrmRefineFramesDirectory, "curveCol.csv")
                    refineCurveCSVRow = os.path.join(nrmRefineFramesDirectory, "curveRow.csv")
                    posFile = os.path.join(framesDirectory, "pos.pfm")
                    nrmFile = os.path.join(framesDirectory, "nrm.pfm")
                    maskFile = os.path.join(framesDirectory, "mask.pfm")
                    nrmTruthFile = os.path.join(framesDirectory, "nrm.pfm")
                    # smooth parameters
                    sigma = "2"
                    hWidth = "0"
                    # scale light intensity
                    scale = "1"
                    # fitting parameters
                    interval = "1"

                    iterMax = "6"
                    resolution = "256"
                    faceID = "5"
                    kernelSize = "5"

                    # CapParseCur
                    if CapParseCurOption:
                        logger.info("CapParseCur view: {0}th".format(v))
                        re = subprocess.run(["CapParseCur", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                             "-inputFramesRow=" + refineInputFramesRow,
                                             "-inputFramesCol=" + refineInputFramesCol,
                                             "-curveFileRow=" + refineCurveFileRow, "-curveFileCol=" + refineCurveFileCol,
                                             "-curveCSVRow=" + refineCurveCSVRow, "-curveCSVCol=" + refineCurveCSVCol,
                                             "-sigma=" + sigma,
                                             "-hWidth=" + hWidth, "-positionStr=" + positionStr, "-saveCurve", "--saveCSV",
                                             "--useLightAVG", "-scale=" + scale, "-maskFile=" + maskFile,
                                             "-rowScanWidth=" + rowScanWidth, "-rowScanHeight=" + rowScanHeight,
                                             "-colScanWidth=" + colScanWidth, "-colScanHeight=" + colScanHeight],
                                            stdout=True, stderr=True, check=True)

            finally:
                os.environ.clear()
                os.environ.update(_environ)

        #-------------------------------------------------------------------------------------------------------------------
        #Forth part RefineNrBases
        if SecondMVSOption:
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
                # configDirectory = os.path.join(COMMON_ROOT, "Setups", "Setup", "Config")
                configDirectory = os.path.join(COMMON_SINGLE_ROOT, "Setup", "Config")
                viewCameraExtrinsic = os.path.join(cameraExtrinDirectory, "view_%04d.txt")
                viewConfigDirectory = os.path.join(COMMON_ROOT, "Setups", "Setup_%04d", "Config")
                # panelConfig = os.path.join(configDirectory, "panelConfig.txt")
                # just test gl rendering
                # panelConfig = os.path.join(COMMON_ROOT, "Setups", "SetupNoLight", "Config", "panelConfig.txt")
                # common camera
                cameraConfig = os.path.join(configDirectory, "cameraConfig.txt")
                poseConfig = os.path.join(viewConfigDirectory, "poseConfig.txt")

                combIterFinal = os.path.join(viewDirectory, "Recover/Combine/Iter/Iter_final")
                combDiffWeight = os.path.join(combIterFinal, "Base_diffuse/weight.pfm")
                combNrm = os.path.join(combIterFinal, "nrmR.pfm")
                combNrmDMsk = os.path.join(combIterFinal, "nrmDMsk.pfm")

                nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
                nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesBase")
                refineNrmR = os.path.join(nrmRefineFramesDirectory, "nrmR.pfm")
                refineNrmD = os.path.join(nrmRefineFramesDirectory, "nrmD.pfm")
                refineNrmS = os.path.join(nrmRefineFramesDirectory, "nrmS.pfm")
                refineNrmDMsk = os.path.join(nrmRefineFramesDirectory, "nrmDMsk.pfm")
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
                dptWeight = "10"
                minDepth = "1.1"
                maxDepth = "1.3"
                nNeighbors = "6"
                nSteps = "1001"
                nRefineIters = "2"
                nRefineSteps = "9"
                nDptIters = "1"
                nFirstKNeighborsForCost = "2"
                checkW = "385"
                checkH = "275"
                positionStr = "0.1982,-0.0921,0"
                fDistTH = "0.1"
                nMetricLabel = "0"

                # modelName = modelName + "rgbWeight="+rgbWeight+"_nrmWeight="+nrmWeight+"_dptWeight="\
                #                  +dptWeight+"_fDistTH="+fDistTH + "_nDptIters="+nDptIters
                modelName = modelName + "_"
                recoverDirName = recoverDirName + "rgbWeight=" + rgbWeight + "_nrmWeight=" + nrmWeight + "_dptWeight=" \
                                 + dptWeight + "_fDistTH=" + fDistTH + "_nDptIters=" + nDptIters

                outputDir = os.path.join(combIterFinal, recoverDirName)
                viewDistImgFile = os.path.join(outputDir, "distR.pfm")
                viewDepthImgFile = os.path.join(outputDir, "depthR.pfm")

                viewDepTruthImgFile = os.path.join(framesDirectory, "depth.pfm")
                viewMaskImgFile = os.path.join(framesDirectory, "mask.pfm")
                viewMaskImgFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")
                viewThMaskImgFile = os.path.join(viewDirectory, "Recover/Mirror/thMsk.pfm")
                # viewMaskImgFile = os.path.join(combIterFinal, "nrmDMsk.pfm")
                # viewMaskImgFile = os.path.join(combIterFinal, "specMsk.pfm")
                # viewMaskImgFile=$combIterFinal/nrmDMsk.pfm
                # modelName = "model" + "RecWithoutDepthConstraintO2NCC"

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
                                         "-viewThMaskImgFile=" + viewThMaskImgFile,
                                         "-modelName=" + modelName, "-rgbWeight=" + rgbWeight, "-nrmWeight=" + nrmWeight,
                                         "-dptWeight=" + dptWeight, "-nDptIters=" + nDptIters,
                                         "-minDepth=" + minDepth, "-maxDepth=" + maxDepth, "-nNeighbors=" + nNeighbors,
                                         "-nSteps=" + nSteps, "-nRefineIters=" + nRefineIters, "-nRefineSteps=" + nRefineSteps,
                                         "-nFirstKNeighborsForCost=" + nFirstKNeighborsForCost, "-nViews=" + nViews,
                                         "-checkW=" + checkW, "-checkH=" + checkH, "--checkOption", "-bDistTHLabel",
                                         "-fDistTH=" + fDistTH, "-nMetricLabel=" + nMetricLabel, "-flipZ", "-GPUOption",
                                         "-viewScale=" + viewScale, "-realOption"], stdout=True, stderr=True, check=True)

            finally:
                os.environ.clear()
                os.environ.update(_environ)

            CombineAllViewOption = 1
            PoissonEachViewOption = 0

            meshCom = trimesh.base.Trimesh()  # combine all views's meshes.
            meshComF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName, "Comb_{0}.txt".format(modelName))
            meshComObjF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName, "Comb_{0}.obj".format(modelName))
            meshComReconF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName, "Recon_{0}.ply".format(modelName))
            meshComReconTrimF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName, "Trim_{0}.ply".format(modelName))
            meshComReconTrimFObj = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName, "Trim_{0}.obj".format(modelName))

            meshComFDir = os.path.dirname(meshComF)
            logger.info("Start")
            if not os.path.exists(meshComFDir):
                os.makedirs(meshComFDir)
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
                    ["PoissonRecon.exe", "--in", meshComF, "--out", meshComReconF, "--normals", "--pointWeight", "0", "--depth",
                     "12","--density", "--threads", "2"], stdout=True, stderr=True, check=True)
                # trim combined mesh
                re = subprocess.run(["SurfaceTrimmer.exe", "--in", meshComReconF, "--out", meshComReconTrimF, "--trim", "6"],
                                    stdout=True, stderr=True, check=True)
                ply2obj(meshComReconTrimF, meshComReconTrimFObj)

            finally:
                os.environ.clear()
                os.environ.update(_environ)
