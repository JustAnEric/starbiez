from utils.starbie import is_starbie_board
from utils import logging, jerryscript_js, path


import board
import digitalio
import time
import wifi
import os

JSCRIPT_MODULES: list[dict] = []


if __name__ == "__main__":
    if not is_starbie_board():
        logging.msg_err("are you sure this is a starbie board?? we can't verify it is. if this is your own design of the starbie board, edit the settings.json file!")
        exit(2)

    if not jerryscript_js.is_jerryscript_available():
        logging.msg_warn("modularity was disabled... you won't be able to use the modules/ directory to write hooks on top of me!!")
        logging.msg_warn("did you manage to flash the correct firmware.uf2 file to me? (https://github.com/JustAnEric/starbiez/blob/main/firmware/README.txt)")
    else:
        if not path.exists("./modules"):
            os.mkdir("./modules")
            logging.msg_boot("no JScript modules were found to load")
        else:
            f_listing = os.listdir("./modules")
            logging.msg_boot(f"loading {len(f_listing)} JScript modules into memory...")

            for entry in f_listing:
                if not entry.lower().strip().endswith(".js"): continue
                JSCRIPT_MODULES.append({
                    "filename": entry,
                    "module": jerryscript_js.run_jscript_file(entry)
                })
                logging.msg_boot(f"  loaded {entry} successfully")
    
    logging.msg_boot("boot has finished")

    