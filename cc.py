#!/usr/bin/env python3
import json
import os
import hashlib
import settings
import logging
import traceback
from contextlib import contextmanager
from json.decoder import JSONDecodeError

error_text = ""
error_count = 0

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


def get_logger():
    """
    Get logger.
    :return: logger
    """
    # Get log level
    if settings.DEBUG:
        print("get_logger()")
    if settings.DEBUG:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    if settings.DEBUG:
        print(f"log_level={log_level}")
    # Get folder for logging
    if settings.log_dir:
        log_dir = settings.log_path
    else:
        log_dir = os.path.join(os.path.dirname(__file__), 'log')
    if settings.DEBUG:
        print(f"log_dir={log_dir}")
    # If folder for loggin does not exist, create it.
    if not os.path.exists(log_dir):
        try:
            os.mkdir(log_dir)
            if settings.DEBUG:
                print(f"Directory {log_dir} created")
        except OSError:
            print(f"CRITICAL ERROR: Creation of the directory {log_dir} failed")
            print(traceback.format_exc())
            exit(1)
    # Get log file name
    if settings.log_name:
        log_name = settings.log_name
    else:
        log_name = "cc.log"
    if settings.DEBUG:
        print(f"log_name={log_name}")
    log_file = os.path.join(log_dir, log_name)
    if settings.DEBUG:
        print(f"log_file={log_file}")
    log_formatter = logging.Formatter('%(asctime)s|%(levelname)8s| %(message)s')
    handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    handler.setFormatter(log_formatter)
    custom_logger = logging.getLogger()
    custom_logger.setLevel(log_level)
    custom_logger.addHandler(handler)
    # print(custom_logger.handlers[0].baseFilename)
    return custom_logger


def main():
    """
    Main program
    """
    try:
        logger = get_logger()
    except:
        print(f"CRITICAL ERROR: get_logger()")
        print(traceback.format_exc())
        exit(1)
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
    # Check if any files have changed
    logger.debug("Getting file information and Check if any files have changed")
    list_config_files = []
    for x in cl:
        # Getting file information
        logger.debug("Getting file information")
        config_file = {'file': x,
                       'size': os.path.getsize(x),
                       'mtime': os.path.getmtime(x),
                       'atime': os.path.getatime(x),
                       'ctime': os.path.getctime(x)}
        logger.debug(f"config_file={config_file}")
        if settings.md5:
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
        list_config_files.append(config_file)

    # Write DB with configuration file information
    with open_file("db.json", "w") as (f, err):
        if err:
            print(f"Error:{err}")
            logger.error(f"Error:{err}")
        else:
            try:
                f.write(json.dumps(list_config_files, indent=4))
                logger.debug("File db.json write ok")
            except Exception as e:
                logger.error(f"ERROR: Dump JSON: {e}")
    logger.info("CC END")


if __name__ == "__main__":
    main()
    if error_text:
        pass
    else:
        exit(0)
