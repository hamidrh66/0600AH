import os
import sys
import re


numbers_dict = {
    "الأول": 1,
    "الثاني": 2,
    "الثالث": 3,
    "الرابع": 4,
    "الخامس": 5,
    "السادس": 6,
    "السابع": 7,
    "الثامن": 8,
    "التاسع": 9,
    "العاشر": 10,
    "الحادي عشر": 11,
    "الثاني عشر": 12,
    "الثالث عشر": 13,
    "الرابع عشر": 14,
    "الخامس عشر": 15,
    "السادس عشر": 16,
    "السابع عشر": 17,
    "الثامن عشر": 18,
    "التاسع عشر": 19,
    "العشرون": 20,
    "الحادي والعشرون": 21,
    "الثاني والعشرون": 22,
    "الثالث والعشرون": 23,
    "الرابع والعشرون": 24,
    "الخامس والعشرون": 25,
    "السادس والعشرون": 26,
    "السابع والعشرون": 27,
    "الثامن والعشرون": 28,
    "التاسع والعشرون": 29,
    "الثلاثون": 30,
    "الحادي والثلاثون": 31,
    "الثاني والثلاثون": 32,
    "الثالث والثلاثون": 33,
    "الرابع والثلاثون": 34,
    "الخامس والثلاثون": 35
    }

def get_page_numbers(text, exclude_zero=True):
    page_numbers = re.findall("PageV\d+P\d+", text)
    if exclude_zero:
        page_numbers = [p for p in page_numbers if p != "PageV00P000"]
    return page_numbers


def print_first_and_last_pages(folder):
    page_list = []
    for fn in os.listdir(folder):
        if fn.endswith("-ara1"):
            fn_id = re.findall("(\d+)-ara1", fn)[0]
            fp = os.path.join(folder, fn)
            with open(fp, mode="r", encoding="utf-8") as file:
                text = file.read()
            page_numbers = get_page_numbers(text)
            page_list.append([fn_id, page_numbers[0], page_numbers[-1]])
    for fn_id, first_page, last_page in sorted(page_list):
        print("{}\t{}\t{}".format(fn_id, first_page, last_page))
    return page_list
    
    

def print_first_and_last_pages_of_every_volume_in_file(fp):
    with open(fp, mode="r", encoding="utf-8") as file:
        text = file.read()
    page_numbers = re.findall("PageV\d+P\d+", text)
    vols = dict()
    for page in page_numbers:
        vol = page[5:7]
        p = page[-3:]
        if vol not in vols:
            vols[vol] = {"first": p, "last": p}
        else:
            vols[vol]["last"] = p
    vol_list = [[vol, vols[vol]["first"], vols[vol]["last"]] for vol in vols]
    for vol, first, last in sorted(vol_list):
        print("{}\t{}\t{}".format(vol, first, last))
    return vol_list

def get_ajza_in_files(folder, regex="الجزء ([\w\s]+?) من المشيخة"):
    juz_list = []
    for fn in os.listdir(folder):
        if fn.endswith("-ara1"):
            fn_id = re.findall("(\d+)-ara1", fn)[0]
            fp = os.path.join(folder, fn)
            with open(fp, mode="r", encoding="utf-8") as file:
                text = file.read()
            ajza = re.findall(regex, text)
            ajza_filtered = []
            for juz in ajza:
                if juz not in ajza_filtered:
                    ajza_filtered.append(juz)
            ajza_numbers = []
            for juz in ajza:
                try:
                    ajza_numbers.append(numbers_dict[juz])
                except:
                    ajza_numbers.append("??")
            juz_list.append([fp, ajza_filtered, ajza_numbers])
    for fp, ajza, ajza_numbers in juz_list:
        print(fp)
        for i, juz in enumerate(ajza):
            print("\t{}\t{}".format(ajza_numbers[i], juz))
    return juz_list

def change_vol_number(fp, vol):
    with open(fp, mode="r", encoding="utf-8") as file:
        text = file.read()
    text = re.sub("PageV\d+P(\d+)", r"PageV{0:02d}P\1".format(vol), text)
    return text


def correct_page_numbers(text):
    """Replace PageV\dP000 page numbers with the correct ones"""
    def page_no(pos, s):
        p = s[pos+8:pos+11]
        #print(p)
        return p

    def vol_no(pos, s):
        return s[pos+5:pos+7]
    
    def repl(s, srt, end, repl_str):
        return "{0}{1:03d}{2}".format(s[:srt], repl_str, s[end:])

    def repl_page_nos(prv_number, new, cur, nxt, j):
        n = prv_number+1
        #print(n)
        new = repl(new, cur+8, cur+11, n)
        for pos in nxt[:-1]:
            n += 1
            #print(n)
            new = repl(new, pos+8, pos+11, n)
        passed = j
        return new, passed
    
    passed = 0
    i = 0
    cur = 0
    prv = 0
    new = text
    nxt = []
    for i in range(len(text)):
        #print("i", i, text[i])
        if i >= passed:
            #print("not yet passed")
            if text[i] == "P":
                if text[i:i+5] == "PageV" and page_no(i, text) != "000":
                    prv = cur
                    cur = i
                    #print(page_no(i, text))
                elif page_no(i, text) == "000":
                    prv = cur
                    cur = i
                    vol = vol_no(i, text)
                    #print("vol:", vol)
                    try:
                        #print(page_no(prv, text))
                        prv_number = int(page_no(prv, text))
                    except:
                        print("failed to convert", page_no(prv, text), "to int")
                        prv_number = 0
                    #print("prv_number", prv_number)
                    for j in range(i+1, len(text)):
                        #print("j", j, text[j])
                        if text[j] == "P":
                            if text[j:j+5] == "PageV":
                                nxt.append(j)
                                #print(prv_number, [page_no(x, text) for x in nxt])
                                if page_no(j, text) != "000":
                                    next_number = int(page_no(j, text))
                                    if prv_number + len(nxt) + 1 == next_number:
##                                        n = prv_number+1
##                                        #print(n)
##                                        new = repl(new, cur+8, cur+11, n)
##                                        for pos in nxt[:-1]:
##                                            n += 1
##                                            #print(n)
##                                            new = repl(new, pos+8, pos+11, n)
##                                        passed = j
                                        new, passed = repl_page_nos(prv_number, new, cur, nxt, j)
                                    nxt = []
                                    #input()
                                    break
                                elif vol_no(j, text) != vol:
                                    new, passed = repl_page_nos(prv_number, new, cur, nxt, j)
                                    nxt = []
                                    break
                    if nxt:
                        print("Replacing last instance")
                        new, passed = repl_page_nos(prv_number, new, cur, nxt, j)
    return new
                                    
                    
            
'''
            

def correct_page_numbers(text):
    """Replace PageV\dP000 page numbers with the correct ones"""
    def get_page_number_as_int(t):
        n = re.findall("PageV\d+P\d+", t)[0][-3:]
        return int(n)

    def escape(s):
        s = s.replace("\\", "\\\\")
        for x in "[](){}|.^$*+?":
            s = s.replace(x, "\\"+x)
        return s

    def correct(text):
        page_numbers = re.findall("[^P]{0,50}PageV\d+P\d+[^P]{0,50}", text)
        #print("correcting; page numbers:", len(page_numbers))
        for i, context in enumerate(page_numbers):
            if "P000" in context:
                #print("len_context", len(context))
                number = re.findall("PageV\d+P\d+", context)[0]
                prv = get_page_number_as_int(page_numbers[i-1])
                nxt = []
                n = 0
                j=i
                while n == 0:
                    j += 1
                    try:
                        nxt.append(get_page_number_as_int(page_numbers[j]))
                        n = nxt[-1]
                    except:
                        print("failed to get next page number")
                        n = "END"
                        return text, True
                #print(prv, nxt)
                if prv + len(nxt) == nxt[-1] - 1:
                    new_number = "PageV{0}P{1:03d}".format(number[5:7], prv+1)
                    #print(">", new_number)
                    new_context = re.sub(number, new_number, context)
                    if len(new_context) != len(context):
                        print("context", len(context))
                        print(context)
                        print("new_context", len(new_context))
                        print(new_context)
                        input()
                else:
                    print(prv, nxt)
                    new_context = re.sub(r"P000", r"PXXX", context)
                #print(escape(context))
                text = re.sub(escape(context), new_context, text)
                #print(new_context)
                return text, False
        print("Finished correcting!")
        return text, True
    
    done = False
    while done == False:
        text, done = correct(text)
    print("left while loop!")
    text = re.sub("PXXX", "P000", text)
    return text
'''

def merge_files(juz_list):
    merge_dic = dict()
    for fp, ajza, numbers in sorted(juz_list, key=lambda x: x[2]):
        print(fp, numbers)
        if len(set(numbers)) > 2:
            pass
        elif len(set(numbers)) == 0:
            msg = "No juz number for {} detected. Write juz number manually: ".format(fp)
            vol = int(input(msg))
            merge_dic[vol] = change_vol_number(fp, vol)
        else:
            merge_dic[numbers[0]] = change_vol_number(fp, numbers[0])
    print(sorted(merge_dic.keys()))
    merged = [merge_dic[k] for k in sorted(merge_dic.keys())]
    merged = "\n\n\n".join(merged)
    header_regex = "\n######OpenITI#.+?#META#Header#End#"
    merged = re.sub(header_regex, "", merged, flags=re.DOTALL)
    orig_len = len(merged)
    merged = correct_page_numbers(merged)
    print("merged length before and after correcting page numbers:", orig_len, len(merged))
    with open("merged.txt", mode="w", encoding="utf-8") as file:
        file.write(merged)    

    return merged
        

#page_list = print_first_and_last_pages(".")
#fp = "0576IbnMuhammadSilafi.MashyakhaBaghdadiyya.Shamela0021634-ara1"
#vol_list = print_first_and_last_pages_of_every_volume_in_file(fp)
juz_list = get_ajza_in_files(".")
merged = merge_files(juz_list)





