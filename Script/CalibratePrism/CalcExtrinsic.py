
# V0: Origin
import os
import subprocess
import shutil
import logging

def CallCalcExtrinsic(objectPoints,imagePointList,intrinsic,extrinsic):
    # re = subprocess.run(["FindPattern", "--inputFile=" +"\""+ inputFile + "\"", "--pointListFile=" + "\"" + pointListFile + "\"",
    #                      "--resultImageFile=" + "\"" + resultImageFile +"\""],
    #                     stdout=True, stderr=True, check=True)
    re = subprocess.run(["CalcExtrinsic", "--objectPoints=" + objectPoints , "--imagePointList=" +  imagePointList ,
                         "--intrinsic=" +  intrinsic, "--extrinsic=" + extrinsic ],
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
        dir = r"D:\v-jiazha\data3"
        objectPoints = os.path.join(dir,"pointList.txt")
        imagePointList = os.path.join(dir,"imagePointList.txt")
        intrinsic = os.path.join(dir,"intrin.txt")
        extrinsic = os.path.join(dir,"detect")
        logger.info("Start Calculate Extrinsic: ")
        CallCalcExtrinsic(objectPoints, imagePointList, intrinsic, extrinsic)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
