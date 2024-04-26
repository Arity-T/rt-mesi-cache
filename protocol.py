"""Файл со всеми логическими компонентами системы. Тут и RT-MESI, и политика замещения,
и сама логика взаимодействия всех компонентов."""

from __future__ import annotations
from copy import copy
from typing import List


class RAM:
    def __init__(
        self,
        size,
        read_callback=lambda: print("RAM READ"),
        write_callback=lambda: print("RAM WRITE"),
    ):
        self.size = size
        self.read_callback = read_callback
        self.write_callback = write_callback
        self.reset()

    def reset(self):
        self.data = [0] * self.size

    def read(self, address: int):
        self.read_callback()
        return self.data[address]

    def write(self, data, address: int):
        self.write_callback()
        self.data[address] = data


class CacheController:
    """Кэш контроллер это самый главный элемент в системе, её главное связующее звено.
    Он принимает запросы на чтение и запись от процессоров, работает с кэшами
    и оперативной памятью. Как раз в нём и реализуется логика RT-MESI протокола.
    См. https://en.wikipedia.org/wiki/Cache_coherency_protocols_(examples)#RT-MESI_protocol
    """

    def __init__(
        self,
        ram: RAM,
        cpus: List[CPU],
        cach_lines_count: int,
        cach_channels_count: int,
        read_miss_callback=lambda cpu_index: print(f"READ MISS {cpu_index}"),
        intervention_callback=lambda cpu_index: print(f"INTERVENTION {cpu_index}"),
        state_callback=lambda cpu_index: print(f"CHANGE STATES {cpu_index}"),
    ):
        self.ram = ram
        self.cpus: List[CPU] = []
        self.cach_lines_count = cach_lines_count
        self.cach_channels_count = cach_channels_count
        self.read_miss_callback = read_miss_callback
        self.intervention_callback = intervention_callback
        self.state_callback = state_callback

        for cpu in cpus:
            self._add_cpu(cpu)

    def _add_cpu(self, cpu: CPU):
        """Подключет CPU к кэш контроллеру."""
        self.cpus.append(cpu)
        cpu.cache_controller = self
        if cpu.cache is None:
            cpu.cache = Cache(self.cach_lines_count, self.cach_channels_count)

    def _get_address_states(self, address: int):
        """Ищет адрес во всех кэшах и возвращает список его состояний.
        Может быть пустым, если адреса нет в кэшах. Состояние I игнорируется."""
        address_states = []

        for cpu in self.cpus:
            cach_line = cpu.cache.get_cache_line_by_address(address)
            if cach_line is not None:
                address_states.append(cach_line.state)

        return address_states

    def _make_address_shared(self, address: int):
        """Ищет адрес во всех кэшах и присваивает ему состояние S."""
        for cpu in self.cpus:
            cach_line = cpu.cache.get_cache_line_by_address(address)
            if cach_line is not None:
                cach_line.state = "S"

    def _get_data_from_m_or_t(self, address: int):
        """Ищет кэш строку с заданным адресом в состоянии M или T и возвращает лежащие
        в ней данные. Меняет состояние на S."""
        for cpu in self.cpus:
            cach_line = cpu.cache.get_cache_line_by_address(address)
            if cach_line is not None and cach_line.state in {"M", "T"}:
                self.intervention_callback(cpu.index)
                cach_line.state = "S"
                return cach_line.data

    def _get_data_from_e_or_r(self, address: int):
        """Ищет кэш строку с заданным адресом в состоянии E или R и возвращает лежащие
        в ней данные. Меняет состояние на S."""
        for cpu in self.cpus:
            cach_line = cpu.cache.get_cache_line_by_address(address)
            if cach_line is not None and cach_line.state in {"E", "R"}:
                self.intervention_callback(cpu.index)
                cach_line.state = "S"
                return cach_line.data

    def _make_address_invalid(self, address: int):
        """Ищет адрес во всех кэшах и устанавливает в состояниe I."""
        for cpu in self.cpus:
            cach_line = cpu.cache.get_cache_line_by_address(address)
            if cach_line is not None:
                cach_line.state = "I"

    def read(self, source_cpu: CPU, address: int) -> int:
        """Обрабатывает запрос процессора на чтение данных по указанному адресу."""

        # READ HIT - данные есть в кэше процессора, состояния никак не меняются
        cache_line = source_cpu.cache.get_cache_line_by_address(address)
        if cache_line is not None:
            return source_cpu.cache.read(address)

        # READ MISS
        self.read_miss_callback(source_cpu.index)
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
            self.state_callback(source_cpu.index)
            data = self._get_data_from_m_or_t(address)

        elif "E" in address_states or "R" in address_states:
            # Данные есть в других кэшах
            state = "R"

            # Shared Intervention
            self.state_callback(source_cpu.index)
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

        if cach_line is not None:
            if cach_line.state in {"M", "E"}:
                source_cpu.cache.write("M", data, address)

            elif cach_line.state in {"T", "R", "S"}:
                self.state_callback(source_cpu.index)
                self._make_address_invalid(address)

                source_cpu.cache.write("M", data, address)

            return

        # WRITE MISS

        # Вариант, когда данных в кэше процессора нет, пока не рассматриваем.
        # Вообще-то он нам и не нужен, так как мы всегда делаем инкремент,
        # т. е. читаем данные (сохраняем в кэш) и увеличиваем на единицу

        raise NotImplementedError


class CPU:
    def __init__(
        self,
        index,
        read_callback=lambda: print("CPU READ"),
        write_callback=lambda: print("CPU WRITE"),
    ):
        self.index = index
        self.read_callback = read_callback
        self.write_callback = write_callback
        self.cache_controller: CacheController = None
        self.cache: Cache = None

    def read(self, address: int) -> int:
        self.read_callback()
        return self.cache_controller.read(self, address)

    def write(self, data, address: int):
        self.write_callback()
        self.cache_controller.write(self, data, address)

    def increment(self, address):
        data = self.read(address)
        data = data + 1
        self.write(data, address)


class CacheLine:
    """Кэш строка - содержит состояние (одно из R, T, M, E, S или I), данные, адрес
    данных в оперативной памяти, а также счётчик, который показывает, как давно было
    последний запрос на чтение или запись к этой кэш строке."""

    def __init__(self):
        self.state: None | str = None
        self.data: None | int = None
        self.address: None | int = None
        self.not_used_counter = 0

    def increment_counter(self):
        """Увеличивает счётчик. Функция должна вызываться, когда поступает запрос
        на чтение или запись к другим кэш строкам того же кэша."""
        self.not_used_counter += 1

    def read(self) -> None | int:
        """Получает данные из кэш строки и обнуляет счётчик."""
        self.not_used_counter = 0
        return self.data

    def write(self, address, data):
        """Записывает данные в кэш строку и обнуляет счётчик."""
        self.not_used_counter = 0
        self.address = address
        self.data = data


class Cache:
    """Наборно-ассоциативный кэш процессора. В нём реализована политика замещения MRU."""

    def __init__(
        self,
        lines_count: int,
        channels_count: int,
        read_callback=lambda: print("CACHE READ"),
        write_callback=lambda: print("CACHE WRITE"),
    ):
        self.lines_count = lines_count
        self.channels_count = channels_count
        self.read_callback = read_callback
        self.write_callback = write_callback

        self.reset()

    def reset(self):
        self.channels = [
            [CacheLine() for _ in range(self.lines_count)]
            for _ in range(self.channels_count)
        ]

    def _cache_lines_counter_increment(self):
        for channel in self.channels:
            for cache_line in channel:
                cache_line.increment_counter()

    def _choose_same_or_empty_line(self, address: int) -> None | CacheLine:
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

    def read(self, address: int) -> int:
        """Обрабатывае запрос на чтение адреса из кэша. Подразумевается, что при вызове
        этой функции точно известно, что данные в кэше есть."""
        self.read_callback()

        self._cache_lines_counter_increment()
        cache_line = self.get_cache_line_by_address(address)
        return cache_line.read()

    def write(self, state, data, address: int) -> None | CacheLine:
        """Записывает в кэш данные с указанным адресом и состоянием. Возвращает
        замещённую кэш строку, либо None, если не пришлось делать замещение."""
        self.write_callback()

        self._cache_lines_counter_increment()

        cache_line = self._choose_same_or_empty_line(address)
        replaced_cache_line = None

        if cache_line is None:
            cache_line = self._choose_line_to_replace(address)
            replaced_cache_line = copy(cache_line)

        cache_line.state = state
        cache_line.write(address, data)

        return replaced_cache_line

    def get_cache_line_by_address(self, address: int) -> None | CacheLine:
        """Находит кэш строку по заданному адресу. Возвращает None, если адреса
        в кэше нет или он находится в состоянии I."""
        line_index = address % self.lines_count

        for channel in self.channels:
            cache_line = channel[line_index]

            if cache_line.state != "I" and address == cache_line.address:
                return cache_line

        return None
