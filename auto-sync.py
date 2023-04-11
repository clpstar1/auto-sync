from typing import List
import subprocess
import os.path as op
import os
import argparse
import yaml

# TODO: If no folders are given, copy stuff in working_dir

class YTDLP:

    def __init__(self, playlist_id: str, archive_path: str, working_dir: str) -> None:
        self.playlist_id: str = playlist_id
        self.archive_path: str = archive_path
        self.working_dir: str = working_dir
    
    def synchronize_youtube_playlist(self):
        # upgrade / install yt-dlp
        subprocess.run(self.cmd_yt_dlp_install(), check=True)
        subprocess.run(self.cmd_yt_dlp_download(), check=True)

    def cmd_yt_dlp_download(self) -> List[str]:
        return command(f"yt-dlp -o {config['working_dir']}/%(title)s.%(ext)s --download-archive {self.archive_path} {self.__build_url_from_playlist_id(self.playlist_id)}")

    def cmd_yt_dlp_install(self) -> List[str]:
        return command("pip install --upgrade yt-dlp")
    
    def __build_url_from_playlist_id(self, playlist_id) -> str:
        return f"https://www.youtube.com/playlist?list={playlist_id}"
    
    def dry_run(self):
        print(f"YT-DLP [Upgrade] -> {uncommand(self.cmd_yt_dlp_install())}")
        print(f"YT-DLP [Download] -> {uncommand(self.cmd_yt_dlp_download())}")

    def __create_archive_file(url):
        CREATE_ARCHIVE_FILE = f"yt-dlp --flat-playlist --force-write-archive -s --download-archive archive.txt {url}".split(" ")
        subprocess.run(CREATE_ARCHIVE_FILE, check=True)

class AdbSync:

    def __init__(self, executable: str, remote_path: str, include_folders: List[str]) -> None:
        self.exetuble: str = executable
        self.remote_path: str = remote_path
        self.include_folders: List[str] = include_folders

    def sync_files_with_phone(self):
        for folder in self.include_folders:
            subprocess.run(self.cmd_adb_sync(folder), check=True)

    def cmd_adb_sync(self, folder: str) -> List[str]:
        remote_path = self.remote_path
        executable = self.exetuble
        return command(f"{executable} {config['working_dir']}/{folder}/ {os.path.join(remote_path, folder)}")

    def dry_run(self):
        for folder in self.include_folders:
            print(f"ADB-SYNC [Copy] -> {uncommand(self.cmd_adb_sync(folder))}")

def ask_user_for_tagging():
    while True:
        wait_for_tagging = input("Tag files before copying? [y/n]\n")

        if wait_for_tagging == "y":
            input("After tagging the files press enter to continue\n")
            break
        
        if wait_for_tagging == "n":
            break


def command(cmd: str, delim=" ") -> List[str]:
    return cmd.split(delim)

def uncommand(cmd: List[str]) -> str:
    return " ".join(cmd)

def get_config(path: str = "config.yml"):
    with open(path, "r") as yaml_config:
        return yaml.safe_load(yaml_config)

def dry_run(ytdlp: YTDLP, adb_sync: AdbSync):
    print("-" * 30)
    print("Stage 1: YT-DLP")
    ytdlp.dry_run()
    print("-" * 30)
    print("Stage 2: ADB-SYNC")
    adb_sync.dry_run()
    print("-" * 30)

def parse_yaml_config(path = "config.yml"):
    with open(path, "r") as yaml_config:
        return yaml.safe_load(yaml_config)
    
def get_or_default(callback, default_val):
    try:
        return callback()
    except KeyError:
        return default_val

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--config')
    args = parser.parse_args()

    if args.config != None:
        config = parse_yaml_config(args.config)
    else:
        config = parse_yaml_config()

    working_dir = get_or_default(lambda: config['working_dir'], ".")

    ytldp_conf = config['yt_dlp']
    ytdlp = YTDLP(
        ytldp_conf['playlist_id'],
        get_or_default(lambda: ytldp_conf['archive_path'], "archive.txt"),
        working_dir
    )

    adb_sync_conf = config['adb_sync']
    adb_sync = AdbSync(
        get_or_default(lambda: adb_sync_conf['executable'], 'adb-sync'),
        adb_sync_conf['remote_path'],
        get_or_default(lambda: adb_sync_conf['include_folders'], [])
    )

    os.chdir(working_dir)

    if args.dry_run:
        dry_run()
    else:
        ytdlp.synchronize_youtube_playlist()
        ask_user_for_tagging()
        adb_sync.sync_files_with_phone()

