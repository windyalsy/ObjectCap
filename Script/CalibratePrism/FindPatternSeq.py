
# V0: Origin
import os
import subprocess
import shutil
import logging

def CallFindPatternSeq(intrinsic,faceTrans,imageList,outputDir):

    re = subprocess.run(["FindPatternSeq", "--intrinsic=" + intrinsic , "--faceTrans=" + faceTrans,
                         "--imageList=" + imageList, "--outputDir=" + outputDir],
                        stdout=True, stderr=True, check=True)
    print(re.args)
    return

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    CALIBPRISM_ROOT = r"D:\v-jiazha\4-projects\5-LED\5-Deployment\CalibrationPrism"
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + CALIBPRISM_ROOT
        else:
            os.environ['PATH'] = CALIBPRISM_ROOT
        dir = r"D:\4-projects\5-LED\4-Backup\3-AfM_Calibration\0-Backup\AfM_Calibration\data3"
        imageList = os.path.join(dir,"imageList.txt")
        intrinsic = os.path.join(dir,"intrin.txt")
        outputDir = os.path.join(dir,"detectSeq")
        faceTrans = os.path.join(dir, "faceTrans.txt")
        logger.info("Start FindPattern Sequence: ")
        CallFindPatternSeq(intrinsic, faceTrans, imageList, outputDir)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
