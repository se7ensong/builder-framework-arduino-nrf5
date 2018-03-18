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
        # For compatibility with sketches designed for AVR@16 MHz (see SPI lib)
        ("F_CPU", "16000000L"),
        "ARDUINO_ARCH_NRF5",
        "NRF5",
        "NRF52",
        ("ARDUINO_BSP_VERSION", '\\"0.7.5\\"' )
    ],

    LIBPATH=[
        join(FRAMEWORK_DIR, "cores",
             env.BoardConfig().get("build.core"), "SDK", "components",
             "toolchain", "gcc")
    ],

    #compiler.nrf.flags=-DARDUINO_NRF52_ADAFRUIT -DNRF5 -DNRF52 -DNRF52832_XXAA -DUSE_LFXO {build.sd_flags} {build.debug_flags} 
    # "-I{nrf.sdk.path}/components/toolchain/" 
    # "-I{nrf.sdk.path}/components/toolchain/cmsis/include" 
    # "-I{nrf.sdk.path}/components/toolchain/gcc/" 
    # "-I{nrf.sdk.path}/components/device/" 
    # "-I{nrf.sdk.path}/components/drivers_nrf/delay/" 
    # "-I{nrf.sdk.path}/components/drivers_nrf/hal/" 
    # "-I{nrf.sdk.path}/components/libraries/util/" 
    # "-I{build.core.path}/softdevice/{build.sd_name}/{build.sd_version}/headers/" 
    # "-I{rtos.path}/source/include" 
    # "-I{rtos.path}/config" 
    # "-I{rtos.path}/portable/GCC/nrf52" 
    # "-I{rtos.path}/portable/CMSIS/nrf52" 
    # "-I{build.core.path}/sysview/SEGGER" 
    # "-I{build.core.path}/sysview/Config" {nffs.includes}

    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", board.get("build.core")),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "SDK", "components", "drivers_nrf", "delay"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "SDK", "components", "drivers_nrf", "hal"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "SDK", "components", "device"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "SDK", "components", "toolchain"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "SDK", "components", "toolchain", "cmsis", "include"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "SDK", "components", "toolchain", "gcc"),
        join(FRAMEWORK_DIR, "cores", board.get("build.core"),
             "SDK", "components", "libraries", "util")
    ],

    LINKFLAGS=[
        "--specs=nano.specs",
        "--specs=nosys.specs",
        "-Wl,--check-sections",
        "-Wl,--unresolved-symbols=report-all",
        "-Wl,--warn-common",
        "-Wl,--warn-section-align"
    ],

    LIBSOURCE_DIRS=[join(FRAMEWORK_DIR, "libraries")])

if env.BoardConfig().get("build.cpu") == "cortex-m4":
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
    CPPDEFINES=["%s" % env.BoardConfig().get("build.mcu", "")[0:5].upper()]
)

# Process softdevice options
softdevice_name = None
cpp_defines = env.Flatten(env.get("CPPDEFINES", []))
softdevice_name = "s132"
softdevice_ver = "5.1.0"
bootloader_type = "dual"
board_name = "feather52"

if softdevice_name:
    env.Append(
        CPPPATH=[
            join(FRAMEWORK_DIR, "cores", board.get("build.core"),
                "softdevice", softdevice_name, softdevice_ver, "headers")
        ],

        CPPDEFINES=[
            "%s" % softdevice_name.upper(),
            "SOFTDEVICE_PRESENT"
        ]
    )

    hex_path = join(FRAMEWORK_DIR, "bin", "bootloader",
                    board_name, softdevice_ver, bootloader_type)

    for f in listdir(hex_path):
        if f.endswith(softdevice_ver + "_" + bootloader_type + ".hex") and f.lower().startswith(board_name):
            env.Append(SOFTDEVICEHEX=join(hex_path, f))

    if "SOFTDEVICEHEX" not in env:
        print "Warning! Cannot find an appropriate softdevice binary!"

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
clock_options = ("USE_LFXO", "USE_LFRC" "USE_LFSYNT")
if not any(d in clock_options for d in cpp_defines):
    env.Append(CPPDEFINES=["USE_LFXO"])

# Construct upload flags
upload_args = []
upload_protocol = env.subst("$UPLOAD_PROTOCOL")
debug_tools = env.BoardConfig().get("debug.tools", {})
if upload_protocol in debug_tools:
    upload_args = ["-s", platform.get_package_dir("tool-openocd") or ""]
    upload_args += debug_tools.get(
        upload_protocol).get("server").get("arguments", [])
    upload_args += ["-c", "program {{$SOURCE}} verify reset; shutdown;"]
else:
    print "Warning! Cannot find an apropriate upload method!"

env.Replace(
    LIBS=["m"],
    UPLOADER="openocd",
    UPLOADERFLAGS=upload_args,
    UPLOADCMD='"$UPLOADER" $UPLOADERFLAGS'
)

#
# Target: Build Core Library
#

libs = []

if "build.variant" in env.BoardConfig():
    env.Append(CPPPATH=[
        join(FRAMEWORK_DIR, "variants", env.BoardConfig().get("build.variant"))
    ])

    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "FrameworkArduinoVariant"),
            join(FRAMEWORK_DIR, "variants",
                 env.BoardConfig().get("build.variant"))))

libs.append(
    env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduino"),
        join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core"))))

env.Prepend(LIBS=libs)
