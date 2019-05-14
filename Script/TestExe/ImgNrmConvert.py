# SfM data preparation.
# V0: Origin
import os
import subprocess
import shutil
import logging


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    ImageMagicPath = r"C:/Program Files/ImageMagick-7.0.8-Q16-HDRI"
    BUILD_ROOT = r"D:\v-jiazha\2-workspaces\Source\ObjectCap\x64\Release"
    TOOL_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    DATA_ROOT_E = r"E:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    TOOL_LCT_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool\LCT"
    COMMON_ROOT = os.path.join(DATA_ROOT, r'RealCommon')
    CONFIG_ROOT = os.path.join(COMMON_ROOT, r"Config0301")

    # OBJECT = r"RealObject-pig2"
    # OBJECT = r"RealObject-penrack3"
    # OBJECT = r"RealObject-pig2"
    # OBJECT = r"RealObject-oatmeal"
    # OBJECT = r"RealObject-oatmeal2"
    OBJECT = r"RealObject-cookies"
    # OBJECT = r"RealObject-gift1"
    # OBJECT = r"RealObject-gift2"
    # OBJECT = r"RealObject-cookies2"
    OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object', OBJECT)
    # OBJECT_ROOT = os.path.join(DATA_ROOT_E, r'Object', OBJECT)
    # OBJECT_ROOT = r"C:\v-jiazha\RealObject-penrack3"
    OBJECT_ViewDir = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
    OBJECT_CalibPrismDir = os.path.join(OBJECT_ROOT, "CalibPrism")
    SfM_ROOT = os.path.join(OBJECT_ROOT, r'SfMExpo')
    SfM_ImagesDir = os.path.join(SfM_ROOT, r'images')
    nViews = 36

    # Setup setting: camera, panel pose
    panelConfig = os.path.join(CONFIG_ROOT, "Setup" + OBJECT, "panelConfig.txt")
    cameraConfig = os.path.join(CONFIG_ROOT, "Setup" + OBJECT, "cameraConfig.txt")
    poseConfig = os.path.join(CONFIG_ROOT, "Setup" + OBJECT, "poseConfig.txt")

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
            framesDirectory = os.path.join(viewDirectory, "Frames")
            nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
            nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesCombine")
            nrmRefineIterFinalDir = os.path.join(nrmRefineDirectory, "Iter", "Iter_final")
            diffWeight = os.path.join(nrmRefineIterFinalDir,"Base_diffuse","weight.pfm")
            featImg = os.path.join(nrmRefineIterFinalDir,"combineFeat.pfm")
            nrmRecImg = os.path.join(nrmRefineIterFinalDir,"nrmR.pfm")
            recNrmDirName = r"refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.1_nDptIters=1"
            nrmInObj = os.path.join(nrmRefineDirectory,recNrmDirName,"nrmInObj.pfm")
            # fullOn = os.path.join(framesDirectory,"origin_full.jpg")
            # imageSrc = diffWeight
            # imageSrc = featImg
            imageSrc = nrmRecImg
            # imageSrc = fullOn
            # imageSrc = nrmInObj
            # imageSrcName = "result_r0001.pfm"
            # imageSrcName = "result_c0100.pfm"
            # imageSrc = os.path.join(framesDirectory, imageSrcName)
            imageTar = os.path.join(SfM_ImagesDir, "image%02d.jpg" % (v+1))

            logger.info("Moving view: {0}th".format(v))
            re = subprocess.run(["ImgNrmConvert", "-in="+imageSrc, "-out=" + imageTar,"-scaleOpt","-expo="+"2.2"], capture_output=True, check=True)



    finally:
        os.environ.clear()
        os.environ.update(_environ)
