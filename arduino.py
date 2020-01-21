# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Arduino

Arduino Wiring-based Framework allows writing cross-platform software to
control devices attached to a wide range of Arduino boards to create all
kinds of creative coding, interactive objects, spaces or physical experiences.
"""

from os import listdir
from os.path import isdir, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

FRAMEWORK_DIR = platform.get_package_dir("framework-arduinoadafruitnrf52")
assert isdir(FRAMEWORK_DIR)

env.Append(
    CFLAGS=["-std=gnu11"],

    CCFLAGS=["--param", "max-inline-insns-single=500"],

    CXXFLAGS=[
        "-std=gnu++11",
        "-fno-threadsafe-statics"
    ],

    CPPDEFINES=[
        ("ARDUINO", 10805),
        # For compatibility with sketches designed for AVR@16 MHz (see SPI lib)
        ("F_CPU", "64000000L"),
        "ARDUINO_ARCH_NRF5",
        "NRF5",
        "NRF52",
        "NRF52832_XXAA",
        ("ARDUINO_BSP_VERSION", '\\"0.7.5\\"' )
    ],

    LIBPATH=[
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "noric", "nrfx", "mdk"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "linker")     
    ],

    #compiler.nrf.flags= -DARDUINO_FEATHER52 -DARDUINO_NRF52_ADAFRUIT -DNRF52_SERIES 
    # {build.sd_flags} {build.debug_flags} 
    # "-I{build.core.path}/cmsis/include" 
    # "-I{nordic.path}" 
    # "-I{nordic.path}/nrfx" 
    # "-I{nordic.path}/nrfx/hal" 
    # "-I{nordic.path}/nrfx/mdk" 
    # "-I{nordic.path}/nrfx/soc" 
    # "-I{nordic.path}/nrfx/drivers/include" 
    # "-I{nordic.path}/softdevice/{build.sd_name}_nrf52_{build.sd_version}_API/include"
    # "-I{rtos.path}/Source/include" "-I{rtos.path}/config" 
    # "-I{rtos.path}/portable/GCC/nrf52" "-I{rtos.path}/portable/CMSIS/nrf52" 
    # "-I{build.core.path}/sysview/SEGGER" 
    # "-I{build.core.path}/sysview/Config" 
    # "-I{build.core.path}/usb" 
    # "-I{build.core.path}/usb/tinyusb/src"


    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "cmsis", "include"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "nordic"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "nordic", "nrfx"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "nordic", "nrfx", "hal"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "nordic", "nrfx", "mdk"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "nordic", "nrfx", "soc"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "nordic", "nrfx", "drivers", "include"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core")),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "utility"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "usb"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "usb", "tinyusb", "src")
    ],

    LINKFLAGS=[
        "--specs=nano.specs",
        "--specs=nosys.specs",
        "-Wl,--check-sections",
        "-Wl,--unresolved-symbols=report-all",
        "-Wl,--warn-common",
        "-Wl,--warn-section-align",
        "-Wl,-Map," + '"' + join("$BUILD_DIR", board.get("build.variant") + ".map") + '"'
    ],

    LIBSOURCE_DIRS=[join(FRAMEWORK_DIR, "libraries")]
)

env.Replace(
    LIBS=["m"]
)

if board.get("build.cpu") == "cortex-m4":
    env.Append(
        CCFLAGS=[
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16",
            "-u _printf_float"
        ],
        LINKFLAGS=[
            "-mfloat-abi=hard",
            "-mfpu=fpv4-sp-d16",
            "-u _printf_float"
        ]
    )

env.Append(
    CPPDEFINES=["%s" % board.get("build.mcu", "")[0:5].upper()]
)

# Process softdevice options
softdevice_name = None
cpp_defines = env.Flatten(env.get("CPPDEFINES", []))
softdevice_name = "s132"
softdevice_ver = "6.1.1"
bootloader_type = "dual"
board_name = "dnaband_v4_1"

if softdevice_name:
    env.Append(
        CPPPATH=[
            join(FRAMEWORK_DIR, "cores", board.get("build.core"),
                "nordic", "softdevice", 
                "%s_nrf52_%s_API" % (softdevice_name, softdevice_ver), "include")
        ],

        CPPDEFINES=[
            "%s" % softdevice_name.upper(),
            ("SD_VER", "611"),
            "SOFTDEVICE_PRESENT"
        ]
    )

    hex_path = join(FRAMEWORK_DIR, "bootloader", board_name)

    for f in listdir(hex_path):
        if f == "%s_bootloader_%s_%s.hex" % (board_name, softdevice_name, softdevice_ver):
            env.Append(DFUBOOTHEX=join(hex_path, f))

    if "DFUBOOTHEX" not in env:
        print ("Warning! Cannot find an appropriate softdevice binary!")

    # Update linker script:
    ldscript_dir = join(FRAMEWORK_DIR, "cores",
                        board.get("build.core"), "linker")
#    mcu_family = board.get("build.ldscript", "").split("_")[1]
#    ldscript_path = ""
#    for f in listdir(ldscript_dir):
#        if f.endswith(mcu_family) and softdevice_name in f.lower():
#            ldscript_path = join(ldscript_dir, f)
    ldscript_name = board.get("build.ldscript", "")
    #"bluefruit52_"+softdevice_name+"_"+softdevice_ver+".ld"

    if ldscript_name:
        env.Append(LINKFLAGS=[
            "-L"+ldscript_dir,
#            "-T"+ldscript_name
        ])
        env.Replace(LDSCRIPT_PATH=ldscript_name)
    else:
        print("Warning! Cannot find an appropriate linker script for the "
              "required softdevice!")

freertos_path = join(FRAMEWORK_DIR, "cores", board.get("build.core"), "freertos")
if(isdir(freertos_path)):
    env.Append(
        CPPPATH=[
            join(freertos_path, "source", "include"),
            join(freertos_path, "config"),
            join(freertos_path, "portable", "GCC", "nrf52"),
            join(freertos_path, "portable", "CMSIS", "nrf52")
        ]
    )

sysview_path = join(FRAMEWORK_DIR, "cores", board.get("build.core"), "sysview")
if(isdir(sysview_path)):
    env.Append(
        CPPPATH=[
            join(sysview_path, "SEGGER"),
            join(sysview_path, "Config")
        ]
    )

# nffs.includes=
# "-I{nffs.path}/fs/nffs/include" 
# "-I{nffs.path}/fs/fs/include"  
# "-I{nffs.path}/fs/disk/include" 
# "-I{nffs.path}/util/crc/include" 
# "-I{nffs.path}/kernel/os/include" 
# "-I{nffs.path}/kernel/os/include/os/arch/cortex_m4" 
# "-I{nffs.path}/hw/hal/include" 
# "-I{nffs.path}/sys/flash_map/include" 
# "-I{nffs.path}/sys/defs/include"

nffs_path = join(FRAMEWORK_DIR, "libraries", "nffs", "src")
if(isdir(nffs_path)):
    env.Append(
        CPPPATH=[
            join(nffs_path, "fs", "nffs", "include"),
            join(nffs_path, "fs", "fs", "include"),
            join(nffs_path, "fs", "disk", "include"),
            join(nffs_path, "util", "crc", "include"),
            join(nffs_path, "kernel", "os", "include"),
            join(nffs_path, "kernel", "os", "include", "os", "arch", "cortex_m4"),
            join(nffs_path, "hw", "hal", "include"),
            join(nffs_path, "sys", "flash_map", "include"),
            join(nffs_path, "sys", "defs", "include")
        ]
    )


#print env.Dump()

# Select crystal oscillator as the low frequency source by default
clock_options = ("USE_LFXO", "USE_LFRC", "USE_LFSYNT")
if not any(d in clock_options for d in cpp_defines):
    env.Append(CPPDEFINES=["USE_LFXO"])

#
# Target: Build Core Library
#

libs = []

if "build.variant" in board:
    env.Append(CPPPATH=[
        join(FRAMEWORK_DIR, "variants", board.get("build.variant"))
    ])

    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "FrameworkArduinoVariant"),
            join(FRAMEWORK_DIR, "variants",
                 board.get("build.variant"))))

libs.append(
    env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduino"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"))))

env.Prepend(LIBS=libs)
