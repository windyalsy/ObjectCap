
# V0: Origin
import os
import subprocess
import shutil
import logging

def CallCalibPrism(imageList, intrinsic, pointList, faceTrans):
    re = subprocess.run(["CalibPrism", "--imageList=" + imageList , "--intrinsic=" + intrinsic,
                         "--pointList=" + pointList, "--faceTrans=" + faceTrans],
                        stdout=True, stderr=True, check=True)
    return

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    CALIBPRISM_ROOT = r"D:\4-projects\5-LED\4-Backup\3-AfM_Calibration\0-Backup\AfM_Calibration\x64\Debug"
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + CALIBPRISM_ROOT
        else:
            os.environ['PATH'] = CALIBPRISM_ROOT
        dir = r"D:\4-projects\5-LED\2-Source\4-MVS\RealCommon\CalibPrism\Prism"
        # dir = r"D:\4-projects\5-LED\4-Backup\3-AfM_Calibration\0-Backup\AfM_Calibration\data3"
        pointList = os.path.join(dir,"pointList.txt")
        imageList = os.path.join(dir,"imageList.txt")
        intrinsic = os.path.join(dir,"intrin.txt")
        faceTrans = os.path.join(dir,"faceTrans.txt")
        logger.info("Start Calibrate Prism: ")
        CallCalibPrism(imageList, intrinsic, pointList, faceTrans)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
