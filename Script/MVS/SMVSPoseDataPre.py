# MVS synthetic multiple-view setup data preparation.
# V0: Origin
import os
import subprocess
import shutil
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    OBJECT = r"Object-testpig"
    BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    OBJECT_ROOT = os.path.join(DATA_ROOT,r'Object', OBJECT)
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')
    SETUPS_ROOT = os.path.join(COMMON_ROOT,r'Setups')
    nViews = 36
    pi = 3.1415926
    scope = pi
    offset = 2 * pi / nViews
    scale = "0.1 0.1 0.1"
    position = "0.199 -0.126 0"
    sourceDirectory = os.path.join(SETUPS_ROOT,r"Setup/Config")

    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT

        for v in range(nViews):
            logger.info("Create view: {0}th".format(v))
            rotationY = v *offset
            rotation = "0 {0} 0".format(rotationY)
            # if view setup dir exists, delete it.
            viewSetupDir = os.path.join(SETUPS_ROOT, "Setup_%04d" % v)
            if os.path.exists(viewSetupDir):
                shutil.rmtree(viewSetupDir)
            # copy directory
            shutil.copy(sourceDirectory,viewSetupDir)
            
            # rewrite pose.txt
            poseConfig = os.path.join(viewSetupDir,r"Config","poseConfig.txt")
            os.remove(poseConfig)
            file = open(poseConfig,"w")
            file.write(scale + "\n")
            file.write(position + "\n")
            file.write(rotation + "\n")

    finally:
        os.environ.clear()
        os.environ.update(_environ)
