import os
import subprocess
import logging


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

    nviews = 1
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
            # # Change Name
            # # first capture row scan, then coloumn scan
            logging.info("rename..." )
            # for n in range(v_size):
            #     src = os.path.join(srcFramesDirectory, r"result__IMG_%04d.cr2" % (n + 1))
            #     dst = os.path.join(srcFramesDirectory, r"result_r%04d.cr2" % n )
            #     os.rename(src,dst)
            #
            # for n in range(u_size):
            #     src = os.path.join(srcFramesDirectory, r"result__IMG_%04d.cr2" % (v_size + n + 1))
            #     dst = os.path.join(srcFramesDirectory, r"result_c%04d.cr2" % n)
            #     os.rename(src,dst)

            # logging.info("cr2 to dng row...")
            # args = ["AdobeDNGConverter", "-c"]
            # for n in range(v_size):
            #     args.append("result_r%04d.cr2" % n)
            # re = subprocess.run(args, stdout=True, stderr=True, check=True, cwd=srcFramesDirectory)

            logging.info("cr2 to dng col...")
            args = ["AdobeDNGConverter", "-c"]
            for n in range(u_size):
                args.append("result_c%04d.cr2" % n)
            re = subprocess.run(args, stdout=True, stderr=True, check=True, cwd=srcFramesDirectory)

            # re = subprocess.run(["dngconvert", "*.dng"],
            #                 stdout=True, stderr=True, check=True, cwd=srcFramesDirectory)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
