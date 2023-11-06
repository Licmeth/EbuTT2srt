import sys
import os
import datetime as dt
from lxml import etree as et

TAG_BODY = "{http://www.w3.org/ns/ttml}body"
TAG_DIV = "{http://www.w3.org/ns/ttml}div"
TAG_SPAN = "{http://www.w3.org/ns/ttml}span"

ATTR_BEGIN = "begin"
ATTR_END = "end"

TIMESTAMP_FORMAT = "%H:%M:%S.%f"

BEGIN = "begin"
END = "end"
MESSAGE = "message"

OUTPUT_EXTENSION = "srt"

def main():
    filename = getInputFilename()
    print(f"Converting {filename}")

    subs = parseInputFile(filename)
    print(f"Found {len(subs)} subtitles.")

    outputFilename = getOutputFilename(filename)
    writeOutput(subs, outputFilename)
    print(f"Subtitles successfully written to {outputFilename}")

    

def getInputFilename():
    if len(sys.argv) < 1:
        print("Error. Please provide an EBU-TT encoded xml file as argument.")
        quit()
    filename = sys.argv[1]

    if not os.path.exists(filename):
        print("Error. The given input file does not exist.")
        quit()

    if not os.path.isabs(filename):
        filename = os.path.abspath(filename)
    
    return filename



def getOutputFilename(inputFilename: str):
    basename, _ = os.path.splitext(inputFilename)
    filename = f"{basename}.{OUTPUT_EXTENSION}"
    if os.path.exists(filename):
        for i in range(1,1000):
            filename = f"{basename}{i:03}.{OUTPUT_EXTENSION}"
            if not os.path.exists(filename):
                return filename
        print("Error. Could not create output file.")
        quit()
    return filename



def parseInputFile(filename: str):
    try:
        root = et.parse(filename)
    except Exception as e:
        print("Error parsing file")
        print(e)
        quit()

    subs = list()
    try:
        for node in root.find(TAG_BODY).find(TAG_DIV):
            sub = dict()
            sub[BEGIN] = getTimestamp(node, ATTR_BEGIN)
            sub[END] = getTimestamp(node, ATTR_END)
            sub[MESSAGE] = getMessage(node)
            if not None in (sub[BEGIN], sub[END], sub[MESSAGE]):
                subs.append(sub)
    except Exception as e:
        print("Error parsing xml content")
        print(e)
        quit()
    return subs



def getTimestamp(node: et.Element, attribute: str):
    try:
        value = node.get(attribute)
        value = f"{value}000"
        timestamp =  dt.datetime.strptime(value, TIMESTAMP_FORMAT)
    except:
        return None
    return timestamp
    


def getMessage(node: et.Element):
    text = None
    for span in node.findall(TAG_SPAN):
        line = span.text
        if not line:
            next
        if text:
            text = f"{text}\n{line}"
        else:
            text = line
    return text



def writeOutput(subs: dict, filename: str):
    with open(filename, 'w', encoding='utf8') as f:
        for i, sub in enumerate(subs):
            f.write(f"{i+1:d}\n")
            f.write(f"{formatOutputTimestamp(sub[BEGIN])} --> {formatOutputTimestamp(sub[END])}\n")
            f.writelines(sub[MESSAGE])
            f.write("\n\n")



def formatOutputTimestamp(timestamp: dt.datetime):
    return f"{timestamp.strftime('%H:%M:%S')},{timestamp.microsecond/1000:03.0f}"



if __name__ == "__main__":
    main()



