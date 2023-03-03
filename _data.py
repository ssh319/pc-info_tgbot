from re import search
from urllib.request import urlopen
from abc import ABC, abstractmethod

_series = {
    r'CPUi[3, 5, 7, 9]$': 'Core_%s-',
    r'GPUgtx': 'GeForce_%s_',
    r'CPUryzen_[3, 5, 7, 9]$': '%s_',
    r'GPUrtx': 'GeForce_%s_',
    r'CPUpentium': '%s_',
    r'GPUradeon': '%s_',
    r'CPUceleron': '%s_',
    r'GPUhd': '%s_Graphics_',
    r'CPUathlon': '%s_',
    r'GPUuhd': '%s_Graphics_',
    r'CPUphenom': '%s_',
    r'GPUquadro': '%s_',
    r'CPUsempron': '%s_',
    r'GPUfirepro': '%s_',
    r'CPUxeon': '%s_',
    r'GPUmobility_radeon': '%s_',
    r'CPUryzen_tr': 'Ryzen_Threadripper_',
    r'GPUgt': 'GeForce_%s_',
    r'CPUepyc': '%s_',
    r'GPUgts': 'GeForce_%s_'
}


class BaseComponent(ABC):
    def __init__(self, series, model):
        self.series = series
        self.model = model

    @abstractmethod
    def _setup(self, keyword: str) -> str: ...

    @abstractmethod
    def _get_name_and_score(self) -> tuple: ...

    @abstractmethod
    def get_params(self) -> str: ...


class CPU(BaseComponent):
    def __init__(self, series, model):
        BaseComponent.__init__(self, series, model)

        if self.series in ("athlon_", "phenom_"):
            self.model = self.model.replace('2_', 'II_', 1).replace('xII', 'x2')

        self.url = f"https://www.chaynikam.info/cpu_comparison.html?{self.series + self.model}"
        self.html = str(urlopen(self.url).read()).replace('\\n', '').replace('<br/>', ' ')

        for i in range(ord('А'), ord('я') + 1):
            self.html = self.html.replace(str(bytearray(chr(i), 'utf-8'))[12:-2], chr(i))

    def _setup(self, keyword: str) -> str:
        pattern = fr'<tr id=\"{keyword}\".+?transparent\">[/+\-(),.\s?\w-]+<?'

        result = search(pattern, self.html).group()
        return search(r'>[/+(),.\w\s-]+<$', result).group()[1:-1]

    def _get_name_and_score(self) -> tuple:
        name_pattern = r"\"text-decoration: underline\">[+(),.\w\s-]+<?"
        score_pattern = r"width:85%\"></div>\d+<"
        name = search(r">[+(),.\w\s-]+<$", search(name_pattern, self.html).group()).group()[1:-1]
        score = search(r"\d+<$", search(score_pattern, self.html).group()).group()[:-1]
        return name, score

    def get_params(self) -> str:
        name, score = self._get_name_and_score()

        cpu_thirdcache = self._setup('trcachel3')
        params = [
            "Год выхода: " + self._setup('tryearofprod'),
            "Тип процессора: " + self._setup('trcpucategory'),
            "Сокет: " + self._setup('trcpusocket'),
            "Количество ядер: " + self._setup('trnumofcores'),
            "Количество потоков: " + self._setup('trnumofthreads'),
            "Базовая частота: " + self._setup('trbasefreq'),
            "Частота TurboBoost: " + self._setup('trturbofreq'),
            "Размер кэша L3: " + cpu_thirdcache if 'нет' in cpu_thirdcache else
            "Размер кэша L3: " + str(round(int(cpu_thirdcache) / 1024)) + ' МБ',
            "Тепловыделение: " + self._setup('trtdp'),
            "Встроенный графический процессор: " + self._setup('trgraphics'),
            "Контроллер ОЗУ: " + self._setup('trmemorycontroller'),
        ]
        return (f"\n{'-' * 30}\n".join(params)
                + f'\n\n\nБалл производительности для\n{name}:\n----------     {score}     ----------')


class GPU(BaseComponent):
    def __init__(self, series, model):
        BaseComponent.__init__(self, series, model)

        self.url = f"https://www.chaynikam.info/gpu_comparison.html?{self.series + self.model}"
        self.html = str(urlopen(self.url).read()).replace('\\n', '').replace('<br/>', ' ')

        for i in range(ord('А'), ord('я') + 1):
            self.html = self.html.replace(str(bytearray(chr(i), 'utf-8'))[12:-2], chr(i))

    def _setup(self, keyword: str) -> str:
        pattern = fr'<tr id=\"{keyword}\".+?style=\"\">[/+\-(),.\s?\w-]+<?'

        result = search(pattern, self.html).group()
        return search(r'>[/+(),.\w\s-]+<$', result).group()[1:-1]

    def _get_name_and_score(self) -> tuple:
        name_pattern = r"class=\"white\".+?title=\"\">[+(),.\w\s-]+<?"
        score_pattern = r"class=\"sp_rat\">\d+<"
        name = search(r">[+(),.\w\s-]+<$", search(name_pattern, self.html).group()).group()[1:-1]
        score = search(r"\d+<$", search(score_pattern, self.html).group()).group()[:-1]
        return name, score

    def get_params(self) -> str:
        name, score = self._get_name_and_score()

        params = [
            "Год выхода: " + self._setup('tr_yearofprod'),
            "Сегмент: " + self._setup('tr_desktopormob'),
            "Тип: " + self._setup('tr_gpucategory'),
            "Частота ядра: " + self._setup('tr_corefrequency'),
            "Шейдерных блоков: " + self._setup('tr_unishaders'),
            "Блоков растеризации (ROP): " + self._setup('tr_numberofrop'),
            "Текстурных блоков (TMU): " + self._setup('tr_numberoftmu'),
            "Тип памяти: " + self._setup('tr_memorytype'),
            "Обьём памяти: " + self._setup('tr_memorysize'),
            "Частота памяти: " + self._setup('tr_memoryfrequency'),
            "Шина памяти: " + self._setup('tr_memorybus'),
            "Пропускная способность: " + self._setup('tr_bandwidth'),
            "Тепловыделение: " + self._setup('tr_tdp'),
            "Мин. блок питания: " + self._setup('tr_bppower'),
            "Разъёмы доп. питания: " + self._setup('tr_doppitanie'),
        ]
        return (f"\n{'-' * 30}\n".join(params)
                + f'\n\n\nБалл производительности для\n{name}:\n----------     {score}     ----------')
