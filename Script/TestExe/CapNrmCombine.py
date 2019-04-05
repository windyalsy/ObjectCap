# CapNrmCombine: combine all views' textures together.
# V0: Origin
import os
import subprocess
import shutil
import logging


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    BUILD_ROOT = r"D:\v-jiazha\2-workspaces\Source\ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')
    CONFIG_ROOT = os.path.join(COMMON_ROOT,r"Config0301")

    OBJECT = r"RealObject-pig2"
    # OBJECT = r"RealObject-penrack"
    OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object', OBJECT)
    OBJECT_ViewDir = os.path.join(OBJECT_ROOT, "Views", "View_%04d")

    panelConfig = os.path.join(CONFIG_ROOT, "Setup", "panelConfig.txt")
    cameraConfig = os.path.join(CONFIG_ROOT, "Setup", "cameraConfig.txt")
    poseConfig = os.path.join(CONFIG_ROOT, "Setup", "poseConfig.txt")

    # MODEL_NAME = r"Pig/Pig_160608.obj"
    # MODEL_NAME = r"Kitty_160420.obj"
    MODEL_NAME = r"sphere_20k.obj"
    positionStr = r"0.1988,-0.09269,0"
    # positionStr = r"0.199,-0.126,0"
    generics = "20"
    genericStart = "0.01"
    genericEnd = "0.60"
    genericRoughnesses = "0.01,0.02,0.04,0.07,0.09,0.11,0.13,0.16,0.20,0.25,0.40"

    resolution = "256"
    faceID = "5"
    nViews = "36"
    texWidth = "1024"
    texHeight = "1024"

    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT

        # combine all views' nrm into uv texture
        logger.info("CapNrmCombine: combine into texture space ")

        if not os.path.exists(OBJECT_ROOT):
            os.makedirs(OBJECT_ROOT)

        viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
        framesDirectory = os.path.join(viewDirectory, "Frames")
        nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
        # nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesBase")
        nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "Frames")

        viewDistImgFile = os.path.join(nrmRefineFramesDirectory, "pos.pfm")
        # viewNrmImgFile = os.path.join(nrmRefineFramesDirectory, "nrmObj.pfm")
        viewRecNrmDir = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-pig2\Views\View_%04d\Recover\Combine\Iter\Iter_final\refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.005_nDptIters=1"
        viewNrmImgFile = os.path.join(viewRecNrmDir,"nrmObj.pfm")
        # viewNrmImgFile = os.path.join(viewDirectory,"Recover/NrmRefine/FramesBase/Base_diffuse/weight.pfm")
        viewMaskImgFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")
        viewTexCoordImgFile = os.path.join(nrmRefineFramesDirectory,"tex.pfm")
        viewThMaskImgFile = os.path.join(viewDirectory, "Recover/Mirror/thMsk.pfm")

        textureImgFile = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "NrmTex.pfm")
        reModel = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "Recover.obj")
        reModelUpt = os.path.join(OBJECT_ROOT, r"Recover\Model\Final", "RecoverUpdate.obj")

        re = subprocess.run(
            ["CapNrmCombine",
             "-viewNrmImgFile=" + viewNrmImgFile, "-viewDistImgFile=" + viewDistImgFile,
             "-viewTexCoordImgFile=" + viewTexCoordImgFile, "-textureImgFile=" + textureImgFile,
             "-viewMaskImgFile=" + viewMaskImgFile,"-nViews=" + nViews, "-width=" + texWidth, "-height=" + texHeight,
             "-srcModelFile=" + reModel, "-tarModelFile=" + reModelUpt, "-flipZ"
             ], stdout=True, stderr=True, check=True)
        print(re.args)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
