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
    CapRefineNrBasesOption = 0
    # render based on refine normal outcome.
    CapSimRefineNrOption = 1
    # parse curves from rendered outcome.
    CapParseCurOption = 1

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    # OBJECT = r"Object-testkitty"
    OBJECT = r"Object-testpig"
    # BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    BUILD_ROOT = r"D:\v-jiazha\2-workspaces\Source\ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    OBJECT_ROOT = os.path.join(DATA_ROOT,r'Object', OBJECT)
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')
    COMMON_SINGLE_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\RealCommon"
    MODEL_NAME = r"Pig/Pig_160608.obj"
    # MODEL_NAME = r"Kitty_160420.obj"
    positionStr = r"0.199,-0.126,0"
    nViews = 1
    nNormal = 121
    generics = "10"
    genericStart = "0.01"
    genericEnd = "0.20"
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

        v = 0
        for n in range(nNormal):
            n = n + 1
            logger.info("Dealing normal: {0}th".format(v))

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
            # nrmRefineFramesDirectory =os.path.join(nrmRefineDirectory,"Frames")
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
            refineNrmD = os.path.join(nrmRefineFramesDirectory,"nrmD.pfm")
            refineNrmS = os.path.join(nrmRefineFramesDirectory,"nrmS.pfm")
            refineNrmDMsk = os.path.join(nrmRefineFramesDirectory,"nrmDMsk.pfm")
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
            thetaStep = "0.2"
            phiStep = "0.2"
            kernelSize = "1"
            if CapRefineNrOption:
                logger.info("CapRefineNr view: {0}th".format(v))
                re = subprocess.run(["CapRefineNr", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                     "-specRouWeightFile=" + combRouWeight, "-diffWeightFile=" + combDiffWeight,
                                     "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                                     "-nrmFile=" + combNrm, "-posFile=" + recPos,"-maskFile=" + viewMaskImgFile,
                                     "-nrmRFile="+refineNrmR, "-nrmDFile="+refineNrmD,
                                     "-nrmSFile="+refineNrmS, "-nrmDMskFile=" + refineNrmDMsk,
                                     "-generics=" + generics,"-genericStart=" + genericStart,"-genericEnd=" + genericEnd,
                                     "-threshold="+threshold,"-rowScanWidth="+rowScanWidth, "-rowScanHeight=" + rowScanHeight,
                                     "-colScanWidth=" + colScanWidth, "-colScanHeight="+ colScanHeight,
                                     "-thetaStep="+thetaStep, "-phiStep="+phiStep, "-kernelSize="+kernelSize],
                                    stdout=True, stderr=True, check=True)

            if CapRefineNrBasesOption:
                logger.info("CapRefineNrBases view: {0}th".format(v))
                re = subprocess.run(["CapRefineNrBases", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                     "-specRouWeightFile=" + combRouWeight, "-diffWeightFile=" + combDiffWeight,
                                     "-inputFramesRow=" + inputFramesRow, "-inputFramesCol=" + inputFramesCol,
                                     "-nrmFile=" + gtNrm, "-posFile=" + gtPos,"-maskFile=" + viewMaskImgFile,
                                     "-nrmTruthFile=" + gtNrm,
                                     "-nrmRFile="+refineNrmR, "-nrmDFile="+refineNrmD,
                                     "-nrmSFile="+refineNrmS, "-nrmDMskFile=" + refineNrmDMsk,
                                     "-generics=" + generics,"-genericStart=" + genericStart,"-genericEnd=" + genericEnd,
                                     "-threshold="+threshold,"-rowScanWidth="+rowScanWidth, "-rowScanHeight=" + rowScanHeight,
                                     "-colScanWidth=" + colScanWidth, "-colScanHeight="+ colScanHeight,
                                     "-thetaStep="+thetaStep, "-phiStep="+phiStep, "-kernelSize="+kernelSize],
                                    stdout=True, stderr=True, check=True)
                print(re.args)

            nrmRefineSearchDirectory = r"D:\Nrm_refine/Nrm_%04d" % n
            nrmRefineSearchFramesDirectory = os.path.join(nrmRefineSearchDirectory, "Frames")

            refineSearchInputFramesCol = os.path.join(nrmRefineSearchFramesDirectory, r"result_c%04d.pfm")
            refineSearchInputFramesRow = os.path.join(nrmRefineSearchFramesDirectory, r"result_r%04d.pfm")
            refineSearchRouWeight = os.path.join(nrmRefineSearchDirectory, r"Base_r_%.5f/weight.pfm")
            refineSearchDiffWeight = os.path.join(nrmRefineSearchDirectory, r"Base_diffuse/weight.pfm")
            searchNrm = os.path.join(nrmRefineSearchDirectory,"nrm.pfm")

            if CapSimRefineNrOption:
                logger.info("CapSimBasesComb normal: {0}th".format(n))
                re = subprocess.run(["CapSimBasesComb", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                     "-specRouWeightFile=" + refineSearchRouWeight, "-diffWeightFile=" + refineSearchDiffWeight,
                                     "-inputFramesRow=" + refineSearchInputFramesRow, "-inputFramesCol=" + refineSearchInputFramesCol,
                                     "-nrmFile=" + searchNrm, "-posFile=" + gtPos, "-maskFile=" + viewMaskImgFile,
                                     "-generics=" + generics,"-genericStart=" + genericStart,"-genericEnd=" + genericEnd,
                                     "-rowScanWidth="+rowScanWidth, "-rowScanHeight=" + rowScanHeight,
                                     "-colScanWidth=" + colScanWidth, "-colScanHeight="+ colScanHeight],
                                    stdout=True, stderr=True, check=True)
            print(re.args)
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
            generics = "10"
            genericStart = "0.01"
            genericEnd = "0.20"
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

            refineSearchCurveFileRow= os.path.join(nrmRefineSearchFramesDirectory,"curveRow.cur")
            refineSearchCurveFileCol = os.path.join(nrmRefineSearchFramesDirectory,"curveCol.cur")
            refineSearchCurveCSVRow = os.path.join(nrmRefineSearchFramesDirectory,"curveRow.csv")
            refineSearchCurveCSVCol = os.path.join(nrmRefineSearchFramesDirectory,"curveCol.csv")
            # CapParseCur
            if CapParseCurOption:
                logger.info("CapParseCur normal: {0}th".format(n))
                re = subprocess.run(["CapParseCur", "-cameraConfig=" + cameraConfig, "-panelConfig=" + panelConfig,
                                     "-inputFramesRow="+refineSearchInputFramesRow,"-inputFramesCol="+refineSearchInputFramesCol,
                                     "-curveFileRow="+refineSearchCurveFileRow, "-curveFileCol="+refineSearchCurveFileCol,
                                     "-curveCSVRow="+refineSearchCurveCSVRow, "-curveCSVCol="+refineSearchCurveCSVCol,
                                     "-sigma="+sigma,
                                     "-hWidth="+hWidth,"-positionStr="+positionStr,"-saveCurve","--saveCSV",
                                     "--useLightAVG", "-scale="+scale, "-maskFile="+maskFile,
                                     "-rowScanWidth="+rowScanWidth,"-rowScanHeight="+rowScanHeight,
                                     "-colScanWidth="+colScanWidth,"-colScanHeight="+colScanHeight],
                                        stdout=True, stderr=True, check=True)


    finally:
        os.environ.clear()
        os.environ.update(_environ)
