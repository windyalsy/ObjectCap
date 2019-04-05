#parallel preprocess scan data
#automatically download image data and preprocess them

import os
import subprocess
import logging
from multiprocessing import Pool
import shutil
import time
import datetime
from ViewCameraExtrin import ViewCameraExtrin

# args[0] src file, arg[1] target file, args[2] working folder
def CallMagick(args):
    re = subprocess.run(["magick", args[0], "-sample", "20%", args[1]], stdout=False, stderr=True, check=True, cwd=args[2])

# # args[0] target file, args[1] working folder
# def CallDNGConverter(args):
#     re = subprocess.run(["dngconvert","-c","1760,300-2560,1100", args[0]], stdout=False, stderr=True, check=True, cwd=args[1])

# args[0] target files, args[1] working folder
def CallADobeDNGConverter(args):
    re = subprocess.run(["AdobeDNGConverter", "-c"] + args[0], stdout=False, stderr=True, check=True, cwd=args[1])

def _logpath(path, names):
    print('Working in %s' % path)
    return []   # nothing will be ignored

if __name__ == "__main__":

    ImageMagicPath = r"C:/Program Files/ImageMagick-7.0.8-Q16-HDRI"
    BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    TOOL_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool"
    COMMON_ROOT = os.path.join(DATA_ROOT, r'RealCommon')

    OBJECT = r"RealObject-penrack3"
    OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object', OBJECT)

    DEPLOYMENT_ROOT = r"D:\v-jiazha\4-projects\5-LED\5-Deployment\CapController\Data_Dir\image"
    DEPLOYMENT_OBJECT_ROOT = os.path.join(DEPLOYMENT_ROOT, OBJECT)
    DEPLOYMENT_ViewDir = os.path.join(DEPLOYMENT_OBJECT_ROOT, "Views","View_%04d")

    #set log
    LOG_ROOT = os.path.join(DATA_ROOT, r"Object/LOG")
    if not os.path.exists(LOG_ROOT):
        os.mkdir(LOG_ROOT)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logFileName = r'LogPreprecess{:%Y-%m-%d}'.format(datetime.datetime.now())
    fileHandler = logging.FileHandler("{0}/{1}.log".format(LOG_ROOT,logFileName))
    fileHandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(fileHandler)
    consoleHander = logging.StreamHandler()
    logger.addHandler(consoleHander)

    SourceOBJECT = "Scan"
    # SourcePath = r"\\minint-qlv0928\users\v-jiazha\Desktop\CapController\Data_Dir\Image"
    # SourcePath = r"D:\v-jiazha\4-projects\5-LED\5-Deployment\CapController\Data_Dir\image"
    SourcePath = r"\\msr-ig-server13\v-jiazha\4-projects\5-LED\5-Deployment\CapController\Data_Dir\image"
    SourceDir = os.path.join(SourcePath,SourceOBJECT)
    SourceViewDir = os.path.join(SourceDir,"Views","View_%04d")
    SourceViewLastFile = os.path.join(SourceViewDir,"Frames", "result__IMG_0409.cr2")

    nViews = 18
    v_size = 184
    u_size = 224
    nTotal = 409
    sleepTime = 60
    miniutesAgo = 60 * (15 + 15)
    timerBarrier = (time.time() - 60 * miniutesAgo) #if file is created after timeBarrier, it's new

    # imageCrop = "1760,300-2560,1100"
    # imageCrop = "1500,600-2300,1400"
    # imageCrop = "1640,640-2160,1100"
    imageCrop = "1380,640-2100,1360"
    # imageCrop = "1320,640-2120,1120"
    downsampleCMD = "50%"
    startView = 17
    logger.info("Start dealing object: {0}".format(OBJECT))
    for v in range(startView,nViews):
        logger.info("Start check view: {0}".format(v))
        signFile = SourceViewLastFile % v
        while True:
            if os.path.isfile(signFile):
                createTime = os.path.getmtime(signFile)
                if createTime > timerBarrier:
                    logger.info("View {0} captured finished".format(v))
                    break
            time.sleep(sleepTime)
        logger.info("Download view: {0}".format(v))
        srcDir = SourceViewDir % v
        tarDir = DEPLOYMENT_ViewDir % v
        # if tar dir exists, delete it.
        if os.path.exists(tarDir):
            shutil.rmtree(tarDir,ignore_errors=True)
        # copy directory
        shutil.copytree(srcDir, tarDir,ignore=_logpath)

        #preprocess images
        logger.info("Preprocess view: {0}".format(v))
        _environ = dict(os.environ)
        try:
            if 'PATH' in _environ:
                os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT + ";" + ImageMagicPath
            else:
                os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT + ";" + ImageMagicPath

            viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
            framesDirectory = os.path.join(viewDirectory, "Frames")
            srcViewDirectory = os.path.join(DEPLOYMENT_OBJECT_ROOT, "Views", "View_%04d" % v)
            srcFramesDirectory = os.path.join(srcViewDirectory, "Frames")
            if not os.path.exists(framesDirectory):
                os.makedirs(framesDirectory)

            # convert full light jpg for probe
            src = os.path.join(srcFramesDirectory, r"result__IMG_0409.cr2" )
            dst = os.path.join(framesDirectory, r"origin_full.jpg")
            re = subprocess.run(["magick.exe", src, dst], stdout=True, stderr=True, check=True)

            logger.info("cr2 to dng ")
            args = ["AdobeDNGConverter", "-c"]
            for n in range(nTotal):
                args.append("result__IMG_%04d.cr2" % (n + 1))
            re = subprocess.run(args, stdout=False, stderr=True, check=True, cwd=srcFramesDirectory)

            # dng to pfm format
            logger.info("dng to pfm ")
            for n in range(nTotal):
                dngFile = "result__IMG_%04d.dng" % (n + 1)
                re = subprocess.run(["dngconvert", "-c", imageCrop, dngFile], stdout=False, stderr=True,
                                    check=True, cwd=srcFramesDirectory)

            # downsample, rename and move
            logger.info("downsample, rename and move pfm ")
            for n in range(v_size):
                src = os.path.join(srcFramesDirectory, r"result__IMG_%04d.pfm" % (n + 1))
                dst = os.path.join(framesDirectory, r"result_r%04d.pfm" % n )
                re = subprocess.run(["magick", src, "-sample", downsampleCMD, dst], stdout=False, stderr=True,
                                    check=True)
            for n in range(u_size):
                src = os.path.join(srcFramesDirectory, r"result__IMG_%04d.pfm" % (v_size + n + 1))
                dst = os.path.join(framesDirectory, r"result_c%04d.pfm" % n)
                re = subprocess.run(["magick", src, "-sample", downsampleCMD, dst], stdout=False, stderr=True,
                                    check=True)
            # full on image
            src = os.path.join(srcFramesDirectory, r"result__IMG_%04d.pfm" % nTotal)
            dst = os.path.join(framesDirectory, r"result_full_on.pfm")
            re = subprocess.run(["magick", src, "-sample", downsampleCMD, dst], stdout=False, stderr=True,
                                check=True)

            logging.info("deleting ...")
            # delete pfm, cr2 files to spare space
            all = os.listdir(srcFramesDirectory)
            for item in all:
                if item.endswith(".pfm"):
                    os.remove(os.path.join(srcFramesDirectory, item))
                    continue
                if item.endswith(".dng"):
                    os.remove(os.path.join(srcFramesDirectory, item))
                    continue
            logging.info("view %04d finished" % v)

        finally:
            os.environ.clear()
            os.environ.update(_environ)

    logging.info("check all file...")
    # check all file exist;
    for v in range(nViews):
        for n in range(v_size):
            dst = os.path.join(framesDirectory, r"result_r%04d.pfm" % n)
            if not os.path.isfile(dst):
                logging.warning("missing file: " + dst)

        for n in range(u_size):
            dst = os.path.join(framesDirectory, r"result_c%04d.pfm" % n)
            if not os.path.isfile(dst):
                logging.warning("missing file: " + dst)

        logger.info("View %04d finished" % v)

    # ViewCameraExtrin(OBJECT)