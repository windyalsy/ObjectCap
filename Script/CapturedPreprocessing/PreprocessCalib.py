import os
import subprocess
import logging

def CallConvertCR2_JPGDir(dir):
    for file in os.listdir(dir):
        filename, extension = os.path.splitext(file)
        if extension.lower() != ".cr2":
            continue
        src = os.path.join(dir,file)
        tar = os.path.join(dir, filename + ".jpg")
        print(src)
        print(tar)
        CallConvertCR2_JPG(src,tar)
    return

if __name__ == "__main__":
    ImageMagicPath = r"C:/Program Files/ImageMagick-7.0.8-Q16-HDRI"
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    TOOL_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool"
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')

    CALIBRATION_ROOT = r"D:\v-jiazha\4-projects\5-LED\5-Deployment\CapController\Data_Dir\image\Calib"
    CALIBPRISM_ROOT = os.path.join(COMMON_ROOT,r'CalibPrism6')

    #Calib light: only need first 5 images.
    count = 5
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT + ";" + ImageMagicPath
        else:
            os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT + ";" + ImageMagicPath

        for c in range(count):
            d = c + 1
            cr2File = os.path.join(CALIBRATION_ROOT, "Calib_IMG_%04d.cr2" % d)

            logging.info("CR2 to DNG %d image: " %c )
            re = subprocess.run(["AdobeDNGConverter","-c", cr2File],
                                stdout=True, stderr=True, check=True)

        re = subprocess.run(["dngconvert","*.dng"],
                            stdout=True, stderr=True, check=True, cwd=CALIBRATION_ROOT)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
