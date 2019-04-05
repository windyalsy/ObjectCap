import os
import subprocess
import logging
import sys
sys.path.append("..")
import Util.ConvertCR2_JPG as convert

if __name__ == "__main__":
    ImageMagicPath = r"C:/Program Files/ImageMagick-7.0.8-Q16-HDRI"
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    BUILD_ROOT = r"D:\v-jiazha\4-projects\5-LED\0-ObjectCap\x64\Release"
    DATA_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS"
    TOOL_ROOT = r"D:\v-jiazha\4-projects\5-LED\2-Source\2-3rdTool"
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')

    SourceOBJECT = "Scan"
    # SourcePath = r"\\minint-qlv0928\users\v-jiazha\Desktop\CapController\Data_Dir\Image"
    SourcePath = r"D:\v-jiazha\4-projects\5-LED\5-Deployment\CapController\Data_Dir\image"
    SourceDir = os.path.join(SourcePath, SourceOBJECT)
    SourceViewDir = os.path.join(SourceDir, "Views", "View_%04d")
    SourceViewLastFile = os.path.join(SourceViewDir, "Frames", "result__IMG_0409.cr2")

    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT + ";" + ImageMagicPath
        else:
            os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT + ";" + ImageMagicPath


        src = os.path.join(SourceViewDir % 0 , "Frames" , "result__IMG_0001.cr2")
        tar = os.path.join(SourceViewDir % 0 , "Frames" , "result__IMG_0001CropArea.jpg")
        convert.CallConvertCR2_JPG(src,tar)
    finally:
        os.environ.clear()
        os.environ.update(_environ)