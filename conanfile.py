from conans import ConanFile, ConfigureEnvironment, tools
import os
from os import path
from shutil import copyfile

class FreeImageConan(ConanFile):
    name    = "freeimage"
    version = "3.17.0"
    license = "FIPL(http://freeimage.sourceforge.net/freeimage-license.txt)", "GPLv2", "GPLv3"

    url     = "https://github.com/paulobrizolara/freeimage-conan"
    settings = "os", "compiler", "arch"

    options = {
        "shared"          : [True, False],
        "use_cxx_wrapper" : [True, False]
    }
    default_options = (
        "shared=False",
        "use_cxx_wrapper=True"
    )

    patches = ("Makefile.gnu", "Makefile.fip")
    exports = patches

    #Downloading from sourceforge
    REPO = "http://downloads.sourceforge.net/project/freeimage/"
    DOWNLOAD_LINK = REPO + "Source%20Distribution/3.17.0/FreeImage3170.zip?r=&ts=1479919512&use_mirror=nbtelecom"
    #Folder inside the zip
    UNZIPPED_DIR = "FreeImage"
    FILE_SHA = 'fbfc65e39b3d4e2cb108c4ffa8c41fd02c07d4d436c594fff8dab1a6d5297f89'

    def source(self):
        zip_name = self.name + ".zip"

        tools.download(self.DOWNLOAD_LINK, zip_name)
        tools.check_sha256(zip_name, self.FILE_SHA)
        tools.unzip(zip_name)
        os.unlink(zip_name)

        self.output.info(os.listdir("."))

        for p in self.patches:
            copyfile(path.join(".", p), path.join(self.UNZIPPED_DIR, p))

    def build(self):
        env = ConfigureEnvironment(self)

        make_env = self.make_env()
        make_cmd = "%s %s make" % (env.command_line, make_env) 
        
        self.run(make_cmd             , cwd=self.UNZIPPED_DIR)
        self.run(make_cmd + " install", cwd=self.UNZIPPED_DIR)

        if self.options.use_cxx_wrapper:
            make_cxx_cmd = "%s %s make -f Makefile.fip" % (env.command_line, make_env)
            
            self.run(make_cxx_cmd               , cwd=self.UNZIPPED_DIR)
            self.run(make_cxx_cmd + " install"  , cwd=self.UNZIPPED_DIR)

    def package(self):
        pass

    def package_info(self):
        self.cpp_info.libs      = ["freeimage"]

        if self.options.use_cxx_wrapper:
            self.cpp_info.libs.append("freeimageplus")

    def make_env(self):
        env = []
        
        if self.options.shared: #valid only for modified makefiles
            env.append("USE_SHARED=1")
        
        if not hasattr(self, 'package_folder'):
            self.package_folder = "dist"
        
        env.append("DESTDIR=" + self.package_folder)
        env.append("INCDIR=" + path.join(self.package_folder, "include"))
        env.append("INSTALLDIR=" + path.join(self.package_folder, "lib"))
            
        return " ".join(env)

    def rename_file(self, dir, filename, newname):
        os.rename(path.join(dir, filename), path.join(dir, newname))
