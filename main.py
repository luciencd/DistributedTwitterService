import sys
import os
from udp_communicator import Communicator
from log import Log
from event import event, EventTypes
from datetime import datetime, date
from dateutil import tz
import socket

DEFAULT_FILENAME = "config.txt"
DEFAULT_PORT = 8923

def readConfig():
    configFile = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILENAME

    nodes = []
    with open(configFile) as f:
        file_lines = f.readlines()
        nodes = [(addr, int(port))
                   for line in file_lines
                    for addr,port in [line.strip().split(":")]]

    return nodes


def collect_tweet(site,now_time):
    tweet_text = input("Enter your tweet: ")

    #print(now_time.astimezone(tz.tzlocal()))
    return event(site, EventTypes.TWEET, tweet_text,now_time)

def collect_block(site,now_time):
    blocked_text = input("Enter your block: ")
    if not blocked_text.isdigit():
        return None
    return event(site, EventTypes.BLOCK, str(site) + event.DELIM + blocked_text,now_time)

def collect_unblock(site,now_time):
    unblocked_text = input("Enter your unblock: ")
    if not unblocked_text.isdigit():
        return None
    return event(site, EventTypes.UNBLOCK, str(site) + event.DELIM + unblocked_text,now_time)

def discover_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 0))
    sock.setblocking(False)
    ip = sock.getsockname()[0]
    sock.close()
    return ip


def main():
    own_port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    own_addr = discover_ip()
    print("My addr is",own_addr)
    own_binding = (own_addr,own_port);

    nodes = readConfig()

    communicator = Communicator(nodes,own_binding)
    communicator.start()

    Log.start(len(nodes), communicator.id)

    user_option = ""
    while user_option != "quit":
        user_option = input("Select an option: ")
        #get current time.
        now_time = datetime.utcnow()
        now_time = now_time.replace(tzinfo=tz.tzutc()).replace(microsecond=0)
        #print(now_time.replace(microsecond=0))
        if user_option == "tweet":
            new_tweet = collect_tweet(communicator.id,now_time)
            Log.tweet(new_tweet)
            communicator.tweet()

        elif user_option =="view":
            list_tweets = Log.view()
            print()
            print(*list_tweets, sep="\n\n", end = "\n\n")

        elif user_option =="block":
            new_block = collect_block(communicator.id,now_time)
            if new_block != None:
                Log.block(new_block)
            else:
                print("Invalid block, doing nothing.")

        elif user_option =="unblock":
            new_unblock = collect_unblock(communicator.id,now_time)
            if new_unblock != None:
                Log.unblock(new_unblock)
            else:
                print("Invalid unblock, doing nothing.")

        elif user_option =="quit":
            print("Shutting down...")

        else:
            print("Invalid operation.")

    communicator.stop()
    Log.stop()




if __name__ == "__main__":
    main()
