#parallel preprocess scan data

import os
import subprocess
import logging
from multiprocessing import Pool
import shutil

# args[0] src file, arg[1] target file, args[2] working folder
def CallMagick(args):
    re = subprocess.run(["magick", args[0], "-sample", "20%", args[1]], stdout=False, stderr=True, check=True, cwd=args[2])

# args[0] target file, args[1] working folder
def CallDNGConverter(args):
    re = subprocess.run(["dngconvert","-c","1760,300-2560,1100", args[0]], stdout=False, stderr=True, check=True, cwd=args[1])

# args[0] target files, args[1] working folder
def CallADobeDNGConverter(args):
    re = subprocess.run(["AdobeDNGConverter", "-c"] + args[0], stdout=False, stderr=True, check=True, cwd=args[1])

if __name__ == "__main__":
    ImageMagicPath = r"C:/Program Files/ImageMagick-7.0.8-Q16-HDRI"
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    TOOL_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool"
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')

    OBJECT = r"RealObject-penrack"
    OBJECT_ROOT = os.path.join(DATA_ROOT,r'Object', OBJECT)

    DEPLOYMENT_ROOT = r"D:\v-jiazha\4-projects\5-LED\5-Deployment\CapController\Data_Dir\image"
    SRC_ROOT = os.path.join(DEPLOYMENT_ROOT,OBJECT)

    nPara = 8
    nviews = 36
    v_size = 184
    u_size = 224
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT + ";" + ImageMagicPath
        else:
            os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT + ";" + ImageMagicPath

        for v in range(nviews):
            viewDirectory = os.path.join(OBJECT_ROOT, "Views", "View_%04d" % v)
            framesDirectory = os.path.join(viewDirectory, "Frames")
            srcViewDirectory = os.path.join(SRC_ROOT, "Views", "View_%04d" % v)
            srcFramesDirectory = os.path.join(srcViewDirectory, "Frames")
            if not os.path.exists(framesDirectory):
                os.makedirs(framesDirectory)

            logging.info("view %04d starting..." % v)
            if os.path.isfile(os.path.join(framesDirectory, r"result_c0223.pfm")):
                logging.info("view %04d already done..." % v)
                continue

            if not os.path.isfile(os.path.join(srcFramesDirectory, r"result_c0223.cr2")):
                # Change Name
                # first capture row scan, then coloumn scan
                logging.info("rename..." )
                for n in range(v_size):
                    src = os.path.join(srcFramesDirectory, r"result__IMG_%04d.cr2" % (n + 1))
                    dst = os.path.join(srcFramesDirectory, r"result_r%04d.cr2" % n )
                    os.rename(src,dst)

                for n in range(u_size):
                    src = os.path.join(srcFramesDirectory, r"result__IMG_%04d.cr2" % (v_size + n + 1))
                    dst = os.path.join(srcFramesDirectory, r"result_c%04d.cr2" % n)
                    os.rename(src,dst)

            if not os.path.isfile(os.path.join(srcFramesDirectory, r"result_c0223.dng")):
                # cr2 to dng format
                logging.info("cr2 to dng row...")
                args = []
                for i in range(nPara):
                    args.append([[],srcFramesDirectory])
                for n in range(v_size):
                    # get remainder
                    (q,r) = divmod(n,nPara)
                    args[r][0].append("result_r%04d.cr2" % n)
                with Pool(nPara) as p:
                    p.map(CallADobeDNGConverter, args)

                logging.info("cr2 to dng col...")
                args = []
                for i in range(nPara):
                    args.append([[], srcFramesDirectory])
                for n in range(u_size):
                    # get remainder
                    (q, r) = divmod(n, nPara)
                    args[r][0].append("result_c%04d.cr2" % n)
                with Pool(nPara) as p:
                    p.map(CallADobeDNGConverter, args)

            if not os.path.isfile(os.path.join(srcFramesDirectory, r"result_c0223.pfm")):
                # dng to pfm format
                logging.info("dng to pfm row...")
                args = []
                for n in range(v_size):
                    args.append(["result_r%04d.dng" % n, srcFramesDirectory])
                with Pool(nPara) as p:
                    p.map(CallDNGConverter, args)

                # dng to pfm format
                logging.info("dng to pfm col...")
                args = []
                for n in range(u_size):
                    args.append(["result_c%04d.dng" % n, srcFramesDirectory])
                with Pool(nPara) as p:
                    p.map(CallDNGConverter, args)

            logging.info("move pfm row...")
            for n in range(v_size):
                src = os.path.join(srcFramesDirectory, r"result_r%04d.pfm" % n)
                if not os.path.isfile(src):
                    continue
                dst = os.path.join(framesDirectory, r"result_r%04d.pfm" % n )
                shutil.move(src,dst)
            logging.info("move pfm col...")
            for n in range(u_size):
                src = os.path.join(srcFramesDirectory, r"result_c%04d.pfm" % n)
                if not os.path.isfile(src):
                    continue
                dst = os.path.join(framesDirectory, r"result_c%04d.pfm" % n)
                shutil.move(src, dst)

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
            logging.info("view %04d finished" %v)

        logging.info("check all file...")
        # check all file exist;
        for v in range(nviews):
            for n in range(v_size):
                dst = os.path.join(framesDirectory, r"result_r%04d.pfm" % n)
                if not os.path.isfile(dst):
                    logging.warning("missing file: " + dst)

            for n in range(u_size):
                dst = os.path.join(framesDirectory, r"result_c%04d.pfm" % n)
                if not os.path.isfile(dst):
                    logging.warning("missing file: " + dst)

    finally:
        os.environ.clear()
        os.environ.update(_environ)