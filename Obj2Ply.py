import os
import trimesh
import trimesh.io.export as ex


def obj2ply(objFile, plyFile):
    mesh = trimesh.load(objFile)
    ex.export_mesh(mesh,plyFile,encoding='ascii',vertex_normal=True)
    return

if __name__ == "__main__":
    OBJECT = r"Object-testkitty"
    BUILD_ROOT = r"D:/v-jiazha/4-projects/5-LED/0-ObjectCap/x64/Release"
    DATA_ROOT = r"D:/v-jiazha/4-projects/5-LED/2-Source/4-MVS"
    OBJECT_ROOT = os.path.join(DATA_ROOT,r'Object',OBJECT)
    COMMON_ROOT = os.path.join(DATA_ROOT,r'RealCommon')

    _environ = dict(os.environ)
    try:
        if 'PATH' in _environ:
            os.environ['PATH'] = os.environ['PATH'] + ";" + BUILD_ROOT
    finally:
        os.environ.clear()
        os.environ.update(_environ)
    #
    # dir=r'D:\v-jiazha\4-projects\5-LED\2-Source\4-MVS\Object\Object' \
    # r'-testkitty\Views\View_0000\Recover\Combine\Iter\Iter_final'
    # inputF=dir+r'\modelRV.obj'
    # outputF=dir+r'\modelRV.ply'
    # obj2ply(inputF,outputF)