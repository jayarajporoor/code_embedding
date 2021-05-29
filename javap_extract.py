def parse_jsonp(src):
    MODULE = 0
    METHOD_DEFS = 1
    METHOD_BODY = 2
    state = MODULE
    curr_method = ""
    curr_method_code = []
    res = {}
    for line in src:
        sline = line.strip()
        if state == MODULE:
            if line[0] == '{':
                state = METHOD_DEFS
        elif state == METHOD_DEFS:
            curr_method = sline
            curr_method_code = []
            state = METHOD_BODY
        elif state == METHOD_BODY:
            if sline == "" or sline == "}":
                state = METHOD_DEFS if sline == "" else MODULE
                if curr_method != "":
                    res[curr_method] = curr_method_code
                curr_method = ""
                curr_method_code = []
            else:
                fields = sline.split(":", 1)
                if len(fields) == 2 and fields[0].isnumeric():
                    curr_method_code.append(fields[1].strip())

    return res

if __name__ == "__main__":
    import sys
    import json
    inpath = sys.argv[1]
    with open(inpath) as fd:
        res = parse_jsonp(fd)
        print(json.dumps(res, indent=4))
