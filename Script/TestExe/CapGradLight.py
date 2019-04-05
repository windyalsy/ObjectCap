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
    # MODEL_NAME = r"hat/basic_fedora_hat_1302.obj"
    # MODEL_NAME = r"Sphere/Mirror/sphere_20k.obj"
    # MODEL_NAME = r"Sphere/Diffuse/sphere_20k.obj"
    positionStr = r"0.199,-0.126,0"
    resolution = "1000"
    distance = "100"
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
            framesDirectory =os.path.join(viewDirectory,"FramesGrad")
            configDirectory =os.path.join(COMMON_ROOT, "Setups", "Setup_%04d" % v, "Config")
            panelConfig = os.path.join(configDirectory, "panelConfig.txt")
            # just test gl rendering
            # panelConfig = os.path.join(COMMON_ROOT, "Setups", "SetupNoLight", "Config", "panelConfig.txt")
            cameraConfig = os.path.join(configDirectory, "cameraConfig.txt")
            poseConfig = os.path.join(configDirectory, "poseConfig.txt")

            logger.info("CapGradLight view: {0}th".format(v))
            re = subprocess.run(["CapGradLight", "-framesDirectory="+framesDirectory, "-modelFile=" + modelFile,
                             "-panelConfig="+panelConfig, "-cameraConfig="+cameraConfig, "-poseConfig="+poseConfig,
                             "-bounding", "-boundingRadius=1","--nonLocal","-positionStr="+positionStr,"-resolution=" + resolution,
                                 "-distance="+distance],
                            stdout = True, stderr=True, check=True)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
