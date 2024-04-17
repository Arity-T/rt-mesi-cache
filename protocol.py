from __future__ import annotations
from typing import List


class RAM:
    def __init__(self, size=16):
        self.data = [0] * size

    def __repr__(self):
        str_repr = "Address\tData\n"
        for i, byte in enumerate(self.data):
            str_repr += f"{i}\t{byte}\n"
        return str_repr

    def read(self, address: int):
        return self.data[address]

    def write(self, data, address: int):
        self.data[address] = data


class CacheController:
    """Кэш контроллер использует MESI-протокол кэш когерентности
    См. https://upload.wikimedia.org/wikipedia/commons/b/b6/MESI_State_Transaction_Diagram.svg
    """

    def __init__(
        self, ram: RAM, cpus: List[CPU], cach_lines_count: int, cach_channels_count: int
    ):
        self.ram = ram
        self.cpus: List[CPU] = []
        self.cach_lines_count = cach_lines_count
        self.cach_channels_count = cach_channels_count

        for cpu in cpus:
            self._add_cpu(cpu)

    def _add_cpu(self, cpu: CPU):
        """Подключет CPU к кэш контроллеру."""
        self.cpus.append(cpu)
        cpu.cache_controller = self
        cpu.cache = Cache(self.cach_lines_count, self.cach_channels_count)

    def _get_address_state(self, address: int):
        """Ищет адрес во всех кэшах и возвращает его состояние,
        либо None, если адреса в кэше нет."""
        for cpu in self.cpus:
            cach_line = cpu.cache.get_cache_line_by_address(address)
            if cach_line is not None and cach_line.state != "I":
                return cach_line.state

        return None

    def _make_address_shared(self, address: int):
        """Ищет адрес во всех кэшах и присваивает ему состояние S."""
        for cpu in self.cpus:
            cach_line = cpu.cache.get_cache_line_by_address(address)
            if cach_line is not None and cach_line.state != "I":
                cach_line.state = "S"

    def _load_modified_address_to_ram(self, address: int):
        """Ищет кэш строку с заданным адресом в состоянии M и выгружает в RAM,
        состояние меняется на S."""
        for cpu in self.cpus:
            cach_line = cpu.cache.get_cache_line_by_address(address)
            if cach_line is not None and cach_line.state == "M":
                cach_line.state = "S"
                self.ram.write(cach_line.data, cach_line.address)
                return

    def _make_address_invalid(self, address: int):
        """Ищет адрес во всех кэшах и устанавливает в состоянии I"""
        for cpu in self.cpus:
            cach_line = cpu.cache.get_cache_line_by_address(address)
            if cach_line is not None:
                cach_line.state = "I"

    def read(self, source_cpu: CPU, address: int):
        """Обрабатывает запрос процессора на чтение данных по указанному адресу."""

        # READ HIT - данные есть в кэшэ процессора, состояния никак не меняются
        cach_line = source_cpu.cache.get_cache_line_by_address(address)
        if cach_line is not None and cach_line.state != "I":
            return cach_line.data

        # READ MISS
        address_state = self._get_address_state(address)
        if address_state is None:
            # Данных нет в других кэшах, а значит они не являются разделяемыми
            state = "E"

        elif address_state in {"S", "E"}:
            # Данные есть в других кэшах
            state = "S"

            # В других кэшах адресс также должен стать shared
            self._make_address_shared(address)

        elif address_state == "M":
            # Данные есть в других кэшах
            state = "S"

            # Выгружаем модифицированные данные в RAM
            self._load_modified_address_to_ram(address)

        # Получаем сами данные из оперативки
        data = self.ram.read(address)

        # Записываем в кэш процессора
        source_cpu.cache.write(state, data, address)

        # Возвращаем запрашиваемые данные процессору
        return data

    def write(self, source_cpu: CPU, data, address: int):
        """Обрабатывает запрос процессора на запись данных по указанному адресу."""
        # WRITE HIT - данные есть в кэше процессора
        cach_line = source_cpu.cache.get_cache_line_by_address(address)
        if cach_line is not None and cach_line.state != "I":
            if cach_line.state == "M":
                cach_line.data = data

            elif cach_line.state == "E":
                cach_line.state = "M"
                cach_line.data = data

            elif cach_line.state == "S":
                self._make_address_invalid(address)

                cach_line.state = "M"
                cach_line.data = data

            return

        # WRITE MISS

        # Вариант, когда данных в кэше процессора нет, пока не рассматриваем.
        # Вообще-то он нам и не нужен, так как мы всегда делаем инкремент,
        # т. е. читаем данные (сохраняем в кэш) и увеличиваем на единицу

        raise NotImplementedError


class CPU:
    def __init__(self, name):
        self.name = name
        self.cache_controller: CacheController = None
        self.cache: Cache = None

    def __repr__(self) -> str:
        str_repr = f"Cache for {self.name} -------- \n\n"
        str_repr += str(self.cache)
        return str_repr

    def read(self, address: int):
        return self.cache_controller.read(self, address)

    def write(self, data, address: int):
        self.cache_controller.write(self, data, address)

    def increment(self, address):
        data = self.read(address)
        data = data + 1
        self.write(data, address)


class CacheLine:
    def __init__(self):
        self.state = None
        self.data = None
        self.address = None

    def read(self):
        return self.data

    def write(self, address, data):
        self.address = address
        self.data = data


class Cache:
    def __init__(self, lines_count=2, channels_count=2):
        self.lines_count = lines_count
        self.channels_count = channels_count
        self.channels = [
            [CacheLine() for _ in range(lines_count)] for _ in range(channels_count)
        ]

    def __repr__(self) -> str:
        str_repr = ""

        for i, channel in enumerate(self.channels):
            str_repr += f"Channel #{i}\n"
            str_repr += "State\tAddress\tData\n"
            for cache_line in channel:
                str_repr += (
                    f"{cache_line.state}\t{cache_line.address}\t{cache_line.data}\n"
                )
            str_repr += "\n"

        return str_repr

    def read(self, address: int):
        cache_line = self.get_cache_line_by_address(address)
        return cache_line.data

    def write(self, state, data, address: int):
        cache_line = self.choose_line(address)
        cache_line.state = state
        cache_line.write(address, data)

    def choose_line(self, address: int) -> CacheLine:
        """Место для логики политики замещения"""
        line_index = address % self.lines_count

        # Если есть пустые строки - заполняем сначала их
        # Если эти этот адрес уже есть в кэше, то работаем с ним
        for channel in self.channels:
            cache_line = channel[line_index]

            if cache_line.data is None or cache_line.address == address:
                return cache_line

        # Тут уже придётся решать, какие данные замещать
        cache_line = self.channels[0][line_index]

        return cache_line

    def get_cache_line_by_address(self, address: int) -> CacheLine:
        line_index = address % self.lines_count

        for channel in self.channels:
            cache_line = channel[line_index]

            if address == cache_line.address:
                return cache_line

        return None
