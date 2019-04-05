# convert mesh obj file into ply file.
# poission reconstruction
# surface trim and combination
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
    OBJECT = r"Object-testpig"
    BUILD_ROOT = r"D:\4-projects\5-LED\0-ObjectCap\x64\Release"
    DATA_ROOT = r"D:\4-projects\5-LED\2-Source\4-MVS"
    TOOL_ROOT = r"D:\4-projects\5-LED\2-Source\2-3rdTool"
    OBJECT_ROOT = os.path.join(DATA_ROOT,r'Object', OBJECT)
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')
    modelName = "model" + "RecWithDepthConstraintO2SAD"
    nViews = 36
    meshCom = trimesh.base.Trimesh()    # combine all views's meshes.
    meshComF = os.path.join(OBJECT_ROOT, "Recover\Model\Combined{0}.ply".format(modelName))
    meshComReconF = os.path.join(OBJECT_ROOT, "Recover\Model\CombinedRecon{0}.ply".format(modelName))
    meshComReconTrimF = os.path.join(OBJECT_ROOT, "Recover\Model\CombinedReconTrim{0}.ply".format(modelName))
    meshComFDir = os.path.dirname(meshComF)
    if not os.path.exists(meshComFDir):
        os.makedirs(meshComFDir)
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT

        for v in range(nViews):
            viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
            combIterFinal = os.path.join(viewDirectory, "Recover","Combine", "Iter", "Iter_final")

            modelObjF = os.path.join(combIterFinal, "{0}.obj".format(modelName))
            modelPlyF = os.path.join(combIterFinal, "{0}_%04d.ply".format(modelName) % v)
            modelReconF = os.path.join(combIterFinal, "{0}Recon_%04d.ply".format(modelName) % v)
            modelReconTrimF = os.path.join(combIterFinal, "{0}ReconTrim_%04d.ply".format(modelName) % v)
            logger.info("PossionRecon view: {0}th".format(v))
            obj2ply(modelObjF, modelPlyF)
            #Poisson reconstruction
            re = subprocess.run(["PoissonRecon.exe", "--in", modelPlyF, "--out", modelReconF, "--normalWeight",
                                 "--density"], stdout=True, stderr=True, check=True)
            #Trim surface
            re = subprocess.run(["SurfaceTrimmer.exe", "--in", modelReconF, "--out", modelReconTrimF, "--trim", "7"],
                                stdout=True, stderr=True, check=True)
            mesh = trimesh.load(modelReconTrimF)
            # mesh = trimesh.load(modelPlyF)
            meshCom = trimesh.util.concatenate(meshCom, mesh)
        #save combined mesh
        ex.export_mesh(meshCom, meshComF, encoding='ascii', vertex_normal=True)
        #poisson reconstruct combined mesh
        re = subprocess.run(["PoissonRecon.exe", "--in", meshComF, "--out", meshComReconF, "--normalWeight",
                             "--density"], stdout=True, stderr=True, check=True)
        #trim combined mesh
        re = subprocess.run(["SurfaceTrimmer.exe", "--in", meshComReconF, "--out", meshComReconTrimF, "--trim", "7"],
                            stdout=True, stderr=True, check=True)
    finally:
        os.environ.clear()
        os.environ.update(_environ)
