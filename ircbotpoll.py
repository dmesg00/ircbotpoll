#!/usr/bin/env python3

################################################################
# IRC Bot for creating polls                                   #
#                                                              #
# Created by q3aql (q3aql@duck.com)                            #
# Licensed by GPL v2.0                                         #
# Last update: 27-08-2025                                      #
#                                                              #
# Requirements:                                                #
#    pip install irc                                           #
################################################################

import sys
import time
import signal
import logging
from collections import defaultdict
from threading import Event, Thread

import irc.client

######## CONFIGURATION (Edit with your settings)
SERVER   = "irc.example.net"
PORT     = 6667
USE_TLS  = False
NICK     = "poll-bot"
REALNAME = "IRC Poll Bot"
CHANNELS = ["#support", "#linux"]
#########

polls = {}

def on_connect(conn, event):
    logging.info("Connected to %s:%s", SERVER, PORT)
    for chan in CHANNELS:
        conn.join(chan)
        logging.info("Joining %s", chan)

def on_join(conn, event):
    nick = irc.client.NickMask(event.source).nick
    channel = event.target

    if nick == NICK:
        return

    logging.info("%s has joined %s", nick, channel)

def on_pubmsg(conn, event):
    channel = event.target
    nick = irc.client.NickMask(event.source).nick
    message = event.arguments[0]

    if message.startswith("!poll"):
        create_poll(conn, channel, message)
    elif message.startswith("!vote"):
        cast_vote(conn, channel, nick, message)
    elif message.startswith("!results"):
        show_results(conn, channel)
    elif message.startswith("!endpoll"):
        end_poll(conn, channel)

def create_poll(conn, channel, message):
    parts = message.split(" ", 1)
    if len(parts) < 2:
        conn.privmsg(channel, "Usage: !poll <question>")
        return

    question = parts[1]
    if channel in polls:
        conn.privmsg(channel, "A poll is already active. Please end it before starting a new one.")
        return

    polls[channel] = {"question": question, "votes": defaultdict(int)}
    conn.privmsg(channel, f"Poll created: {question} - Use !vote <option> to vote.")

def cast_vote(conn, channel, nick, message):
    if channel not in polls:
        conn.privmsg(channel, "No active poll in this channel.")
        return

    parts = message.split(" ", 1)
    if len(parts) < 2:
        conn.privmsg(channel, "Usage: !vote <option>")
        return

    option = parts[1]
    polls[channel]["votes"][option] += 1
    conn.privmsg(channel, f"{nick} voted for: {option}")

def show_results(conn, channel):
    if channel not in polls:
        conn.privmsg(channel, "No active poll in this channel.")
        return

    poll = polls[channel]
    results = ", ".join(f"{option}: {count}" for option, count in poll["votes"].items())
    conn.privmsg(channel, f"Results for '{poll['question']}': {results}")

def end_poll(conn, channel):
    if channel not in polls:
        conn.privmsg(channel, "No active poll in this channel.")
        return

    results = show_results(conn, channel)
    conn.privmsg(channel, f"Poll ended: {polls[channel]['question']} - {results}")
    del polls[channel]

def on_disconnect(conn, event):
    logging.warning("Disconnected from the server – reconnecting in 10s...")
    time.sleep(10)
    connect_and_start()

def on_error(conn, event):
    logging.error("ERROR from server: %s", event.arguments)

def connect_and_start():
    reactor = irc.client.Reactor()

    try:
        if USE_TLS:
            conn = reactor.server().connect_ssl(
                SERVER, PORT, NICK, password=None, ssl_verify=False
            )
        else:
            conn = reactor.server().connect(SERVER, PORT, NICK, password=None)
    except irc.client.ServerConnectionError as e:
        logging.error("Unable to connect: %s", e)
        logging.warning("Retrying connection in 10s...")
        time.sleep(10)
        connect_and_start()

    conn.add_global_handler("welcome", on_connect)   # 001
    conn.add_global_handler("join", on_join)
    conn.add_global_handler("pubmsg", on_pubmsg)
    conn.add_global_handler("disconnect", on_disconnect)
    conn.add_global_handler("error", on_error)
    reactor.process_forever()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        connect_and_start()
    finally:
        pass
