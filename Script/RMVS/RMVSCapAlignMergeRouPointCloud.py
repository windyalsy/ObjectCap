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
    OBJECT_Model_Dir_MERGE = os.path.join(OBJECT_ROOT_MERGE, "Recover", "Model","Final")

    OBJECT1 = r"RealObject-cookies"
    OBJECT_ROOT1 = os.path.join(DATA_ROOT, r'Object',OBJECT1)
    OBJECT_ViewDir1 = os.path.join(OBJECT_ROOT1, "Views", "View_%04d")
    OBJECT_Model_Dir1 = os.path.join(OBJECT_ROOT1, "Recover", "Model","FinalOpt")

    OBJECT2 = r"RealObject-cookies2"
    OBJECT_ROOT2 = os.path.join(DATA_ROOT, r'Object',OBJECT2)
    OBJECT_ViewDir2 = os.path.join(OBJECT_ROOT2, "Views", "View_%04d")
    OBJECT_Model_Dir2 = os.path.join(OBJECT_ROOT2, "Recover", "Model","FinalOpt")

    # Setup setting: camera,
    cameraConfig1 = os.path.join(CONFIG_ROOT, "Setup" + OBJECT1, "cameraConfig.txt")
    cameraConfig2 = os.path.join(CONFIG_ROOT, "Setup" + OBJECT2, "cameraConfig.txt")

    # Camera extrinsic, scale setting
    viewScale = "0.009"
    cameraExtrinDirectory1 = os.path.join(OBJECT_ROOT1, "CalibPrism", "Extrinsic")
    cameraExtrinDirectory2 = os.path.join(OBJECT_ROOT2, "CalibPrism", "Extrinsic")

    # keyPointsUVFile1 = os.path.join(OBJECT_Model_Dir_MERGE,"keyPointsUV1.txt")
    # keyPointsUVFile2 = os.path.join(OBJECT_Model_Dir_MERGE,"keyPointsUV2.txt")
    keyPointsUVFile1 = os.path.join(OBJECT_Model_Dir1,"keyPointsUV.txt")
    keyPointsUVFile2 = os.path.join(OBJECT_Model_Dir2,"keyPointsUV.txt")
    keyPointsPosFile1 = os.path.join(OBJECT_Model_Dir_MERGE,"keyPointsPos1.txt")
    keyPointsPosFile2 = os.path.join(OBJECT_Model_Dir_MERGE,"keyPointsPos2.txt")

    # tranform second point cloud into the first one
    transExtrinFile = os.path.join(OBJECT_Model_Dir_MERGE,"transExtrin.txt")

    # refine normal MVS setting
    # nrmRefRecDirName1 = "refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.5_nDptIters=1"
    nrmRefRecDirName1 = "refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=10_dptWeight=10_fDistTH=1_nDptIters=2"
    nrmRefRecDirName2 = "refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=10_dptWeight=10_fDistTH=1_nDptIters=1"

    src1Model = os.path.join(OBJECT_ROOT1,"Recover/Model/NrmRefine",nrmRefRecDirName1,"Comb_refine_.obj")
    src2Model = os.path.join(OBJECT_ROOT2,"Recover/Model/NrmRefine",nrmRefRecDirName2,"Comb_refine_.obj")
    # src1Model = os.path.join(OBJECT_Model_Dir1,"RecoverUpdate.obj")
    # src2Model = os.path.join(OBJECT_Model_Dir2,"RecoverUpdate.obj")
    alignModel = os.path.join(OBJECT_Model_Dir_MERGE,"AlignPoindCloud.obj")
    alignModelPly = os.path.join(OBJECT_Model_Dir_MERGE,"AlignPoindCloud.ply")
    alignModelPoi = os.path.join(OBJECT_Model_Dir_MERGE,"Align_Poi.ply")
    alignModelTrim = os.path.join(OBJECT_Model_Dir_MERGE,"Align_Trim.ply")
    alignModelRec = os.path.join(OBJECT_Model_Dir_MERGE,"Recover.obj")
    meshFinalDirObj = os.path.join(OBJECT_Model_Dir_MERGE,"RecoverFinal.obj")

    # Option setting
    CapCreateKeyPointsOpt = 0
    CapAlignPointCloudOpt = 1
    CleanPointCloudOption = 0
    logger.info("Start merging objects:")
    if not os.path.exists( OBJECT_Model_Dir_MERGE):
        os.makedirs( OBJECT_Model_Dir_MERGE)
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT + ";" + TOOL_LCT_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT + ";" + TOOL_LCT_ROOT

        if CapCreateKeyPointsOpt:
            logger.info("Create keypoint position list: ")
            texPosImgFile1 = os.path.join(OBJECT_Model_Dir1,"TexPos.pfm")
            re = subprocess.run(
                ["CapCreateKeyPointsList", "-keyPointsUVFile=" + keyPointsUVFile1,
                 "-keyPointsPosFile=" + keyPointsPosFile1,
                 "-flipZ", "-texPosImgFile=" + texPosImgFile1],
                stdout=True, stderr=True, check=True)

            texPosImgFile2 = os.path.join(OBJECT_Model_Dir2,"TexPos.pfm")
            re = subprocess.run(
                ["CapCreateKeyPointsList", "-keyPointsUVFile=" + keyPointsUVFile2,
                 "-keyPointsPosFile=" + keyPointsPosFile2,
                 "-flipZ", "-texPosImgFile=" + texPosImgFile2],
                stdout=True, stderr=True, check=True)

        if CapAlignPointCloudOpt:
            logger.info("Combine point clouds: ")
            re = subprocess.run(
                ["CapAlignPointCloud", "-src1ModelFile=" + src1Model, "-src2ModelFile=" + src2Model,
                 "-keyPointsFile1=" + keyPointsPosFile1,
                 "-keyPointsFile2=" + keyPointsPosFile2, "-tarModelFile=" + alignModel, "-transExtrin=" + transExtrinFile,
                 "-viewScale=" + viewScale, "-flipZ", "-nViews=" + nViews],
                stdout=True, stderr=True, check=True)

            obj2ply(alignModel, alignModelPly)
            logger.info("PoissonRecon: ")
            re = subprocess.run(
                ["PoissonRecon.exe", "--in", alignModelPly, "--out", alignModelPoi, "--normals", "--pointWeight",
                 "0",
                 "--depth",
                 "9", "--density", "--threads", "15"], stdout=True, stderr=True,
                check=True)
            # trim combined mesh
            re = subprocess.run(
                ["SurfaceTrimmer.exe", "--in", alignModelPoi, "--out", alignModelTrim, "--trim", "6"],
                stdout=True, stderr=True, check=True)
            ply2obj(alignModelTrim,alignModelRec)
            shutil.copy(alignModelRec,meshFinalDirObj)

        if CleanPointCloudOption:
            logger.info("Clean point cloud ")

            CapMultiSimOption = 0
            CapDilateMaskOption =0
            CapCleanOption = 0
            clean_nIters = 1

            # each view: format string
            viewDirectory1 = os.path.join(OBJECT_ROOT1, "Views", "View_%04d")
            nrmRefineDirectory1 = os.path.join(viewDirectory1, "Recover/NrmRefine")
            viewMeshCleanDir1 = os.path.join(nrmRefineDirectory1, "Iter_Merge_Clean")

            viewDirectory2 = os.path.join(OBJECT_ROOT2, "Views", "View_%04d")
            nrmRefineDirectory2 = os.path.join(viewDirectory2, "Recover/NrmRefine")
            viewMeshCleanDir2 = os.path.join(nrmRefineDirectory2, "Iter_Merge_Clean")

            # recovered model dir:
            meshFinalDir = OBJECT_Model_Dir_MERGE
            iterDir = os.path.join(meshFinalDir, "Iter_Merge_Clean")
            firstRecModel = alignModelRec
            firstCombModel = alignModel
            if not os.path.exists(iterDir):
                os.makedirs(iterDir)

            # combined
            for iter in range(clean_nIters):
                logger.info("Iter: {} ".format(iter) )
                viewIterDir1 = os.path.join(viewDirectory1,"Iter_Clean_Merge","Iter_%04d" % iter)
                viewIterFramesDir1 = os.path.join(viewIterDir1, "Frames")
                viewIterDir2 = os.path.join(viewDirectory2,"Iter_Clean_Merge","Iter_%04d" % iter)
                viewIterFramesDir2 = os.path.join(viewIterDir2, "Frames")

                cleanModel = os.path.join(iterDir,"Iter_%04d_clean.obj")
                cleanModelPly = os.path.join(iterDir, "Iter_%04d_clean.ply")
                poissonModel = os.path.join(iterDir,"Iter_%04d_poi.ply")
                trimModel = os.path.join(iterDir,"Iter_%04d_trim.ply")
                recModel = os.path.join(iterDir,"Iter_%04d_rec.obj")
                preModel = recModel % (iter-1)
                preComModel = cleanModel % (iter -1)
                if iter == 0:
                    preModel = firstRecModel
                    preComModel = firstCombModel

                logger.info("CapMultiSim ")
                if CapMultiSimOption:
                    cameraExtrinsic1 = os.path.join(cameraExtrinDirectory1, "view_%04d.txt")
                    renderOption = "2"
                    re = subprocess.run(
                        ["CapMultiSim", "-framesDirectory=" + viewIterFramesDir1,
                         "-modelFile=" + preModel,
                         "-cameraConfig=" + cameraConfig1, "-cameraExtrin=" + cameraExtrinsic1,
                         "-viewScale=" + viewScale, "-flipZ",
                         "-renderOption=" + renderOption, "-nViews=" + nViews],
                        stdout=True, stderr=True, check=True)

                    cameraExtrinsic2 = os.path.join(cameraExtrinDirectory2, "view_%04d.txt")
                    renderOption = "2"
                    re = subprocess.run(
                        ["CapMultiSim", "-framesDirectory=" + viewIterFramesDir2,
                         "-modelFile=" + preModel,
                         "-cameraConfig=" + cameraConfig2, "-cameraExtrin=" + cameraExtrinsic2,
                         "-transExtrin=" + transExtrinFile,
                         "-viewScale=" + viewScale, "-flipZ",
                         "-renderOption=" + renderOption, "-nViews=" + nViews],
                        stdout=True, stderr=True, check=True)

                logger.info("Dilate mask ")
                if CapDilateMaskOption:
                    # dilate masks
                    for v in range(nViewsCount):
                        nDil = "20"
                        inputFile = os.path.join(viewIterFramesDir1 % v, "mask.pfm")
                        outputFile = os.path.join(viewIterFramesDir1 % v, "mask_dil.pfm")
                        re = subprocess.run(
                            ["ImgDilator", "-in=" + inputFile, "-out=" + outputFile, "-n="+nDil], stdout=True, stderr=True,
                            check=True)
                    for v in range(nViewsCount):
                        nDil = "20"
                        inputFile = os.path.join(viewIterFramesDir2 % v, "mask.pfm")
                        outputFile = os.path.join(viewIterFramesDir2 % v, "mask_dil.pfm")
                        re = subprocess.run(
                            ["ImgDilator", "-in=" + inputFile, "-out=" + outputFile, "-n=" + nDil], stdout=True,
                            stderr=True,
                            check=True)

                logger.info("Clean outliers ")
                if CapCleanOption:
                    cameraExtrinsic1 = os.path.join(cameraExtrinDirectory1, "view_%04d.txt")
                    viewMaskImgFile1 = os.path.join(viewIterFramesDir1, "mask_dil.pfm")
                    srcModel = preComModel
                    tarModel = cleanModel % iter
                    re = subprocess.run(
                        ["CapCleanPointCloud", "-cameraConfig=" + cameraConfig1, "-cameraExtrin=" + cameraExtrinsic1,
                         "-viewMaskImgFile=" + viewMaskImgFile1,
                         "-srcModelFile=" + srcModel, "-tarModelFile=" + tarModel,
                         "-viewScale=" + viewScale, "-flipZ", "-nViews=" + nViews],
                        stdout=True, stderr=True, check=True)

                    cameraExtrinsic2 = os.path.join(cameraExtrinDirectory2, "view_%04d.txt")
                    viewMaskImgFile2 = os.path.join(viewIterFramesDir2, "mask_dil.pfm")
                    srcModel = cleanModel % iter
                    tarModel = cleanModel % iter
                    re = subprocess.run(
                        ["CapCleanPointCloud", "-cameraConfig=" + cameraConfig2, "-cameraExtrin=" + cameraExtrinsic2,
                         "-viewMaskImgFile=" + viewMaskImgFile2,
                         "-srcModelFile=" + srcModel, "-tarModelFile=" + tarModel,
                         "-viewScale=" + viewScale, "-flipZ", "-nViews=" + nViews],
                        stdout=True, stderr=True, check=True)
                    # poisson reconstruct combined mesh

                modelInP = cleanModelPly % iter
                modelOutP = poissonModel % iter
                obj2ply(cleanModel % iter,modelInP)
                re = subprocess.run(
                    ["PoissonRecon.exe", "--in", modelInP, "--out", modelOutP, "--normals",
                     "--pointWeight", "0",
                     "--depth",
                     "8", "--density", "--threads", "2", "--samplesPerNode", "1"], stdout=True,
                    stderr=True, check=True)
                # trim combined mesh
                modelInT = modelOutP
                modelOutT = trimModel % iter
                re = subprocess.run(
                    ["SurfaceTrimmer.exe", "--in", modelInT, "--out", modelOutT, "--trim",
                     "4"],
                    stdout=True, stderr=True, check=True)
                ply2obj(modelOutT, recModel % iter)


            shutil.copy(recModel  % (clean_nIters - 1), meshFinalDirObj)




    finally:
        os.environ.clear()
        os.environ.update(_environ)


