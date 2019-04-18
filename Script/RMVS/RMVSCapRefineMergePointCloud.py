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
    DATA_ROOT_E = r"E:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
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
    # genericRoughnesses = "0.01,0.02,0.04,0.07,0.09,0.11,0.13,0.16,0.20,0.25,0.40"
    # genericRoughnesses = "0.01,0.02,0.03,0.05,0.07,0.09,0.11,0.13,0.16,0.20,0.25"
    genericRoughnesses = "0.01,0.02,0.04,0.07,0.09,0.11,0.13,0.16,0.20,0.25"

    # Downsampled lights
    rowScanWidth = "7"
    rowScanHeight = "1"
    colScanWidth = "1"
    colScanHeight = "23"

    OBJECT_MERGE = r"RealObject-cookiesMerge"
    OBJECT_ROOT_MERGE = os.path.join(DATA_ROOT, r'Object',OBJECT_MERGE)
    OBJECT_Model_Dir_MERGE = os.path.join(OBJECT_ROOT_MERGE, "Recover", "Model","FinalSfM")
    OBJECT_Model_Dir_MERGE_OPT = os.path.join(OBJECT_ROOT_MERGE, "Recover", "Model", "FinalOpt")

    OBJECT1 = r"RealObject-cookies"
    OBJECT_ROOT1 = os.path.join(DATA_ROOT_E, r'Object',OBJECT1)
    OBJECT_ViewDir1 = os.path.join(OBJECT_ROOT1, "Views", "View_%04d")
    OBJECT_Model_Dir1 = os.path.join(OBJECT_ROOT1, "Recover", "Model","FinalOpt")

    OBJECT2 = r"RealObject-cookies2"
    OBJECT_ROOT2 = os.path.join(DATA_ROOT_E, r'Object',OBJECT2)
    OBJECT_ViewDir2 = os.path.join(OBJECT_ROOT2, "Views", "View_%04d")
    OBJECT_Model_Dir2 = os.path.join(OBJECT_ROOT2, "Recover", "Model","FinalOpt")

    # Setup setting: camera,
    cameraConfig1 = os.path.join(CONFIG_ROOT, "Setup" + OBJECT1, "cameraConfig.txt")
    cameraConfig2 = os.path.join(CONFIG_ROOT, "Setup" + OBJECT2, "cameraConfig.txt")

    # Camera extrinsic, scale setting
    # viewScale = "0.009"
    viewScale = "1"
    # cameraExtrinDirectory1 = os.path.join(OBJECT_ROOT1, "CalibPrism", "Extrinsic")
    # cameraExtrinDirectory2 = os.path.join(OBJECT_ROOT2, "CalibPrism", "Extrinsic")
    cameraExtrinDirectory1 = os.path.join(OBJECT_ROOT1, "ColmapSfM", "Extrinsic")
    cameraExtrinDirectory2 = os.path.join(OBJECT_ROOT2, "ColmapSfM", "Extrinsic")

    keyPointsUVFile1 = os.path.join(OBJECT_Model_Dir_MERGE,"keyPointsUV1.txt")
    keyPointsUVFile2 = os.path.join(OBJECT_Model_Dir_MERGE,"keyPointsUV2.txt")
    keyPointsPosFile1 = os.path.join(OBJECT_Model_Dir_MERGE,"keyPointsPos1.txt")
    keyPointsPosFile2 = os.path.join(OBJECT_Model_Dir_MERGE,"keyPointsPos2.txt")

    # tranform second point cloud into the first one
    # transExtrinFile = os.path.join(OBJECT_Model_Dir_MERGE,"transExtrin.txt")
    transExtrinFile = os.path.join(OBJECT_Model_Dir_MERGE,"transExtrinIdentity.txt")


    # refine normal MVS setting
    # nrmRefRecDirName1 = "refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.5_nDptIters=1"
    # nrmRefRecDirName1 = "refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=10_dptWeight=10_fDistTH=1_nDptIters=2"
    # nrmRefRecDirName2 = "refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=10_dptWeight=10_fDistTH=1_nDptIters=1"
    nrmRefRecDirName1 = "ColmapSfM"
    nrmRefRecDirName2 = "ColmapSfM"

    # Option setting

    logger.info("Start merging objects:")
    if not os.path.exists( OBJECT_Model_Dir_MERGE):
        os.makedirs( OBJECT_Model_Dir_MERGE)
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT + ";" + TOOL_LCT_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT + ";" + TOOL_LCT_ROOT

        FinalMeshOpt = 1
        if FinalMeshOpt:
            MeshOpt = 1
            MeshOptPreprocess = 1
            MeshOptCapNrmCombine = 1
            MeshOptSecond = 1
            MeshOptSecondPreprocess = 1
            MeshOptSecondCapNrmCombine = 1
            FitRouOption = 1
            texWidth = "1024"
            texHeight = "1024"
            edgeLength = "0.003"
            meshOpt_nIter = 2

            # MODEL_ROOT = os.path.join(OBJECT_ROOT, r"Recover\Model")
            # MeshOptIter = os.path.join(OBJECT_ROOT, r"Recover\Model","MeshOpt")


            if MeshOpt:
                logger.info("Meah opt:")

                # each view: format string
                viewDirectory1 = os.path.join(OBJECT_ROOT1, "Views", "View_%04d")
                nrmRefineDirectory1 = os.path.join(viewDirectory1, "Recover/NrmRefine")
                viewMeshOptDir1 = os.path.join(nrmRefineDirectory1, "FramesMeshMerge")

                viewDirectory2 = os.path.join(OBJECT_ROOT2, "Views", "View_%04d")
                nrmRefineDirectory2 = os.path.join(viewDirectory2, "Recover/NrmRefine")
                viewMeshOptDir2 = os.path.join(nrmRefineDirectory2, "FramesMeshMerge")

                # recovered model dir:
                meshFinalDir =OBJECT_Model_Dir_MERGE
                iterDir = os.path.join(meshFinalDir, "Iter_MeshOpt")
                firstModel = os.path.join(meshFinalDir, "Recover.obj")
                finalIterModel = os.path.join(meshFinalDir, "RecoverFinal.obj")
                lastIterModel = os.path.join(iterDir, "Iter_%04d_RecoverFinal.obj" % (meshOpt_nIter - 1))

                if not os.path.exists(iterDir):
                    os.makedirs(iterDir)

                for iter in range(meshOpt_nIter):
                    logger.info("Mesh opt iter {}".format(iter))
                    viewIterDir1 = os.path.join(viewMeshOptDir1, "Iter_%04d" % iter)
                    viewIterFramesDir1 = os.path.join(viewIterDir1, "Frames")

                    viewIterDir2 = os.path.join(viewMeshOptDir2, "Iter_%04d" % iter)
                    viewIterFramesDir2 = os.path.join(viewIterDir2, "Frames")

                    reModel = os.path.join(iterDir, "Iter_%04d_RecoverFinal.obj" % (iter - 1))
                    reModelR = os.path.join(iterDir, "Iter_%04d_RecoverR.obj" % iter)
                    reModelUV = os.path.join(iterDir, "Iter_%04d_RecoverUV.obj" % iter)
                    reModelUVR = os.path.join(iterDir, "Iter_%04d_RecoverUVR.obj" % iter)
                    reModelUpt = os.path.join(iterDir, "Iter_%04d_RecoverUpdate.obj" % iter)
                    reModelUptPly = os.path.join(iterDir, "Iter_%04d_RecoverUpdate.ply" % iter)
                    reModelFinal = os.path.join(iterDir, "Iter_%04d_RecoverFinal.ply" % iter)
                    reModelFinalObj = os.path.join(iterDir, "Iter_%04d_RecoverFinal.obj" % iter)
                    reModelFinalPoission = os.path.join(iterDir, "Iter_%04d_RecoverFinalPoission.ply" % iter)
                    reModelFinalTrim = os.path.join(iterDir, r"Iter_%04d_RecoverFinalTrim.ply" % iter)
                    reModelFinalPost = os.path.join(iterDir, "Iter_%04d_RecoverPostProcess.obj" % iter)
                    if (iter == 0):
                        reModel = firstModel
                    if MeshOptPreprocess:
                        logger.info("Preprocess model ")
                        # remove degenerated faces
                        # rmBadFace(reModel, reModelR)
                        print(reModel)
                        mesh = trimesh.load(reModel)
                        mesh.remove_degenerate_faces()
                        # mesh = mesh.subdivide()
                        mesh.export(reModelR)

                        logger.info("Remesh model ")
                        re = subprocess.run(
                            ["LCT", "-i", reModelR, "-o", reModelR, "-l", edgeLength],
                            stdout=True, stderr=True, check=True)

                        logger.info("UVAtlas ")
                        # UVAtlas parameterization
                        re = subprocess.run(
                            ["UVAtlas", "-iv", "TEXCOORD", "-w", texWidth, "-h", texHeight, "-y", "-o",
                             reModelUV, reModelR],
                            stdout=True, stderr=True, check=True)

                        logger.info("Project recovered model into each view:")

                        logger.info("CapMultiSim ")
                        CapMultiSimOption = 1
                        if CapMultiSimOption:

                            cameraExtrinsic1 = os.path.join(cameraExtrinDirectory1, "view_%04d.txt")
                            renderOption = "2"
                            re = subprocess.run(
                                ["CapMultiSim", "-framesDirectory=" + viewIterFramesDir1,
                                 "-modelFile=" + reModelUV,
                                 "-cameraConfig=" + cameraConfig1, "-cameraExtrin=" + cameraExtrinsic1,
                                 "-viewScale=" + viewScale, "-flipZ",
                                 "-renderOption=" + renderOption, "-nViews=" + nViews],
                                stdout=True, stderr=True, check=True)

                            cameraExtrinsic2 = os.path.join(cameraExtrinDirectory2, "view_%04d.txt")
                            renderOption = "2"
                            re = subprocess.run(
                                ["CapMultiSim", "-framesDirectory=" + viewIterFramesDir2,
                                 "-modelFile=" + reModelUV,
                                 "-cameraConfig=" + cameraConfig2, "-cameraExtrin=" + cameraExtrinsic2,
                                 "-transExtrin="+transExtrinFile,
                                 "-viewScale=" + viewScale, "-flipZ",
                                 "-renderOption=" + renderOption, "-nViews=" + nViews],
                                stdout=True, stderr=True, check=True)

                    if MeshOptCapNrmCombine:
                        # combine all views' nrm into uv texture
                        logger.info("CapTexCombine: combine into texture space ")

                        framesDirectory1 = os.path.join(viewDirectory1, "Frames")
                        nrmRefineDirectory1 = os.path.join(viewDirectory1, "Recover/NrmRefine")
                        nrmRefineIterFinalDir1 = os.path.join(nrmRefineDirectory1, "Iter", "Iter_final")
                        cameraExtrinsic1 = os.path.join(cameraExtrinDirectory1, "view_%04d.txt")

                        # viewRecNrmDir = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-pig2\Views\View_%04d\Recover\Combine\Iter\Iter_final\refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.01_nDptIters=1"
                        viewNrmRefineImgFile1 = os.path.join(nrmRefineIterFinalDir1,
                                                            r"nrmR.pfm")  # in world space where nrm is estimated
                        # need to be changed
                        viewRecNrmDir1 = os.path.join(nrmRefineDirectory1, nrmRefRecDirName1)
                        viewDistImgFile1 = os.path.join(viewRecNrmDir1, "distR.pfm")
                        viewNrmImgFile1 = os.path.join(viewRecNrmDir1, "nrmObj.pfm")
                        # viewMaskImgFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")
                        viewGeoNrmImgFile1 = os.path.join(viewIterFramesDir1, "nrmObj.pfm")
                        viewTexCoordImgFile1 = os.path.join(viewIterFramesDir1, "tex.pfm")
                        viewMaskImgFile1 = os.path.join(nrmRefineIterFinalDir1, "specNicePeakMask.pfm")

                        refineNrmRouWeight1 = os.path.join(nrmRefineIterFinalDir1, r"Base_r_%.5f/weight.pfm")
                        refineNrmDiffWeight1 = os.path.join(nrmRefineIterFinalDir1, r"Base_diffuse/weight.pfm")

                        framesDirectory2 = os.path.join(viewDirectory2, "Frames")
                        nrmRefineDirectory2 = os.path.join(viewDirectory2, "Recover/NrmRefine")
                        nrmRefineIterFinalDir2 = os.path.join(nrmRefineDirectory2, "Iter", "Iter_final")
                        cameraExtrinsic2 = os.path.join(cameraExtrinDirectory2, "view_%04d.txt")

                        # viewRecNrmDir = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-pig2\Views\View_%04d\Recover\Combine\Iter\Iter_final\refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.01_nDptIters=1"
                        viewNrmRefineImgFile2 = os.path.join(nrmRefineIterFinalDir2,
                                                            r"nrmR.pfm")  # in world space where nrm is estimated
                        # need to be changed
                        viewRecNrmDir2 = os.path.join(nrmRefineDirectory2, nrmRefRecDirName2)
                        viewDistImgFile2 = os.path.join(viewRecNrmDir2, "distR.pfm")
                        viewNrmImgFile2 = os.path.join(viewRecNrmDir2, "nrmObj.pfm")
                        # viewMaskImgFile = os.path.join(nrmRefineFramesDirectory, "mask.pfm")
                        viewGeoNrmImgFile2 = os.path.join(viewIterFramesDir2, "nrmObj.pfm")
                        viewTexCoordImgFile2 = os.path.join(viewIterFramesDir2, "tex.pfm")
                        viewMaskImgFile2 = os.path.join(nrmRefineIterFinalDir2, "specNicePeakMask.pfm")

                        refineNrmRouWeight2 = os.path.join(nrmRefineIterFinalDir2, r"Base_r_%.5f/weight.pfm")
                        refineNrmDiffWeight2 = os.path.join(nrmRefineIterFinalDir2, r"Base_diffuse/weight.pfm")

                        texNrmImgFile = os.path.join(OBJECT_Model_Dir_MERGE, "TexNrm.pfm")
                        texPosImgFile = os.path.join(OBJECT_Model_Dir_MERGE,"TexPos.pfm")
                        texDiffImgFile = os.path.join(OBJECT_Model_Dir_MERGE,
                                                      r"Base_diffuse/weight.pfm")
                        texSpecRouImgFile = os.path.join(OBJECT_Model_Dir_MERGE,
                                                         r"Base_r_%.5f/weight.pfm")
                        texSpecFitImgFile = os.path.join(OBJECT_Model_Dir_MERGE,
                                                         "result_specular.pfm")
                        texRouFitImgFile = os.path.join(OBJECT_Model_Dir_MERGE,
                                                        "result_roughness_fitted.pfm")

                        re = subprocess.run(
                            ["CapMultiTexCombine",
                             "-viewFramesDirectory1=" + viewRecNrmDir1,
                             "-viewFramesDirectory2=" + viewRecNrmDir2,
                             "-viewNrmImgFile1=" + viewNrmImgFile1, "-viewGeoNrmImgFile1=" + viewGeoNrmImgFile1,
                             "-viewNrmImgFile2=" + viewNrmImgFile2, "-viewGeoNrmImgFile2=" + viewGeoNrmImgFile2,
                             "-viewMaskImgFile1=" + viewMaskImgFile1,
                             "-viewMaskImgFile2=" + viewMaskImgFile2,
                             "-genericRoughnesses=" + genericRoughnesses,
                             "-texNrmImgFile=" + texNrmImgFile,
                             "-texPosImgFile=" + texPosImgFile,
                             "-nViews=" + nViews, "-uvWidth=" + texWidth,
                             "-uvHeight=" + texHeight,
                             "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ",
                             "-cameraConfig1=" + cameraConfig1, "-cameraExtrin1=" + cameraExtrinsic1,
                             "-cameraConfig2=" + cameraConfig2, "-cameraExtrin2=" + cameraExtrinsic2,
                             "-transExtrin=" + transExtrinFile,
                             "-viewScale=" + viewScale
                             ], stdout=True, stderr=True, check=True)

                        logger.info("Update normal")
                        re = subprocess.run(
                            ["CapUpdateNrm",
                             "-texNrmImgFile=" + texNrmImgFile,
                             "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ", "-merge"
                             ], stdout=True, stderr=True, check=True)

                        logger.info("Change obj into ply")
                        # mesh.export(plyFile, "ply", encoding='ascii', vertex_normal=True)
                        obj2ply(reModelUpt, reModelUptPly)

                        re = subprocess.run(
                            ["mesh_opt", reModelUptPly, "-lambda", "0.1", "norm:" + reModelFinal], stdout=True,
                            stderr=True, check=True)

                        # re = subprocess.run(
                        #     ["PoissonRecon.exe", "--in", reModelFinal, "--out", reModelFinalPoission, "--normals", "--pointWeight",
                        #      "0",
                        #      "--depth",
                        #      "10", "--density", "--threads", "2"], stdout=True, stderr=True,
                        #     check=True)
                        # # trim combined mesh
                        # re = subprocess.run(
                        #     ["SurfaceTrimmer.exe", "--in", reModelFinalPoission, "--out", reModelFinalTrim, "--trim", "6"],
                        #     stdout=True, stderr=True, check=True)

                        ply2obj(reModelFinal, reModelFinalObj)

                shutil.move(lastIterModel, finalIterModel)

            if MeshOptSecond:
                viewDirectory1 = os.path.join(OBJECT_ROOT1, "Views", "View_%04d")
                viewDirectory2 = os.path.join(OBJECT_ROOT2, "Views", "View_%04d")

                nrmRefineDirectory1 = os.path.join(viewDirectory1, "Recover/NrmRefine")
                viewMeshMergeFinalDir1 = os.path.join(nrmRefineDirectory1, "FramesMeshMergeFinal")
                nrmRefineDirectory2 = os.path.join(viewDirectory2, "Recover/NrmRefine")
                viewMeshMergeFinalDir2 = os.path.join(nrmRefineDirectory2, "FramesMeshMergeFinal")


                meshFinalOptDir = os.path.join(OBJECT_Model_Dir_MERGE_OPT)
                if not os.path.exists(meshFinalOptDir):
                    os.makedirs(meshFinalOptDir)
                # when mesh_opt finished, combine all textures together using new uv
                reModel = os.path.join(OBJECT_Model_Dir_MERGE, "RecoverFinal.obj")
                reModelR = os.path.join(OBJECT_Model_Dir_MERGE_OPT, "RecoverR.obj")
                reModelUV = os.path.join(OBJECT_Model_Dir_MERGE_OPT, "RecoverUV.obj")
                reModelUpt = os.path.join(OBJECT_Model_Dir_MERGE_OPT, "RecoverUpdate.obj")
                reModelFinalObjFlip = os.path.join(OBJECT_Model_Dir_MERGE_OPT,"Object",
                                                   "RecoverFinalFlip.obj")

                texDiffImgFile = os.path.join(OBJECT_Model_Dir_MERGE_OPT,
                                              r"Base_diffuse/weight.pfm")
                texSpecRouImgFile = os.path.join(OBJECT_Model_Dir_MERGE_OPT,
                                                 r"Base_r_%.5f/weight.pfm")
                texSpecFitImgFile = os.path.join(OBJECT_Model_Dir_MERGE_OPT, "result_specular.pfm")
                texRouFitImgFile = os.path.join(OBJECT_Model_Dir_MERGE_OPT,
                                                "result_roughness_fitted.pfm")

                if MeshOptSecondPreprocess:
                    logger.info("Preprocess model ")
                    # remove degenerated faces
                    rmBadFace(reModel, reModelR)

                    logger.info("Remesh model ")
                    re = subprocess.run(
                        ["LCT", "-i", reModelR, "-o", reModelR, "-l", edgeLength],
                        stdout=True, stderr=True, check=True)

                    logger.info("UVAtlas ")
                    # UVAtlas parameterization
                    re = subprocess.run(
                        ["UVAtlas", "-iv", "TEXCOORD", "-w", texWidth, "-h", texHeight, "-y", "-o", reModelUV,
                         reModelR],
                        stdout=True, stderr=True, check=True)

                    logger.info("Project recovered model into each view:")
                    CapMultiSimOption = 1
                    if CapMultiSimOption:
                        cameraExtrinsic1 = os.path.join(cameraExtrinDirectory1, "view_%04d.txt")
                        renderOption = "2"
                        re = subprocess.run(
                            ["CapMultiSim", "-framesDirectory=" + viewMeshMergeFinalDir1,
                             "-modelFile=" + reModelUV,
                             "-cameraConfig=" + cameraConfig1, "-cameraExtrin=" + cameraExtrinsic1,
                             "-viewScale=" + viewScale, "-flipZ",
                             "-renderOption=" + renderOption, "-nViews=" + nViews],
                            stdout=True, stderr=True, check=True)

                        cameraExtrinsic2 = os.path.join(cameraExtrinDirectory2, "view_%04d.txt")
                        renderOption = "2"
                        re = subprocess.run(
                            ["CapMultiSim", "-framesDirectory=" + viewMeshMergeFinalDir2,
                             "-modelFile=" + reModelUV,
                             "-cameraConfig=" + cameraConfig2, "-cameraExtrin=" + cameraExtrinsic2,
                             "-transExtrin=" + transExtrinFile,
                             "-viewScale=" + viewScale, "-flipZ",
                             "-renderOption=" + renderOption, "-nViews=" + nViews],
                            stdout=True, stderr=True, check=True)

                if MeshOptSecondCapNrmCombine:
                    # combine all views' nrm into uv texture
                    logger.info("CapTexCombine: combine into texture space ")
                    framesDirectory1 = os.path.join(viewDirectory1, "Frames")
                    nrmRefineDirectory1 = os.path.join(viewDirectory1, "Recover/NrmRefine")
                    nrmRefineIterFinalDir1 = os.path.join(nrmRefineDirectory1, "Iter", "Iter_final")
                    cameraExtrinsic1 = os.path.join(cameraExtrinDirectory1, "view_%04d.txt")

                    # viewRecNrmDir = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-pig2\Views\View_%04d\Recover\Combine\Iter\Iter_final\refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.01_nDptIters=1"
                    viewNrmRefineImgFile1 = os.path.join(nrmRefineIterFinalDir1,
                                                         r"nrmR.pfm")  # in world space where nrm is estimated
                    # need to be changed
                    nrmRefineFramesDirectory1 = os.path.join(nrmRefineDirectory1,"FramesCombine")
                    viewRecNrmDir1 = os.path.join(nrmRefineDirectory1, nrmRefRecDirName1)
                    viewDistImgFile1 = os.path.join(viewRecNrmDir1, "distR.pfm")
                    viewNrmImgFile1 = os.path.join(viewRecNrmDir1, "nrmObj.pfm")
                    viewMaskImgFile1 = os.path.join(nrmRefineFramesDirectory1, "mask.pfm")
                    viewGeoNrmImgFile1 = os.path.join(viewMeshMergeFinalDir1, "nrmObj.pfm")
                    # viewMaskImgFile1 = os.path.join(nrmRefineIterFinalDir1, "specNicePeakMask.pfm")

                    refineNrmRouWeight1 = os.path.join(nrmRefineIterFinalDir1, r"Base_r_%.5f/weight.pfm")
                    refineNrmDiffWeight1 = os.path.join(nrmRefineIterFinalDir1, r"Base_diffuse/weight.pfm")

                    framesDirectory2 = os.path.join(viewDirectory2, "Frames")
                    nrmRefineDirectory2 = os.path.join(viewDirectory2, "Recover/NrmRefine")
                    nrmRefineIterFinalDir2 = os.path.join(nrmRefineDirectory2, "Iter", "Iter_final")
                    cameraExtrinsic2 = os.path.join(cameraExtrinDirectory2, "view_%04d.txt")

                    # viewRecNrmDir = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\RealObject-pig2\Views\View_%04d\Recover\Combine\Iter\Iter_final\refineNrBasesIter(WithTH)_rgbWeight=1_nrmWeight=1_dptWeight=1_fDistTH=0.01_nDptIters=1"
                    viewNrmRefineImgFile2 = os.path.join(nrmRefineIterFinalDir2,
                                                         r"nrmR.pfm")  # in world space where nrm is estimated
                    # need to be changed
                    nrmRefineFramesDirectory2 = os.path.join(nrmRefineDirectory2,"FramesCombine")
                    viewRecNrmDir2 = os.path.join(nrmRefineDirectory2, nrmRefRecDirName2)
                    viewDistImgFile2 = os.path.join(viewRecNrmDir2, "distR.pfm")
                    viewNrmImgFile2 = os.path.join(viewRecNrmDir2, "nrmObj.pfm")
                    viewMaskImgFile2 = os.path.join(nrmRefineFramesDirectory2, "mask.pfm")
                    viewGeoNrmImgFile2 = os.path.join(viewMeshMergeFinalDir2, "nrmObj.pfm")
                    # viewMaskImgFile2 = os.path.join(nrmRefineIterFinalDir2, "specNicePeakMask.pfm")

                    refineNrmRouWeight2 = os.path.join(nrmRefineIterFinalDir2, r"Base_r_%.5f/weight.pfm")
                    refineNrmDiffWeight2 = os.path.join(nrmRefineIterFinalDir2, r"Base_diffuse/weight.pfm")

                    texNrmImgFile = os.path.join(OBJECT_Model_Dir_MERGE_OPT, "TexNrm.pfm")
                    texPosImgFile = os.path.join(OBJECT_Model_Dir_MERGE_OPT, "TexPos.pfm")
                    texDiffImgFile = os.path.join(OBJECT_Model_Dir_MERGE_OPT,
                                                  r"Base_diffuse/weight.pfm")
                    texSpecRouImgFile = os.path.join(OBJECT_Model_Dir_MERGE_OPT,
                                                     r"Base_r_%.5f/weight.pfm")
                    texSpecFitImgFile = os.path.join(OBJECT_Model_Dir_MERGE_OPT,
                                                     "result_specular.pfm")
                    texRouFitImgFile = os.path.join(OBJECT_Model_Dir_MERGE_OPT,
                                                    "result_roughness_fitted.pfm")

                    re = subprocess.run(
                        ["CapMultiTexCombine",
                         "-viewFramesDirectory1=" + viewRecNrmDir1,
                         "-viewFramesDirectory2=" + viewRecNrmDir2,
                         "-viewNrmImgFile1=" + viewNrmImgFile1, "-viewGeoNrmImgFile1=" + viewGeoNrmImgFile1,
                         "-viewNrmImgFile2=" + viewNrmImgFile2, "-viewGeoNrmImgFile2=" + viewGeoNrmImgFile2,
                         "-viewMaskImgFile1=" + viewMaskImgFile1,
                         "-viewMaskImgFile2=" + viewMaskImgFile2,
                         "-genericRoughnesses=" + genericRoughnesses,
                         "-texNrmImgFile=" + texNrmImgFile,
                         "-texPosImgFile=" + texPosImgFile,
                         "-nViews=" + nViews, "-uvWidth=" + texWidth,
                         "-uvHeight=" + texHeight,
                         "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ",
                         "-cameraConfig1=" + cameraConfig1, "-cameraExtrin1=" + cameraExtrinsic1,
                         "-cameraConfig2=" + cameraConfig2, "-cameraExtrin2=" + cameraExtrinsic2,
                         "-transExtrin=" + transExtrinFile,
                         "-viewScale=" + viewScale
                         ], stdout=True, stderr=True, check=True)

                    logger.info("Update normal")
                    re = subprocess.run(
                        ["CapUpdateNrm",
                         "-texNrmImgFile=" + texNrmImgFile,
                         "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ", "--merge"
                         ], stdout=True, stderr=True, check=True)

                    re = subprocess.run(
                        ["CapMultiBRDFCombine",
                         "-viewFramesDirectory1=" + viewRecNrmDir1,
                         "-viewNrmImgFile1=" + viewGeoNrmImgFile1,
                         "-viewMaskImgFile1=" + viewMaskImgFile1,
                         "-viewDiffWeightFile1=" + refineNrmDiffWeight1,
                         "-viewSpecRouWeightFile1=" + refineNrmRouWeight1,
                         "-viewFramesDirectory2=" + viewRecNrmDir2,
                         "-viewNrmImgFile2=" + viewGeoNrmImgFile2,
                         "-viewMaskImgFile2=" + viewMaskImgFile2,
                         "-viewDiffWeightFile2=" + refineNrmDiffWeight2,
                         "-viewSpecRouWeightFile2=" + refineNrmRouWeight2,
                         "-genericRoughnesses=" + genericRoughnesses,
                         "-texNrmImgFile=" + texNrmImgFile,
                         "-texPosImgFile=" + texPosImgFile,
                         "-texDiffImgFile=" + texDiffImgFile,
                         "-texSpecRouImgFile=" + texSpecRouImgFile,
                         "-nViews=" + nViews, "-uvWidth=" + texWidth,
                         "-uvHeight=" + texHeight,
                         "-srcModelFile=" + reModelUV, "-tarModelFile=" + reModelUpt, "-flipZ", "-solveRou",
                         "-texSpecFitImgFile=" + texSpecFitImgFile, "-texRouFitImgFile=" + texRouFitImgFile,
                         "-cameraConfig1=" + cameraConfig1, "-cameraExtrin1=" + cameraExtrinsic1,
                         "-cameraConfig2=" + cameraConfig2, "-cameraExtrin2=" + cameraExtrinsic2,
                         "-transExtrin=" + transExtrinFile,
                         "-viewScale=" + viewScale
                         ], stdout=True, stderr=True, check=True)

                    if not os.path.exists(os.path.dirname(reModelFinalObjFlip)):
                        os.makedirs(os.path.dirname(reModelFinalObjFlip))

                if FitRouOption:
                    logger.info("Create model: ")
                    re = subprocess.run(
                        ["ModelTool",
                         "-srcModelFile=" + reModelUpt, "-tarModelFile=" + reModelFinalObjFlip, "-flipZ",
                         "--flipVC", "-tarTex",
                         "-tarTexDiffFile=" + texDiffImgFile, "-tarTexSpecFile=" + texSpecFitImgFile,
                         "-tarTexRouFile=" + texRouFitImgFile
                         ], stdout=True, stderr=True, check=True)
                    logger.info("Dilate textures: ")
                    CapDilateTextureOption = 1
                    if CapDilateTextureOption:
                        # dilate texture
                        inputDir = os.path.dirname(reModelFinalObjFlip)
                        nDil = "2"
                        inputFile = os.path.join(inputDir, "result_diff.pfm")
                        outputFile = os.path.join(inputDir, "result_diff.pfm")
                        re = subprocess.run(
                            ["ImgDilator", "-in=" + inputFile, "-out=" + outputFile], stdout=True, stderr=True,
                            check=True)

                        inputFile = os.path.join(inputDir, "result_spec.pfm")
                        outputFile = os.path.join(inputDir, "result_spec.pfm")
                        re = subprocess.run(
                            ["ImgDilator", "-in=" + inputFile, "-out=" + outputFile], stdout=True, stderr=True,
                            check=True)

                        inputFile = os.path.join(inputDir, "result_roughness.pfm")
                        outputFile = os.path.join(inputDir, "result_roughness.pfm")
                        re = subprocess.run(
                            ["ImgDilator", "-in=" + inputFile, "-out=" + outputFile], stdout=True, stderr=True,
                            check=True)
    finally:
        os.environ.clear()
        os.environ.update(_environ)