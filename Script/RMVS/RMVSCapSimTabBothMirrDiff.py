# CapSim virtual ball and construct different bases including both mirror and diffuse
# V0: Origin
import os
import subprocess
import shutil
import logging


if __name__ == "__main__":
    CapSimDiffOption = 1
    CapSimSpecOption = 1
    CapTabDiffOption = 1
    CapTabSpecOption = 1
    CapPreNrDiffOption = 0
    CapPreNrSpecOption = 0

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    BUILD_ROOT = r"D:\v-jiazha\2-workspaces\Source\ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')
    CONFIG_ROOT = os.path.join(COMMON_ROOT,r"Config0301")

    panelConfig = os.path.join(CONFIG_ROOT, "Setup", "panelConfig.txt")
    cameraConfig = os.path.join(CONFIG_ROOT, "Setup", "cameraConfig.txt")
    poseConfig = os.path.join(CONFIG_ROOT, "Setup", "poseConfig.txt")

    # MODEL_NAME = r"Pig/Pig_160608.obj"
    # MODEL_NAME = r"Kitty_160420.obj"
    MODEL_NAME = r"sphere_20k.obj"
    positionStr = r"0.1988,-0.09269,0"
    # positionStr = r"0.199,-0.126,0"
    generics = "10"
    genericStart = "0.01"
    genericEnd = "0.40"
    # genericRoughnesses = "0.13,0.16,0.20,0.25,0.30,0.4,0.5,0.6,0.7"
    resolution = "256"
    faceID = "5"

    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT
        # -----------------------------------------------------------------------------------------------
        # Mirror
        BALL_TYPE = r"Mirror"
        OBJECT = BALL_TYPE
        OBJECT_ROOT = os.path.join(CONFIG_ROOT, OBJECT)

        modelDirectory =os.path.join(COMMON_ROOT, "Model", "sphere",BALL_TYPE)
        modelFile = os.path.join(modelDirectory, MODEL_NAME)

        framesDirectory =os.path.join(OBJECT_ROOT,"Frames")

        # CapSim synthetic
        if CapSimSpecOption:
            logger.info("CapSim mirror :")
            re = subprocess.run(["CapSim", "-framesDirectory="+framesDirectory, "-modelFile=" + modelFile,
                                 "-panelConfig=" + panelConfig, "-cameraConfig="+cameraConfig, "-poseConfig="+poseConfig,
                                 "-bounding", "-boundingRadius=1","--nonLocal","-positionStr="+positionStr],
                                stdout=True, stderr=True, check=True)

        inputFramesCol = os.path.join(framesDirectory, r"result_c%04d.pfm")
        curveFileCol = os.path.join(framesDirectory, r"curveCol.cur")
        inputFramesRow = os.path.join(framesDirectory, r"result_r%04d.pfm")
        curveFileRow = os.path.join(framesDirectory, "curveRow.cur")
        curveCSVCol = os.path.join(framesDirectory, "curveCol.csv")
        curveCSVRow = os.path.join(framesDirectory, "curveRow.csv")
        posFile = os.path.join(framesDirectory, "pos.pfm")
        nrmFile = os.path.join(framesDirectory,  "nrm.pfm")
        maskFile =os.path.join(framesDirectory, "mask.pfm")

        recoverDirectory = os.path.join(OBJECT_ROOT, "Recover", BALL_TYPE)
        tableFile = os.path.join(recoverDirectory, "nrmTab.pfm")
        tableCountFile = os.path.join(recoverDirectory, "nrmTabCnt.pfm")

        # CapTab Mirror
        if CapTabSpecOption:
            logger.info("CapTab spec :")
            re = subprocess.run(["CapTab", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                 "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                                 "-curveFileRow=" + curveFileRow, "-curveFileCol=" + curveFileCol,
                                 "-curveCSVRow=" + curveCSVRow, "-curveCSVCol=" + curveCSVCol,
                                 "-posFile=" + posFile, "-positionStr="+positionStr,
                                 "-nrmFile=" + nrmFile, "-maskFile=" + maskFile, "-tableFile=" + tableFile,
                                 "-tableCountFile=" + tableCountFile, "-saveCurve", "--saveCSV","-useLightAVG"],
                                stdout=True, stderr=True, check=True)

        iterDirectory = os.path.join(recoverDirectory, "Iter")
        basesDirectory =os.path.join(iterDirectory ,"Bases")
        # CapPreNr spec
        if CapPreNrSpecOption:
            logger.info("CapPreNr spec: ")
            re = subprocess.run(["CapPreNr", "-basesDirectory="+basesDirectory,"-generics="+generics,
                                 "-genericStart="+genericStart,"-genericEnd="+genericEnd,
                                 # "-genericRoughnesses=" + genericRoughnesses,
                                 "-panelConfig=" + panelConfig, "-cameraConfig=" + cameraConfig,
                                 "-poseConfig="+poseConfig, "-render","-saveCurve", "-resolution="+resolution,
                                 "-faceID="+faceID,"-positionStr="+positionStr,"--diffBase"],
                                stdout=True, stderr=True, check=True)
        # -----------------------------------------------------------------------------------------------
        # Diffuse
        BALL_TYPE = r"Diffuse"
        OBJECT = BALL_TYPE

        OBJECT_ROOT = os.path.join(CONFIG_ROOT, OBJECT)

        modelDirectory = os.path.join(COMMON_ROOT, "Model","sphere", BALL_TYPE)
        modelFile = os.path.join(modelDirectory, MODEL_NAME)

        framesDirectory = os.path.join(OBJECT_ROOT, "Frames")

        # CapSim synthetic
        if CapSimDiffOption:
            logger.info("CapSim diff :")
            re = subprocess.run(["CapSim", "-framesDirectory=" + framesDirectory, "-modelFile=" + modelFile,
                                 "-panelConfig=" + panelConfig, "-cameraConfig=" + cameraConfig,
                                 "-poseConfig=" + poseConfig,
                                 "-bounding", "-boundingRadius=1", "--nonLocal", "-positionStr=" + positionStr],
                                stdout=True, stderr=True, check=True)

        inputFramesCol = os.path.join(framesDirectory, r"result_c%04d.pfm")
        curveFileCol = os.path.join(framesDirectory, r"curveCol.cur")
        inputFramesRow = os.path.join(framesDirectory, r"result_r%04d.pfm")
        curveFileRow = os.path.join(framesDirectory, "curveRow.cur")
        curveCSVCol = os.path.join(framesDirectory, "curveCol.csv")
        curveCSVRow = os.path.join(framesDirectory, "curveRow.csv")
        posFile = os.path.join(framesDirectory, "pos.pfm")
        nrmFile = os.path.join(framesDirectory, "nrm.pfm")
        maskFile = os.path.join(framesDirectory, "mask.pfm")

        recoverDirectory = os.path.join(OBJECT_ROOT, "Recover", BALL_TYPE)
        tableFile = os.path.join(recoverDirectory, "nrmTab.pfm")
        tableCountFile = os.path.join(recoverDirectory, "nrmTabCnt.pfm")

        # CapTab Diff
        if CapTabDiffOption:
            logger.info("CapTab diff :")
            re = subprocess.run(["CapTab", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                 "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                                 "-curveFileRow=" + curveFileRow, "-curveFileCol=" + curveFileCol,
                                 "-curveCSVRow=" + curveCSVRow, "-curveCSVCol=" + curveCSVCol,
                                 "-posFile=" + posFile, "-positionStr="+positionStr,
                                 "-nrmFile=" + nrmFile, "-maskFile=" + maskFile, "-tableFile=" + tableFile,
                                 "-tableCountFile=" + tableCountFile, "-saveCurve", "--saveCSV","-useLightAVG"],
                                stdout=True, stderr=True, check=True)

        iterDirectory = os.path.join(recoverDirectory, "Iter")
        basesDirectory = os.path.join(iterDirectory, "Bases")
        # CapPreNr diff
        if CapPreNrDiffOption:
            logger.info("CapPreNr diff: ")
            re = subprocess.run(["CapPreNr", "-basesDirectory=" + basesDirectory, "-generics=" + generics,
                                 "-genericStart=" + genericStart, "-genericEnd=" + genericEnd,
                                 "-panelConfig=" + panelConfig, "-cameraConfig=" + cameraConfig,
                                 "-poseConfig=" + poseConfig, "-render", "-saveCurve", "-resolution=" + resolution,
                                 "-faceID=" + faceID, "-positionStr=" + positionStr, "-diffBase"],
                                stdout=True, stderr=True, check=True)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
