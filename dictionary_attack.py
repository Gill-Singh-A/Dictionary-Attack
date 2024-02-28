#! /usr/bin/env python3

import hashlib, pickle, json
from pathlib import Path
from datetime import date
from optparse import OptionParser
from colorama import Fore, Back, Style
from time import strftime, localtime, time
from multiprocessing import Lock, Pool, cpu_count

status_color = {
    '+': Fore.GREEN,
    '-': Fore.RED,
    '*': Fore.YELLOW,
    ':': Fore.CYAN,
    ' ': Fore.WHITE
}

def display(status, data, start='', end='\n'):
    print(f"{start}{status_color[status]}[{status}] {Fore.BLUE}[{date.today()} {strftime('%H:%M:%S', localtime())}] {status_color[status]}{Style.BRIGHT}{data}{Fore.RESET}{Style.RESET_ALL}", end=end)

def get_arguments(*args):
    parser = OptionParser()
    for arg in args:
        parser.add_option(arg[0], arg[1], dest=arg[2], help=arg[3])
    return parser.parse_args()[0]

hash_algorithms = {
    "md5" : hashlib.md5,
    "sha1" : hashlib.sha1,
    "sha224" : hashlib.sha224,
    "sha256" : hashlib.sha256,
    "sha384" : hashlib.sha384,
    "sha3_224" : hashlib.sha3_224,
    "sha3_256" : hashlib.sha3_256,
    "sha3_384" : hashlib.sha3_384,
    "sha3_512" : hashlib.sha3_512,
    "sha512" : hashlib.sha512,
}
number_of_hashes = 100000000

def calculateHashes(words, algorithm):
    hashes = {}
    for word in words:
        hashes[hash_algorithms[algorithm](word.encode()).hexdigest()] = word
    return hashes
def HashingHandler(words, algorithm):
    threads = []
    hashes = {}
    thread_count = cpu_count()
    word_count = len(words)
    pool = Pool(thread_count)
    word_divisions = [words[group*word_count//thread_count: (group+1)*word_count//thread_count] for group in range(thread_count)]
    for word_division in word_divisions:
        threads.append(pool.apply_async(calculateHashes, (word_division, algorithm)))
    for thread in threads:
        hashes.update(thread.get())
    pool.close()
    pool.join()
    return hashes

if __name__ == "__main__":
    data = get_arguments(('-l', "--load", "load", "List of Wordlists (seperated by ',')"),
                         ('-H', "--hash", "hash", "Hashes/Hash Files to Load (seperated by ',')"),
                         ('-a', "--hashing-algorithm", "hashing_algorithm", f"Hashing Algorithm ({','.join(hash_algorithms.keys())})"),
                         ('-n', "--hashes", "number_of_hashes", f"Number of Hashes to load from a file at one time if the file is large enough that it can't be read at once (Default={number_of_hashes})"),
                         ('-w', "--write", "write", "Name of the File for the data to be dumped (default=current data and time)"),
                         ('-t', "--save-type", "save_type", "File type to dump the data into (text, csv, json, pickle, Default=text)"))
    if not data.hash:
        display('-', "Please specify Hashes/Hash Files to Load!")
        exit(0)
    else:
        hashes_data = data.hash.split(',')
        hashes = []
        for hash_data in hashes_data:
            if Path(hash_data).is_file():
                with open(hash_data, 'r') as file:
                    hashes.extend([hash.lower() for hash in file.read().split('\n')])
            else:
                hashes.append(hash_data.lower())
    display(':', f"Hashes Loaded = {len(hashes)}")
    if not data.hashing_algorithm or data.hashing_algorithm not in hash_algorithms.keys():
        display('-', "Please specify a Valid Hashing Algorithm!")
        display(':', f"Hashing Algorithms = {','.join(hash_algorithms.keys())}")
        exit(0)
    display(':', f"Hashing Algorithm = {Back.MAGENTA}{data.hashing_algorithm}{Back.RESET}")
    if not data.load:
        display('-', "Please specifiy Wordlists to Load!")
        exit(0)
    if not data.number_of_hashes:
        data.number_of_hashes = number_of_hashes
    else:
        data.number_of_hashes = int(data.number_of_hashes)
    if not data.write:
        data.write = f"{date.today()} {strftime('%H_%M_%S', localtime())}"
    wordlists = data.load.split(',')
    cracked_hashes = {}
    hashes_calculated = 0
    display(':', f"Total Wordlists = {Back.MAGENTA}{len(wordlists)}{Back.RESET}")
    for file_index, wordlist in enumerate(wordlists):
        try:
            display(':', f"Loading File {Back.MAGENTA}{file_index+1}/{len(wordlists)} => {wordlist}{Back.RESET}", start='\n')
            with open(wordlist, 'rb') as file:
                words = [word.replace('\r', '') for word in file.read().decode(errors="ignore").split('\n')]
        except FileNotFoundError:
            display('-', f"File {Back.YELLOW}{wordlist}{Back.RESET} not found!")
            continue
        except MemoryError:
            display('-', f"File {Back.MAGENTA}{wordlist}{Back.RESET} too big to load!")
            display(':', f"Loading {Back.MAGENTA}{data.number_of_hashes}{Back.RESET} words at once from the file.")
            with open(wordlist, 'rb') as file:
                done = False
                words_loaded = 0
                current_file_cracked_hashes = 0
                while not done:
                    current_words_loaded = 0
                    words = []
                    t1 = time()
                    while len(words) < data.number_of_hashes and not done:
                        word = file.readline().decode(errors="ignore")
                        if word == '':
                            done = True
                        words.append(word.replace('\n', '').replace('\r', ''))
                        current_words_loaded += 1
                    words_loaded += current_words_loaded
                    t2 = time()
                    display('+', f"Loaded {Back.MAGENTA}{data.number_of_hashes}{Back.RESET} words from the file.")
                    display(':', f"\tTime Taken = {Back.MAGENTA}{t2-t1:.2f} seconds{Back.RESET}")
                    display(':', f"\tRate = {Back.MAGENTA}{current_words_loaded/(t2-t1):.2f} words/second{Back.RESET}")
                    display(':', "Calculating Hashes")
                    t1 = time()
                    words = HashingHandler(words, data.hashing_algorithm)
                    t2 = time()
                    display('+', "Done Calculating Hashes", start='\n')
                    display(':', f"\tHashes Calculated = {Back.MAGENTA}{current_words_loaded}{Back.RESET}")
                    display(':', f"\tTime Taken = {Back.MAGENTA}{t2-t1:.2f} seconds{Back.RESET}")
                    display(':', f"\tRate = {Back.MAGENTA}{current_words_loaded/(t2-t1):.2f} hashes/second{Back.RESET}")
                    display(':', f"Comparing Calculated Hashes...")
                    current_cracked_hashes = 0
                    t1 = time()
                    for hash_index, hash in enumerate(hashes):
                        if hash in words.keys():
                            cracked_hashes[hash] = words[hash]
                            current_cracked_hashes += 1
                    t2 = time()
                    current_file_cracked_hashes += current_cracked_hashes
                    display('+', "Done Comparing Hashes", start='\n')
                    display(':', f"\tTime Taken = {Back.MAGENTA}{t2-t1:.2f}{Back.RESET} seconds")
                    display(':', f"\tHashes Cracked from Current Batch = {Back.MAGENTA}{current_cracked_hashes}{Back.RESET}")
                    display(':', f"\tHashes Cracked from Current File  = {Back.MAGENTA}{current_file_cracked_hashes}{Back.RESET}")
                display(':', f"\tHashes Cracked from Current file = {Back.MAGENTA}{current_file_cracked_hashes}{Back.RESET}")
                display(':', f"Total Cracked Hashes = {Back.MAGENTA}{len(cracked_hashes)}{Back.RESET}")
                if len(cracked_hashes) == len(hashes):
                    display('+', f"Done Cracking all the Hashes!")
                    break
            continue
        except:
            display('-', f"Error while reading File {Back.YELLOW}{wordlist}{Back.RESET}")
            continue
        display('+', f"Words Loaded = {Back.MAGENTA}{len(words)}{Back.RESET}")
        display(':', f"Calculating Hashes...")
        t1 = time()
        current_hashes = HashingHandler(words, data.hashing_algorithm)
        t2 = time()
        hashes_calculated += len(words)
        display('+', "Done Calculating Hashes", start='\n')
        display(':', f"\tHashes Calculated = {Back.MAGENTA}{len(words)}{Back.RESET}")
        display(':', f"\tTime Taken = {Back.MAGENTA}{t2-t1:.2f} seconds{Back.RESET}")
        display(':', f"\tRate = {Back.MAGENTA}{len(words)/(t2-t1):.2f} hashes/second{Back.RESET}")
        display(':', f"Comparing Calculated Hashes...")
        current_cracked_hashes = 0
        t1 = time()
        for hash_index, hash in enumerate(hashes):
            if hash in current_hashes.keys():
                cracked_hashes[hash] = current_hashes[hash]
                current_cracked_hashes += 1
            display(':', f"Hashes Compared = {Back.MAGENTA}{hash_index+1}/{len(hashes)} ({(hash_index+1)/len(hashes)*100:.2f}%){Back.RESET}", start='\r', end='')
        t2 = time()
        display('+', "Done Comparing Hashes", start='\n')
        display(':', f"\tTime Taken = {Back.MAGENTA}{t2-t1:.2f}{Back.RESET} seconds")
        display(':', f"\tHashes Cracked from Current file = {Back.MAGENTA}{current_cracked_hashes}{Back.RESET}")
        display(':', f"Total Cracked Hashes = {Back.MAGENTA}{len(cracked_hashes)}{Back.RESET}")
        if len(cracked_hashes) == len(hashes):
            display('+', f"Done Cracking all the Hashes!")
            break
    print()
    print('\n'.join([f"{Fore.GREEN}{hash}{Fore.WHITE}:{Fore.BLUE}{word}{Fore.RESET}" for hash, word in cracked_hashes.items()]))
    display(':', f"Total Hashes Loaded = {Back.MAGENTA}{len(hashes)}{Back.RESET}", start='\n')
    display(':', f"Total Hashes Calculated = {Back.MAGENTA}{hashes_calculated}{Back.RESET}")
    display(':', f"Total Hashes Cracked = {Back.MAGENTA}{len(cracked_hashes)}{Back.RESET}")
    display(':', f"Success Rate = {Back.MAGENTA}{len(cracked_hashes)/len(hashes)*100:.2f}%{Back.RESET}")
    display(':', f"Dumping Cracked Hashes to File {Back.MAGENTA}{data.write}{Back.RESET}", start='\n')
    if data.save_type == "pickle":
        with open(data.write, 'wb') as file:
            pickle.dump(cracked_hashes, file)
    else:
        with open(data.write, 'w') as file:
            if data.save_type == "csv":
                file.write("Hash,Word\n"+'\n'.join([f"{hash},{word}" for hash, word in cracked_hashes.items()]))
            elif data.save_type == "json":
                json.dump(cracked_hashes, file)
            else:
                file.write('\n'.join([f"{hash}:{word}" for hash, word in cracked_hashes.items()]))
    display('+', f"Dumped Cracked Hashes to File {Back.MAGENTA}{data.write}{Back.RESET}")