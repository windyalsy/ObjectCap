# SfM data preparation.
# V0: Origin
import os
import subprocess
import shutil
import logging

# SfM data preparation.
# V0: Origin
import os
import subprocess
import shutil
import logging

if __name__ == "__main__":

    CapSimOption = 0
    CapRefineNrOption = 0
    CapRefineNrBasesOption = 1
    # render based on refine normal outcome.
    CapSimRefineNrOption = 0
    # parse curves from rendered outcome.
    CapParseCurOption = 0

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    # OBJECT = r"Object-testkitty"
    # OBJECT = r"Object-testpig"
    # OBJECT = r"Object-testduck"
    OBJECT = r"Object-testmuck"
    # BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    BUILD_ROOT = r"D:\v-jiazha\2-workspaces\Source\ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    OBJECT_ROOT = os.path.join(DATA_ROOT,r'Object', OBJECT)
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')
    COMMON_SINGLE_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\RealCommon"
    MODEL_NAME = r"Pig/Pig_160608.obj"
    # MODEL_NAME = r"Kitty_160420.obj"
    positionStr = r"0.199,-0.126,0"
    nViews = 36
    # generics = "10"
    # genericStart = "0.01"
    # genericEnd = "0.20"
    generics = "15"
    genericStart = "0.01"
    genericEnd = "0.6"
    modelName = "Recover"
    meshComReconTrimFObj = os.path.join(OBJECT_ROOT, r"Recover\Model","{0}.obj".format(modelName))

    if not os.path.exists(OBJECT_ROOT):
        os.makedirs(OBJECT_ROOT)
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT

        for v in range(nViews):

            logger.info("Dealing view: {0}th".format(v))
            modelFile = meshComReconTrimFObj

            viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
            framesDirectory =os.path.join(viewDirectory,"FramesDownsample")
            configDirectory =os.path.join(COMMON_ROOT, "Setups", "Setup_%04d" % v, "Config")
            panelConfig = os.path.join(configDirectory, "panelConfig.txt")
            # just test gl rendering
            # panelConfig = os.path.join(COMMON_ROOT, "Setups", "SetupNoLight", "Config", "panelConfig.txt")
            cameraConfig = os.path.join(configDirectory, "cameraConfig.txt")
            poseConfig = os.path.join(configDirectory, "poseConfig.txt")

            nrmRefineDirectory = os.path.join(viewDirectory, "Recover/NrmRefine")
            # nrmRefineFramesDirectory =os.path.join(nrmRefineDirectory,"FramesTestScope")
            # nrmRefineFramesDirectory =os.path.join(nrmRefineDirectory,"FramesTestValuePeak")
            nrmRefineFramesDirectory =os.path.join(nrmRefineDirectory,"FramesBase")

            renderOption = "1"
            if CapSimOption:
                logger.info("CapSim view: {0}th".format(v))
                re = subprocess.run(["CapSim", "-framesDirectory="+nrmRefineFramesDirectory, "-modelFile=" + modelFile,
                                 "-cameraConfig="+cameraConfig, "-poseConfig="+poseConfig,
                                 "-bounding", "-boundingRadius=1","--nonLocal","-positionStr="+positionStr,
                                 "-renderOption="+renderOption],
                                stdout = True, stderr=True, check=True)

            inputFramesCol = os.path.join(framesDirectory, r"result_c%04d.pfm")
            inputFramesRow = os.path.join(framesDirectory, r"result_r%04d.pfm")

            gtNrm = os.path.join(framesDirectory,"nrm.pfm")
            gtPos = os.path.join(framesDirectory,"pos.pfm")
            constantPos = os.path.join(framesDirectory, "posConstant.pfm")

            combIterFinal =os.path.join(viewDirectory, "Recover/Combine/Iter/Iter_final")
            combRouWeight =os.path.join(combIterFinal, "Base_r_%.5f/weight.pfm")
            combDiffWeight =os.path.join(combIterFinal, "Base_diffuse/weight.pfm")
            combNrm =os.path.join(combIterFinal,"nrmR.pfm")
            combErr =os.path.join(combIterFinal,"errorR.pfm")
            combSpecMsk =os.path.join(combIterFinal,"specMsk.pfm")
            combDiffMsk =os.path.join(combIterFinal,"diffMsk.pfm")
            combNrmD =os.path.join(combIterFinal ,"nrmD.pfm")
            combNrmS =os.path.join(combIterFinal , "nrmS.pfm")
            combNrmDMsk =os.path.join(combIterFinal,"nrmDMsk.pfm")

            recPos = os.path.join(nrmRefineFramesDirectory,"pos.pfm")
            refineNrmR = os.path.join(nrmRefineFramesDirectory,"nrmR.pfm")
            refineErrR = os.path.join(nrmRefineFramesDirectory,"errorR.pfm")
            refineNrmD = os.path.join(nrmRefineFramesDirectory,"nrmD.pfm")
            refineNrmS = os.path.join(nrmRefineFramesDirectory,"nrmS.pfm")
            refineNrmDMsk = os.path.join(nrmRefineFramesDirectory,"nrmDMsk.pfm")
            nrmRefineItersDirectory = os.path.join(nrmRefineFramesDirectory, "Iter","Iter_%04d")

            threshold = "5.0"

            modelName = "re" + "RecWithDepthConstraintO2NCC"
            recoverDirName = "re_RGBN_DptCon"

            outputDir = os.path.join(combIterFinal, recoverDirName)
            viewPosImgFile = os.path.join(outputDir, "pos.pfm")
            viewDistImgFile = os.path.join(outputDir, "distR.pfm")
            viewDepthImgFile = os.path.join(outputDir, "depthR.pfm")
            viewDepTruthImgFile = os.path.join(framesDirectory, "depth.pfm")
            viewMaskImgFile = os.path.join(framesDirectory, "mask.pfm")

            rowScanWidth = "7"
            rowScanHeight = "1"
            colScanWidth = "1"
            colScanHeight = "23"
            thetaStep = "0.3"
            phiSize = "45"
            nIter = "2"
            thetaSize = "10"
            # tempDir =os.path.join(r"D:\Nrm_refine\Nrm_0025")
            # combRouWeight =os.path.join(tempDir, "Base_r_%.5f/weight.pfm")
            # combDiffWeight =os.path.join(tempDir, "Base_diffuse/weight.pfm")


            # output refinement weight files
            refineNrmRouWeight = os.path.join(nrmRefineFramesDirectory, r"Base_r_%.5f/weight.pfm")
            refineNrmDiffWeight = os.path.join(nrmRefineFramesDirectory, r"Base_diffuse/weight.pfm")
            if CapRefineNrBasesOption:
                logger.info("CapRefineNrBases view: {0}th".format(v))
                re = subprocess.run(["CapRefineNrBases", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                     "-specRouWeightFile=" + refineNrmRouWeight, "-diffWeightFile=" + refineNrmDiffWeight,
                                     "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                                     "-iterDirectory=" + nrmRefineItersDirectory,
                                     "-nrmFile=" + combNrm, "-posFile=" + recPos,"-maskFile=" + viewMaskImgFile,
                                     "-nrmTruthFile=" + gtNrm,
                                     "-nrmRFile="+refineNrmR, "-errRFile="+refineErrR, "-nrmDFile="+refineNrmD,
                                     "-nrmSFile="+refineNrmS, "-nrmDMskFile=" + refineNrmDMsk,
                                     "-generics=" + generics,"-genericStart=" + genericStart,"-genericEnd=" + genericEnd,
                                     "-threshold="+threshold,"-rowScanWidth="+rowScanWidth, "-rowScanHeight=" + rowScanHeight,
                                     "-colScanWidth=" + colScanWidth, "-colScanHeight="+ colScanHeight,
                                     "-thetaStep="+thetaStep, "-phiSize="+phiSize, "-nIter="+nIter,"-thetaSize="+thetaSize,
                                     "-recordIter"],
                                    stdout=True, stderr=True, check=True)
                print(re.args)

            refineInputFramesCol = os.path.join(nrmRefineFramesDirectory, r"result_c%04d.pfm")
            refineInputFramesRow = os.path.join(nrmRefineFramesDirectory, r"result_r%04d.pfm")

            if CapSimRefineNrOption:
                logger.info("CapSimBasesComb view: {0}th".format(v))
                re = subprocess.run(["CapSimBasesComb", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                     "-specRouWeightFile=" + refineNrmRouWeight, "-diffWeightFile=" + refineNrmDiffWeight,
                                     "-inputFramesRow=" + refineInputFramesRow, "-inputFramesCol=" + refineInputFramesCol,
                                     "-nrmFile=" + refineNrmR, "-posFile=" + recPos, "-maskFile=" + viewMaskImgFile,
                                     "-generics=" + generics,"-genericStart=" + genericStart,"-genericEnd=" + genericEnd,
                                     "-rowScanWidth="+rowScanWidth, "-rowScanHeight=" + rowScanHeight,
                                     "-colScanWidth=" + colScanWidth, "-colScanHeight="+ colScanHeight],
                                    stdout=True, stderr=True, check=True)

            refineCurveFileCol = os.path.join(nrmRefineFramesDirectory, r"curveCol.cur")
            refineCurveFileRow = os.path.join(nrmRefineFramesDirectory, "curveRow.cur")
            refineCurveCSVCol = os.path.join(nrmRefineFramesDirectory, "curveCol.csv")
            refineCurveCSVRow = os.path.join(nrmRefineFramesDirectory, "curveRow.csv")
            posFile = os.path.join(framesDirectory, "pos.pfm")
            nrmFile = os.path.join(framesDirectory, "nrm.pfm")
            maskFile = os.path.join(framesDirectory, "mask.pfm")
            nrmTruthFile = os.path.join(framesDirectory, "nrm.pfm")
            # smooth parameters
            sigma = "2"
            hWidth = "0"
            # scale light intensity
            scale = "1"
            # fitting parameters
            interval = "1"

            iterMax = "6"
            resolution = "256"
            faceID = "5"
            kernelSize = "5"
            # rowScanWidth = "224"
            # rowScanHeight = "4"
            # colScanWidth = "4"
            # colScanHeight = "736"
            rowScanWidth = "7"
            rowScanHeight = "1"
            colScanWidth = "1"
            colScanHeight = "23"


            # CapParseCur
            if CapParseCurOption:
                logger.info("CapParseCur view: {0}th".format(v))
                re = subprocess.run(["CapParseCur", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                     "-inputFramesRow="+refineInputFramesRow,"-inputFramesCol="+refineInputFramesCol,
                                     "-curveFileRow="+refineCurveFileRow, "-curveFileCol="+refineCurveFileCol,
                                     "-curveCSVRow="+refineCurveCSVRow, "-curveCSVCol="+refineCurveCSVCol,
                                     "-sigma="+sigma,
                                     "-hWidth="+hWidth,"-positionStr="+positionStr,"-saveCurve","--saveCSV",
                                     "--useLightAVG", "-scale="+scale, "-maskFile="+maskFile,
                                     "-rowScanWidth="+rowScanWidth,"-rowScanHeight="+rowScanHeight,
                                     "-colScanWidth="+colScanWidth,"-colScanHeight="+colScanHeight],
                                        stdout=True, stderr=True, check=True)


    finally:
        os.environ.clear()
        os.environ.update(_environ)
