"""Основные параметры системы и некоторые настройки визуализации"""

CPU_COUNT = 4
CACH_CHANNELS_COUNT = 2  # aka ассоциативность
CACH_CACHLINES_COUNT = 2
RAM_SIZE = 16

WINDOW_SIZE = (1500, 800)
TOP_LEFT_CORNER = (20, 0)
BOTTOM_RIGHT_CORNER = (1480, 780)
TICK_MS = 100
TITLE = "RT-MESI with MRU visualization"

BUS_LENGTH = WINDOW_SIZE[0] - TOP_LEFT_CORNER[0] * 2
CPU_Y_COORD = TOP_LEFT_CORNER[1] + 180
CPU_X_COORDS = [TOP_LEFT_CORNER[0] + 125 + 250 * i for i in range(CPU_COUNT)]
RAM_Y_COORD = TOP_LEFT_CORNER[1] + 180
