
def choose_chinese_character(goal):
    for each in goal:
        x = 80
        status = True
        while status:
            s = bytes(each["title"], 'utf8')[:x]
            try:
                sss = s.decode('utf8')
            except:
                x -= 1
            else:
                status = False
        each["title"] = sss
    return