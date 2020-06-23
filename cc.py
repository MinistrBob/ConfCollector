#!/usr/bin/env python3
import json
import os
import hashlib
from contextlib import contextmanager
from json.decoder import JSONDecodeError


@contextmanager
def open_file(filename, mode="r"):
    try:
        f = open(filename, mode, encoding='utf-8')
    except IOError as err:
        yield None, err
    else:
        try:
            yield f, None
        finally:
            f.close()


def main():
    with open_file("config.list", "r") as (f, err):
        if err:
            print(f"Error:{err}")
        else:
            cl = [line.rstrip('\n') for line in f]
    with open_file("db.json", "r") as (f, err):
        if err:
            print(f"Error:{err}")
        else:
            try:
                db = json.load(f)
            except JSONDecodeError as e:
                pass  # db.json is empty?
    list_config_files = []
    for x in cl:
        config_file = {'file': x, 'size': os.path.getsize(x), 'mtime': os.path.getmtime(x)}
        # print(x)
        # file_size = os.path.getsize(x)
        # print(file_size)
        # print(config_file)

        with open_file(x) as (f, err):
            if err:
                print(f"Error:{err}")
            else:
                try:
                    # read contents of the file
                    file_content = f.read()
                    # pipe contents of the file through
                    config_file['md5'] = hashlib.md5(file_content.encode('utf-8')).hexdigest()
                except Exception as e:
                    print(f"ERROR: I can't md5 {e}")
        print(config_file)
        list_config_files.append(config_file)

    with open_file("db.json", "w") as (f, err):
        if err:
            print(f"Error:{err}")
        else:
            try:
                f.write(json.dumps(list_config_files, indent=4))
            except Exception as e:
                print(f"ERROR: Dump JSON: {e}")


if __name__ == "__main__":
    main()
