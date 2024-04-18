from __future__ import annotations
from copy import copy
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
    """Кэш контроллер использует RTMESI-протокол кэш когерентности
    См. https://upload.wikimedia.org/wikipedia/commons/4/4a/RT-MESI_Protocol_-_State_Transaction_Diagram.svg
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

    def _get_address_states(self, address: int):
        """Ищет адрес во всех кэшах и возвращает список его состояний.
        Может быть пустым, если адреса нет в кэшах. Состояние I игнорируется."""
        address_states = []

        for cpu in self.cpus:
            cach_line = cpu.cache.get_cache_line_by_address(address)
            if cach_line is not None and cach_line.state != "I":
                address_states.append(cach_line.state)

        return address_states

    def _make_address_shared(self, address: int):
        """Ищет адрес во всех кэшах и присваивает ему состояние S."""
        for cpu in self.cpus:
            cach_line = cpu.cache.get_cache_line_by_address(address)
            if cach_line is not None and cach_line.state != "I":
                cach_line.state = "S"

    def _get_data_from_m_or_t(self, address: int):
        """Ищет кэш строку с заданным адресом в состоянии M или T и возвращает лежащие
        в ней данные. Меняет состояние на S."""
        for cpu in self.cpus:
            cach_line = cpu.cache.get_cache_line_by_address(address)
            if cach_line is not None and cach_line.state in {"M", "T"}:
                cach_line.state = "S"
                return cach_line.data

    def _get_data_from_e_or_r(self, address: int):
        """Ищет кэш строку с заданным адресом в состоянии E или R и возвращает лежащие
        в ней данные. Меняет состояние на S."""
        for cpu in self.cpus:
            cach_line = cpu.cache.get_cache_line_by_address(address)
            if cach_line is not None and cach_line.state in {"E", "R"}:
                cach_line.state = "S"
                return cach_line.data

    def _make_address_invalid(self, address: int):
        """Ищет адрес во всех кэшах и устанавливает в состоянии I"""
        for cpu in self.cpus:
            cach_line = cpu.cache.get_cache_line_by_address(address)
            if cach_line is not None:
                cach_line.state = "I"

    def read(self, source_cpu: CPU, address: int):
        """Обрабатывает запрос процессора на чтение данных по указанному адресу."""

        # READ HIT - данные есть в кэше процессора, состояния никак не меняются
        cache_line = source_cpu.cache.get_cache_line_by_address(address)
        if cache_line is not None and cache_line.state != "I":
            return cache_line.read()

        # READ MISS
        address_states = self._get_address_states(address)
        if not address_states:
            # Данных нет в других кэшах, а значит они не являются разделяемыми
            state = "E"

            # Берём данные из оперативной памяти
            data = self.ram.read(address)

        elif "M" in address_states or "T" in address_states:
            # Данные есть в других кэшах
            state = "T"

            # Dirty Intervention
            data = self._get_data_from_m_or_t(address)

        elif "E" in address_states or "R" in address_states:
            # Данные есть в других кэшах
            state = "R"

            # Shared Intervention
            data = self._get_data_from_e_or_r(address)

        elif "S" in address_states:
            # Данные есть в других кэшах только в состоянии S
            state = "R"

            # Берём данные из оперативной памяти
            data = self.ram.read(address)

        # Записываем в кэш процессора
        replaced_cache_line = source_cpu.cache.write(state, data, address)

        if replaced_cache_line is not None and replaced_cache_line.state in {"T", "M"}:
            # Copy-Back
            self.ram.write(replaced_cache_line.data, replaced_cache_line.address)

        # Возвращаем запрашиваемые данные процессору
        return data

    def write(self, source_cpu: CPU, data, address: int):
        """Обрабатывает запрос процессора на запись данных по указанному адресу."""

        # WRITE HIT - данные есть в кэше процессора
        cach_line = source_cpu.cache.get_cache_line_by_address(address)

        if cach_line is not None and cach_line.state != "I":
            if cach_line.state in {"M", "E"}:
                cach_line.state = "M"
                cach_line.write(address, data)

            elif cach_line.state in {"T", "R", "S"}:
                self._make_address_invalid(address)

                cach_line.state = "M"
                cach_line.write(address, data)

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
        self.not_used_counter = 0

    def increment_counter(self):
        self.not_used_counter += 1

    def read(self):
        self.not_used_counter = 0
        return self.data

    def write(self, address, data):
        self.not_used_counter = 0
        self.address = address
        self.data = data


class Cache:
    def __init__(self, lines_count=2, channels_count=2):
        self.lines_count = lines_count
        self.channels_count = channels_count

        self.channels = [
            [CacheLine() for _ in range(lines_count)] for _ in range(channels_count)
        ]

    def _cache_lines_counter_increment(self):
        for channel in self.channels:
            for cache_line in channel:
                cache_line.increment_counter()

    def read(self, address: int):
        self._cache_lines_counter_increment()
        cache_line = self.get_cache_line_by_address(address)
        return cache_line.read()

    def write(self, state, data, address: int) -> None | CacheLine:
        """Записывает в кэш данные с указанным адресом и состоянием. Возвращает
        замещённую кэш строку, либо None, если не пришлось делать замещение."""
        self._cache_lines_counter_increment()

        cache_line = self._choose_same_or_empty_line(address)
        replaced_cache_line = None

        if cache_line is None:
            cache_line = self._choose_line_to_replace(address)
            replaced_cache_line = copy(cache_line)

        cache_line.state = state
        cache_line.write(address, data)

        return replaced_cache_line

    def _choose_same_or_empty_line(self, address: int):
        """Возвращает кэш строку с указанным адресом, либо подбирает пустую или Invalid
        строку, если такого адреса в кэше нет. Если пустых строк нет, возвращает None.
        """
        line_index = address % self.lines_count

        for channel in self.channels:
            cache_line = channel[line_index]

            if (
                cache_line.data is None
                or cache_line.state == "I"
                or cache_line.address == address
            ):
                return cache_line

        return None

    def _choose_line_to_replace(self, address: int) -> CacheLine:
        """Место для логики политики замещения. Сейчас это MRU."""
        line_index = address % self.lines_count
        choosen_line = self.channels[0][line_index]

        for channel in self.channels:
            cache_line = channel[line_index]

            # MRU - выбираем строку, которая использовалась "наиболее недавно"
            if cache_line.not_used_counter < choosen_line.not_used_counter:
                choosen_line = cache_line

        return choosen_line

    def get_cache_line_by_address(self, address: int) -> CacheLine:
        line_index = address % self.lines_count

        for channel in self.channels:
            cache_line = channel[line_index]

            if address == cache_line.address:
                return cache_line

        return None
