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
    SrcHeadPath = r"D:"
    TarHeadPath = r"\\minigpu2"
    BUILD_ROOT = r"v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    DATA_ROOT = r"v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    OBJECT_ROOT = os.path.join(DATA_ROOT,r'Object', OBJECT)
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')
    SETUPS_ROOT = os.path.join(COMMON_ROOT,r'Setups')
    nViews = 36
    pi = 3.1415926
    scope = pi
    offset = 2 * pi / nViews
    scale = "0.1 0.1 0.1"
    position = "0.199 -0.126 0"
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT

        for v in range(nViews):
            logger.info("Move view: {0}th".format(v))
            viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
            combIterFinal = os.path.join(viewDirectory, "Recover/Combine/Iter/Iter_final")
            srcDir = os.path.join(SrcHeadPath, combIterFinal)
            tarDir = os.path.join(TarHeadPath, combIterFinal)
            # if tar dir exists, delete it.
            if os.path.exists(tarDir):
                shutil.rmtree(tarDir)
            # copy directory
            shutil.move(srcDir,tarDir)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
