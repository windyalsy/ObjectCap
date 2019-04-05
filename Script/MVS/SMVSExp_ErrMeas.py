# SfM data preparation.
# V0: Origin
import os
import subprocess
import shutil
import logging


if __name__ == "__main__":
    ErrorMeasOption = 3
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

        modelDirectory =os.path.join(COMMON_ROOT, "Model")
        modelFile = os.path.join(modelDirectory, MODEL_NAME)
        # viewConfigDirectory=$COMMON_ROOT/Setups/Setup_%04d/Config

        viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
        framesDirectory =os.path.join(viewDirectory,"Frames")
        configDirectory = os.path.join(COMMON_ROOT, "Setups", "Setup", "Config")
        viewConfigDirectory =os.path.join(COMMON_ROOT, "Setups", "Setup_%04d", "Config")
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

        viewRGBImgFile = combDiffWeight
        viewNrmImgFile = combNrm

        # recoverDirName = "re_RGBN"
        recoverDirName = "re_RGBN_DptCon"
        recoverOutputDir = os.path.join(combIterFinal, recoverDirName)
        modelName = "re" + "WithGivenDepth"

        viewDepTruthImgFile = os.path.join(framesDirectory, "depth.pfm")
        viewMaskImgFile = os.path.join(framesDirectory, "mask.pfm")
        # viewMaskImgFile = os.path.join(combIterFinal, "nrmDMsk.pfm")
        # viewMaskImgFile = os.path.join(combIterFinal, "specMsk.pfm")
        # viewMaskImgFile=$combIterFinal/nrmDMsk.pfm
        # modelName = "model" + "RecWithoutDepthConstraintO2NCC"

        if ErrorMeasOption == 3:
            outputDir = os.path.join(combIterFinal, "re_depth_DptCon_errMeas")
            viewDistImgFile = os.path.join(outputDir, "distR.pfm")
            viewDepthImgFile = os.path.join(recoverOutputDir, "depthR.pfm")

        if ErrorMeasOption == 2:
            outputDir = os.path.join(combIterFinal, "gt_depth_errMeas")
            viewDistImgFile = os.path.join(outputDir, "distR.pfm")
            viewDepthImgFile = os.path.join(framesDirectory, "depth.pfm")

        if ErrorMeasOption == 1:
            outputDir = os.path.join(combIterFinal, "re_depth_errMeas")
            viewDistImgFile = os.path.join(outputDir, "distR.pfm")
            viewDepthImgFile = os.path.join(recoverOutputDir, "depthR.pfm")

        rgbWeight = "1"
        nrmWeight = "100"
        dptWeight = "1"
        minDepth = "1.1"
        maxDepth = "1.2"
        nNeighbors = "6"
        nSteps = "1001"
        nRefineIters = "2"
        nRefineSteps = "9"
        nDptIters = "0"
        nFirstKNeighborsForCost = "4"
        nViews = "36"
        checkW = "385"
        checkH = "275"
        positionStr = "0.199,-0.126,0"

        logger.info("Experiment_ErrMeas")
        re = subprocess.run(["Experiment_ErrMeas", "-cameraConfig="+cameraConfig, "-poseConfig="+poseConfig,
                             "-viewFramesDirectory="+outputDir, "-viewRGBImgFile=" + viewRGBImgFile,
                             "-viewNrmImgFile="+viewNrmImgFile, "-viewDistImgFile=" + viewDistImgFile,
                            "-viewDepthImgFile=" + viewDepthImgFile,
                             "-viewDepTruthImgFile="+viewDepTruthImgFile, "-viewMaskImgFile=" + viewMaskImgFile,
                             "-modelName=" + modelName,"-rgbWeight=" + rgbWeight,"-nrmWeight=" + nrmWeight,
                             "-dptWeight=" + dptWeight, "-nDptIters=" + nDptIters,
                             "-minDepth=" + minDepth, "-maxDepth=" + maxDepth, "-nNeighbors=" + nNeighbors,
                             "-nSteps="+nSteps, "-nRefineIters="+nRefineIters, "-nRefineSteps="+nRefineSteps,
                             "-nFirstKNeighborsForCost=" + nFirstKNeighborsForCost,"-nViews="+nViews,
                             "-checkW="+checkW, "-checkH="+checkH, "--checkOption"],
                        stdout = True, stderr=True, check=True)

    finally:
        os.environ.clear()
        os.environ.update(_environ)


