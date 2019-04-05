# SfM data preparation.
# V0: Origin
import os
import subprocess
import shutil
import logging


if __name__ == "__main__":
    CapSimOption = 1
    CapParseCurOption = 1
    CapNrDiffOption = 1
    CapNrSpecOption = 1
    CapRefineNrBasesDiffOption = 1
    CapRefineNrBasesSpecOption = 1
    CapCombineOption = 1
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    # OBJECT = r"Object-testkitty"
    # OBJECT = r"Object-testpig"
    # OBJECT = r"Object-testduck"
    # OBJECT = r"Object-testmuck"
    # OBJECT = r"Object-testgallon"
    OBJECT = r"Object-testspray"
    # MODEL_NAME = r"Pig/Pig_160608.obj"
    # MODEL_NAME = r"Kitty_160420.obj"
    # MODEL_NAME = r"Duck/duck_160415.obj"
    # MODEL_NAME = r"Muck/travel_mug_STNL8LC.obj"
    # MODEL_NAME = r"Gallon/Gallon_Metal_Drum_55.obj"
    MODEL_NAME = r"Spray/spray_can_dirt.obj"
    # BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    BUILD_ROOT = r"D:\v-jiazha\2-workspaces\Source\ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    OBJECT_ROOT = os.path.join(DATA_ROOT,r'Object', OBJECT)
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')
    COMMON_SINGLE_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\RealCommon"

    positionStr = r"0.199,-0.126,0"
    nViews = 36
    generics = "15"
    genericStart = "0.01"
    genericEnd = "0.60"
    if not os.path.exists(OBJECT_ROOT):
        os.makedirs(OBJECT_ROOT)
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT

        for v in range(nViews):
            logger.info("Dealing view: {0}th".format(v))
            modelDirectory =os.path.join(COMMON_ROOT, "Model")
            modelFile = os.path.join(modelDirectory, MODEL_NAME)

            viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
            framesDirectory =os.path.join(viewDirectory,"Frames")
            # framesDirectory =os.path.join(viewDirectory,"FramesDownsample")
            downsampleFramesDirectory =os.path.join(viewDirectory,"FramesDownsample")
            configDirectory =os.path.join(COMMON_ROOT, "Setups", "Setup_%04d" % v, "Config")
            panelConfig = os.path.join(configDirectory, "panelConfig.txt")
            # just test gl rendering
            # panelConfig = os.path.join(COMMON_ROOT, "Setups", "SetupNoLight", "Config", "panelConfig.txt")
            cameraConfig = os.path.join(configDirectory, "cameraConfig.txt")
            poseConfig = os.path.join(configDirectory, "poseConfig.txt")

            # rowScanWidth = "2"
            # rowScanHeight = "1"
            # colScanWidth = "1"
            # colScanHeight = "6"
            rowScanWidth = "7"
            rowScanHeight = "1"
            colScanWidth = "1"
            colScanHeight = "23"
            # rowScanWidth = "224"
            # rowScanHeight = "4"
            # colScanWidth = "4"
            # colScanHeight = "736"
            framesDir = "FramesDownsample" + "_rowScanW_"+rowScanWidth+"_rowScanH_"+rowScanHeight+"_colScanW_"+colScanWidth+"_colScanH_"+colScanHeight
            framesDirectory = os.path.join(viewDirectory, "FramesDownsample")

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
                                     "--useLightAVG", "-scale=" + scale, "-maskFile=" + maskFile,
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

            # CapNr diffuse
            if CapNrDiffOption:
                logger.info("CapNr diffuse view: {0}th".format(v))
                re = subprocess.run(["CapNr", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                     "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                                     "-curveFileRow=" + curveFileRowAVG, "-curveFileCol=" + curveFileColAVG,
                                     "-curveCSVRow=" + curveCSVRowAVG, "-curveCSVCol=" + curveCSVColAVG,
                                     "-posFile=" + posFile,
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
            phiSize = "32"
            nIter = "2"
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
                     "-nrmTruthFile=" + nrmTruthFile,
                     "-nrmRFile=" + refineNrmR, "-errRFile=" + refineErrR, "-nrmDFile=" + refineNrmD,
                     "-nrmSFile=" + refineNrmS, "-nrmDMskFile=" + refineNrmDMsk,
                     "-generics=" + generics, "-genericStart=" + genericStart, "-genericEnd=" + genericEnd,
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

            # CapNr specular
            if CapNrSpecOption:
                logger.info("CapNr spec view: {0}th".format(v))
                re = subprocess.run(["CapNr", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                     "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                                     "-curveFileRow="+curveFileRowAVG, "-curveFileCol="+curveFileColAVG,
                                     "-curveCSVRow="+curveCSVRowAVG, "-curveCSVCol="+curveCSVColAVG, "-posFile="+posFile,
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

            thetaStep = "0.5"
            phiSize = "36"
            nIter = "2"
            thetaSize = "10"
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
                     "-nrmTruthFile=" + nrmTruthFile,
                     "-nrmRFile=" + refineNrmR, "-errRFile=" + refineErrR, "-nrmDFile=" + refineNrmD,
                     "-nrmSFile=" + refineNrmS, "-nrmDMskFile=" + refineNrmDMsk,
                     "-generics=" + generics, "-genericStart=" + genericStart, "-genericEnd=" + genericEnd,
                     "-threshold=" + threshold, "-rowScanWidth=" + rowScanWidth, "-rowScanHeight=" + rowScanHeight,
                     "-colScanWidth=" + colScanWidth, "-colScanHeight=" + colScanHeight,
                     "-thetaStep=" + thetaStep, "-phiSize=" + phiSize, "-nIter=" + nIter, "-thetaSize=" + thetaSize,
                     "-positionStr=" + positionStr, "--nonLocal", "-posFile="+posFile,
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
                                     "-nrmTruthFile=" + nrmTruthFile,"-combNrmD=" + combNrmD, "-combNrmS=" + combNrmS,
                                     "-combNrmDMsk=" + combNrmDMsk, "-threshold="+threshold],
                                    stdout=True, stderr=True, check=True)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
