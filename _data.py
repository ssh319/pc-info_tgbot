from abc import ABC, abstractmethod
from lxml.html import fromstring
from urllib.request import urlopen


series_list = {
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
    r'GPUgts': 'GeForce_%s_',
    r'CPUfx': '%s-',
    r'GPUgeforce': '%s_'
}


class BaseComponent(ABC):
    def __init__(self, series, model):
        self.series = series
        self.model = model

        if self.__class__ is CPU:
            if self.series in ("athlon_", "phenom_"):
                self.model = self.model.replace('2_', 'II_', 1).replace('xII', 'x2')

            elif self.series == 'pentium_' and self.model[:2] in ('2_', '3_'):
                self.model = self.model.replace('2_', 'II_', 1).replace('3_', 'III_', 1)

        self.url = (
            "https://www.chaynikam.info/"
            f"{self.__class__.__name__.lower()}"
            "_comparison.html?"
            f"{self.series + self.model}"
        )

        with urlopen(self.url) as request:
            self.html = fromstring(request.read().decode('utf-8'))

    @abstractmethod
    def _setup(self, keyword: str) -> str: ...

    @abstractmethod
    def _get_name_and_score(self) -> tuple: ...

    @abstractmethod
    def get_params(self) -> str: ...


class CPU(BaseComponent):
    def _setup(self, keyword: str) -> str:
        result = self.html.xpath(
            "body"
            "//div[@class='body']"
            "//table[@id='table1']"
            f"/tr[@id='{keyword}']"
            "/td[@class='td6']"
            "/text()"
        )
        return result[0] if result else "Нет"

    def _get_name_and_score(self) -> tuple:
        result = self.html.xpath(
            "body"
            "//div[@id='rating']"
            "//table"
            "/tr[3]"
            "//text()"
        )
        return result[:2] if result else ('0', '0')

    def get_params(self) -> str:
        name, score = self._get_name_and_score()

        params = [
            "Год выхода: " + self._setup('tryearofprod'),
            "Тип процессора: " + self._setup('trcpucategory'),
            "Сокет: " + self._setup('trcpusocket'),
            "Количество ядер: " + self._setup('trnumofcores'),
            "Количество потоков: " + self._setup('trnumofthreads'),
            "Базовая частота: " + self._setup('trbasefreq'),
            "Частота TurboBoost: " + self._setup('trturbofreq'),
            "Размер кэша L3: " + (
                lambda value: value if 'нет' in value.lower() else
                str(round(int(value) / 1024)) + ' МБ'
            )(self._setup('trcachel3')),
            "Тепловыделение: " + self._setup('trtdp'),
            "Встроенный графический процессор: " + self._setup('trgraphics'),
            "Контроллер ОЗУ: " + self._setup('trmemorycontroller'),
        ]
        return (
                f"\n{'-' * 30}\n".join(params) +
                f"\n\n\nБалл производительности для\n{name}:\n----------     {score}     ----------"
        ) if score != '0' else "Неверная модель процессора."


class GPU(BaseComponent):
    def _setup(self, keyword: str) -> str:
        result = self.html.xpath(
            "//div[@class='body']"
            "//table[@id='tableosn']"
            f"/tr[@id='{keyword}']"
            "/td[@class='tk1']"
            "/text()"
        )
        return result[0] if result else "Нет"

    def _get_name_and_score(self) -> tuple:
        name = self.html.xpath(
            "body"
            "//div[@id='ratdivob']"
            "//table[@id='tabrating']"
            "//tr[2]"
            "//a[@class='white']"
            "/text()"
        )

        score = self.html.xpath(
            "body"
            "//div[@id='ratdivob']"
            "//table[@id='tabrating']"
            "//tr[2]"
            "//span[@class='sp_rat']"
            "/text()"
        )
        return (name[0], score[0]) if (name and score) else ('0', '0')

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
        return (
                f"\n{'-' * 30}\n".join(params) +
                f"\n\n\nБалл производительности для\n{name}:\n----------     {score}     ----------"
        ) if score != '0' else "Неверная модель видеокарты."
