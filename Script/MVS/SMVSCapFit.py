# Call SMVSCapFIt.sh
# V0: Origin
import os
import subprocess
import shutil
import logging


if __name__ == "__main__":
    CapFitDiffOption = 1
    CapFitSpecOption = 1
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    # OBJECT = r"Object-testkitty"
    OBJECT = r"Object-testpig"
    BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    OBJECT_ROOT = os.path.join(DATA_ROOT,r'Object', OBJECT)
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')
    COMMON_SINGLE_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\RealCommon"
    # MODEL_NAME = r"Pig/Pig_160608.obj"
    MODEL_NAME = r"Kitty_160420.obj"
    positionStr = r"0.199,-0.126,0"
    nViews = 36
    if not os.path.exists(OBJECT_ROOT):
        os.makedirs(OBJECT_ROOT)
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT

        # common parameters for both diffuse and specular pipeline
        modelDirectory =os.path.join(COMMON_ROOT, "Model")
        modelFile = os.path.join(modelDirectory, MODEL_NAME)
        configDirectory =os.path.join(COMMON_ROOT, "Setups", "Setup", "Config")
        panelConfig = os.path.join(configDirectory, "panelConfig.txt")
        # just test gl rendering
        # panelConfig = os.path.join(COMMON_ROOT, "Setups", "SetupNoLight", "Config", "panelConfig.txt")
        cameraConfig = os.path.join(configDirectory, "cameraConfig.txt")
        poseConfig = os.path.join(configDirectory, "poseConfig.txt")

        viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
        framesDirectory =os.path.join(viewDirectory, "Frames")

        curveFileCol = os.path.join(framesDirectory, r"curveCol.cur")
        curveFileRow = os.path.join(framesDirectory, r"curveRow.cur")
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
        generics = "10"
        genericStart = "0.01"
        genericEnd = "0.20"
        iterMax = "6"
        resolution = "256"
        faceID = "5"
        kernelSize = "5"
        nViews = "36"

        BALL_TYPE = r"Diffuse"
        recoverDirectory = os.path.join(viewDirectory, "Recover", BALL_TYPE)
        tableFile = os.path.join(COMMON_SINGLE_ROOT, BALL_TYPE, "Recover" ,BALL_TYPE, "nrmTab.pfm")
        nrmRFile =os.path.join(recoverDirectory, "nrmR.pfm")
        nrmSFile =os.path.join(recoverDirectory, "nrmS.pfm")
        nrmDFile =os.path.join(recoverDirectory, "nrmD.pfm")
        loggingFile =os.path.join(recoverDirectory,"logging.txt")

        iterDirectory = os.path.join(recoverDirectory, "Iter")
        basesDirectory =os.path.join(COMMON_SINGLE_ROOT,BALL_TYPE,"Recover",BALL_TYPE,"Iter/Bases")
        nrmFile = os.path.join(recoverDirectory, "nrmR.pfm")

        if CapFitDiffOption:
            logger.info("CapFit diffuse view: ")
            re = subprocess.run(["MVSCapFit", "-basesDirectory="+basesDirectory, "-iterDirectory="+iterDirectory,
                                 "-framesDirectory="+framesDirectory,  "-nrmFile=" + nrmFile, "-posFile=" + posFile,
                                 "-maskFile="+maskFile, "-panelConfig=" + panelConfig, "-cameraConfig=" + cameraConfig,
                                 "-poseConfig="+poseConfig, "-generics="+generics, "-genericStart="+genericStart,
                                 "-genericEnd="+genericEnd, "-nViews=" + nViews,
                                 "-curveFileRow="+curveFileRow,"-curveFileCol=" + curveFileCol,
                                 "-iterMax="+iterMax, "-resolution="+resolution, "-faceID="+faceID, "-positionStr="+positionStr,
                                 "--saveCur", "-kernelSize="+kernelSize, "-diffBase","-nrmTruthFile="+nrmTruthFile],
                                stdout=True, stderr=True, check=True)


        BALL_TYPE = "Mirror"
        recoverDirectory = os.path.join(viewDirectory, "Recover", BALL_TYPE)
        tableFile = os.path.join(COMMON_SINGLE_ROOT, BALL_TYPE, "Recover", BALL_TYPE, "nrmTab.pfm")
        nrmRFile = os.path.join(recoverDirectory, "nrmR.pfm")
        nrmSFile = os.path.join(recoverDirectory, "nrmS.pfm")
        nrmDFile = os.path.join(recoverDirectory, "nrmD.pfm")
        loggingFile = os.path.join(recoverDirectory, "logging.txt")

        iterDirectory = os.path.join(recoverDirectory, "Iter")
        basesDirectory = os.path.join(COMMON_SINGLE_ROOT, BALL_TYPE, "Recover", BALL_TYPE, "Iter/Bases")
        nrmFile = os.path.join(recoverDirectory, "nrmR.pfm")
        diffErrorFile = os.path.join(viewDirectory, "Recover/Diffuse/Iter/Iter_final/errorR.pfm")
        nrmDiffFile = os.path.join(viewDirectory,"Recover/Diffuse/Iter/Iter_final/nrmR.pfm")

        if CapFitSpecOption:
            logger.info("CapFit spec view:")
            re = subprocess.run(["MVSCapFit", "-basesDirectory=" + basesDirectory, "-iterDirectory=" + iterDirectory,
                                 "-framesDirectory=" + framesDirectory, "-nrmFile=" + nrmFile,
                                 "-posFile=" + posFile,
                                 "-maskFile=" + maskFile, "-panelConfig=" + panelConfig,
                                 "-cameraConfig=" + cameraConfig,
                                 "-poseConfig=" + poseConfig, "-generics=" + generics,
                                 "-genericStart=" + genericStart,
                                 "-genericEnd=" + genericEnd,"-nViews=" + nViews,
                                 "-curveFileRow=" + curveFileRow, "-curveFileCol=" + curveFileCol,
                                 "-iterMax=" + iterMax, "-resolution=" + resolution, "-faceID=" + faceID,
                                 "-positionStr=" + positionStr,
                                 "--saveCur", "-kernelSize=" + kernelSize, "-specBase",
                                 "-nrmTruthFile=" + nrmTruthFile, "-nrmDiffFile="+nrmDiffFile],
                                stdout=True, stderr=True, check=True)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
