#coding=utf-8
import sys
import datetime
import os
import traceback
import codecs
_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(_dir)
import gateway

def get_all_isbn():
    f=open(_dir+'/batch_isbn.txt','r')
    lines=f.readlines()
    f.close()
    return lines

def get_book(src,handler):
    filename="batch_%s_result.txt" % src
    os.remove(_dir + "/" + filename)
    for line in get_all_isbn():
        isbn=line.strip()
        arr=None
        if len(isbn):
            arr = gateway.try_to_get_book(handler,src,isbn,"batch_error.txt")
            if arr is None:arr=[isbn,"error"]
        else:
            arr=["","empty"]
        gateway.write_to_file_with_gbk(['\t'.join(arr)+"\r\n"],filename,"a")
   
if __name__=="__main__":
    src = sys.argv[1]
    if src=="opac":
        get_book(src,gateway.opac_handler)
    elif src=="douban":
        def douban_handler(isbn):
            import time
            time.sleep(1.5)
            return gateway.douban_handler(isbn)
        get_book(src,douban_handler)
