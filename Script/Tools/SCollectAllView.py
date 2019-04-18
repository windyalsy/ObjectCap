# extract each view's camera extrinsic
import os
import subprocess
import logging

def CollectAllView(OBJECT):
    ImageMagicPath = r"C:/Program Files/ImageMagick-7.0.8-Q16-HDRI"
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    # DATA_ROOT_E = r"E:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    TOOL_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool"
    COMMON_ROOT = os.path.join(DATA_ROOT, r'RealCommon')

    CALIBPRISM_BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\5-Deployment\CalibrationPrism"

    # OBJECT = r"RealObject-penrack"
    OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object', OBJECT)

    nviews = 36
    v_size = 184
    u_size = 224
    nIndex = 409

    collectViewDir = os.path.join(OBJECT_ROOT,  "Experiment","FramesCollection")
    if not os.path.exists(collectViewDir):
        os.makedirs(collectViewDir)
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
            src = os.path.join(viewDirectory,r"Recover\NrmRefine\Experiment\Frames\nrmObj.pfm")
            tar = os.path.join(collectViewDir,"View_%04d_prjNrm.jpg"%v)


            # src = os.path.join(r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-cookiesMerge\SfMCookie\images","image%02d.jpg"%(v+1))
            # tar = os.path.join(collectViewDir,"View_%04d_diff.jpg"%v)

            # cr2 convert to jpg
            re = subprocess.run(["magick.exe", src, tar], stdout=True, stderr=True, check=True)


    finally:
        os.environ.clear()
        os.environ.update(_environ)

if __name__ == "__main__":
    OBJECT = r"RealObject-cookies"
    CollectAllView(OBJECT)