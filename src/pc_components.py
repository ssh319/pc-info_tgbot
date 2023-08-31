from abc import ABC, abstractmethod
from lxml.html import fromstring
from urllib.request import urlopen


class BaseComponent(ABC):
    """Base class for CPU and GPU classes that provide
    HTML parsing and building response methods"""

    def __init__(self, series: str, model: str) -> None:
        """Class constructor performs a request to the
        web-site and saves received HTML document
        to parse necessary data from it with XPath"""
        self.series = series
        self.model = model

        self.url = (
            "https://www.chaynikam.info/" +

            # Class of a component has a name
            # either 'CPU' or 'GPU', thus producing a
            # 'cpu_comparison.html'/'gpu_comparison.html' string
            # for correct URL
            self.__class__.__name__.lower() +
            
            "_comparison.html?" +
            self.series + self.model
        )
        
        with urlopen(self.url) as request:
            self.html = fromstring(request.read().decode("utf-8"))

    def _get_formatted_chat_response(self, name: str, score: str, params: list[str]) -> str:
        return (
            f"\n{'-' * 30}\n".join(params) +
            f"\n\n\nБалл производительности для\n{name}:\n----------     {score}     ----------"
        )

    @abstractmethod
    def _parse_info(self, keyword: str) -> str:
        """Table cells that contain information are marked
        with short descriptive keywords in their HTML IDs
        for each component characteristic"""
        pass

    @abstractmethod
    def _parse_name_and_score(self) -> tuple[str]:
        pass

    @abstractmethod
    def get_response(self) -> str:
        pass


class CPU(BaseComponent):
    def _parse_info(self, keyword: str) -> str:
        result = self.html.xpath(
            "body"
            "//div[@class='body']"
            "//table[@id='table1']"
            f"/tr[@id='{keyword}']"
            "/td[@class='td6']"
            "/text()"
        )

        if not result:
            return "Нет"
        return result[0] if len(result) == 1 else " ".join(result[:2])

    def _parse_name_and_score(self) -> tuple[str] | None:
        result = self.html.xpath(
            "body"
            "//div[@id='rating']"
            "//table"
            "/tr[3]"
            "//text()"
        )
        return result[:2] if result else None

    def get_response(self) -> str:
        name_and_score = self._parse_name_and_score()
        if name_and_score is not None:
            name, score = name_and_score
        else:
            return "Неверная модель процессора."
        
        # If requested CPU model is not found, web-site returns "0" as a performance score
        if score == "0":
            return "Неверная модель процессора."

        params = [
            "Год выхода: " + self._parse_info('tryearofprod'),
            "Тип процессора: " + self._parse_info('trcpucategory'),
            "Сокет: " + self._parse_info('trcpusocket'),
            "Количество ядер: " + self._parse_info('trnumofcores'),
            "Количество потоков: " + self._parse_info('trnumofthreads'),
            "Базовая частота: " + self._parse_info('trbasefreq'),
            "Частота TurboBoost: " + self._parse_info('trturbofreq'),
            "Размер кэша L3: " + (
                # Convert L3 Cache size from KBs to MBs
                lambda cache_size: cache_size if 'нет' in cache_size.lower() else
                str(round(int(cache_size) / 1024)) + ' МБ'
            )(self._parse_info('trcachel3')),
            "Тепловыделение: " + self._parse_info('trtdp'),
            "Встроенный графический процессор: " + self._parse_info('trgraphics'),
            "Контроллер ОЗУ: " + self._parse_info('trmemorycontroller'),
        ]

        return self._get_formatted_chat_response(name, score, params)


class GPU(BaseComponent):
    def _parse_info(self, keyword: str) -> str:
        result = self.html.xpath(
            "body"
            "//div[@class='body']"
            "//table[@id='tableosn']"
            f"/tr[@id='{keyword}']"
            "/td[@class='tk1']"
            "/text()"
        )

        if not result:
            return "Нет"
        return result[0] if len(result) == 1 else " ".join(result[:2])

    def _parse_name_and_score(self) -> tuple[str] | None:
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
        return (name[0], score[0]) if (name and score) else None

    def get_response(self) -> str:
        name_and_score = self._parse_name_and_score()
        if name_and_score is not None:
            name, score = name_and_score
        else:
            return "Неверная модель видеокарты."

        params = [
            "Год выхода: " + self._parse_info('tr_yearofprod'),
            "Сегмент: " + self._parse_info('tr_desktopormob'),
            "Тип: " + self._parse_info('tr_gpucategory'),
            "Частота ядра: " + self._parse_info('tr_corefrequency'),
            "Шейдерных блоков: " + self._parse_info('tr_unishaders'),
            "Блоков растеризации (ROP): " + self._parse_info('tr_numberofrop'),
            "Текстурных блоков (TMU): " + self._parse_info('tr_numberoftmu'),
            "Тип памяти: " + self._parse_info('tr_memorytype'),
            "Обьём памяти: " + self._parse_info('tr_memorysize'),
            "Частота памяти: " + self._parse_info('tr_memoryfrequency'),
            "Шина памяти: " + self._parse_info('tr_memorybus'),
            "Пропускная способность: " + self._parse_info('tr_bandwidth'),
            "Тепловыделение: " + self._parse_info('tr_tdp'),
            "Мин. блок питания: " + self._parse_info('tr_bppower'),
            "Разъёмы доп. питания: " + self._parse_info('tr_doppitanie'),
        ]

        return self._get_formatted_chat_response(name, score, params)
