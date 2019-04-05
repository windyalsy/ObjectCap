# Project recovered object into other veiws
# V0: Origin
import os
import subprocess
import shutil
import logging


if __name__ == "__main__":
    CapSimOption = 1
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    OBJECT = r"Object-testkitty"
    BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    OBJECT_ROOT = os.path.join(DATA_ROOT,r'Object', OBJECT)
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')
    COMMON_SINGLE_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\RealCommon"
    MODEL_NAME = r"beforeConvert_modelGWithDepthConstraint.obj"
    positionStr = r"0.199,-0.126,0"
    nViews = 36
    nNeigh = 6
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
            viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
            combIterFinal =os.path.join(viewDirectory, "Recover/Combine/Iter/Iter_final")
            modelFile = os.path.join(combIterFinal, MODEL_NAME)
            for i in range( -nNeigh // 2, nNeigh // 2):
                id = (int(i + v + nViews) % int(nViews))
                configDirectory =os.path.join(COMMON_ROOT, "Setups", "Setup_%04d" % id, "Config")
                poseConfig = os.path.join(configDirectory, "poseConfig.txt")
                cameraConfig = os.path.join(configDirectory, "cameraConfig.txt")
                panelConfig = os.path.join(COMMON_ROOT, "Setups", "SetupNoLight", "Config", "panelConfig.txt")
                framesDirectory = os.path.join(combIterFinal,"Project_2_%04d" % id)

                # CapSim synthetic
                if CapSimOption:
                    logger.info("CapSim view: {0}th".format(i))
                    re = subprocess.run(["CapSim", "-framesDirectory="+framesDirectory, "-modelFile=" + modelFile,
                                     "-panelConfig="+panelConfig, "-cameraConfig="+cameraConfig, "-poseConfig="+poseConfig,
                                     "--bounding", "-boundingRadius=1","--nonLocal","-positionStr="+positionStr, "-flipZ","-flipVC"],
                                    stdout = True, stderr=True, check=True)


    finally:
        os.environ.clear()
        os.environ.update(_environ)
