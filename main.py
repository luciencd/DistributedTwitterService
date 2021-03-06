import sys
import os
from udp_communicator import Communicator
from log import Log
from event import event, EventTypes
from datetime import datetime, date
from dateutil import tz
from urllib.request import urlopen
import socket

DEFAULT_FILENAME = "config.txt"
DEFAULT_PORT = 8923

def readConfig():
    configFile = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILENAME

    nodes = []
    with open(configFile) as f:
        file_lines = f.readlines()
        nodes = [(addr, int(port),name)
                   for line in file_lines
                    for addr,port,name in [line.strip().split(":")]]
    return (list(map(lambda x: x[:-1],nodes)),list(map(lambda x: x[-1],nodes)))


def collect_tweet(site,now_time,names):
    tweet_text = input("Enter your tweet: ")

    return event(site, EventTypes.TWEET, tweet_text,now_time,names[site])

def collect_block(site,now_time,names):
    blocked_text = input("Enter your block: ")
    if (blocked_text.isdigit() and int(blocked_text) > len(names)) \
         or blocked_text not in set(names):
        return None
    blocked_text = str(blocked_text) if blocked_text.isdigit() else str(names.index(blocked_text))
    return event(site, EventTypes.BLOCK, str(site) + event.DELIM + blocked_text,now_time,names[site])

def collect_unblock(site,now_time,names):
    unblocked_text = input("Enter your unblock: ")
    if (unblocked_text.isdigit() and int(unblocked_text) > len(names)) \
         or unblocked_text not in set(names):
        return None
    unblocked_text = str(unblocked_text) if unblocked_text.isdigit() else str(names.index(unblocked_text))
    return event(site, EventTypes.UNBLOCK, str(site) + event.DELIM + unblocked_text,now_time,names[site])

def discover_site(communicator):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 0))
    sock.setblocking(False)
    ip = sock.getsockname()[0]
    sock.close()

    potential_id = communicator.nodes_by_addr.get(ip)
    if potential_id == None:
        #We might be in EC2 -- try to discover public IP via their metadata API
        ip = urlopen("http://169.254.169.254/latest/meta-data/public-ipv4").readlines()[0].decode()
        potential_id = communicator.nodes_by_addr.get(ip)
        if potential_id == None:
            #TODO: it'd be nice if we had a generic way to run this behind NAT
            raise NotImplementedError("Running behind a non-EC2 router is not currently supported.")
    return potential_id



def main():

    nodes,names = readConfig()

    communicator = Communicator(nodes)

    self_id = discover_site(communicator)

    communicator.start(self_id)


    Log.start(len(nodes), communicator.id, names)

    user_option = ""
    while user_option != "quit":
        user_option = input("Select an option: ")
        #get current time.
        now_time = datetime.utcnow()
        now_time = now_time.replace(tzinfo=tz.tzutc()).replace(microsecond=0)

        if user_option == "tweet":
            new_tweet = collect_tweet(self_id,now_time,names)
            Log.tweet(new_tweet)
            communicator.tweet()

        elif user_option =="view":
            list_tweets =Log.view()
            print()
            print(*list_tweets, sep="\n\n", end = "\n\n")

        elif user_option =="block":
            new_block = collect_block(self_id,now_time,names)
            if new_block != None:
                Log.block(new_block)
            else:
                print("Invalid block, doing nothing.")

        elif user_option =="unblock":
            new_unblock = collect_unblock(self_id,now_time,names)
            if new_unblock != None:
                Log.unblock(new_unblock)
            else:
                print("Invalid unblock, doing nothing.")

        elif user_option == "name":
            print("My name is:",communicator.name)

        elif user_option =="quit":
            print("Shutting down...")

        else:
            print("Invalid operation.")

    communicator.stop()
    Log.stop()




if __name__ == "__main__":
    main()
