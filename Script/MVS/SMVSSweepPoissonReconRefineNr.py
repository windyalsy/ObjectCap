# SfM data preparation.
# V0: Origin
import os
import subprocess
import numpy as np
import shutil
import logging
import trimesh
import trimesh.io.export as ex

def obj2ply(objFile, plyFile):
    mesh = trimesh.load(objFile)
    ex.export_mesh(mesh,plyFile,encoding='ascii',vertex_normal=True)
    return

def ply2obj(plyFile, objFile):
    mesh = trimesh.load(plyFile)
    ex.export_mesh(mesh,objFile,include_normals=True,
                     include_texture=True)
    return

if __name__ == "__main__":
    MVSSweepOption = 5
    RGBNPlaneSweepMVSOption = 1
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    # OBJECT = r"Object-testkitty"
    # OBJECT = r"Object-testpig"
    OBJECT = r"Object-testduck"
    # BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    BUILD_ROOT = r"D:\v-jiazha\2-workspaces\Source\ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    OBJECT_ROOT = os.path.join(DATA_ROOT,r'Object', OBJECT)
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')
    COMMON_SINGLE_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\RealCommon"
    # MODEL_NAME = r"Pig/Pig_160608.obj"
    MODEL_NAME = r"Kitty_160420.obj"
    positionStr = r"0.199,-0.126,0"
    nViews = 36
    if not os.path.exists(OBJECT_ROOT):
        os.makedirs(OBJECT_ROOT)
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT

        modelDirectory =os.path.join(COMMON_ROOT, "Model")
        modelFile = os.path.join(modelDirectory, MODEL_NAME)
        # viewConfigDirectory=$COMMON_ROOT/Setups/Setup_%04d/Config

        viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d")
        framesDirectory =os.path.join(viewDirectory,"FramesDownsample")
        configDirectory = os.path.join(COMMON_ROOT, "Setups", "Setup", "Config")
        viewConfigDirectory =os.path.join(COMMON_ROOT, "Setups", "Setup_%04d", "Config")
        # panelConfig = os.path.join(configDirectory, "panelConfig.txt")
        # just test gl rendering
        # panelConfig = os.path.join(COMMON_ROOT, "Setups", "SetupNoLight", "Config", "panelConfig.txt")
        # common camera
        cameraConfig = os.path.join(configDirectory, "cameraConfig.txt")
        poseConfig = os.path.join(viewConfigDirectory, "poseConfig.txt")

        combIterFinal = os.path.join(viewDirectory, "Recover/Combine/Iter/Iter_final")
        combDiffWeight = os.path.join(combIterFinal, "Base_diffuse/weight.pfm")
        combNrm = os.path.join(combIterFinal, "nrmR.pfm")
        combNrmDMsk = os.path.join(combIterFinal, "nrmDMsk.pfm")

        nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
        nrmRefineFramesDirectory = os.path.join(nrmRefineDirectory, "FramesBase")
        refineNrmR = os.path.join(nrmRefineFramesDirectory, "nrmR.pfm")
        refineNrmD = os.path.join(nrmRefineFramesDirectory, "nrmD.pfm")
        refineNrmS = os.path.join(nrmRefineFramesDirectory, "nrmS.pfm")
        refineNrmDMsk = os.path.join(nrmRefineFramesDirectory, "nrmDMsk.pfm")
        refineDiffWeight = os.path.join(nrmRefineFramesDirectory, "Base_diffuse/weight.pfm")

        if MVSSweepOption == 2:
            viewRGBImgFile = os.path.join(framesDirectory, "diff.pfm")
            viewNrmImgFile = os.path.join(framesDirectory, "nrm.pfm")
            modelName = "gt_"
            recoverDirName = "gt_"

        if MVSSweepOption == 1:
            viewRGBImgFile=combDiffWeight
            viewNrmImgFile=combNrm
            modelName = "re_"
            recoverDirName = "re_"

        if MVSSweepOption == 3:
            viewRGBImgFile = combDiffWeight
            viewNrmImgFile = combNrm
            modelName = "re_"
            recoverDirName = "re_"

        if MVSSweepOption == 4:
            viewRGBImgFile = combDiffWeight
            viewNrmImgFile = refineNrmR
            modelName = "refine_"
            recoverDirName = "refine_"

        if MVSSweepOption == 5:
            viewRGBImgFile = combDiffWeight
            viewNrmImgFile = refineNrmR
            modelName = "refine_"
            recoverDirName = "refineNrBasesIter1_"

        rgbWeight = "1"
        nrmWeight = "1"
        dptWeight = "1"
        minDepth = "1.1"
        maxDepth = "1.3"
        nNeighbors = "6"
        nSteps = "1001"
        nRefineIters = "2"
        nRefineSteps = "9"
        nDptIters = "0"
        nFirstKNeighborsForCost = "4"
        nViews = "36"
        checkW = "385"
        checkH = "275"
        positionStr = "0.199,-0.126,0"
        fDistTH = "1"
        nMetricLabel = "0"

        # modelName = modelName + "rgbWeight="+rgbWeight+"_nrmWeight="+nrmWeight+"_dptWeight="\
        #                  +dptWeight+"_fDistTH="+fDistTH + "_nDptIters="+nDptIters
        modelName = modelName +"_"
        recoverDirName = recoverDirName + "rgbWeight="+rgbWeight+"_nrmWeight="+nrmWeight+"_dptWeight="\
                         +dptWeight+"_fDistTH="+fDistTH + "_nDptIters="+nDptIters

        outputDir = os.path.join(combIterFinal, recoverDirName)
        viewDistImgFile = os.path.join(outputDir, "distR.pfm")
        viewDepthImgFile = os.path.join(outputDir, "depthR.pfm")

        viewDepTruthImgFile = os.path.join(framesDirectory, "depth.pfm")
        viewMaskImgFile = os.path.join(framesDirectory, "mask.pfm")
        # viewMaskImgFile = os.path.join(combIterFinal, "nrmDMsk.pfm")
        # viewMaskImgFile = os.path.join(combIterFinal, "specMsk.pfm")
        # viewMaskImgFile=$combIterFinal/nrmDMsk.pfm
        # modelName = "model" + "RecWithoutDepthConstraintO2NCC"

        # Sweep
        if RGBNPlaneSweepMVSOption:
            logger.info("RGBNPlaneSweepMVS")
            re = subprocess.run(["RGBNPlaneSweepMVS", "-cameraConfig="+cameraConfig, "-poseConfig="+poseConfig,
                                 "-viewFramesDirectory="+outputDir, "-viewRGBImgFile=" + viewRGBImgFile,
                                 "-viewNrmImgFile="+viewNrmImgFile, "-viewDistImgFile=" + viewDistImgFile,
                                "-viewDepthImgFile=" + viewDepthImgFile,
                                 "-viewDepTruthImgFile="+viewDepTruthImgFile, "-viewMaskImgFile=" + viewMaskImgFile,
                                 "-modelName=" + modelName,"-rgbWeight=" + rgbWeight,"-nrmWeight=" + nrmWeight,
                                 "-dptWeight=" + dptWeight, "-nDptIters=" + nDptIters,
                                 "-minDepth=" + minDepth, "-maxDepth=" + maxDepth, "-nNeighbors=" + nNeighbors,
                                 "-nSteps="+nSteps, "-nRefineIters="+nRefineIters, "-nRefineSteps="+nRefineSteps,
                                 "-nFirstKNeighborsForCost=" + nFirstKNeighborsForCost,"-nViews="+nViews,
                                 "-checkW="+checkW, "-checkH="+checkH, "--checkOption", "-bDistTHLabel",
                                 "-fDistTH="+fDistTH,"-nMetricLabel="+nMetricLabel, "-flipZ", "-GPUOption"],
                            stdout = True, stderr=True, check=True)

    finally:
        os.environ.clear()
        os.environ.update(_environ)

    CombineAllViewOption = 1
    PoissonEachViewOption = 0
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    TOOL_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool"
    OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object', OBJECT)
    COMMON_ROOT = os.path.join(DATA_ROOT, r'RealCommon')
    nViews = 36

    meshCom = trimesh.base.Trimesh()  # combine all views's meshes.
    meshComF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName, "Comb_{0}.txt".format(modelName))
    meshComObjF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName, "Comb_{0}.obj".format(modelName))
    meshComReconF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName,"Recon_{0}.ply".format(modelName))
    meshComReconTrimF = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName,"Trim_{0}.ply".format(modelName))
    meshComReconTrimFObj = os.path.join(OBJECT_ROOT, r"Recover\Model", recoverDirName, "Trim_{0}.obj".format(modelName))

    meshComFDir = os.path.dirname(meshComF)
    logger.info("Start")
    if not os.path.exists(meshComFDir):
        os.makedirs(meshComFDir)
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT
        if CombineAllViewOption:
            for v in range(nViews):
                viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
                combIterFinal = os.path.join(viewDirectory, "Recover", "Combine", "Iter", "Iter_final")
                outputDir = os.path.join(combIterFinal, recoverDirName)

                modelObjF = os.path.join(outputDir, "{0}.obj".format(modelName))
                modelPlyF = os.path.join(outputDir, "{0}_%04d.ply".format(modelName) % v)
                modelReconF = os.path.join(outputDir, "{0}Recon_%04d.ply".format(modelName) % v)
                modelReconTrimF = os.path.join(outputDir, "{0}ReconTrim_%04d.ply".format(modelName) % v)
                logger.info("PossionRecon view: {0}th".format(v))
                if PoissonEachViewOption:
                    obj2ply(modelObjF, modelPlyF)
                    # Poisson reconstruction
                    re = subprocess.run(["PoissonRecon.exe", "--in", modelPlyF, "--out", modelReconF,
                                         "--density"], stdout=True, stderr=True, check=True)
                    # Trim surface
                    re = subprocess.run(
                        ["SurfaceTrimmer.exe", "--in", modelReconF, "--out", modelReconTrimF, "--trim", "7"],
                        stdout=True, stderr=True, check=True)
                    # mesh = trimesh.load(modelReconTrimF)
                    # mesh = trimesh.load(modelPlyF)
                mesh = trimesh.load(modelObjF)
                if v == 0:
                    vertices = mesh.vertices
                    vertexNrms = mesh.vertex_normals
                else:
                    vertices = np.concatenate((vertices, mesh.vertices), axis=0)
                    vertexNrms = np.concatenate((vertexNrms, mesh.vertex_normals), axis=0)
                meshCom = trimesh.util.concatenate(meshCom, mesh)
                # save combined mesh
                # meshCom.vertices = vertices
                # meshCom.vertex_normals = vertexNrms
            pointCloud = np.concatenate((vertices, vertexNrms), axis=1)
            np.savetxt(meshComF, pointCloud, delimiter=" ")
            # meshCom = trimesh.base.Trimesh(vertices=vertices)
            ex.export_mesh(meshCom, meshComObjF, include_normals=True)
            # obj2ply(meshComObjF,meshComF)
            # ex.export_mesh(meshCom, meshComF, encoding='ascii', vertex_normal=True)

            # poisson reconstruct combined mesh
        re = subprocess.run(
            ["PoissonRecon.exe", "--in", meshComF, "--out", meshComReconF, "--normals", "--pointWeight", "0", "--depth","12",
           "--density"], stdout=True, stderr=True, check=True)
        # trim combined mesh
        re = subprocess.run(["SurfaceTrimmer.exe", "--in", meshComReconF, "--out", meshComReconTrimF, "--trim", "6"],
                            stdout=True, stderr=True, check=True)
        ply2obj(meshComReconTrimF, meshComReconTrimFObj)

    finally:
        os.environ.clear()
        os.environ.update(_environ)

