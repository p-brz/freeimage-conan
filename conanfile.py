from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools
from conans.tools import download, check_sha256, unzip, replace_in_file
import os
from os import path
from shutil import copy, copyfile


class Recipe(ConanFile):
    name    = "freeimage"
    version = "3.17.0.2"
    license = "FIPL(http://freeimage.sourceforge.net/freeimage-license.txt)", "GPLv2", "GPLv3"
    description = "Open source image loading library"

    url     = "https://github.com/p-brz/freeimage-conan"
    generators = "cmake"
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

    exports = ("CMakeLists.txt", "patches/*")

    #Downloading from sourceforge
    REPO = "http://downloads.sourceforge.net/project/freeimage/"
    DOWNLOAD_LINK = REPO + "Source%20Distribution/3.17.0/FreeImage3170.zip"
    #Folder inside the zip
    SRCDIR = "FreeImage"
    FILE_SHA = 'fbfc65e39b3d4e2cb108c4ffa8c41fd02c07d4d436c594fff8dab1a6d5297f89'

    def configure(self):
        if self.settings.os == "Android":
            self.options.no_soname = True

        if self.settings.compiler == "Visual Studio":
            self.options.use_cxx_wrapper = False

    def source(self):
        self.download_source()
        self.apply_patches()

    def download_source(self):
        zip_name = self.name + ".zip"

        download(self.DOWNLOAD_LINK, zip_name)
        check_sha256(zip_name, self.FILE_SHA)
        unzip(zip_name)
        os.unlink(zip_name)

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self.build_visualstudio()
        else:
            self.build_make()
            
    def build_visualstudio(self):
        cmake = CMake(self.settings)
        options = ''
        self.print_and_run('cmake . %s %s' % (cmake.command_line, options), cwd=self.SRCDIR)
        self.print_and_run("cmake --build . %s" % (cmake.build_config), cwd=self.SRCDIR)
         
    def build_make(self):
        with tools.environment_append(self.make_env()):
            self.make_and_install()
               
    def make_and_install(self):
        options= "" if not self.options.use_cxx_wrapper else "-f Makefile.fip"

        make_cmd = "make %s" % (options)

        self.print_and_run(make_cmd               , cwd=self.SRCDIR)
        self.print_and_run(make_cmd + " install"  , cwd=self.SRCDIR)

    def package(self):
        if self.settings.compiler != "Visual Studio":
            self.output.info("files already installed in build step")
            return
            
        include_dir = path.join(self.SRCDIR, 'Source')
        self.copy("FreeImage.h", dst="include", src=include_dir)
        
        if self.options.shared:
            self.copy("*.so", dst="lib", src=self.SRCDIR, keep_path=False)
            self.copy("*.dll", dst="bin", src=self.SRCDIR, keep_path=False)
        else:
            self.copy("*.lib", dst="lib", src=self.SRCDIR, keep_path=False)
            self.copy("*.a", dst="lib", src=self.SRCDIR, keep_path=False)

    def package_info(self):

        if self.options.use_cxx_wrapper:
            self.cpp_info.libs.append("freeimageplus")
        else:
            self.cpp_info.libs      = ["freeimage"]

    ################################ Helpers ######################################

    def print_and_run(self, cmd, **kw):
        cwd_ = "[%s] " % kw.get('cwd') if 'cwd' in kw else ''
        
        self.output.info(cwd_ + str(cmd))
        self.run(cmd, **kw)
        
    def make_env(self):
        env_build = AutoToolsBuildEnvironment(self)

        env = env_build.vars

        # AutoToolsBuildEnvironment sets CFLAGS and CXXFLAGS, so the default value
        # on the makefile is overwriten. So, we set here the default values again
        env["CFLAGS"] += " -O3 -fPIC -fexceptions -fvisibility=hidden"
        env["CXXFLAGS"] += " -O3 -fPIC -fexceptions -fvisibility=hidden -Wno-ctor-dtor-privacy"

        if self.options.shared: #valid only for modified makefiles
            env["BUILD_SHARED"] = "1"
        if self.settings.os == "Android":
            env["NO_SWAB"] = "1"
        if self.options.no_soname:
            env["NO_SONAME"] = "1"

        if not hasattr(self, 'package_folder'):
            self.package_folder = "dist"

        env["DESTDIR"]    = self.package_folder
        env["INCDIR"]     = path.join(self.package_folder, "include")
        env["INSTALLDIR"] = path.join(self.package_folder, "lib")
            
        return env

    def apply_patches(self):
        self.output.info("Applying patches")
        
        #Copy "patch" files
        copy('CMakeLists.txt', self.SRCDIR)
        self.copy_tree("patches", self.SRCDIR)

        self.patch_android_swab_issues()
        self.patch_android_neon_issues()
        
        if self.settings.compiler == "Visual Studio":
            self.patch_visual_studio()

    def patch_android_swab_issues(self):
        librawlite = path.join(self.SRCDIR, "Source", "LibRawLite")
        missing_swab_files = [
            path.join(librawlite, "dcraw", "dcraw.c"),
            path.join(librawlite, "internal", "defines.h")
        ]
        replaced_include = '\n'.join(('#include <unistd.h>', '#include "swab.h"'))
        
        for f in missing_swab_files:
            self.output.info("patching file '%s'" % f)
            replace_in_file(f, "#include <unistd.h>", replaced_include)

    def patch_android_neon_issues(self):
        # avoid using neon
        libwebp_src = path.join(self.SRCDIR, "Source", "LibWebP", "src")
        rm_neon_files = [   path.join(libwebp_src, "dsp", "dsp.h") ]
        for f in rm_neon_files:
            self.output.info("patching file '%s'" % f)
            replace_in_file(f, "#define WEBP_ANDROID_NEON", "")

    def patch_visual_studio(self):
        replace_in_file(path.join(self.SRCDIR, 'Source/FreeImage/Plugin.cpp'), 's_plugins->AddNode(InitWEBP);', '')
        replace_in_file(path.join(self.SRCDIR, 'Source/FreeImage/Plugin.cpp'), 's_plugins->AddNode(InitJXR);', '')
        # snprintf was added in VS2015
        if self.settings.compiler.version >= 14:
            replace_in_file(path.join(self.SRCDIR, 'Source/LibRawLite/internal/defines.h'), '#define snprintf _snprintf', '')
            replace_in_file(path.join(self.SRCDIR, 'Source/ZLib/gzguts.h'), '#  define snprintf _snprintf', '')
            replace_in_file(path.join(self.SRCDIR, 'Source/LibTIFF4/tif_config.h'), '#define snprintf _snprintf', '')

    def copy_tree(self, src_root, dst_root):
        for root, dirs, files in os.walk(src_root):
            for d in dirs:
                dst_dir = path.join(dst_root, d)
                if not path.exists(dst_dir):
                    os.mkdir(dst_dir)
                    
                self.copy_tree(path.join(root, d), dst_dir)
            
            for f in files:
                copyfile(path.join(root, f), path.join(dst_root, f))

            break
