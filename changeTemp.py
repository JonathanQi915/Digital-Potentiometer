import serial

class serialCom:
    # dictionaries that relate all temperature within a range to a step and vice versa
    tempToStep = {
            48:255,
            49:246,
            50:239,
            51:232,
            52:225,
            53:218,
            54:213,
            55:206,
            56:202,
            57:197,
            58:190,
            59:185,
            60:182,
            61:177,
            62:172,
            63:167,
            64:163,
            65:158,
            66:155,
            67:152,
            68:147,
            69:143,
            70:139,
            71:136,
            72:133,
            73:130,
            74:126,
            75:123,
            76:120,
            77:117,
            78:115,
            79:112,
            80:109,
            81:106,
            82:104,
            83:101,
            84:99,
            85:96,
            86:93,
            87:91,
            88:89,
            89:87,
            90:85,
            91:83,
            92:81,
            93:79,
            94:77,
            95:75,
            96:74,
            97:72,
            98:71,
            99:69,
            100:67,
            101:66,
            102:64,
            103:62,
            104:61,
            105:60,
            106:59,
            107:57,
            108:56,
            109:55,
            110:53,
            111:52,
            112:51,
            113:50,
            114:49,
            115:48,
            116:47,
            117:46,
            118:45,
            119:44,
            120:43,
            121:42,
            122:41,
            123:40,
            124:39,
            125:38,
            126:37,
            127:37,
            128:36,
            129:35,
            130:35,
            131:34,
            132:33,
            133:33,
            134:32,
            135:31,
            136:31,
            137:30,
            138:29,
            139:29,
            140:28,
            141:27,
            142:27,
            143:26,
            144:26,
            145:25,
            146:25,
            147:24,
            148:24,
            149:23,
            150:23,
            151:22,
            152:22,
            153:21,
            154:21,
            155:20,
            156:20,
            157:20,
            158:19,
            159:9,
            160:18,
            161:18,
            162:17,
            163:17,
            164:17,
            165:16,
            166:16,
            167:16,
            168:15,
            169:15,
            170:15,
            171:14,
            172:14,
            173:14,
            174:13,
            175:13,
            176:13,
            177:13,
            178:12,
            179:12,
            180:12,
            181:11,
            182:11,
            183:11,
            184:11,
            185:11,
            186:10,
            187:10,
            188:10,
            189:10,
            190:10,
            191:9,
            192:9,
            193:9,
            194:9,
            195:9,
            196:8,
            197:8,
            198:8,
            199:8,
            200:8,
            201:7,
            202:7,
            203:7,
            204:7,
            205:7,
            206:6,
            207:6,
            208:6,
            209:6,
            210:6,
        }
    stepToTemp = {
        0:300,
        1:273,
        2:253,
        3:239,
        4:228,
        5:218,
        6:210,
        7:203,
        8:196,
        9:192,
        10:188,
        11:182,
        12:178,
        13:175,
        14:171,
        15:168,
        16:165,
        17:163,
        18:160,
        19:157,
        20:155,
        21:153,
        22:150,
        23:148,
        24:146,
        25:144,
        26:142,
        27:141,
        28:139,
        29:137,
        30:136,
        31:134,
        32:133,
        33:132,
        34:130,
        35:129,
        36:128,
        37:127,
        38:125,
        39:124,
        40:123,
        41:122,
        42:121,
        43:120,
        44:119,
        45:118,
        46:117,
        47:116,
        48:115,
        49:114,
        50:113,
        51:112,
        52:111,
        53:110,
        54:110,
        55:109,
        56:108,
        57:107,
        58:107,
        59:106,
        60:105,
        61:104,
        62:103,
        63:103,
        64:102,
        65:102,
        66:101,
        67:100,
        68:100,
        69:99,
        70:99,
        71:98,
        72:97,
        73:97,
        74:96,
        75:95,
        76:95,
        77:94,
        78:94,
        79:93,
        80:93,
        81:92,
        82:92,
        83:91,
        84:91,
        85:90,
        86:90,
        87:89,
        88:89,
        89:88,
        90:88,
        91:87,
        92:87,
        93:86,
        94:86,
        95:85,
        96:85,
        97:85,
        98:84,
        99:84,
        100:84,
        101:83,
        102:83,
        103:82,
        104:82,
        105:82,
        106:81,
        107:81,
        108:80,
        109:80,
        110:80,
        111:79,
        112:79,
        113:79,
        114:78,
        115:78,
        116:78,
        117:77,
        118:77,
        119:76,
        120:76,
        121:76,
        122:75,
        123:75,
        124:75,
        125:74,
        126:74,
        127:74,
        128:74,
        129:73,
        130:73,
        131:73,
        132:72,
        133:72,
        134:72,
        135:71,
        136:71,
        137:71,
        138:70,
        139:70,
        140:70,
        141:69,
        142:69,
        143:69,
        144:69,
        145:69,
        146:68,
        147:68,
        148:68,
        149:68,
        150:67,
        151:67,
        152:67,
        153:67,
        154:66,
        155:66,
        156:66,
        157:65,
        158:65,
        159:65,
        160:65,
        161:65,
        162:64,
        163:64,
        164:64,
        165:64,
        166:63,
        167:63,
        168:63,
        169:63,
        170:62,
        171:62,
        172:62,
        173:62,
        174:62,
        175:61,
        176:61,
        177:61,
        178:61,
        179:61,
        180:60,
        181:60,
        182:60,
        183:60,
        184:59,
        185:59,
        186:59,
        187:59,
        188:58,
        189:58,
        190:58,
        191:58,
        192:58,
        193:58,
        194:57,
        195:57,
        196:57,
        197:57,
        198:57,
        199:57,
        200:56,
        201:56,
        202:56,
        203:56,
        204:55,
        205:55,
        206:55,
        207:55,
        208:55,
        209:55,
        210:55,
        211:54,
        212:54,
        213:54,
        214:54,
        215:54,
        216:53,
        217:53,
        218:53,
        219:53,
        220:53,
        221:53,
        222:53,
        223:52,
        224:52,
        225:52,
        226:52,
        227:52,
        228:52,
        229:51,
        230:51,
        231:51,
        232:51,
        233:51,
        234:51,
        235:51,
        236:50,
        237:50,
        238:50,
        239:50,
        240:50,
        241:50,
        242:50,
        243:49,
        244:49,
        245:49,
        246:49,
        247:49,
        248:49,
        249:49,
        250:48,
        251:48,
        252:48,
        253:48,
        254:48,
        255:48
    }
    # initialize the class with serial connection information
    def __init__(self, serialPort, baud):
        self.serialPort = serialPort
        self.baud = baud
        self.temp = 54
    # method to change the temperature to the given temp
    def changeTemp(self, temp): 
        # times below the upper and lower ranges will just default to the highest and lowest number
        if temp < 54:
            temp = 54
        if temp > 210:
            temp = 210
        s = serial.Serial(port = self.serialPort, baudrate = self.baud)
        # how the digital potentiometer recieves data
        myBytes = bytearray()
        myBytes.append(254)
        myBytes.append(171)
        myBytes.append(self.tempToStep[temp])
        self.temp = temp
        s.write(myBytes)
    # method to change the step to the given step
    def changeStep(self, step):
        if step < 0 or step > 255:
             raise Exception("out of range")
        # conncect to com port
        s = serial.Serial(port = self.serialPort, baudrate = self.baud)
        # how the digital potentiometer recieves data
        myBytes = bytearray()
        myBytes.append(254)
        myBytes.append(171)
        myBytes.append(step)
        self.temp = self.stepToTemp[step]
        s.write(myBytes)
    # pints all of the current information 
    def printInfo(self):
        print("Temp: " + str(self.temp))
        print("Step: " + str(self.tempToStep[self.temp]))
        print("Resistance: " + str(195.3 * self.tempToStep[self.temp]))
