#coding:utf-8
import urllib2
import urllib
import random
import re
import xml.etree.ElementTree

def get_mainpage():
    return urllib2.urlopen("http://opac.nlc.gov.cn/F?RN=" + str(int(random.random() * 1000000000))).read()

def get_formaction(page):
    r = re.compile(r'form method=get name=form1 action="(.+?)" onsubmit')
    return r.search(page).group(1)

def get_bookpage(url, searchtyp, searchval):
    url = url + "?func=find-b&find_code=%s&request=%s&local_base=NLC01" % (searchtyp, searchval)
    return urllib2.urlopen(url).read()

def get_shiftfmturl(page):
    r = re.compile(r'var url="(.+?)\?func=full-set-set_body')
    return r.search(page).group(1)

def get_setnumber(page):
    r = re.compile(r"SET-NUMBER:(.+?)$", re.IGNORECASE | re.MULTILINE)
    return r.search(page).group(1).strip()

def get_setentry(page):#not used
    r = re.compile(r"input type=hidden id=set_entry value=(.+?)>")
    return r.search(page).group(1)

def get_count(page):
    try:
        r = re.compile(r"条记录\(共(.+?)条\)")
        count = int(r.search(page).group(1).strip())
    except:
        try:
            r = re.compile(r"记录(.+?)of(.+?)\(最大显示记录")
            count = int(r.search(page).group(2).strip())
        except:
            count = 1
    #print count
    return count


def get_bookhtml(url, setnumber, setentry, fmt):
    url = url + "?func=full-set-set_body&set_number=%s&set_entry=%s&format=%s" % (setnumber, setentry, fmt)
    return urllib2.urlopen(url).read()

searchcfg = dict(isbn = 'ISB', title = 'WTP', all = 'WRD')
fmtcfg = dict(std = '999', card = '037', quote = '040', field = '002', marc = '001')
def get_bookshtml(searchtyp, searchval, fmtCd, maxcount = 1):
    mainPage = get_mainpage()
    formAction = get_formaction(mainPage)
#    print formAction
    bookPage = get_bookpage(formAction, searchtyp, searchval)
#    print bookPage
    setNumber = get_setnumber(bookPage)
#    print setNumber

    if searchtyp == 'ISB':
        shiftfmtUrl = get_shiftfmturl(bookPage)
        count = get_count(bookPage)
    else:
        shiftfmtUrl = formAction + "-123456"
        count = min(get_count(bookPage), maxcount)
    setEntryArr = []
    for i in range(1, count + 1):
        setEntryArr.append(str(i).rjust(6, "0"))
    fmt = fmtcfg[fmtCd]
    ret = []
    for setEntry in setEntryArr:
        ret.append("<table>%s</table>" % get_bookhtml(shiftfmtUrl, setNumber, setEntry, fmt))
    return ret

#print get_bookshtml("isbn", "9787111165057", "marc")

def fixhtml(html):
    html = html.replace('&nbsp;', ' ')
    return re.sub(r" class=(.+?)>", lambda matchobj:">", html)

def html2xml(html):
    return xml.etree.ElementTree.XML(html)

def parse_marc(table):
    def _parserow(vals):
        row = []
        row.append({'TEXT':vals})
        for val in vals.split('|'):
            if len(val) == len(vals):break
            if len(val) == 0:continue
            _k = val[0]
            _v = val[2:].strip()
            row.append({_k:_v})
        return row

    def _finditem(ret, key):
        for item in ret:
            if item.has_key(key):return item
        item = {key:[]}
        ret.append(item)
        return item

    ret = []
    for tr in table.findall('tr'):
        tds = tr.findall('td')
        key = tds[0].text
        vals = tds[1].text
        item = _finditem(ret, key)[key]
        item.append(_parserow(vals))
    return ret

marccfg = dict(isbn = "010|a", price = "010|d",
               lang = '1010|a',
               pubcountry = "102|a", pubarea = "102|b",
               title = "2001|a", subtitle = "2001|e", auth = "2001|f", trans = "2001|g", pinyin = "2001|9",
               volumetitle = "2001|i", volumecode = "2001|h", volumeid = "2001|v",
               pubaddr = "210|a", publisher = "210|c", pubdt = "210|d",
               edition2 = "205|a",
               pgcont = "215|a", pgsize = "215|d",
               series1 = "2251|a",
               series2 = "2252|a",
               edition = "305|a",
               summary = "330|a",
               title2 = "5101|a", subtitle2 = "5101|e",
               arttype = "690|a",
               authdetail = "701 0|c",
               transdetail = "702 0|a",
               tag = "6060|a", tag2 = "6060|x"
               )
def get_detail(marc, desc):
    t = marccfg[desc].split('|')
    field = t[0]
    code = t[1]
    ret = []
    for item in marc:
        if not item.has_key(field): continue
        for _ls in item[field]:
            for _item in _ls:
                if _item.has_key(code):
                    ret.append(_item[code])
    return ret

def urlquote(val):
    """
    Quotes a string for use in a URL.
    
        >>> urlquote('://?f=1&j=1')
        '%3A//%3Ff%3D1%26j%3D1'
        >>> urlquote(None)
        ''
        >>> urlquote(u'\u203d')
        '%E2%80%BD'
    """
    if val is None: return ''
    if not isinstance(val, unicode): val = str(val)
    else: val = val.encode('utf-8')
    return urllib.quote(val)

def get_bookdetail(searchtypnm, searchval, maxcount = 1):
    books = get_bookshtml(searchcfg[searchtypnm], urlquote(searchval), "marc", maxcount)
    ret = []
    for book in books:
        fix_html = fixhtml(book)
        table = html2xml(fix_html)
        marc = parse_marc(table)
        detail = {}
        for k in marccfg:
            detail[k] = ','.join(get_detail(marc, k))
        ret.append(detail)
    return ret

def get_keys():
    return "isbn title subtitle price pubdt publisher auth trans pgcont pgsize arttype".split(' ') 
    #"edition title2 subtitle2 series1 series2 tag tag2 authdetail transdetail pinyin pubcountry pubaddr pubarea lang"

if __name__ == "__main__":
    #"9787121006661"
    #"978-7-5083-5594-8"
    #"978-7-111-33624-2"
    #"9787111216322"
    #"9787807570189"
    #"978-7-115-22673-0"
    #"9787111165057"
    #"9787111216322"
    #"9787115226730"
    isbn = "9787807570875"#"9787219068861"                 #"9787807570875""9787807570189"#重号  有多少显示多少
    ret = get_bookdetail("isbn", isbn)     #isbn方式下，maxcount不起作用

#    title = u'汇编语言 王爽'
#    ret = get_bookdetail("all", title, 10)#less 10

#    title = u'CSS权威'
#    ret = get_bookdetail("all", title, 10)#less 10

#    title = u'CSS'
#    ret = get_bookdetail("all", title, 6)#more 10 but eq 6

    print len(ret)
    for detail in ret:
        print "=".ljust(60, '=')
        ls = [k.ljust(12, ' ') + ":\t" + v  for k, v in detail.items()]
        ls.sort()
        for item in ls:
            print item


