# SfM data preparation.
# V0: Origin
import os
import subprocess
import shutil
import logging

# SfM data preparation.
# V0: Origin
import os
import subprocess
import shutil
import logging

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    # OBJECT = r"Object-testkitty"
    OBJECT = r"Object-testpig"
    # BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    BUILD_ROOT = r"D:\v-jiazha\2-workspaces\Source\ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    OBJECT_ROOT = os.path.join(DATA_ROOT,r'Object', OBJECT)
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')
    COMMON_SINGLE_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\RealCommon"
    MODEL_NAME = r"Pig/Pig_160608.obj"
    # MODEL_NAME = r"Kitty_160420.obj"
    positionStr = r"0.199,-0.126,0"
    nViews = 1
    generics = "10"
    genericStart = "0.01"
    genericEnd = "0.20"
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
            configDirectory =os.path.join(COMMON_ROOT, "Setups", "Setup_%04d" % v, "Config")
            panelConfig = os.path.join(configDirectory, "panelConfig.txt")
            # just test gl rendering
            # panelConfig = os.path.join(COMMON_ROOT, "Setups", "SetupNoLight", "Config", "panelConfig.txt")
            cameraConfig = os.path.join(configDirectory, "cameraConfig.txt")
            poseConfig = os.path.join(configDirectory, "poseConfig.txt")

            gtNrm = os.path.join(framesDirectory,"nrm.pfm")
            gtPos = os.path.join(framesDirectory,"pos.pfm")
            constantPos = os.path.join(framesDirectory, "posConstant.pfm")

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

            modelName = "re" + "RecWithDepthConstraintO2NCC"
            recoverDirName = "re_RGBN_DptCon"

            outputDir = os.path.join(combIterFinal, recoverDirName)
            viewPosImgFile = os.path.join(outputDir, "pos.pfm")
            viewDistImgFile = os.path.join(outputDir, "distR.pfm")
            viewDepthImgFile = os.path.join(outputDir, "depthR.pfm")
            viewDepTruthImgFile = os.path.join(framesDirectory, "depth.pfm")
            viewMaskImgFile = os.path.join(framesDirectory, "mask.pfm")

            logger.info("CapRefine view: {0}th".format(v))
            re = subprocess.run(["CapRefineNr", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                 "-specRouWeightFile=" + combRouWeight, "-diffWeightFile=" + combDiffWeight,
                                 "-nrmFile=" + combNrm, "-posFile=" + viewPosImgFile,"-maskFile=" + viewMaskImgFile,
                                 "-nrmTruthFile=" + gtNrm,
                                 "-generics=" + generics,"-genericStart=" + genericStart,"-genericEnd=" + genericEnd,
                                 "-threshold="+threshold],
                                stdout=True, stderr=True, check=True)
            print(re.args)
    finally:
        os.environ.clear()
        os.environ.update(_environ)
