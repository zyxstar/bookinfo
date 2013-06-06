#coding=utf-8
import sys
import datetime
import os
import traceback
import codecs
_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(_dir)

def try_to_get_book(handler,src,isbn,logfile):
    try:
        return handler(isbn)
    except:
        log = open(_dir + "/" + logfile, 'a')
        log.write("\r\n\r\n%s %s %s========================================\r\n" % (src,isbn,str(datetime.datetime.now())))
        traceback.print_exc(file = log)
        log.close()

def write_to_file_with_gbk(arr,filename,mode):
    lines='\r\n'.join(arr)
    f = codecs.open(_dir + "/" + filename, mode, "gbk")
    f.writelines(lines)
    f.close()
        
def get_book(src,isbn,handler):
    ret = [isbn, src ,str(datetime.datetime.now().time())]    
    arr=try_to_get_book(handler,src,isbn,"gateway_error.txt")
    if arr is not None: ret.extend(arr)
    write_to_file_with_gbk(ret,"gateway_data.txt","w")

def dic_to_arr(dic,keys):
    return [dic[k] for k in keys]
    
def douban_handler(isbn):
    import parse_douban
    arr=dic_to_arr(parse_douban.get_book(isbn),parse_douban.get_keys())
    return map(lambda txt:unicode(txt,'utf-8'),arr)
   
def opac_handler(isbn):
    import parse_opac
    books=parse_opac.get_bookdetail("isbn", isbn)#return match books list
    keys=parse_opac.get_keys()
    arr=[]
    for book in books:
        arr.extend(dic_to_arr(book,keys))
    return arr
   
if __name__=="__main__":
    src = sys.argv[1]
    isbn = sys.argv[2]#'9787121006661'
    if src=="opac":
        get_book(src,isbn,opac_handler)
    elif src=="douban":
        get_book(src,isbn,douban_handler)
