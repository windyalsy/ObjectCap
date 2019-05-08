#parallel preprocess scan data
#automatically download image data and preprocess them

import os
import subprocess
import logging
import shutil
import time

import numpy as np
import logging
import trimesh
from datetime import datetime

def obj2ply(objFile, plyFile):
    mesh = trimesh.load(objFile,process=None)
    mesh.export(plyFile,"ply",encoding='ascii',vertex_normal=True)
    # mesh = pymesh.load_mesh(objFile)
    # pymesh.save_mesh(plyFile, mesh, ascii=True)
    return

def ply2obj(plyFile, objFile):
    mesh = trimesh.load(plyFile,process=None,vertex_normal=True)
    print(len(mesh.vertex_normals))
    mesh.export(objFile)
    return

def rmBadFace(objFile,objRFile):
    mesh = trimesh.load(objFile,process=None,vertex_normal=True)
    mesh.remove_degenerate_faces()
    print(len(mesh.vertex_normals))
    mesh.export(objRFile)

def _logpath(path, names):
    print('Working in %s' % path)
    return []   # nothing will be ignored

if __name__ == "__main__":

    ImageMagicPath = r"C:/Program Files/ImageMagick-7.0.8-Q16-HDRI"
    BUILD_ROOT = r"D:\v-jiazha\2-workspaces\Source\ObjectCap\x64\Release"
    TOOL_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    DATA_ROOT_E = r"E:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    TOOL_LCT_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool\LCT"
    COMMON_ROOT = os.path.join(DATA_ROOT, r'RealCommon')
    CONFIG_ROOT = os.path.join(COMMON_ROOT,r"Config0301")

    # OBJECT = r"RealObject-pig2"
    OBJECT = r"RealObject-penrack3"
    # OBJECT = r"RealObject-pig2"
    # OBJECT = r"RealObject-oatmeal"
    # OBJECT = r"RealObject-oatmeal2"
    # OBJECT = r"RealObject-cookies"
    # OBJECT = r"RealObject-cookies2"
    # OBJECT = r"RealObject-gift1"
    # OBJECT = r"RealObject-gift2"
    # OBJECT = r"RealObject-oatmealMerge"
    # OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object', OBJECT)
    OBJECT_ROOT = os.path.join(DATA_ROOT_E, r'Object', OBJECT)
    # OBJECT_ROOT = r"C:\v-jiazha\RealObject-penrack3"
    OBJECT_ViewDir = os.path.join(OBJECT_ROOT, "Views","View_%04d")
    OBJECT_CalibPrismDir = os.path.join(OBJECT_ROOT, "CalibPrism")
    OBJECT_ColmapSfM_Dir = os.path.join(OBJECT_ROOT,"ColmapSfM")

    # Log setting
    LOG_ROOT = os.path.join(DATA_ROOT, r"Object/LOG")
    if not os.path.exists(LOG_ROOT):
        os.mkdir(LOG_ROOT)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logFileName = r'LogAutoDownloadRMVS{:%Y-%m-%d}'.format(datetime.now())
    fileHandler = logging.FileHandler("{0}/{1}.log".format(LOG_ROOT,logFileName))
    fileHandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(fileHandler)
    consoleHander = logging.StreamHandler()
    logger.addHandler(consoleHander)

    # Bases Setting
    generics = "20"
    genericStart = "0.01"
    genericEnd = "0.60"
    # genericRoughnesses = "0.20"
    genericRoughnesses = "0.01,0.02,0.04,0.09,0.13,0.20,0.40"
    # genericRoughnesses = "0.01,0.02,0.04,0.07,0.09,0.11,0.13,0.16,0.20,0.25,0.40"
    # genericRoughnesses = "0.01,0.02,0.03,0.05,0.07,0.09,0.11,0.13,0.16,0.20,0.25"
    # genericRoughnesses = "0.01,0.02,0.04,0.07,0.09,0.11,0.13,0.16,0.20,0.25"

    texWidth="256"
    texHeight="256"

    logger.info("Solve roughness and texture: ")
    # MODEL_ROOT = os.path.join(OBJECT_ROOT, r"Recover\Model")
    # MeshOptIter = os.path.join(OBJECT_ROOT, r"Recover\Model","MeshOpt")
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT +";" + TOOL_LCT_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT + ";" + TOOL_LCT_ROOT

        # srcDir = r"E:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-penrack3\Recover\Model\FinalOpt\GlobalRefine\Division\Div_W0002_H0002"
        # srcDir = r"E:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-penrack3\Recover\Model\FinalOpt\GlobalRefine\Division\Div_W0002_H0002\Ransac\Ransac_Iter_0001\Init\Iter_0001"
        # srcDir = r"E:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-penrack3\Recover\Model\FinalOpt\GlobalRefine\Division\Div_W0002_H0002"
        srcDir = r"E:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-penrack3\Recover\Model\FinalOpt\GlobalRefine\Division\Div_W0002_H0002\Ransac\Ransac_Iter_0000\Init\Iter_0000"
        texDiffImgFile = os.path.join(srcDir, r"Base_diffuse/weight.pfm")
        texSpecRouImgFile = os.path.join(srcDir, r"Base_r_%.5f/weight.pfm")
        texSpecFitImgFile = os.path.join(srcDir, "result_specular.pfm")
        texRouFitImgFile = os.path.join(srcDir, "result_roughness_fitted.pfm")

        logger.info("Solve roughness: ")
        re = subprocess.run(
            ["CapSolveRoughness",
             "-genericRoughnesses=" + genericRoughnesses,
             "-texSpecRouImgFile=" + texSpecRouImgFile,
            "-uvWidth=" + texWidth,"-uvHeight=" + texHeight,
             "-texSpecFitImgFile=" + texSpecFitImgFile, "-texRouFitImgFile=" + texRouFitImgFile,
             ], stdout=True, stderr=True, check=True)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
