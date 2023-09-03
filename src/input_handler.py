from re import search
import pc_components


class UserInput:
    """Class that processes user message and
    looks for desired PC component in it."""

    CPU_FAMILIES_LIST = {
        r"i[3, 5, 7, 9]$": "Core_%s-",
        r"ryzen_[3, 5, 7, 9]$": "%s_",
        r"pentium": "%s_",
        r"celeron": "%s_",
        r"athlon": "%s_",
        r"phenom": "%s_",
        r"sempron": "%s_",
        r"xeon": "%s_",
        r"ryzen_threadripper": "%s_",
        r"epyc": "%s_",
        r"fx": "%s-",
        r"a[4, 6, 8, 9, 10, 12]": "%s-"
    }

    GPU_FAMILIES_LIST = {
        r"gtx": "GeForce_%s_",
        r"rtx": "GeForce_%s_",
        r"radeon": "%s_",
        r"hd": "%s_Graphics_",
        r"uhd": "%s_Graphics_",
        r"quadro": "%s_",
        r"firepro": "%s_",
        r"mobility_radeon": "%s_",
        r"gt": "GeForce_%s_",
        r"gts": "GeForce_%s_",
        r"geforce": "%s_"
    }

    def __init__(self, input_message: str) -> None:
        self.input_message = input_message.strip().lower()

    def _get_splitted_input_values(self) -> list[str]:
        """Split user input by whitespaces to get 
        requested device's family and model as a list."""
        if ((not self.input_message.startswith("ryzen")) and 
            (not self.input_message.startswith("mobility"))):
            
            return self.input_message.split(maxsplit=1)

        else:
            # Split message by 2nd whitespace since "Ryzen 3/5/7" and "Mobility Radeon"
            # contain two words in their series name
            splitted_values = self.input_message.split(maxsplit=2)
            family = " ".join(splitted_values[:2])
            model = splitted_values[2]
            return [family, model]
        
    def _are_splitted_input_values_valid(self, values_list: list) -> bool:
        """Check if '_get_splitted_input_values'
        has returned correct values"""
        return (values_list is not None) and (len(values_list) == 2)
    
    def _handle_exceptional_cases(self) -> None:
        """Some CPUs and GPUs have different, non-standard URLs.
        This method directly edits entered device family and
        model as class attributes to make them valid
        for further request sending."""

        if self.input_family in ("athlon_", "phenom_"):
            self.input_model = self.input_model.replace('2_', 'II_', 1).replace('xII', 'x2')

        elif self.input_family == 'pentium_' and self.input_model[:2] in ('2_', '3_'):
            self.input_model = self.input_model.replace('2_', 'II_', 1).replace('3_', 'III_', 1)
            
        if self.input_model == "gold_g6400":
            self.input_model += "_"

        elif self.input_model == "1060":
            self.input_model += "_6gb"

        elif self.input_model == "hd_5650":
            self.input_family = "ATI_" + self.input_family
        

    def get_requested_component(self) -> pc_components.CPU | pc_components.GPU | None:
        """Returns either the desired by user PC component for further
        request to the website and HTML-parsing of its parameters, or
        'None' if no device recognized in user's message"""
        splitted_values = self._get_splitted_input_values()

        if self._are_splitted_input_values_valid(splitted_values):
            self.input_family, self.input_model = splitted_values
        else:
            return None
        
        # URLs do not have whitespaces but underscores
        self.input_family = self.input_family.strip().replace(" ", "_")
        self.input_model = self.input_model.strip().replace(" ", "_")

        # Looking for a device series in user message with regular expression
        for pattern, component_url in self.CPU_FAMILIES_LIST.items():
            if search(pattern, self.input_family):

                # Paste entered by user device series into a formattable string
                # to produce "Core_i3" from "i3" e.g. for a valid request URL
                self.input_family = component_url % self.input_family

                self._handle_exceptional_cases()

                component = pc_components.CPU(series=self.input_family, model=self.input_model)
                return component

        for pattern, component_url in self.GPU_FAMILIES_LIST.items():
            if search(pattern, self.input_family):

                self.input_family = component_url % self.input_family

                self._handle_exceptional_cases()

                component = pc_components.GPU(series=self.input_family, model=self.input_model)
                return component