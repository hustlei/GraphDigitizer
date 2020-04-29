# -*- coding: utf-8 -*-
"""Zip file store and open operations

Copyright (c) 2019 lileilei <hustlei@sina.cn>
"""

import os
import shutil
from tempfile import TemporaryDirectory
from zipfile import ZipFile


class FileOp():
    def __init__(self):
        self.temp = TemporaryDirectory()
        self.dir = self.temp.name
        self.datafile = os.path.join(self.dir, "digi.dump")
        self.datafilename = "digi.dump"
        self.imgfile = None
        self.imgfilename = None

    def close(self):
        self.temp.cleanup()

    def addImage(self, imagefile):
        if os.path.exists(imagefile):
            self.imgfilename = "image" + os.path.splitext(imagefile)[-1]
            self.imgfile = os.path.join(self.dir, self.imgfilename)
            try:
                shutil.copyfile(imagefile, self.imgfile)
                return True
            except:
                return False
        return False

    def open(self, zipfile):
        # with ZipFile('spam.zip') as myzip:
        #     with myzip.open('eggs.txt') as myfile:
        #         print(myfile.read())
        if os.path.exists(zipfile):
            z = ZipFile(zipfile, "r")
            # 打印zip文件中的文件列表
            try:
                for filename in z.namelist():
                    if filename.startswith("image."):
                        self.imgfile = os.path.join(self.dir, filename)
                        self.imgfilename = filename
                z.extractall(self.dir)
            except Exception as e:
                print("extract zip failure:" + e.args)
                z.close()
                return False
            if os.path.exists(self.imgfile) and os.path.exists(self.datafile):
                z.close()
                return True
        return False

    def save(self, zipfile):
        z = ZipFile(zipfile, 'w')
        if os.path.exists(self.imgfile):
            z.write(self.imgfile, self.imgfilename)
        if os.path.exists(self.datafile):
            z.write(self.datafile, self.datafilename)
        z.close()
