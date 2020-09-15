#!/usr/bin/python
"""
@package libraw.py
Python Bindings for libraw

use the documentation of libraw C API for function calls
based on: https://gist.github.com/campaul/ee30b2dbc2c11a699bde

@author: Pavel Rojtberg (http://www.rojtberg.net)
@see: https://github.com/paroj/libraw.py
@copyright: LGPLv2 (same as libraw) <http://opensource.org/licenses/LGPL-2.1>

@change: Modified for use on Raspberry Pi by Dan Kimberling.
@see: https://github.com/Dan-in-CA/LibRaw-forPi
"""

# standard library imports
from ctypes import *
import numpy as np
import os
import sys

so_file = "libraw.so.20.0.0"
 
def find(name):
    """
    locate the *.so (shared object) file to bind to. 
    """
    try:
        for root, dirs, files in os.walk("/"):
            if name in files:
                return os.path.join(root, name)
    except Exception as e:
        print("LibRaw file not found " + e )
 
try:
    _hdl = cdll.LoadLibrary("/usr/local/lib/libraw.so.20.0.0")
except OSError:
    so_path = find(so_file)
    _hdl = cdll.LoadLibrary(so_path)
    print("Using {}".format(so_path))
    
# enum_LibRaw_thumbnail_formats = c_int
time_t = c_long

class libraw_decoder_info_t(Structure):
    """Describes a raw format decoder name and format."""
    _fields_ = [
        ('decoder_name', c_char_p),
        ('decoder_flags', c_uint),
 
    ]

class libraw_internal_output_params_t(Structure):
    _fields_ = [
        ('mix_green', c_uint),
        ('raw_color', c_uint),
        ('zero_is_bad', c_uint),
        ('shrink', c_ushort),
        ('fuji_width', c_ushort),
    ]


class libraw_processed_image_t(Structure):
    """A container for processed image data."""
    _fields_ = [
        ('type', c_uint),  # Libraw_image_formats
        ('height', c_ushort),
        ('width', c_ushort),
        ('colors', c_ushort),
        ('bits', c_ushort),
        ('data_size', c_uint),
        ('data', c_ubyte * 1),
    ]
 
    
class libraw_iparams_t(Structure):
    """The primary parameters of the image."""
    _fields_ = [
        ('guard', c_char * 4),
        ('make', c_char * 64),
        ('model', c_char * 64),
        ('software', c_char * 64),
        ('normalized_make', c_char * 64),
        ("normalized_model", c_char * 64),
        ("maker_index", c_uint),        
        ('raw_count', c_uint),
        ('dng_version', c_uint),
        ('is_foveon', c_uint),
        ('colors', c_int),
        ('filters', c_uint),
        ('xtrans', c_char * 6 * 6),
        ('xtrans_abs', c_char * 6 * 6),
        ('cdesc', c_char * 5),
        ('xmplen', c_uint),
        ('xmpdata', POINTER(c_char)),
    ]
 
    
class libraw_raw_inset_crop_t(Structure):
    """Describes the crop of an image."""
    _fields_ = [
        ('cleft', c_ushort),
        ('ctop', c_ushort),
        ('cwidth', c_ushort),
        ('cheight', c_ushort),
        ('aspect', c_ushort),
    ]   


class libraw_image_sizes_t(Structure):
    """Describes the size of the image."""
    _fields_ = [
        ('raw_height', c_ushort),
        ('raw_width', c_ushort),
        ('height', c_ushort),
        ('width', c_ushort),
        ('top_margin', c_ushort),
        ('left_margin', c_ushort),
        ('iheight', c_ushort),
        ('iwidth', c_ushort),
        ('raw_pitch', c_uint),
        ('pixel_aspect', c_double),
        ('flip', c_int),
        ('mask', c_int * 8 * 4),
        ('raw_inset_crop', libraw_raw_inset_crop_t),
    ]


class ph1_t(Structure):
    _fields_ = [
        ('format', c_int),
        ('key_off', c_int),
        ('tag_21a', c_int),
        ('t_black', c_int),
        ('split_col', c_int),
        ('black_col', c_int),
        ('split_row', c_int),
        ('black_row', c_int),
        ('tag_210', c_float),
    ]


class libraw_dng_color_t(Structure):
    _fields_ = [
        ('parsedfields', c_uint),
        ('illuminant', c_ushort),
        ('_calibration', (c_float * 4) * 4),
        ('_colormatrix', (c_float * 4) * 3),
        ('_forwardmatrix', c_float * 3 * 4),
    ]
    
    @property
    def calibration(self):
        return _array_from_memory(self._calibration, (4, 4), np.float32)   
    
    @property
    def colormatrix(self):
        return _array_from_memory(self._colormatrix, (4, 3), np.float32).T
   
    @property
    def forwardmatrix(self):
        return _array_from_memory(self._forwardmatrix, (3, 4), np.float32)

    
class libraw_dng_levels_t(Structure):
    _fields_ = [
        ('parsedFields', c_uint),
        ('dng_cblack', c_uint * 4102),
        ('dng_black', c_uint),
        ('dng_whitelevel', c_uint * 4),
        ('default_crop', c_uint * 4),  # Origin and size
        ('preview_colorspace', c_uint),
        ('analogbalance', c_float * 4),
    ]


class libraw_P1_color_t(Structure):
    _fields_ = [
        ('romm_cam', c_float * 9),
    ]
 
 
class libraw_canon_makernotes_t(Structure):
    _fields_ = [
        ('ColorDataVer', c_int),
        ('ColorDataSubVer', c_int),
        ('SpecularWhiteLevel', c_int),
        ('NormalWhiteLevel', c_int),
        ('ChannelBlackLevel', c_int * 4),
        ('AverageBlackLevel', c_int),
        ('multishot', c_uint * 4),
        ('MeteringMode', c_short),
        ('SpotMeteringMode', c_short),
        ('FlashMeteringMode', c_char),
        ('FlashExposureLock', c_short),
        ('ExposureMode', c_short),
        ('AESetting', c_short),
        ('HighlightTonePriority', c_char),
        ('ImageStabilization', c_short),
        ('FocusMode', c_short),
        ('AFPoint', c_short),
        ('FocusContinuous', c_short),
        ('AFPointsInFocus30D', c_short),
        ('AFPointsInFocus1D', c_char * 8),
        ('AFPointsInFocus5D', c_ushort),
        ('AFAreaMode', c_ushort),
        ('NumAFPoints', c_ushort),
        ('ValidAFPoints', c_ushort),
        ('AFImageWidth', c_ushort),
        ('AFImageHeight', c_ushort),
        ('AFAreaWidths', c_short * 61),
        ('AFAreaHeights', c_short * 61),
        ('AFAreaXPositions', c_short * 61),
        ('AFAreaYPositions', c_short * 61),
        ('AFPointsInFocus', c_short * 4),
        ('AFPointsSelected', c_short * 4),
        ('PrimaryAFPoint', c_ushort),
        ('FlashMode', c_short),
        ('FlashActivity', c_short),
        ('FlashBits', c_short),
        ('ManualFlashOutput', c_short),
        ('FlashOutput', c_short),
        ('FlashGuideNumber', c_short),
        ('ContinuousDrive', c_short),
        ('SensorWidth', c_short),
        ('SensorHeight', c_short),
        ('SensorLeftBorder', c_short),
        ('SensorTopBorder', c_short),
        ('SensorRightBorder', c_short),
        ('SensorBottomBorder', c_short),
        ('BlackMaskLeftBorder', c_short),
        ('BlackMaskTopBorder', c_short),
        ('BlackMaskRightBorder', c_short),
        ('BlackMaskBottomBorder', c_short),
        ('AFMicroAdjMode', c_int),
        ('AFMicroAdjValue', c_float),
        ('MakernotesFlip', c_short),
        ('RecordMode', c_short),
        ('SRAWQuality', c_short),
        ('wbi', c_uint),
        ('firmware', c_float),
        ('RF_lensID', c_short),
    ]    


class libraw_hasselblad_makernotes_t(Structure):
    _fields_ = [
        ('BaseISO', c_int),
        ('Gain', c_double),
        ('Sensor', c_char * 8),
        ('SensorUnit', c_char * 64),
        ('HostBody', c_char * 64),
        ('SensorCode', c_int),
        ('SensorSubCode', c_int),
        ('CoatingCode', c_int),
        ('uncropped', c_int),
        ('CaptureSequenceInitiator', c_char * 32),
        ('SensorUnitConnector', c_char * 64),
        ('format', c_int),
        ('nIFD_CM', c_int),
        ('RecommendedCrop', c_int),
        ('mnColorMatrix', c_double),
    ]


class libraw_fuji_info_t(Structure):
    _fields_ = [
        ('ExpoMidPointShift', c_float),
        ('DynamicRange', c_ushort),
        ('FilmMode', c_ushort),
        ('DynamicRangeSetting', c_ushort),
        ('DevelopmentDynamicRange', c_ushort),
        ('AutoDynamicRange', c_ushort),
        ('DRangePriority', c_ushort),
        ('DRangePriorityAuto', c_ushort),
        ('DRangePriorityFixed', c_ushort),
        ('BrightnessCompensation', c_float),
        ('FocusMode', c_ushort),
        ('AFMode', c_ushort),
        ('FocusPixel', c_ushort * 2),
        ('ImageStabilization', c_ushort * 3),
        ('FlashMode', c_ushort),
        ('WB_Preset', c_ushort),
        ('ShutterType', c_ushort),
        ('ExrMode', c_ushort),
        ('Macro', c_ushort),
        ('Rating', c_uint),
        ('CropMode', c_ushort),
        ('FrameRate', c_ushort),
        ('FrameWidth', c_ushort),
        ('FrameHeight', c_ushort),
        ('SerialSignature', c_char * (0x0c + 1)),
        ('RAFVersion', c_char * (4 + 1)),
        ('RAFDataVersion', c_ushort),
        ('isTSNERDTS', c_uint),
        ('DriveMode', c_ushort),
    ]
 
    
class libraw_sensor_highspeed_crop_t(Structure):
    _fields_ = [
        ('cleft', c_ushort),
        ('ctop', c_ushort),
        ('cwidth', c_ushort),
        ('cheight', c_ushort),
    ]
 
    
class libraw_nikon_makernotes_t(Structure):
    _fields_ = [
        ('ExposureBracketValue', c_double),
        ('ActiveDLighting', c_ushort),
        ('ShootingMode', c_ushort),
        ('ImageStabilization', c_ubyte * 7),
        ('VibrationReduction', c_ubyte),
        ('VRMode', c_ubyte),
        ('FocusMode', c_char * 7),
        ('AFPoint', c_ubyte),
        ('AFPointsInFocus', c_ushort),
        ('ContrastDetectAF', c_ubyte),
        ('AFAreaMode', c_ubyte),
        ('PhaseDetectAF', c_ubyte),
        ('PrimaryAFPoint', c_ubyte),
        ('AFPointsUsed', c_ubyte * 29),
        ('AFImageWidth', c_ushort),
        ('AFImageHeight', c_ushort),
        ('AFAreaXPposition', c_ushort),
        ('AFAreaYPosition', c_ushort),
        ('AFAreaWidth', c_ushort),
        ('AFAreaHeight', c_ushort),
        ('ContrastDetectAFInFocus', c_ubyte),
        ('FlashSetting', c_char * 13),
        ('FlashType', c_char * 20),
        ('FlashExposureCompensation', c_ubyte * 4),
        ('ExternalFlashExposureComp', c_ubyte * 4),
        ('FlashExposureBracketValue', c_ubyte * 4),
        ('FlashMode', c_ubyte),
        ('FlashExposureCompensation2', c_char),
        ('FlashExposureCompensation3', c_char),
        ('FlashExposureCompensation4', c_char),
        ('FlashSource', c_ubyte),
        ('FlashFirmware', c_ubyte * 2),
        ('ExternalFlashFlags', c_ubyte),
        ('FlashControlCommanderMode', c_ubyte),
        ('FlashOutputAndCompensation', c_ubyte),
        ('FlashFocalLength', c_ubyte),
        ('FlashGNDistance', c_ubyte),
        ('FlashGroupControlMode', c_ubyte * 4),
        ('FlashGroupOutputAndCompensation', c_ubyte * 4),
        ('FlashColorFilter', c_ubyte),
        ('NEFCompression', c_ushort),
        ('ExposureMode', c_int),
        ('ExposureProgram', c_int),
        ('nMEshots', c_int),
        ('MEgainOn', c_int),
        ('ME_WB', c_double * 4),
        ('AFFineTune', c_ubyte),
        ('AFFineTuneIndex', c_ubyte),
        ('AFFineTuneAdj', c_int8),
        ('LensDataVersion', c_uint),
        ('FlashInfoVersion', c_uint),
        ('ColorBalanceVersion', c_uint),
        ('key', c_ubyte),
        ('NEFBitDepth', c_ushort * 4),
        ('HighSpeedCropFormat', c_ushort),
        ('SensorHighSpeedCrop', libraw_sensor_highspeed_crop_t),
        ('SensorWidth', c_ushort),
        ('SensorHeight', c_ushort),
    ]
 
    
class libraw_olympus_makernotes_t(Structure):
    _fields_ = [
        ('SensorCalibration', c_int * 2),
        ('FocusMode', c_ushort * 2),
        ('AutoFocus', c_ushort),
        ('AFPoint', c_ushort),
        ('AFAreas', c_uint * 64),
        ('AFPointSelected', c_double * 5),
        ('AFResult', c_ushort),
        ('DriveMode', c_ushort * 5),
        ('ColorSpace', c_ushort),
        ('AffineTune', c_ubyte),
        ('AffineTuneAdj', c_short * 3),
        ("CameraType2", c_char * 6)
    ]
 
    
class libraw_panasonic_makernotes_t(Structure):
    _fields_ = [
        # Compression:
        # 34826 (Panasonic RAW 2): LEICA DIGILUX 2;
        # 34828 (Panasonic RAW 3): LEICA D-LUX 3; LEICA V-LUX 1; Panasonic DMC-LX1; Panasonic DMC-LX2; Panasonic DMC-FZ30; Panasonic DMC-FZ50;
        # 34830 (not in exiftool): LEICA DIGILUX 3; Panasonic DMC-L1;
        # 34316 (Panasonic RAW 1): others (LEICA, Panasonic, YUNEEC);
        ('Compression', c_ushort),
        ('BlackLevelDim', c_ushort),
        ('BlackLevel', c_float * 8),
        ('Multishot', c_uint),
        ('gamma', c_float),
        ('HighISOMultiplier', c_int * 3),
    ]

    
class libraw_pentax_makernotes_t(Structure):
    _fields_ = [
        ('FocusMode', c_ushort),
        ('AFPointSelected', c_ushort),
        ('AFPointsInFocus', c_uint),
        ('FocusPosition', c_ushort),
        ('DriveMode', c_ubyte * 4),
        ('AFAdjustment', c_short),
        ('MultiExposure', c_ubyte),
        ('Quality', c_ushort),
    ]


class libraw_kodak_makernotes_t(Structure):
    _fields_ = [
        ('BlackLevelTop', c_ushort),
        ('BlackLevelBottom', c_ushort),
        ('offset_left', c_short),  # KDC files, negative values or zeros
        ('offset_top', c_short),  # KDC files, negative values or zeros
        ('clipBlack', c_ushort),  # valid for P712, P850, P880
        ('clipWhite', c_ushort),  # valid for P712, P850, P880
        ('romm_camDaylight', c_float * 3 * 3),
        ('romm_camTungsten', c_float * 3 * 3),
        ('romm_camFlourescent', c_float * 3 * 3),
        ('romm_camFlash', c_float * 3 * 3),
        ('romm_camCustom', c_float * 3 * 3),
        ('romm_camAuto', c_float * 3 * 3),
        ('val018percent', c_ushort),
        ('val100percent', c_ushort),
        ('val170percent', c_ushort),
        ('MakerNoteKodak8a', c_short),
        ('ISOCalibrationGain', c_float),
        ('AnalogISO', c_float),
    ]


class libraw_p1_makernotes_t(Structure):
    _fields_ = [
        ('Software', c_byte * 64),
        ('SystemType', c_byte * 64),
        ('FirmwareString', c_byte * 256),
        ('SystemModel', c_byte * 64),
    ] 


class libraw_sony_info_t(Structure):
    _fields_ = [
        ('CameraType', c_ushort),
        ('Sony0x9400_version', c_ubyte), # 0 if not found/deciphered, 0xa, 0xb, 0xc following exiftool convention
        ('Sony0x9400_ReleaseMode2', c_ubyte),
        ('Sony0x9400_SequenceImageNumber', c_uint),
        ('Sony0x9400_SequenceLength1', c_ubyte),
        ('Sony0x9400_SequenceFileNumber', c_uint),
        ('Sony0x9400_SequenceLength2', c_ubyte),
        ('AFAreaModeSetting', c_ubyte),
        ('FlexibleSpotPosition', c_ushort),
        ('AFPointSelected', c_ubyte),
        ('AFPointsUsed', c_ubyte),
        ('AFTracking', c_ubyte),
        ('AFType', c_ubyte),
        ('FocusLocation', c_ushort),
        ('AFMicroAdjValue', c_int8),
        ('AFMicroAdjOn', c_int8),
        ('AFMicroAdjRegisteredLenses;', c_ubyte),
        ('VariableLowPassFilter', c_ushort),
        ('LongExposureNoiseReduction', c_uint),
        ('HighISONoiseReduction', c_ushort),
        ('HDR', c_ushort * 2),
        ('group2010', c_ushort),
        ('real_iso_offset', c_ushort),
        ('MeteringMode_offset', c_ushort),
        ('ExposureProgram_offset', c_ushort),
        ('ReleaseMode2_offset', c_ushort),
        ('MinoltaCamID', c_uint),
        ('firmware', c_float),
        ('ImageCount3_offset', c_ushort),
        ('ImageCount3', c_uint),
        ('ElectronicFrontCurtainShutter', c_uint),
        ('MeteringMode2', c_ushort),
        ('SonyDateTime', c_char * 20),
        ('ShotNumberSincePowerUp', c_uint),
        ('PixelShiftGroupPrefix', c_ushort),
        ('PixelShiftGroupID', c_uint),
        ('nShotsInPixelShiftGroup', c_char),
        ('numInPixelShiftGroup', c_char),
        ('prd_ImageHeight', c_ushort),
        ('prd_ImageWidth', c_ushort),
        ('prd_RawBitDepth', c_ushort),
        ('prd_StorageMethod', c_ushort),
        ('prd_BayerPattern', c_ushort),
        ('SonyRawFileType', c_ushort),
        ('RAWFileType', c_ushort),
        ('Quality', c_uint),
        ('FileFormat' , c_ushort),
    ]


class libraw_colordata_t(Structure):
    _fields_ = [
        ('_curve', c_ushort * 0x10000),
        ('_cblack', c_uint * 4102),
        ('black', c_uint),
        ('data_maximum', c_uint),
        ('maximum', c_uint),
        ('linear_max', c_long * 4),
        ('fmaximum', c_float),
        ('fnorm', c_float),
        ('white', c_ushort * 8 * 8),
        ('_cam_mul', c_float * 4),
        ('_pre_mul', c_float * 4),
        ('_cmatrix', (c_float * 4) * 3),
        ('ccm', c_float * 3 * 4),
        ('_rgb_cam', (c_float * 4) * 3),
        ('_cam_xyz', (c_float * 3) * 4),
        ('phase_one_data', ph1_t),
        ('flash_used', c_float),
        ('canon_ev', c_float),
        ('model2', c_char * 64),
        ('UniqueCameraModel', c_char * 64),
        ('LocalizedCameraModel', c_char * 64),
        ('ImageUniqueID', c_char * 64),
        ('RawDataUniqueID', c_char * 17),
        ('OriginalRawFileName', c_char * 64),      
        ('profile', c_void_p),
        ('profile_length', c_uint),
        ('black_stat', c_uint * 8),
        ('dng_color', libraw_dng_color_t * 2),
        ('dng_levels', libraw_dng_levels_t),
        ('WB_Coeffs', c_int * 256 * 4),
        ('WBCT_Coeffs', c_float * 64 * 5),
        ('as_shot_wb_applied', c_int),
        ('P1_color', libraw_P1_color_t * 2),
        ('raw_bps', c_uint),
        ('ExifColorSpace', c_int),
    ]

    @property
    def curve(self):
        return _array_from_memory(self._curve, (0x10000,), np.uint16)
    
    @property
    def cblack(self):
        return _array_from_memory(self._cblack, (4102,), np.uint32)
    
    @property
    def cam_mul(self):
        return _array_from_memory(self._cam_mul, (4,), np.float32)

    @property
    def pre_mul(self):
        return _array_from_memory(self._pre_mul, (4,), np.float32)

    @property
    def cmatrix(self):
        return _array_from_memory(self._cmatrix, (3, 4), np.float32)

    @property
    def rgb_cam(self):
        return _array_from_memory(self._rgb_cam, (3, 4), np.float32)
    
    @property
    def cam_xyz(self):
        return _array_from_memory(self._cam_xyz, (3, 4), np.float32)


class libraw_thumbnail_t(Structure):
    _fields_ = [
        ('tformat', c_uint),  # LibRaw_thumbnail_formats
        ('twidth', c_ushort),
        ('theight', c_ushort),
        ('tlength', c_uint),
        ('tcolors', c_int),
        ('thumb', POINTER(c_char)),
    ]


class libraw_gps_info_t(Structure):
    _fields_ = [
        ('latitude', c_float * 3),
        ('longtitude', c_float * 3),
        ('gpstimestamp', c_float * 3),
        ('altitude', c_float),
        ('altref', c_char),
        ('latref', c_char),
        ('longref', c_char),
        ('gpsstatus', c_char),
        ('gpsparsed', c_char),
    ]
 
    
class libraw_imgother_t(Structure):
    _fields_ = [
        ('iso_speed', c_float),
        ('shutter', c_float),
        ('aperture', c_float),
        ('focal_len', c_float),
        ('timestamp', time_t),
        ('shot_order', c_uint),
        ('gpsdata', c_uint * 32),
        ('parsed_gps', libraw_gps_info_t),
        ('desc', c_char * 512),
        ('artist', c_char * 64),
        ('analogbalance', c_float * 4),
    ]


class libraw_metadata_common_t(Structure):
    _fields_ = [  
        ('FlashEC', c_float),
        ('FlashGN', c_float),
        ('CameraTemperature', c_float),
        ('SensorTemperature', c_float),
        ('SensorTemperature2', c_float),
        ('LensTemperature', c_float),
        ('AmbientTemperature', c_float),
        ('BatteryTemperature', c_float),
        ('exifAmbientTemperature', c_float),
        ('exifHumidity', c_float),
        ('exifPressure', c_float),
        ('exifWaterDepth', c_float),
        ('exifAcceleration', c_float),
        ('exifCameraElevationAngle', c_float),
        ('real_ISO', c_float),
        ('exifExposureIndex', c_float),
        ('ColorSpace', c_ushort),
        ('firmware', c_char),
    ]
 
    
class libraw_output_params_t(Structure):
    """Output parameters for processing the image with dcraw."""
    _fields_ = [                      #  Related dcraw switches:
        ('greybox', c_uint * 4),      # -A  x1 y1 x2 y2
        ('cropbox', c_uint * 4),      # -B x1 y1 x2 y2
        ('aber', c_double * 4),       # -C
        ('gamm', c_double * 6),       # -g
        ('user_mul', c_float * 4),    # -r mul0 mul1 mul2 mul3
        ('shot_select', c_uint),      # -s
        ('bright', c_float),          # -b
        ('threshold', c_float),       # -n
        ('half_size', c_int),         # -h
        ('four_color_rgb', c_int),    # -f
        ('highlight', c_int),         # -H
        ('use_auto_wb', c_int),       # -a
        ('use_camera_wb', c_int),     # -w
        ('use_camera_matrix', c_int), # +M/-M
        ('output_color', c_int),      # -o
        ('output_profile', c_char_p), # -o
        ('camera_profile', c_char_p), # -p
        ('bad_pixels', c_char_p),     # -P
        ('dark_frame', c_char_p),     # -K
        ('output_bps', c_int),        # -4
        ('output_tiff', c_int),       # -T
        ('user_flip', c_int),         # -t
        ('user_qual', c_int),         # -q
        ('user_black', c_int),        # -k
        ('user_cblack', c_int * 4),
        ('user_sat', c_int),          # -S
        ('med_passes', c_int),        # -m
        ('auto_bright_thr', c_float),
        ('adjust_maximum_thr', c_float),
        ('no_auto_bright', c_int),    # -W
        ('use_fuji_rotate', c_int),   # -j
        ('green_matching', c_int),
        # DCB parameters
        ('dcb_iterations', c_int),
        ('dcb_enhance_fl', c_int),
        ('fbdd_noiserd', c_int),
        ('exp_correc', c_int),
        ('exp_shift', c_float),
        ('exp_preser', c_float),
        # Raw speed
        ('use_rawspeed', c_int),
        # DNG SDK
        ('use_dngsdk', c_int),
        # Disable Auto-scale
        ('no_auto_scale', c_int),
        # Disable intepolation
        ('no_interpolation', c_int),
        ('raw_processing_options', c_uint),
        ('max_raw_memory_mb', c_uint),
        ('sony_arw2_posterization_thr', c_int),
        # Nikon Coolscan
        ('coolscan_nef_gamma', c_float),
        ('p4shot_order', c_char * 5),
        # Custom camera list
        ('custom_camera_strings', POINTER(c_char_p)),
    ]


class libraw_makernotes_lens_t(Structure):
    _fields_ = [
        ('LensID', c_ulonglong),
        ('Lens', c_char * 128),
        ('LensFormat', c_ushort),
        ('LensMount', c_ushort),
        ('CamID', c_ulonglong),
        ('CameraFormat', c_ushort),
        ('CameraMount', c_ushort),
        ('body', c_char * 64),
        ('FocalType', c_short),
        ('LensFeatures_pre', c_char * 16),
        ('LensFeatures_suf', c_char * 16),
        ('MinFocal', c_float),
        ('MaxFocal', c_float),
        ('MaxAp4MinFocal', c_float),
        ('MaxAp4MaxFocal', c_float),
        ('MinAp4MinFocal', c_float),
        ('MinAp4MaxFocal', c_float),
        ('MaxAp', c_float),
        ('MinAp', c_float),
        ('CurFocal', c_float),
        ('CurAp', c_float),
        ('MaxAp4CurFocal', c_float),
        ('MinAp4CurFocal', c_float),
        ('LensFStops', c_float),
        ('TeleconverterID', c_ulonglong),
        ('Teleconverter', c_char * 128),
        ('AdapterID', c_ulonglong),
        ('Adapter', c_char * 128),
        ('AttachmentID', c_ulonglong),
        ('Attachment', c_char * 128),
        ('CanonFocalUnits', c_short),
        ('FocalLengthIn35mmFormat', c_float),
    ]


class libraw_nikonlens_t(Structure):
    _fields_ = [
        ('NikonEffectiveMaxAp', c_float),
        ('NikonLensIDNumber', c_ubyte),
        ('NikonLensFStops', c_ubyte),
        ('NikonMCUVersion', c_ubyte),
        ('NikonLensType', c_ubyte),
    ]


class libraw_dnglens_t(Structure):
    _fields_ = [
        ('MinFocal', c_float),
        ('MaxFocal', c_float),
        ('MaxAp4MinFocal', c_float),
        ('MaxAp4MaxFocal', c_float),
    ]


class libraw_lensinfo_t(Structure):
    _fields_ = [
        ('MinFocal', c_float),
        ('MaxFocal', c_float),
        ('MaxAp4MinFocal', c_float),
        ('MaxAp4MaxFocal', c_float),
        ('EXIF_MaxAp', c_float),
        ('LensMake', c_char * 128),
        ('Lens', c_char * 128),
        ('LensSerial', c_char * 128),
        ('InternalLensSerial', c_char * 128),
        ('FocalLengthIn35mmFormat', c_ushort),
        ('nikon', libraw_nikonlens_t),
        ('dng', libraw_dnglens_t),
        ('makernotes', libraw_makernotes_lens_t),
    ]


class libraw_makernotes_t(Structure):
    _fields_ = [
        ('canon', libraw_canon_makernotes_t),
        ('nikon', libraw_nikon_makernotes_t),
        ('hasselblad', libraw_hasselblad_makernotes_t),
        ('fuji', libraw_fuji_info_t),
        ('olympus', libraw_olympus_makernotes_t),
        ('sony', libraw_sony_info_t),
        ('kodak', libraw_kodak_makernotes_t),
        ('panasonic', libraw_panasonic_makernotes_t),
        ('pentax', libraw_pentax_makernotes_t),
        ('phaseone', libraw_p1_makernotes_t),
        ('common', libraw_metadata_common_t),    
    ]


class libraw_shootinginfo_t(Structure):
    _fields_ = [
        ('DriveMode', c_short),
        ('FocusMode', c_short),
        ('MeteringMode', c_short),
        ('AFPoint', c_short),
        ('ExposureMode', c_short),
        ('ExposureProgram', c_short),
        ('ImageStabilization', c_short),
        ('BodySerial', c_char * 64),
        ('InternalBodySerial', c_char * 64),
    ]


class libraw_custom_camera_t(Structure):
    _fields_ = [
        ('fsize', c_uint),
        ('rw', c_ushort),
        ('rh', c_ushort),
        ('lm', c_ubyte),
        ('tm', c_ubyte),
        ('rm', c_ubyte),
        ('bm', c_ubyte),
        ('lf', c_ubyte),
        ('cf', c_ubyte),
        ('max', c_ubyte),
        ('flags', c_ubyte),
        ('t_make', c_char * 10),
        ('t_model', c_char * 20),
        ('offset', c_ushort)
    ]

    
class libraw_rawdata_t(Structure):
    """
    No longer exposed by LibRaw. Use raw2image.
    raw2image converts from bayer data (flat, 1 value per pixel) to 4-component image.
    Only one component of image is non-zero after raw2image. This is NOT demosaiced image,
    but data prepared for demosaic (this format is back-compatible to old LibRaw versions.
    """
    _fields_ = [
        ('raw_alloc', c_void_p),
        ('raw_image', POINTER(c_ushort)),       
        ('color4_image', POINTER(c_ushort * 4)),
        ('color3_image', POINTER(c_ushort * 3)),
        ('float_image', POINTER(c_float)),
        ('float3_image', POINTER(c_float * 3)),
        ('float4_image', POINTER(c_float * 4)),
        ('ph1_black', POINTER(c_short * 2)),                
        ('ph1_rblack', POINTER(c_short * 2)),
        ('iparams', libraw_iparams_t),
        ('sizes', libraw_image_sizes_t),        
        ('ioparams', libraw_internal_output_params_t),
        ('color', libraw_colordata_t),
    ]
        
    
class libraw_data_t(Structure): # is LibRaw.imgdata
    _fields_ = [
        ('_image', POINTER(c_ushort * 4)),        
        ('sizes', libraw_image_sizes_t),
        ('idata', libraw_iparams_t),
        ('lens', libraw_lensinfo_t),
        ('makernotes', libraw_makernotes_t),
        ('shootinginfo', libraw_shootinginfo_t),
        ('params', libraw_output_params_t),
        ('progress_flags', c_uint),
        ('process_warnings', c_uint),
        ('color', libraw_colordata_t),
        ('other', libraw_imgother_t),
        ('thumbnail', libraw_thumbnail_t),
        ('rawdata', libraw_rawdata_t),
        ('parent_class', c_void_p),
    ]

    @property
    def image(self):       
        size = (self.sizes.iheight, self.sizes.iwidth, 4)
        return _array_from_memory(self._image, size, np.uint16)


class fuji_compressed_params(Structure):
    _fields_ = [
        ('q_table', POINTER(c_int8)),  # quantization table
        ('q_points', c_int * 5),      # quantization points
        ('max_bits', c_int),
        ('min_value', c_int),
        ('raw_bits', c_int),
        ('total_values', c_int),
        ('maxDiff', c_int),
        ('line_width', c_ushort),
    ]

_hdl.libraw_init.restype = POINTER(libraw_data_t)
_hdl.libraw_unpack_function_name.restype = c_char_p
_hdl.libraw_strerror.restype = c_char_p
_hdl.libraw_version.restype = c_char_p

# buffer from memory definition
_buffer_from_memory = None
if sys.version_info.major >= 3: #  Python3
    _buffer_from_memory = lambda ptr, size: pythonapi.PyMemoryView_FromMemory(ptr, size, 0x200)  # writable
    pythonapi.PyMemoryView_FromMemory.restype = py_object
else:
    _buffer_from_memory = pythonapi.PyBuffer_FromReadWriteMemory
    _buffer_from_memory.restype = py_object

def _array_from_memory(ptr, shape, type):
    size = int(np.prod(shape) * np.dtype(type).itemsize)
    return np.frombuffer(_buffer_from_memory(ptr, size), type).reshape(shape)
    
def strerror(e):
    return _hdl.libraw_strerror(e).decode("utf-8")

def version():
    return _hdl.libraw_version().decode("utf-8")

def versionNumber():
    v = _hdl.libraw_versionNumber()
    return ((v >> 16) & 0x0000ff, (v >> 8) & 0x0000ff, v & 0x0000ff)
    
class LibRaw:
    def __init__(self, flags=0):
        if versionNumber()[1] != 20:
            sys.stdout.write("libraw.py: warning - structure definitions are not compatible with your version.\n")
        
        self._proc = _hdl.libraw_init(flags)
        assert(self._proc.contents)
        self.imgdata = self._proc.contents
        
    def __getattr__(self, name):
        rawfun = getattr(_hdl, "libraw_" + name)
        
        def handler(*args):
            # do not pass python strings to C
            args = [a.encode("utf-8") if isinstance(a, str) else a for a in args]
            
            e = rawfun(self._proc, *args)
            if e != 0:
                raise Exception(strerror(e))
        
        setattr(self, name, handler)  # cache value
        return handler
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage {} <rawfile>".format(sys.argv[0]))
        sys.exit(1)
    
#   Instantiante LibRaw
    proc = LibRaw()
    
    # Load the RAW file 
    pname = os.path.dirname(sys.argv[1])
    f = os.path.basename(sys.argv[1])
    fname = f.rsplit('.', 1)[0]
    proc.open_file(sys.argv[1])   
    print("file opened") 
    
    # Develop the RAW file
    print("unpacking")
    proc.unpack()
    
#     To access the raw data as a numpy array:
#     
#     proc.raw2image
#     mosaic = proc.imgdata.image
    
    
    print("processing")    
    proc.dcraw_process()
    proc.dcraw_ppm_tiff_writer(pname + "/" + fname + ".ppm")