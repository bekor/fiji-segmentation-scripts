import os
from dotenv import load_dotenv, dotenv_values 
load_dotenv()
java_path = os.getenv("JAVA_HOME_PATH")
if os.environ.get('JAVA_HOME') is None:
    os.environ['JAVA_HOME'] = java_path

import imagej

from macro import macro

def initImageJ():
    print("Init imageJ")
    ij = imagej.init('sc.fiji:fiji:2.17.0',add_legacy=False)
    print(f"ImageJ version: {ij.getVersion()}")
    return ij

if __name__ == "__main__":
    ij = initImageJ()

    args = {
        'inputDirectory': os.getenv("INPUT_DIR"),
        'outputDirectory': os.getenv("OUTPUT_DIR")
    }
    print("Start processing images")
    result = ij.py.run_macro(macro, args)
    print("Done")
