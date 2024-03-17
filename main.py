import requests
import threading
import math
import time
import sys


def get_word_list(wordlist_file_path):
    """
    This function will extract the word list from the file and then store it in an array
    :param wordlist_file_path: the path to the wordlist file
    :return: an array containing all the words in the file
    """
    word_list = []
    with open(wordlist_file_path, 'r', encoding='utf') as file:
        print(f"Collecting words from {wordlist_file_path} ...")
        for line in file:
            word_list.append(line.strip())
    return word_list


def get_thread_numbers(word_list_number, thread_max_word_number):
    """
    This function is used to get the necessary number of threads to use
    :param word_list_number: the number of word in the wordlist
    :param thread_max_word_number: the maximum number of words to check in a thread
    :return: the required number of threads
    """
    return math.ceil(word_list_number / int(thread_max_word_number))


def chunks(word_list, n):
    """
    This function will split the long word list into smaller chunks
    :param word_list: the list of all words
    :param n: the next index to split the list
    :return: a smaller chunk list of the words
    """
    for i in range(0, len(word_list), n):
        yield word_list[i:i + n]


def check_path(word_list, website_url):
    """
    In this function, we're going to check the available paths for the website
    :param word_list: the list of the words to check
    :param website_url: the url of the targeted website
    :return: a list of existing paths and their state according to the state_dict dictionary
    """
    existing_paths = []
    for word in word_list:
        to_check = website_url + word
        response = requests.get(to_check)
        status_code = response.status_code
        if status_code != 404:
            existing_paths.append((to_check, f"Status Code: {status_code}"))
    return existing_paths


def thread_function(word_list, website_url, result_list, lock):
    """
    This function defines the function to be executed by each threads
    :param word_list: list of all words to check
    :param website_url: the target website url
    :param result_list: the list which will contains the existing paths
    :param lock: a lock which will be used to acquire a lock
    """
    with lock:
        result_list.extend(check_path(word_list, website_url))


def process_in_mutli_threads(wordlist_file_path, website_url, thread_max_word_number):
    """
    Here we are going to process the program to check available paths for the given website using multiple threads
    :param thread_max_word_number: the maximum number of words to check in a thread
    :param wordlist_file_path: path to the file containing the word list
    :param website_url: the target website
    :return: Show the list of available paths according to their states
    """
    start_time = time.time()
    word_list = get_word_list(wordlist_file_path)
    thread_numbers = get_thread_numbers(len(word_list), thread_max_word_number)
    chunk_list = list(chunks(word_list, thread_numbers))
    threads = []
    result_list = []
    lock = threading.Lock()
    print("Thread numbers: ", thread_numbers)
    print("Check in progress...")
    for chunk in chunk_list:
        thread = threading.Thread(target=thread_function, args=(chunk, website_url, result_list, lock))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for url, status_code in result_list:
        print(f"URL: {url}, {status_code}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    # This will show how long the program took to run
    print("Elapsed: {} seconds".format(elapsed_time))


def process_in_single_thread(wordlist_file_path, website_url):
    """
    Here we are going to process the program to check available paths for the given website in a single thread
    :param wordlist_file_path: path to the file containing the word list
    :param website_url: the target website
    :return: Show the list of available paths according to their states
    """
    start_time = time.time()
    word_list = get_word_list(wordlist_file_path)
    result_list = check_path(word_list, website_url)
    for url, status_code in result_list:
        print(f"URL: {url}, {status_code}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    # This will show how long the program took to run
    print("Elapsed: {} seconds".format(elapsed_time))


if __name__ == '__main__':
    """
    Main function of the program
    """

    use_mono_thread = input("Run the program in a mono thread? (y/n): ")

    if use_mono_thread == "n":
        file_path = input("Enter the path to the file containing the word list: ")
        website = input("Enter the target website: ")
        max_word_number_per_thread = input("Enter the maximum number of words per thread: ")
        process_in_mutli_threads(file_path, website, max_word_number_per_thread)
    elif use_mono_thread == "y":
        file_path = input("Enter the path to the file containing the word list: ")
        website = input("Enter the target website: ")
        process_in_single_thread(file_path, website)
    else:
        print("Invalid input.")
        sys.exit(1)
