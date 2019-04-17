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
    mesh = trimesh.load(objFile)
    mesh.remove_degenerate_faces()
    mesh.export(objRFile)

def _logpath(path, names):
    print('Working in %s' % path)
    return []   # nothing will be ignored

if __name__ == "__main__":

    ImageMagicPath = r"C:/Program Files/ImageMagick-7.0.8-Q16-HDRI"
    BUILD_ROOT = r"D:\v-jiazha\2-workspaces\Source\ObjectCap\x64\Release"
    TOOL_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    TOOL_LCT_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool\LCT"
    # TOOL_COLMAP_ROOT = r"C:\Users\v-jiazha\Desktop\COLMAP-dev-windows"
    TOOL_COLMAP_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool\COLMAP-dev-windows"
    COMMON_ROOT = os.path.join(DATA_ROOT, r'RealCommon')
    CONFIG_ROOT = os.path.join(COMMON_ROOT,r"Config0301")


    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    v_size = 184
    u_size = 224
    nTotal = 409

    # Option Setting
    # positionStr = r"0.1982,-0.0921,0"
    positionStr = r"0.1988,-0.09269,0"
    nViewsCount = 36
    nViews = "36"
    # Bases Setting
    generics = "20"
    genericStart = "0.01"
    genericEnd = "0.60"
    genericRoughnesses = "0.01,0.02,0.04,0.07,0.09,0.11,0.13,0.16,0.20,0.25,0.40"
    # genericRoughnesses = "0.01,0.02,0.03,0.05,0.07,0.09,0.11,0.13,0.16,0.20,0.25"

    # Downsampled lights
    rowScanWidth = "7"
    rowScanHeight = "1"
    colScanWidth = "1"
    colScanHeight = "23"

    OBJECT_MERGE = r"RealObject-cookiesMerge"
    OBJECT_ROOT_MERGE = os.path.join(DATA_ROOT, r'Object',OBJECT_MERGE)
    OBJECT_ROOT_MERGE_SFM = os.path.join(OBJECT_ROOT_MERGE, r'SfM')
    OBJECT_ROOT_MERGE_SFM_CONFIG = os.path.join(OBJECT_ROOT_MERGE, r'SfM1','SfMConfig')
    OBJECT_Model_Dir_MERGE = os.path.join(OBJECT_ROOT_MERGE, "Recover", "Model","Final")

    # nCount = "2"
    # OBJECT_LIST = "RealObject-cookies,RealObject-cookies2"
    nCount = "1"
    OBJECT_LIST = "RealObject-cookies"

    OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object',"%s")
    OBJECT_ViewDir = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
    OBJECT_Model_Dir = os.path.join(OBJECT_ROOT, "Recover", "Model","FinalOpt")

    # Camera extrinsic, scale setting
    viewScale = "0.009"
    cameraExtrinDirectory = os.path.join(OBJECT_ROOT, "CalibPrism", "Extrinsic")

    # Colmap Setting
    OBJECT_COLMAP_ROOT = os.path.join(OBJECT_ROOT_MERGE_SFM,"SfM_FIRST_OBJECT")
    OBJECT_COLMAP_IMGDIR = os.path.join(OBJECT_COLMAP_ROOT,"images")
    OBJECT_COLMAP_CONFIG = os.path.join(OBJECT_COLMAP_ROOT,"config")
    colmap_sparse_model_dir = os.path.join(OBJECT_COLMAP_ROOT,"sparse","model")
    colmap_dense_model_dir = os.path.join(OBJECT_COLMAP_ROOT,"output")
    colmap_database = os.path.join(OBJECT_COLMAP_ROOT,"database.db")
    colmap_project = os.path.join(OBJECT_COLMAP_ROOT,"project.ini")


    # Option setting
    firstOpt = 0
    feature_extractorOpt = 1
    exhaustive_matcherOpt = 1
    point_triangulatorOpt = 1
    add_feature_extractorOpt = 0
    add_vocab_tree_matcherOpt = 0
    add_image_registerOpt = 1
    logger.info("Start merging objects:")
    if not os.path.exists(OBJECT_Model_Dir_MERGE):
        os.makedirs( OBJECT_Model_Dir_MERGE)

    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT + ";" + TOOL_LCT_ROOT +  ";" + TOOL_COLMAP_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT + ";" + TOOL_LCT_ROOT +  ";" + TOOL_COLMAP_ROOT
        if firstOpt:
            if feature_extractorOpt:
                if os.path.exists(colmap_database):
                    os.remove(colmap_database)
                re = subprocess.run(
                    ["colmap.bat", "feature_extractor",
                     "--database",colmap_database,
                     "--image_path",OBJECT_COLMAP_IMGDIR],
                    stdout=True, stderr=True, check=True)

            if exhaustive_matcherOpt:
                re = subprocess.run(
                    ["colmap.bat", "exhaustive_matcher",
                     "--database",colmap_database],
                    stdout=True, stderr=True, check=True)

            if point_triangulatorOpt:
                if not os.path.exists(colmap_sparse_model_dir):
                    os.makedirs(colmap_sparse_model_dir)
                re = subprocess.run(
                    ["colmap.bat", "point_triangulator",
                     "--database",colmap_database,
                     "--image_path",OBJECT_COLMAP_IMGDIR,
                     "--input_path",OBJECT_COLMAP_CONFIG,
                     "--output_path",colmap_sparse_model_dir],
                    stdout=True, stderr=True, check=True)

        colmap_sparse_modelUpt_dir = os.path.join(OBJECT_COLMAP_ROOT, "sparse", "modelUpt")
        colmap_modelUpt_imageList = os.path.join(OBJECT_COLMAP_CONFIG, "addImageList.txt")
        colmap_modelUpt_images_dir = os.path.join(OBJECT_COLMAP_ROOT, "addImages")
        colmap_sparse_modelUpt_dir = os.path.join(OBJECT_COLMAP_ROOT, "sparse", "modelUpt","vocab-tree.bin")
        if not os.path.exists(colmap_sparse_modelUpt_dir):
            os.makedirs(colmap_sparse_modelUpt_dir )

        # if add_feature_extractorOpt:
        #     re = subprocess.run(
        #         ["colmap.bat", "feature_extractor",
        #          "--database",colmap_database,
        #          "--image_path",colmap_modelUpt_images_dir,
        #          "--image_list_path", colmap_modelUpt_imageList,
        #          # "--ImageReader.camera_model", "OPENCV",
        #          # "--ImageReader.camera_params", "2539.21,2541.91,67.707,232.282,0,0,0,0"
        #          # "--ImageReader.existing_camera_id","0"
        #          ],
        #         stdout=True, stderr=True, check=True)
        # if add_vocab_tree_matcherOpt:
        #     re = subprocess.run(
        #     ["colmap.bat", "vocab_tree_matcher",
        #          "--database",colmap_database,
        #          "--VocabTreeMatching.vocab_tree_path",OBJECT_COLMAP_IMGDIR,
        #          "--VocabTreeMatching.match_list_path", colmap_modelUpt_imageList],
        #         stdout=True, stderr=True, check=True)
        if add_image_registerOpt:
            re = subprocess.run(
                ["colmap.bat", "image_registrator",
                 "--database",colmap_database,
                 "--input_path",colmap_sparse_model_dir,
                 "--output_path",colmap_sparse_modelUpt_dir,
                 "--Mapper.ba_refine_focal_length", "0",
                 "--Mapper.ba_refine_principal_point", "0",
                 "--Mapper.ba_refine_extra_params", "0"],
                stdout=True, stderr=True, check=True)

    finally:
        os.environ.clear()
        os.environ.update(_environ)


