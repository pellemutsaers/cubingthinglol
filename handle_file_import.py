#Paste the export txt file from cstimer in the cstimerdata folder, the script will automatically take the top file in the folder.
import os
from typing import Tuple, Union

class CSTimerDataHandler:
    def __init__(self, csfile):
        self.filename = f"static/{csfile}"
        with open(self.filename, encoding = "utf8") as txtfile:
            self.lines = str(txtfile.readlines())
            self.session_names = self.get_session_name(self.lines)

    def get_sessions(self, session_number):
        sessions = self.lines.split("properties")[0].split('":')
        session = sessions[session_number]
        session = session.split("]],")[0] + "]]"
        session_handled = parse_cstimer_data(session)
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
        end = lines.index("]}}")
        containing_names = lines[start + 3:end+3]
        print(containing_names)
        dictionary = parse_cstimer_data(containing_names)

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

def parse_dict_element(string: str) -> tuple[object, object]:
    new_string = string.replace(chr(92), "")
    return new_string[:new_string.index(":")], new_string[new_string.index(":")+ 1:]

def unnested_split_dict(string: str) -> dict:
    start = 0
    end = None
    returns = {}
    netto_sq_bracket = 0
    netto_bracket = 0
    netto_quote = False
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
        elif v == '"':
            netto_quote = not netto_quote
        elif (not netto_bracket) and (not netto_sq_bracket) and (not netto_quote) and (v == ","):
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
    netto_quote = False
    # print("list parse:", string)
    for i, v in enumerate(string):
        end = i
        if v == "[":
            netto_bracket += 1
        elif v == "]":
            netto_bracket -= 1
        elif v == '"':
            netto_quote = not netto_quote
        elif (not netto_bracket) and (not netto_quote) and (v == ","):
            returns.append(string[start:end])
            start = end + 1
    if string:
        returns.append(string[start:end+1])
    return returns

def string_seq_conversion(string: str) -> list | dict:
    if "{" == string[0]:
        return {k : string_seq_conversion(v) for k, v in unnested_split_dict(string[1:-1]).items()}
    if "[" in string:
        return [string_seq_conversion(i) for i in unnested_split_list(string[1:-1])]
    return string

def remove_double_quotes(py_object: list | dict | str):
    if isinstance(py_object, str):
        return py_object.replace('"', '')
    elif isinstance(py_object, list):
        for i, v in enumerate(py_object):
            py_object[i] = remove_double_quotes(v)
        return py_object
    elif isinstance(py_object, dict):
        for key, value in list(py_object.items()):
            py_object.pop(key)
            py_object[remove_double_quotes(key)] = remove_double_quotes(value)
        return py_object
    else:
        print("WARNING: unknown datatype found")
        return py_object
    
def parse_cstimer_data(data_string):
    parsed_string = string_seq_conversion(data_string)
    return remove_double_quotes(parsed_string)

# Credit to Gijs Peletier ^
