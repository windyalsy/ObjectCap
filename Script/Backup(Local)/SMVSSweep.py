# SfM data preparation.
# V0: Origin
import os
import subprocess
import shutil
import logging


if __name__ == "__main__":
    MVSSweepOption = 1
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    # OBJECT = r"Object-testkitty"
    OBJECT = r"Object-testpig"
    BUILD_ROOT = r"D:/1-workspace/7-visual_studio_2017/Source/ObjectCap/x64/Release"
    DATA_ROOT = r"D:\4-projects\5-LED\2-Source\4-MVS"
    OBJECT_ROOT = os.path.join(DATA_ROOT,r'Object', OBJECT)
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')
    COMMON_SINGLE_ROOT = r"D:\4-projects\5-LED\2-Source\RealCommon"
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

        viewRGBImgFile = os.path.join(framesDirectory, "diff.pfm")
        viewNrmImgFile = os.path.join(framesDirectory, "nrm.pfm")
        # viewRGBImgFile=combDiffWeight
        # viewNrmImgFile=combNrm
        viewDistImgFile = os.path.join(combIterFinal, "distR.pfm")
        viewDepthImgFile = os.path.join(combIterFinal, "depthR.pfm")
        viewDepTruthImgFile = os.path.join(framesDirectory, "depth.pfm")
        # temporaly use diff(ground truth) as mask
        viewMaskImgFile = os.path.join(framesDirectory, "diff.pfm")
        # viewMaskImgFile = os.path.join(framesDirectory, "nrmDMsk.pfm")
        # viewMaskImgFile=$combIterFinal/nrmDMsk.pfm
        modelName = "model" + "RecWithDepthConstraintO2SAD"
        rgbWeight = "0.1"
        nrmWeight = "10"
        dptWeight = "10"
        minDepth = "1.0"
        maxDepth = "1.3"
        nNeighbors = "4"
        nSteps = "1001"
        nRefineIters = "1"
        nRefineSteps = "9"
        nDptIters = "5"
        nFirstKNeighborsForCost = "2"
        nViews = "36"
        checkW = "330"
        checkH = "205"
        positionStr = "0.199,-0.126,0"
        # Sweep
        if MVSSweepOption:
            logger.info("RGBNPlaneSweepMVS")
            re = subprocess.run(["RGBNPlaneSweepMVS", "-cameraConfig="+cameraConfig, "-poseConfig="+poseConfig,
                                 "-viewFramesDirectory="+combIterFinal, "-viewRGBImgFile=" + viewRGBImgFile,
                                 "-viewNrmImgFile="+viewNrmImgFile, "-viewDistImgFile=" + viewDistImgFile,
                                "-viewDepthImgFile=" + viewDepthImgFile,
                                 "-viewDepTruthImgFile="+viewDepTruthImgFile, "-viewMaskImgFile=" + viewMaskImgFile,
                                 "-modelName=" + modelName,"-rgbWeight=" + rgbWeight,"-nrmWeight=" + nrmWeight,
                                 "-dptWeight=" + dptWeight, "-nDptIters=" + nDptIters,
                                 "-minDepth=" + minDepth, "-maxDepth=" + maxDepth, "-nNeighbors=" + nNeighbors,
                                 "-nSteps="+nSteps, "-nRefineIters="+nRefineIters, "-nRefineSteps="+nRefineSteps,
                                 "-nFirstKNeighborsForCost=" + nFirstKNeighborsForCost,"-nViews="+nViews,
                                 "-checkW="+checkW, "-checkH="+checkH,"-checkOption"],
                            stdout = True, stderr=True, check=True)

    finally:
        os.environ.clear()
        os.environ.update(_environ)


