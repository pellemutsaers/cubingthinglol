#Paste the export txt file from cstimer in the cstimerdata folder, the script will automatically take the top file in the folder.
import os
from typing import Tuple

class CSTimerDataHandler:
    def __init__(self):
        self.lines = None
        self.filename = self.get_filename()
        with open(self.filename) as txtfile:
            self.lines = str(txtfile.readlines())
            session_names = self.get_session_name(self.lines)
            for i, name in enumerate(session_names):
                print(f"{i + 1}: {name}")

    def get_filename(self):
        for index, i in enumerate(os.listdir("./cstimerdata")):
            print(f"{index + 1}: {i}")

        cstimer_file = 1 #int(input("Enter index of the file you want to use: "))

        if os.name == "posix":
            filenames = os.listdir("./cstimerdata")
            self.filename = f"./cstimerdata/{filenames[cstimer_file - 1]}"
        else:
            filenames = os.listdir(".\cstimerdata")
            self.filename = f".\cstimerdata\{filenames[cstimer_file - 1]}"
        return self.filename

    def get_sessions(self, session_number):
        sessions = self.lines.split("properties")[0].split('":')
        session = sessions[session_number]
        session = session.split("]],")[0] + "]]"
        session_handled = string_list_conversion(session)
        session_name = self.get_session_name(self.lines, session_number)
        return self.get_times(session_handled), session_name

    def get_times(self, session):
        timeslist = []
        for solve in session:
            try:
                time = int(solve[0][1])
                if solve[0][0] == "-1":
                    timeslist.append(float("nan"))
                elif solve[0][0] != "0":
                    timeslist.append(round((time + solve[0][0]) / 1000, 2))
                else:
                    timeslist.append(round(time / 1000, 2))
            except:
                pass
        return timeslist

    def get_session_name(self, lines, session_number=0):
        start = lines.index('":"')
        end = lines.rindex('","color"')
        containing_names = lines[start + 3:end]
        dictionary = string_list_conversion(containing_names)

        if session_number:
            session_info = dictionary[str(session_number)]
            session_name = session_info["name"]
            return session_name

        else:
            names = []
            for i in range(len(dictionary)):
                session_info = dictionary[str(i + 1)]
                names.append(session_info["name"])
            return names

# -------------------------------------------------------------------------

def parse_dict_element(string: str) -> Tuple[object, object]:
    new_string = string.replace(chr(92), "").replace('"', '')
    return new_string[:new_string.index(":")], new_string[new_string.index(":")+ 1:]

def unnested_split_dict(string: str) -> dict:
    start = 0
    end = None
    returns = {}
    netto_sq_bracket = 0
    netto_bracket = 0
    for i, v in enumerate(string):
        end = i
        if v == "{":
            netto_bracket += 1
        elif v == "}":
            netto_bracket -= 1
        elif v == "[":
            netto_sq_bracket += 1
        elif v == "]":
            netto_sq_bracket -= 1
        elif (not netto_bracket) and (not netto_sq_bracket) and v == ",":
            key, value = parse_dict_element(string[start:end])
            returns[key] = value
            start = end + 1
    if string:
        key, value = parse_dict_element(string[start:end+1])
        returns[key] = value
    return returns

def unnested_split_list(string: str) -> list:
    start = 0
    end = None
    returns = []
    netto_bracket = 0
    for i, v in enumerate(string):
        end = i
        if v == "[":
            netto_bracket += 1
        elif v == "]":
            netto_bracket -= 1
        elif (not netto_bracket) and v == ",":
            returns.append(string[start:end])
            start = end + 1
    if string:
        returns.append(string[start:end+1])
    return returns

def string_list_conversion(string: str) -> list | dict:
    if "{" == string[0]:
        return {k : string_list_conversion(v) for k, v in unnested_split_dict(string[1:-1]).items()}
    if "[" in string:
        return [string_list_conversion(i) for i in unnested_split_list(string[1:-1])]
    return string

# Credit to Gijs Peletier ^