# DepMap2Obj Construct object file from depth map
# V0: Origin
import os
import subprocess
import logging
import trimesh
import trimesh.io.export as ex


def obj2ply(objFile, plyFile):
    mesh = trimesh.load(objFile)
    ex.export_mesh(mesh,plyFile,encoding='ascii',vertex_normal=True)
    return

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    OBJECT = r"Object-testkitty"
    BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    TOOL_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool"
    OBJECT_ROOT = os.path.join(DATA_ROOT,r'Object', OBJECT)
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')
    modelName = "model" + "DepNrmExm"
    nViews = 36
    meshCom = trimesh.base.Trimesh()    # combine all views's meshes.
    meshComF = os.path.join(OBJECT_ROOT, "Recover\Model\Combined{0}.ply".format(modelName))
    meshComReconF = os.path.join(OBJECT_ROOT, "Recover\Model\CombinedRecon{0}.ply".format(modelName))
    meshComReconTrimF = os.path.join(OBJECT_ROOT, "Recover\Model\CombinedReconTrim{0}.ply".format(modelName))
    meshComFDir = os.path.dirname(meshComF)
    Option = 1
    if not os.path.exists(meshComFDir):
        os.makedirs(meshComFDir)
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT
        v = 0
        viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
        framesDirectory = os.path.join(viewDirectory, "Frames")
        configDirectory = os.path.join(COMMON_ROOT, "Setups", "Setup", "Config")
        viewConfigDirectory = os.path.join(COMMON_ROOT, "Setups", "Setup_%04d" % v, "Config")
        cameraConfig = os.path.join(configDirectory, "cameraConfig.txt")
        poseConfig = os.path.join(viewConfigDirectory, "poseConfig.txt")

        combIterFinal = os.path.join(viewDirectory, r"Recover\Combine\Iter\Iter_final")
        combDiffWeight = os.path.join(combIterFinal, r"Base_diffuse\weight.pfm")
        combNrm = os.path.join(combIterFinal, "nrmR.pfm")
        combNrmDMsk = os.path.join(combIterFinal, "nrmDMsk.pfm")

        gtRGBImgFile = os.path.join(framesDirectory, "diff.pfm")
        gtNrmImgFile = os.path.join(framesDirectory, "nrm.pfm")
        reRGBImgFile = combDiffWeight
        reNrmImgFile = combNrm

        reDistImgFile = os.path.join(combIterFinal, "distR.pfm")
        reDepthImgFile = os.path.join(combIterFinal, "depthR.pfm")
        gtDepTruthImgFile = os.path.join(framesDirectory, "depth.pfm")
        # temporaly use diff(ground truth) as mask
        gtMaskImgFile = os.path.join(framesDirectory, "diff.pfm")
        reMaskImgFile = os.path.join(combIterFinal, "maskR.pfm")

        # Option 0: using recovered depth and gt normal to recover
        if Option == 0:
            rgbImgFile = gtRGBImgFile
            nrmImgFile = gtNrmImgFile
            depthImgFile = reDepthImgFile
            maskImgFile = reMaskImgFile
            distImgFile = reDistImgFile
            modelDir = os.path.join(combIterFinal,"gtNrmreDep")

        # Option 1: using recoverd normal and gt depth to recover
        if Option == 1:
            rgbImgFile = gtRGBImgFile
            nrmImgFile = reNrmImgFile
            depthImgFile = gtDepTruthImgFile
            maskImgFile = gtMaskImgFile
            distImgFile = reDistImgFile
            modelDir = os.path.join(combIterFinal, "gtDepreNrm")

        # # Option 2: using gt normal and gt depth to recover
        # if Option == 2:
        #         rgbImgFile = gtRGBImgFile
        #     nrmImgFile = gtNrmImgFile
        #     depthImgFile = gtDepTruthImgFile
        #     maskImgFile = gtMaskImgFile
        #     distImgFile = reDistImgFile
        #     modelDir = os.path.join(combIterFinal, "gtDepreNrm")

        # depth map into obj
        re = subprocess.run(["DptMap2Obj.exe", "-cameraConfig="+cameraConfig, "-poseConfig="+poseConfig,
                            "-rgbImgFile=" + rgbImgFile,"-nrmImgFile="+nrmImgFile, "-depthImgFile=" + depthImgFile,
                            "-maskImgFile=" + maskImgFile, "-distImgFile="+distImgFile, "-modelDir=" + modelDir,
                            "-modelName=" + modelName],
                            stdout = True, stderr=True, check=True)

        modelObjF = os.path.join(modelDir, "{0}.obj".format(modelName))
        modelPlyF = os.path.join(modelDir, "{0}_%04d.ply".format(modelName) % v)
        modelReconF = os.path.join(modelDir, "{0}Recon_%04d.ply".format(modelName) % v)
        modelReconTrimF = os.path.join(modelDir, "{0}ReconTrim_%04d.ply".format(modelName) % v)
        logger.info("PossionRecon view: {0}th".format(v))

        obj2ply(modelObjF, modelPlyF)
        #Poisson reconstruction
        re = subprocess.run(["PoissonRecon.exe", "--in", modelPlyF, "--out", modelReconF, "--normalWeight",
                             "--density"], stdout=True, stderr=True, check=True)
        #Trim surface
        re = subprocess.run(["SurfaceTrimmer.exe", "--in", modelReconF, "--out", modelReconTrimF, "--trim", "7"],
                            stdout=True, stderr=True, check=True)
        # mesh = trimesh.load(modelReconTrimF)
        # mesh = trimesh.load(modelPlyF)
        # meshCom = trimesh.util.concatenate(meshCom, mesh)
        # #save combined mesh
        # ex.export_mesh(meshCom, meshComF, encoding='ascii', vertex_normal=True)
        # #poisson reconstruct combined mesh
        # re = subprocess.run(["PoissonRecon.exe", "--in", meshComF, "--out", meshComReconF, "--normalWeight",
        #                      "--density"], stdout=True, stderr=True, check=True)
        # #trim combined mesh
        # re = subprocess.run(["SurfaceTrimmer.exe", "--in", meshComReconF, "--out", meshComReconTrimF, "--trim", "7"],
        #                     stdout=True, stderr=True, check=True)
    finally:
        os.environ.clear()
        os.environ.update(_environ)
