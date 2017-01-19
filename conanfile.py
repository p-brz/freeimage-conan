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
        "use_cxx_wrapper" : [True, False],
        
        # if set, build library without "version number" (eg.: not generate libfreeimage-3-17.0.so)
        "no_soname"       : [True, False] 
    }
    default_options = (
        "shared=False",
        "use_cxx_wrapper=True",
        "no_soname=False"
    )

    exports = ("patches/*")

    #Downloading from sourceforge
    REPO = "http://downloads.sourceforge.net/project/freeimage/"
    DOWNLOAD_LINK = REPO + "Source%20Distribution/3.17.0/FreeImage3170.zip?r=&ts=1479919512&use_mirror=nbtelecom"
    #Folder inside the zip
    UNZIPPED_DIR = "FreeImage"
    FILE_SHA = 'fbfc65e39b3d4e2cb108c4ffa8c41fd02c07d4d436c594fff8dab1a6d5297f89'

    def configure(self):
        if self.settings.os == "Android":
            self.options.no_soname = True

    def source(self):
        zip_name = self.name + ".zip"

        tools.download(self.DOWNLOAD_LINK, zip_name)
        tools.check_sha256(zip_name, self.FILE_SHA)
        tools.unzip(zip_name)
        os.unlink(zip_name)

        self.apply_patches()
            
    def build(self):
        env = ConfigureEnvironment(self)

        make_env = self.make_env()
        env_line = "%s %s " % (env.command_line, make_env)
        
        self.make_and_install(env_line)
            
        if self.options.use_cxx_wrapper:
            self.make_and_install(env_line, "-f Makefile.fip")
               
    def make_and_install(self, env_line, options=""):
        make_cmd = "%s make %s" % (env_line, options)
     
        self.print_and_run(make_cmd               , cwd=self.UNZIPPED_DIR)
        self.print_and_run(make_cmd + " install"  , cwd=self.UNZIPPED_DIR)

    def package(self):
        pass

    def package_info(self):
        self.cpp_info.libs      = ["freeimage"]

        if self.options.use_cxx_wrapper:
            self.cpp_info.libs.append("freeimageplus")

    ################################ Helpers ######################################

    def print_and_run(self, cmd, **kw):
        cwd_ = "[%s] " % kw.get('cwd') if kw.has_key('cwd') else ''
        
        self.output.info(cwd_ + str(cmd))
        self.run(cmd, **kw)
        
    def make_env(self):
        env = []
        
        if self.options.shared: #valid only for modified makefiles
            env.append("BUILD_SHARED=1")
        
        if not hasattr(self, 'package_folder'):
            self.package_folder = "dist"
        
        if self.settings.os == "Android":
#        if self.options.no_swab:
            env.append("NO_SWAB=1")
        if self.options.no_soname:
            env.append("NO_SONAME=1")
        
        env.append("DESTDIR=" + self.package_folder)
        env.append("INCDIR=" + path.join(self.package_folder, "include"))
        env.append("INSTALLDIR=" + path.join(self.package_folder, "lib"))
            
        return " ".join(env)

    def rename_file(self, dir, filename, newname):
        os.rename(path.join(dir, filename), path.join(dir, newname))


    def apply_patches(self):
        self.output.info("Applying patches")
        
        #Copy "patch" files
        self.copy_tree("patches", self.UNZIPPED_DIR)

        self.patch_android_swab_issues()
        self.patch_android_neon_issues()
        
    def patch_android_swab_issues(self):
        librawlite = path.join(self.UNZIPPED_DIR, "Source", "LibRawLite")
        missing_swab_files = [
            path.join(librawlite, "dcraw", "dcraw.c"),
            path.join(librawlite, "internal", "defines.h")
        ]
        replaced_include = '\n'.join(('#include <unistd.h>', '#include "swab.h"'))
        
        for f in missing_swab_files:
            self.output.info("patching file '%s'" % f)
            tools.replace_in_file(f, "#include <unistd.h>", replaced_include)

    def patch_android_neon_issues(self):
        # avoid using neon
        libwebp_src = path.join(self.UNZIPPED_DIR, "Source", "LibWebP", "src")
        rm_neon_files = [   path.join(libwebp_src, "dsp", "dsp.h") ]
        for f in rm_neon_files:
            self.output.info("patching file '%s'" % f)
            tools.replace_in_file(f, "#define WEBP_ANDROID_NEON", "")

    def copy_tree(self, src_root, dst_root):
#        for p in self.patches:
#        for p in os.listdir('patches'):
        for root, dirs, files in os.walk(src_root):
            for d in dirs:
                dst_dir = path.join(dst_root, d)
                if not path.exists(dst_dir):
                    os.mkdir(dst_dir)
                    
                self.copy_tree(path.join(root, d), dst_dir)
            
            for f in files:
                copyfile(path.join(root, f), path.join(dst_root, f))

            break
