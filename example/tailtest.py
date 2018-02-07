#-*- coding: utf-8 -*-

import sys
import asyncio
import os
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent.joinpath('src')))
import pytail

async def tailwatch_simple(filename, loop):
    follow = pytail.TailFollow(filename)
    try:
        async for line in follow.watch_async(loop) :
            sys.stdout.write(line)
    except Exception as ex:
        loop.stop()
        raise ex

async def gen_testfile(filename):
    import random
    while True:
        with open(filename, 'a') as f:
            f.write('%s\n' % ['ずん','どこ'][random.randint(0,1)])
        await asyncio.sleep(0.1)

def main():
    # print('\n'.join(pytail.tail('testfile10.txt', 10)))

    basedir = os.path.abspath(os.path.dirname(__file__))

    loop = asyncio.get_event_loop()

    asyncio.ensure_future(gen_testfile(os.path.join(basedir, 'testfile_append.txt')))

    asyncio.ensure_future(tailwatch_simple(os.path.join(basedir, 'testfile_append.txt'), loop))
    loop.run_until_complete(asyncio.sleep(5))
    # asyncio.ensure_future(delay_exec(5, lambda: loop.stop()))

    #loop.run_forever()

if __name__ == '__main__':
    main()