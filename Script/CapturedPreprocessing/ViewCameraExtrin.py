# extract each view's camera extrinsic
import os
import subprocess
import logging

def ViewCameraExtrin(OBJECT):
    ImageMagicPath = r"C:/Program Files/ImageMagick-7.0.8-Q16-HDRI"
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    TOOL_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool"
    COMMON_ROOT = os.path.join(DATA_ROOT, r'RealCommon')

    CALIBPRISM_BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\5-Deployment\CalibrationPrism"

    # OBJECT = r"RealObject-penrack"
    OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object', OBJECT)

    DEPLOYMENT_ROOT = r"D:\v-jiazha\4-projects\5-LED\5-Deployment\CapController\Data_Dir\image"
    SRC_ROOT = os.path.join(DEPLOYMENT_ROOT, OBJECT)
    # SRC_ROOT = os.path.join(DEPLOYMENT_ROOT, "Scan")

    COMMON_PRISM_ROOT = os.path.join(COMMON_ROOT, r"CalibPrism\Prism")

    # commmon file for current prism
    intrinsic = os.path.join(COMMON_PRISM_ROOT, "intrin.txt")
    faceTrans = os.path.join(COMMON_PRISM_ROOT, "faceTrans.txt")
    objectPoints = os.path.join(COMMON_PRISM_ROOT, "pointList.txt")

    OBJECT_PRISM_ROOT = os.path.join(OBJECT_ROOT, r'CalibPrism')
    if not os.path.exists(OBJECT_PRISM_ROOT):
        os.makedirs(OBJECT_PRISM_ROOT)

    detectDir = os.path.join(OBJECT_PRISM_ROOT, r'Detect')
    if not os.path.exists(detectDir):
        os.makedirs(detectDir)
    # detectDir = OBJECT_PRISM_ROOT

    extrinsicDir = os.path.join(OBJECT_PRISM_ROOT, r'Extrinsic')
    if not os.path.exists(extrinsicDir):
        os.makedirs(extrinsicDir)
    # imageList need to be created
    imageList = os.path.join(OBJECT_PRISM_ROOT, "imageList.txt")
    imagePointList = os.path.join(OBJECT_PRISM_ROOT, "imagePointList.txt")
    imageListFile = open(imageList, "w")
    imagePointListFile = open(imagePointList, "w")

    nviews = 36
    v_size = 184
    u_size = 224
    nIndex = 409

    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ[
                                     'PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT + ";" + CALIBPRISM_BUILD_ROOT + ";" + ImageMagicPath
        else:
            os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT + ";" + CALIBPRISM_BUILD_ROOT + ";" + ImageMagicPath

        # data prepare
        logging.info("Data prepare")
        for v in range(nviews):

            viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
            framesDirectory = os.path.join(viewDirectory, "Frames")
            srcViewDirectory = os.path.join(SRC_ROOT, "Views", "View_%04d" % v)
            srcFramesDirectory = os.path.join(srcViewDirectory, "Frames")

            src = os.path.join(srcFramesDirectory, r"result__IMG_%04d.cr2" % nIndex)
            tar = os.path.join(OBJECT_PRISM_ROOT, r"view_%04d.jpg" % v)
            # cr2 convert to jpg
            re = subprocess.run(["magick.exe", src, tar], stdout=True, stderr=True, check=True)
            imageListFile.write(tar + "\n")

            pointFile = os.path.join(detectDir, r"view_%04d.txt" % v)
            imagePointListFile.write(pointFile + "\n")
        imageListFile.close()
        imagePointListFile.close()

        # find pattern sequence
        re = subprocess.run(["FindPatternSeq", "--intrinsic=" + intrinsic, "--faceTrans=" + faceTrans,
                             "--imageList=" + imageList, "--outputDir=" + detectDir],
                            stdout=True, stderr=True, check=True)

        # # calculate camera extrinsic
        print(objectPoints)
        re = subprocess.run(["CalcExtrinsic", "--objectPoints=" + objectPoints, "--imageList=" + imageList, "--imagePointList=" + imagePointList,
                             "--intrinsic=" + intrinsic, "--extrinsic=" + extrinsicDir],
                            stdout=True, stderr=True, check=True)
    finally:
        os.environ.clear()
        os.environ.update(_environ)

if __name__ == "__main__":
    OBJECT = r"RealObject-mouse"
    ViewCameraExtrin(OBJECT)