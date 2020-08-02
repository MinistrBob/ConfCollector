import os
# DEBUG mod on\off (determined by an environment variable DEBUG)
DEBUG = (os.getenv("DEBUG") == 'True')

conf = dict(
    md5=True,  # Whether to calculate and check the md5.
    log_dir="",  # Directory for logging. Not set by default. Logging to the folder where the program is running + \log.
    log_name="cc.log",  # Name log file.
    # Repository types:
    #     'storage' - file storate (folder on disk);
    #     'git' - git repository (in fact, it is also a folder on disk, but also only push to a remote repository)
    repository={
        'type': 'storage',
        'path': r"c:\MyGit\ConfigCollector\test\repos",
        'fos': True  # whether to create a folder structure in storage
    },
    # repository={
    #     'type': 'git',
    #     'path': r"c:\MyGit\ConfigCollector\test\repos",
    #     'fos': True  # whether to create a folder structure in storage
    # },
    admin_emails=['xxx@gmail.com']  # email addresses to which notifications will be sent
)

if DEBUG:
    conf_debug = dict(
        admin_emails=['yyy@gmail.com']
    )
    # print(settings)
    # merge dictionary Python 3.5 or greater (https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-in-python)
    conf = {**conf, **conf_debug}

if __name__ == '__main__':
    print(conf)
