import os
import shutil
import logging
import argparse
import time

def logger_setup(log_file):
    logger = logging.getLogger('FolderSyncLogger')
    logger.setLevel(logging.DEBUG)

    file_h = logging.FileHandler(log_file)
    file_h.setLevel(logging.DEBUG)

    console_h =logging.StreamHandler()
    console_h.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    file_h.setFormatter(formatter)
    console_h.setFormatter(formatter)

    logger.addHandler(file_h)
    logger.addHandler(console_h)

    return logger

def folder_sync(source,replica,logger):
    if not os.path.isdir(source):
        raise ValueError(f"The source folder provided ({source}) does not exist.")
    
    if not os.path.isdir(replica):
        os.makedirs(replica)
        logger.info(f'Created a replica directory: {replica}')

    for root, dirs, files in os.walk(source):
        re_root = root.replace(source,replica,1) #construts the path corresponding to replica

        for dir in dirs:
            path_dir = os.path.join(re_root,dir)
            if not os.path.isdir(path_dir):
                os.makedirs (path_dir)
                logger.info(f'Created a directory: {path_dir}')

        for file in files:                      #Copying files from source to replica
            file_s_path = os.path.join(root,file)
            file_r_path = os.path.join(re_root,file)
            if not os.path.isdir(file_r_path) or os.path.getmtime(file_s_path) > os.path.getmtime(file_r_path):
                shutil.copy2(file_s_path,file_r_path)
                logger.info(f'Copied a file from {file_s_path} to {file_r_path}')

    for root,dirs,files in os.walk(replica):
        so_root=root.replace(replica,source,1)

        for file in files:                      #Removing files from replica that do not exist in source
            file_s_path = os.path.join(so_root,file)
            file_r_path = os.path.join(root,file)
            if not os.path.exists(file_s_path):
                os.remove(file_r_path)
                logger.info(f'Removed a file : {file_r_path}')

        for dir in dirs:                        #Removing directories from replica that arent present in source
            dir_s_path = os.path.join(root,file)
            dir_r_path = os.path.join(re_root,file)
            if not os.path.isdir(dir_s_path):
                shutil.rmtree(dir_r_path)
                logger.info(f'Removed a directory: {dir_r_path}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Synchronize two folders periodically.')
    parser.add_argument('--source', type=str, default="Source", help='Path to the source folder')
    parser.add_argument('--replica', type=str, default="Replica", help='Path to the replica folder')
    parser.add_argument('--interval', type=int, default=60, help='Synchronization interval in seconds')
    parser.add_argument('--log', type=str, default='folder_sync.log', help='Path to the log file')

    args = parser.parse_args()

    logger = logger_setup(args.log)

    try:
        while True:
            folder_sync(args.source, args.replica, logger)
            logger.info("Folder synchronization completed successfully.")
            time.sleep(args.interval)
    except Exception as e:
        logger.error(f"Error during folder synchronization: {e}")