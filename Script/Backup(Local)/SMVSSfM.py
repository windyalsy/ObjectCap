# SfM data preparation.
# V0: Origin
import os
import subprocess
import shutil
import logging
import trimesh
import trimesh.io.export as ex


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    OBJECT = r"Object-testpig"
    BUILD_ROOT = r"D:\4-projects\5-LED\0-ObjectCap\x64\Release"
    DATA_ROOT = r"D:\4-projects\5-LED\2-Source\4-MVS"
    TOOL_ROOT = r"D:\4-projects\5-LED\2-Source\2-3rdTool"
    OBJECT_ROOT = os.path.join(DATA_ROOT, r'Object', OBJECT)
    COMMON_ROOT = os.path.join(DATA_ROOT, r'RealCommon')
    ColMap_ROOT = os.path.join(TOOL_ROOT, r'COLMAP-dev-windows')
    SfM_ROOT = os.path.join(OBJECT_ROOT, r'SfM')
    SfM_ImagesDir = os.path.join(SfM_ROOT, r'images')
    nViews = 36

    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT + ";" + TOOL_ROOT + ";" + ColMap_ROOT
        else:
            os.environ['PATH'] = BUILD_ROOT + ";" + TOOL_ROOT + ";" + ColMap_ROOT

        # Poisson reconstruction
        re = subprocess.run(["colmap.bat", "automatic_reconstructor", "--workspace_path", SfM_ROOT, "--image_path",
                             SfM_ImagesDir], stdout=True, stderr=True, check=True)

    finally:
        os.environ.clear()
        os.environ.update(_environ)
