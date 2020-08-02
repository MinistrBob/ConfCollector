#!/usr/bin/env python3
import json
import os
import hashlib
import logging
import traceback
from contextlib import contextmanager
from json.decoder import JSONDecodeError
from shutil import copy
from settings import conf, DEBUG

error_text = ""
error_count = 0

try:
    # Get logger.
    # Get log level
    if DEBUG:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    if DEBUG:
        print(f"log_level={log_level}")
    # Get folder for logging
    if conf['log_dir']:
        log_dir = conf['log_path']
    else:
        log_dir = os.path.join(os.path.dirname(__file__), 'log')
    if DEBUG:
        print(f"log_dir={log_dir}")
    # If folder for loggin does not exist, create it.
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
            if DEBUG:
                print(f"Directory {log_dir} created")
        except OSError:
            print(f"CRITICAL ERROR: Creation of the directory {log_dir} failed")
            print(traceback.format_exc())
            exit(1)
    # Get log file name
    if conf['log_name']:
        log_name = conf['log_name']
    else:
        log_name = "cc.log"
    if DEBUG:
        print(f"log_name={log_name}")
    log_file = os.path.join(log_dir, log_name)
    if DEBUG:
        print(f"log_file={log_file}")
    log_formatter = logging.Formatter('%(asctime)s|%(levelname)8s| %(message)s')
    handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    handler.setFormatter(log_formatter)
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(handler)
except:
    print(f"CRITICAL ERROR: get_logger()")
    print(traceback.format_exc())
    exit(1)


@contextmanager
def open_file(filename, mode="r"):
    """
    File Open Procedure
    :param filename: full file path
    :param mode: r = read, w = write
    :return: either error or file
    """
    try:
        f = open(filename, mode, encoding='utf-8')
    except IOError as err:
        yield None, err
    else:
        try:
            yield f, None
        finally:
            f.close()


def copy_file(file):
    try:
        if conf['repository']['fos']:
            extra_path = os.path.dirname(file)
            if ":" in extra_path:
                extra_path = extra_path.replace(":", "")
            dst = os.path.join(conf['repository']['path'], extra_path)
            if not os.path.exists(dst):
                try:
                    os.makedirs(dst)
                    if DEBUG:
                        print(f"Directory {dst} created")
                except OSError:
                    print(f"CRITICAL ERROR: Creation of the directory {dst} failed")
                    print(traceback.format_exc())
                    exit(1)
        else:
            dst = conf['repository']['path']
        logger.info(f"Copy file:\n{file} to\n{dst}")
        copy(file, dst)
    except Exception as err:
        print(f"Error: Can't copy file from {file} to {conf['repository']['path']}\n{err}")
        logger.error(f"Error: Can't get file information\n{err}")


def push_to_git():
    pass


def send_file_to_repository(file):
    if conf['repository']['type'] == "storage":
        copy_file(file)
    elif conf['repository']['type'] == "git":
        copy_file(file)
        push_to_git()


def main():
    """
    Main program
    """
    logger.info("-" * 120)
    logger.info("CC START")
    # Read list of monitored files (file.list) into cl
    logger.debug("Read list of monitored files (file.list) into cl")
    with open_file("file.list", "r") as (f, err):
        if err:
            logger.error(f"Error:\n{err}")
        else:
            cl = [line.rstrip('\n') for line in f]
            logger.debug(f"cl:{cl}")
    # Read program settings (settings.py) into settings
    logger.debug("Read program settings (settings.py) into settings")
    with open_file("settings.py", "r") as (f, err):
        if err:
            logger.error(f"Error:{err}")
        else:
            try:
                settings = json.load(f)
                logger.debug(f"settings:{settings}")
            except JSONDecodeError as e:
                pass  # db.json is empty?
    # Read DB with configuration file information (db.json) into db
    logger.debug("Read DB with configuration file information (db.json) into db")
    with open_file("db.json", "r") as (f, err):
        if err:
            logger.error(f"Error:{err}")
        else:
            try:
                db = json.load(f)
                logger.debug(f"db:{db}")
            except JSONDecodeError as e:
                pass  # db.json is empty?
    # Getting file information and Check if any files have changed
    logger.debug("Getting file information and Check if any files have changed")
    dict_config_files = {}
    for x in cl:
        # Getting file information
        logger.debug("Getting file information")
        try:
            config_file = {'size': os.path.getsize(x),
                           'mtime': os.path.getmtime(x)}
        except Exception as err:
            print(f"Error: Can't get file information\n{err}")
            logger.error(f"Error: Can't get file information\n{err}")
        logger.debug(f"config_file={config_file}")
        if conf['md5']:
            # md5 calculation
            logger.debug("md5 calculation")
            with open_file(x) as (f, err):
                if err:
                    logger.error(f"Error:{err}")
                else:
                    try:
                        # read contents of the file
                        file_content = f.read()
                        # pipe contents of the file through
                        config_file['md5'] = hashlib.md5(file_content.encode('utf-8')).hexdigest()
                        logger.debug(f"md5={config_file['md5']}")
                    except Exception as e:
                        logger.error(f"ERROR: I can't md5 {e}")
            logger.debug(f"config_file={config_file}")
        dict_config_files[x] = config_file
        # Check the file have changed (path, size, mtime default)
        if x in db:
            if conf['md5']:
                if dict_config_files[x]['md5'] != db[x]['md5']:
                    logger.debug("md5 did not match, copy to repository")
                    send_file_to_repository(x)
            else:
                if dict_config_files[x]['size'] != db[x]['size']:
                    logger.debug("size did not match, copy to repository")
                    send_file_to_repository(x)
                if dict_config_files[x]['mtime'] != db[x]['mtime']:
                    logger.debug("mtime did not match, copy to repository")
                    send_file_to_repository(x)

    # Write DB with configuration file information
    with open_file("db.json", "w") as (f, err):
        if err:
            print(f"Error:{err}")
            logger.error(f"Error:{err}")
        else:
            try:
                f.write(json.dumps(dict_config_files, indent=4))
                logger.debug("File db.json write ok")
            except Exception as e:
                logger.error(f"ERROR: Dump JSON: {e}")
    logger.info("CC END")


if __name__ == "__main__":
    # Check setting
    if not conf['repository']['path']:
        print(f"CRITICAL ERROR: Storage path (conf['repository']['path']) not defined")
        exit(1)
    main()
    if error_text:
        pass
    else:
        exit(0)
