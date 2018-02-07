#-*- coding: utf-8 -*-
import io
import os
import os.path
import sys
import codecs
import asyncio

import watchdog.events
import watchdog.observers

_BUFFER = 256 # type: int

class ChangeDetectionHandler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self, func, filename):
        super().__init__(patterns=[filename])
        self.func = func

    def on_created(self, ev):
        self.func(ev)

    def on_modified(self, ev):
        self.func(ev)

class TailFollow() :
    def __init__(self, filepath):
        self.filepath = filepath
        self.basepath = os.path.dirname(filepath)
        self.filename = os.path.basename(filepath)

        self.async_event = asyncio.Event()
        self.last_read = []
        self._stop = False

    def on_changed(self, loop : asyncio.AbstractEventLoop):
        current_filesize = os.path.getsize(self.filepath)

        if current_filesize > self.last_filesize:
            with open(self.filepath) as f:
                f.seek(self.last_filesize)
                self.last_read = f.readlines()

            self.last_filesize = current_filesize
            loop.call_soon_threadsafe(self.async_event.set)

    async def watch_async(self, loop : asyncio.AbstractEventLoop, start_position:int = -1) :
        if start_position == -1:
            self.last_filesize = os.path.getsize(self.filepath)
        else :
            self.last_filesize = start_position

        handler = ChangeDetectionHandler(lambda ev:self.on_changed(loop), self.filepath)
        observer = watchdog.observers.Observer()
        observer.schedule(handler, self.basepath, recursive=True)

        self.async_event.clear()
        self.last_read = []
        self._stop = False

        observer.start()

        while True:
            await self.async_event.wait()
            self.async_event.clear()
            for line in self.last_read :
                do_stop = yield line
                if do_stop :
                    self._stop = True
                    break
            self.last_read = []

            if self._stop :
                break

        observer.stop()

    def watch_stop(self):
        self._stop = True
        self.async_event.set()

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

async def tailwatch(filename, loop):
    follow = TailFollow(filename)
    try:
        async for line in follow.watch_async(loop) :
            sys.stdout.write(line)
    except Exception as ex:
        loop.stop()
        raise ex

