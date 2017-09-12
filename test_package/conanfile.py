from conans import ConanFile, CMake
import os
from os import path

username = os.getenv("CONAN_USERNAME", "pbrz")
channel = os.getenv("CONAN_CHANNEL", "testing")
version = "3.17.0.2"
package = "freeimage"

class TestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "%s/%s@%s/%s" % (package, version, username, channel)
    generators = "cmake"

    def build(self):
        cmake = CMake(self.settings)

        configure_cmd = 'cmake "%s" %s' % (self.conanfile_directory, cmake.command_line)
        self.output.info(configure_cmd)
        self.run(configure_cmd)

        build_cmd = "cmake --build . %s" % cmake.build_config
        self.output.info(build_cmd)
        self.run(build_cmd)

    def imports(self):
        self.copy("*.dll", "bin", "bin")
        self.copy("*.dylib", "bin", "bin")

    def test(self):
        self.output.info("running from: " + os.getcwd())
        exec_path = path.join("bin","example") 
        img_path = path.join(self.conanfile_directory, "test.png")
        self.run("%s %s" % (exec_path, img_path))
