# SfM data preparation.
# V0: Origin
import os
import subprocess
import shutil
import logging


if __name__ == "__main__":
    CapSimOption = 0
    CapNrDiffOption = 1
    CapNrSpecOption = 0
    CapFitDiffOption = 0
    CapFitSpecOption = 0
    CapCombineOption = 0
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    # OBJECT = r"Object-testkitty"
    OBJECT = r"Object-testpig"
    BUILD_ROOT = r"D:\v-jiazha\2-workspaces\Source\ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    OBJECT_ROOT = os.path.join(DATA_ROOT,r'Object', OBJECT)
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')
    COMMON_SINGLE_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\RealCommon"
    MODEL_NAME = r"Pig/Pig_160608.obj"
    # MODEL_NAME = r"Kitty_160420.obj"
    positionStr = r"0.199,-0.126,0"
    nViews = 1
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
            # framesDirectory =os.path.join(viewDirectory,"nrmTest")
            framesDirectory =os.path.join(viewDirectory,"FramesDownsample")
            configDirectory =os.path.join(COMMON_ROOT, "Setups", "Setup_%04d" % v, "Config")
            panelConfig = os.path.join(configDirectory, "panelConfig.txt")
            # just test gl rendering
            # panelConfig = os.path.join(COMMON_ROOT, "Setups", "SetupNoLight", "Config", "panelConfig.txt")
            cameraConfig = os.path.join(configDirectory, "cameraConfig.txt")
            poseConfig = os.path.join(configDirectory, "poseConfig.txt")

            # CapSim synthetic
            if CapSimOption:
                logger.info("CapSim view: {0}th".format(v))
                re = subprocess.run(["CapSim", "-framesDirectory="+framesDirectory, "-modelFile=" + modelFile,
                                 "-panelConfig="+panelConfig, "-cameraConfig="+cameraConfig, "-poseConfig="+poseConfig,
                                 "-bounding", "-boundingRadius=1","--nonLocal","-positionStr="+positionStr],
                                stdout = True, stderr=True, check=True)

            # inputFramesCol = os.path.join(framesDirectory, r"nrm_0000_col_%04d.pfm")
            # curveFileCol = os.path.join(framesDirectory, r"nrm_0000_curveCol.cur")
            # inputFramesRow = os.path.join(framesDirectory, r"nrm_0000_row_%04d.pfm")
            # curveFileRow = os.path.join(framesDirectory, "nrm_0000_curveRow.cur")
            # curveCSVCol = os.path.join(framesDirectory, "nrm_0000_curveCol.csv")
            # curveCSVRow = os.path.join(framesDirectory, "nrm_0000_curveRow.csv")
            inputFramesCol = os.path.join(framesDirectory, r"result_c%04d.pfm")
            curveFileCol = os.path.join(framesDirectory, r"curveCol.cur")
            inputFramesRow = os.path.join(framesDirectory, r"result_r%04d.pfm")
            curveFileRow = os.path.join(framesDirectory, "curveRow.cur")
            curveCSVCol = os.path.join(framesDirectory, "curveCol.csv")
            curveCSVRow = os.path.join(framesDirectory, "curveRow.csv")
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
            # rowScanWidth = "224"
            # rowScanHeight = "4"
            # colScanWidth = "4"
            # colScanHeight = "736"
            rowScanWidth = "7"
            rowScanHeight = "1"
            colScanWidth = "1"
            colScanHeight = "23"

            BALL_TYPE = r"Diffuse"
            recoverDirectory = os.path.join(viewDirectory, "Recover_nrmTest", BALL_TYPE)
            tableFile = os.path.join(COMMON_SINGLE_ROOT, BALL_TYPE, "Recover" ,BALL_TYPE, "nrmTab.pfm")
            nrmRFile =os.path.join(recoverDirectory, "nrmR.pfm")
            nrmSFile =os.path.join(recoverDirectory, "nrmS.pfm")
            nrmDFile =os.path.join(recoverDirectory, "nrmD.pfm")
            loggingFile =os.path.join(recoverDirectory,"logging.txt")

            # CapNr diffuse
            if CapNrDiffOption:
                logger.info("CapParseCur diffuse view: {0}th".format(v))
                re = subprocess.run(["CapParseCur", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                     "-inputFramesRow="+inputFramesRow,"-inputFramesCol="+inputFramesCol,
                                     "-curveFileRow="+curveFileRow, "-curveFileCol="+curveFileCol,
                                     "-curveCSVRow="+curveCSVRow, "-curveCSVCol="+curveCSVCol,"-sigma="+sigma,
                                     "-hWidth="+hWidth,"-positionStr="+positionStr,"-saveCurve","--saveCSV",
                                     "--useLightAVG", "-scale="+scale, "-maskFile="+maskFile,
                                     "-rowScanWidth="+rowScanWidth,"-rowScanHeight="+rowScanHeight,
                                     "-colScanWidth="+colScanWidth,"-colScanHeight="+colScanHeight],
                                        stdout=True, stderr=True, check=True)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
