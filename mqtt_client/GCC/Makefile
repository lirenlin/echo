# Copyright Statement:
#
# (C) 2005-2016  MediaTek Inc. All rights reserved.
#
# This software/firmware and related documentation ("MediaTek Software") are
# protected under relevant copyright laws. The information contained herein
# is confidential and proprietary to MediaTek Inc. ("MediaTek") and/or its licensors.
# Without the prior written permission of MediaTek and/or its licensors,
# any reproduction, modification, use or disclosure of MediaTek Software,
# and information contained herein, in whole or in part, shall be strictly prohibited.
# You may only use, reproduce, modify, or distribute (as applicable) MediaTek Software
# if you have agreed to and been bound by the applicable license agreement with
# MediaTek ("License Agreement") and been granted explicit permission to do so within
# the License Agreement ("Permitted User").  If you are not a Permitted User,
# please cease any access or use of MediaTek Software immediately.
# BY OPENING THIS FILE, RECEIVER HEREBY UNEQUIVOCALLY ACKNOWLEDGES AND AGREES
# THAT MEDIATEK SOFTWARE RECEIVED FROM MEDIATEK AND/OR ITS REPRESENTATIVES
# ARE PROVIDED TO RECEIVER ON AN "AS-IS" BASIS ONLY. MEDIATEK EXPRESSLY DISCLAIMS ANY AND ALL
# WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE OR NONINFRINGEMENT.
# NEITHER DOES MEDIATEK PROVIDE ANY WARRANTY WHATSOEVER WITH RESPECT TO THE
# SOFTWARE OF ANY THIRD PARTY WHICH MAY BE USED BY, INCORPORATED IN, OR
# SUPPLIED WITH MEDIATEK SOFTWARE, AND RECEIVER AGREES TO LOOK ONLY TO SUCH
# THIRD PARTY FOR ANY WARRANTY CLAIM RELATING THERETO. RECEIVER EXPRESSLY ACKNOWLEDGES
# THAT IT IS RECEIVER'S SOLE RESPONSIBILITY TO OBTAIN FROM ANY THIRD PARTY ALL PROPER LICENSES
# CONTAINED IN MEDIATEK SOFTWARE. MEDIATEK SHALL ALSO NOT BE RESPONSIBLE FOR ANY MEDIATEK
# SOFTWARE RELEASES MADE TO RECEIVER'S SPECIFICATION OR TO CONFORM TO A PARTICULAR
# STANDARD OR OPEN FORUM. RECEIVER'S SOLE AND EXCLUSIVE REMEDY AND MEDIATEK'S ENTIRE AND
# CUMULATIVE LIABILITY WITH RESPECT TO MEDIATEK SOFTWARE RELEASED HEREUNDER WILL BE,
# AT MEDIATEK'S OPTION, TO REVISE OR REPLACE MEDIATEK SOFTWARE AT ISSUE,
# OR REFUND ANY SOFTWARE LICENSE FEES OR SERVICE CHARGE PAID BY RECEIVER TO
# MEDIATEK FOR SUCH MEDIATEK SOFTWARE AT ISSUE.
#


SOURCE_DIR = ../../../../..
BINPATH    = ~/gcc-arm-none-eabi/bin

PWD        = $(shell pwd)

FEATURE    = feature.mk

include $(FEATURE)

# Gloabl Config
-include $(SOURCE_DIR)/.config
# IC Config
-include $(SOURCE_DIR)/config/chip/$(IC_CONFIG)/chip.mk
# Board Config
-include $(SOURCE_DIR)/config/board/$(BOARD_CONFIG)/board.mk
# EPT Config
-include $(SOURCE_DIR)/driver/board/mt76x7_hdk/ept/module.mk
# Minisupp Config
-include $(SOURCE_DIR)/middleware/MTK/minisupp/module.mk

RAM_BOOTING=0

DEBUG      = 0
FLOAT_TYPE = hard
BUILD_DIR  = $(PWD)/Build

# Project name
PROJ_NAME = mqtt_client
PROJ_PATH = $(PWD)
OUTPATH = $(PWD)/Build

# Main APP files
APP_NAME = mqtt_client
APP_PATH = project/mt7687_hdk/apps/mqtt_client
APP_PATH_SRC = $(APP_PATH)/src
APP_FILES =    $(APP_PATH_SRC)/sys_init.c \
               $(APP_PATH_SRC)/wifi_lwip.c \
               $(APP_PATH_SRC)/system_mt7687.c \
               $(APP_PATH)/GCC/syscalls.c \

C_FILES += $(APP_FILES)
C_FILES += $(APP_PATH_SRC)/main.c
C_FILES += $(APP_PATH_SRC)/mqtt.c
C_FILES += $(APP_PATH_SRC)/mqtt_tls.c
C_FILES += $(APP_PATH_SRC)/ept_gpio_var.c
C_FILES += $(APP_PATH_SRC)/ept_eint_var.c


# add startup file to build
S_FILES += $(APP_PATH)/GCC/startup_mt7687.s

C_OBJS = $(C_FILES:%.c=$(BUILD_DIR)/%.o)
S_OBJS = $(S_FILES:%.s=$(BUILD_DIR)/%.o)

CFLAGS += -DMTK_FW_VERSION=\"$(MTK_FW_VERSION)\"

###################################################
# include path
CFLAGS += -I$(SOURCE_DIR)/$(APP_PATH)/inc
CFLAGS += -I$(SOURCE_DIR)/driver/chip/mt7687/inc
CFLAGS += -I$(SOURCE_DIR)/driver/chip/inc
CFLAGS += -I$(SOURCE_DIR)/middleware/third_party/lwip/src/include
CFLAGS += -I$(SOURCE_DIR)/middleware/third_party/lwip/ports/include
CFLAGS += -I$(SOURCE_DIR)/middleware/third_party/mqtt/MQTTClient-C/src/mediatek
CFLAGS += -I$(SOURCE_DIR)/middleware/third_party/mqtt/MQTTClient-C/src
CFLAGS += -I$(SOURCE_DIR)/middleware/third_party/mqtt/MQTTPacket/src
CFLAGS += -I$(SOURCE_DIR)/driver/board/mt76x7_hdk/ept/inc

###################################################
# LD Flags
LDFLAGS = $(ALLFLAGS) $(FPUFLAGS) --specs=nano.specs -lnosys -nostartfiles
LDFLAGS += -Wl,-wrap=malloc -Wl,-wrap=calloc -Wl,-wrap=realloc -Wl,-wrap=free
ifeq ($(RAM_BOOTING), 1)
LDFLAGS += -Wl,-Tmt7687_sram.ld -Wl,--gc-sections
else
LDFLAGS += -Wl,-Tmt7687_flash.ld -Wl,--gc-sections
endif

###################################################
# Libraries
LIBS += $(OUTPATH)/libbspex.a
LIBS += $(OUTPATH)/libmqtt.a
LIBS += $(OUTPATH)/libmbedtls.a
LIBS += $(OUTPATH)/libbsp.a
ifeq ($(MTK_NVDM_ENABLE), y)
LIBS += $(OUTPATH)/libnvdm_CM4_GCC.a
endif
LIBS += $(OUTPATH)/librtos.a
LIBS += $(OUTPATH)/libservice.a
LIBS += $(OUTPATH)/liblwip.a
LIBS += $(OUTPATH)/libhal.a
LIBS += $(OUTPATH)/libdhcpd.a


MODULE_PATH += $(KRL_OS_PATH)
MODULE_PATH += $(MID_LWIP_PATH)
MODULE_PATH += $(MID_DHCPD_PATH)
MODULE_PATH += $(MID_MBEDTLS_PATH)
MODULE_PATH += $(MID_MQTT_PATH)
ifeq ($(MTK_NVDM_ENABLE), y)
MODULE_PATH += $(MID_NVDM_PATH)
endif
MODULE_PATH += $(MID_BSPEXT_PATH)
MODULE_PATH += $(DRV_CHIP_PATH)
MODULE_PATH += $(KRL_SRV_PATH)
MODULE_PATH += $(DRV_BSP_PATH)
###################################################
# Rules
.PHONY: proj clean $(MODULE_PATH)

all: cleanlog proj
	@mkdir -p $(BUILD_DIR)
	@$(SIZE) $(OUTPATH)/$(PROJ_NAME).elf
	@echo "Generate Assembly from elf:"
	@$(OBJDUMP) -S $(OUTPATH)/$(PROJ_NAME).elf > $(OUTPATH)/$(PROJ_NAME).elf.s
	@$(SOURCE_DIR)/tools/scripts/build/copy_firmware.sh $(SOURCE_DIR) $(OUTPATH) $(IC_CONFIG) $(BOARD_CONFIG) $(PROJ_NAME).bin $(PWD)

MOD_EXTRA = BUILD_DIR=$(BUILD_DIR) OUTPATH=$(OUTPATH) PROJ_PATH=$(PROJ_PATH) CONFIG_PATH=$(APP_PATH)/inc

$(LIBS): $(MODULE_PATH)

$(MODULE_PATH):
	@+make -C $@ $(MOD_EXTRA) $($@_EXTRA)


proj: $(OUTPATH)/$(PROJ_NAME).elf

$(OUTPATH)/$(PROJ_NAME).elf: $(C_OBJS) $(S_OBJS) $(LIBS)
	@echo Linking...
	@if [ -e "$@" ]; then rm -f "$@"; fi
	@if [ -e "$(OUTPATH)/$(PROJ_NAME).map" ]; then rm -f "$(OUTPATH)/$(PROJ_NAME).map"; fi
	@if [ -e "$(OUTPATH)/$(PROJ_NAME).hex" ]; then rm -f "$(OUTPATH)/$(PROJ_NAME).hex"; fi
	@if [ -e "$(OUTPATH)/$(PROJ_NAME).bin" ]; then rm -f "$(OUTPATH)/$(PROJ_NAME).bin"; fi
	@$(CC) $(LDFLAGS) -Wl,--start-group $^ -Wl,--end-group -Wl,-Map=$(OUTPATH)/$(PROJ_NAME).map -lm -o $@ 2>>$(ERR_LOG)
	@$(OBJCOPY) -O ihex $(OUTPATH)/$(PROJ_NAME).elf $(OUTPATH)/$(PROJ_NAME).hex
	@$(OBJCOPY) -O binary $(OUTPATH)/$(PROJ_NAME).elf $(OUTPATH)/$(PROJ_NAME).bin
	@echo Done

include $(SOURCE_DIR)/.rule.mk

clean:
	rm -rf $(OUTPATH)

print-%  : ; @echo $* = $($*)
