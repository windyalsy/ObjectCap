# SfM data preparation.
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
    SfM_ROOT = os.path.join(OBJECT_ROOT, r'SfM')
    SfM_ImagesDir = os.path.join(SfM_ROOT, r'images')
    nViews = 36
    # imageSrcName = r"weight.pfm"
    imageSrcName = r"diff.pfm"
    if not os.path.exists(SfM_ImagesDir):
        os.makedirs(SfM_ImagesDir)
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT

        for v in range(nViews):
            viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
            # diffAlbedoDirectory = os.path.join(viewDirectory, "Recover/Combine/Iter/Iter_final/Base_diffuse")
            diffAlbedoDirectory = os.path.join(viewDirectory, "Frames")
            imageSrc = os.path.join(diffAlbedoDirectory, imageSrcName)
            imageTar = os.path.join(SfM_ImagesDir, "image%d.jpg" % (v+1))

            logger.info("Moving view: {0}th".format(v))
            re = subprocess.run(["ImageConvert", "-in="+imageSrc, "-out=" + imageTar],stdout=True, stderr=True, check=True)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
