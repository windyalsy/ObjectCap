# Call SMVSCapFIt.sh
# V0: Origin
import os
import subprocess
import shutil
import logging

def CallFindPattern(inputFile, pointListFile, resultImageFile):
    # re = subprocess.run(["FindPattern", "--inputFile=" +"\""+ inputFile + "\"", "--pointListFile=" + "\"" + pointListFile + "\"",
    #                      "--resultImageFile=" + "\"" + resultImageFile +"\""],
    #                     stdout=True, stderr=True, check=True)
    re = subprocess.run(["FindPattern", "--inputFile=" + inputFile , "--pointListFile=" +  pointListFile ,
                         "--resultImageFile=" +  resultImageFile ],
                        stdout=True, stderr=True, check=True)
    print(re.args)
    return

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    CALIBPRISM_ROOT = r"D:\4-projects\5-LED\4-Backup\3-AfM_Calibration\0-Backup\AfM_Calibration\x64\Release"
    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + CALIBPRISM_ROOT
        else:
            os.environ['PATH'] = CALIBPRISM_ROOT

        dir = r"D:\4-projects\5-LED\4-Backup\3-AfM_Calibration\0-Backup\AfM_Calibration\dataTest"
        inputFile = os.path.join(dir,"IMG_20160328_142944.jpg")
        outputFile = os.path.join(dir,"IMG_20160328_142944 - CopyList.txt")
        resultImageFile = os.path.join(dir,"IMG_20160328_142944 - CopyFind.jpg")
        logger.info("Start Find Pattern: ")
        CallFindPattern(inputFile,outputFile,resultImageFile)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
