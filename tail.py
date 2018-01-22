#-*- coding: utf-8 -*-
import io
import os
import codecs

_BUFFER = 256 # type: int

def tail_file(f:io.IOBase, linenum:int, read_to:int = 0, encoding:str='utf-8', retry_count:int = 0) -> [str]:
    # seek to start position
    read_amount_calc = _BUFFER * (2**retry_count)
    read_amount = read_amount_calc if read_amount_calc >= read_to else read_to
    read_from = read_to - read_amount
    f.seek(read_from, os.SEEK_SET)

    # read last lines
    read_lines = f.read(read_amount).splitlines()

    linecount = len(read_lines)

    if linecount > linenum:
        # if read enough
        return read_lines[-linenum:]
    elif read_to - read_amount <= 0:
        # if read all
        return read_lines
    else:
        # if lack
        # Drop first line and read remaining lines.
        firstline_size = len(read_lines[0].encode(encoding))
        return tail_file(f,
                linenum = linenum - linecount + 1,
                encoding = encoding,
                read_to = read_from + firstline_size,
                retry_count = retry_count+1) + \
                        read_lines[1:][-linenum:] # drop first line

def tail(filename:str, linenum:int, encoding:str='utf-8') -> [str]:
    with codecs.open(filename, 'r', encoding=encoding) as f:
        return tail_file(f, linenum, read_to = os.path.getsize(filename),
                encoding = encoding)

def main():
    print('\n'.join(tail('testfile10.txt', 10)))

if __name__ == '__main__':
    main()
