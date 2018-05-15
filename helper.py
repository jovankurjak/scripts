#!/usr/bin/python3

import re

# MMX grep constants
dict_startup = {
    'MMX_STARTUP': [r".startup>|Kernel Dumper information"]
}
dict_cpu_memory = {
    'MMX_LOW_MEM': [
        r"out-of-memory|crashed.*OutOfMemory|JavaCOMM detected|checkFreeMem:|low memory|memmonit_free_mem_lt"],
    'MMX_HIGH_CPU': [r"HB:.*CPU.(100|9[5-9])"]
}
dict_reset_shutdown = {
    'MMX_RESET': [
        r"SYSTEM RESET REQUESTED: RESET: reason|out-of-memory reset|requestSystemReset|SYSTEM.*RESET|RESET.*System|ErrorHandler.*reset|ooc.*(SHUTDOWN|FAST).*(FAST|SUTDOWN)|rebootSystem|watchdog.*reset"],
    'MMX_3FR_RESET': [r"Update upcoming RESET"]
}
dict_importaint_info = {
    'MMX_HW': [r"MMX BENCH_Startup PROJ"],
    'MMX_SW': [r"IMG_VER"],
    'MMX_RUNMODE': [r"RMG:STS.*Runmode"],
    'MMX_BOOT_NO': [r"BOOT CYCLE NUMBER"],
    'MMX_CLAMP_CHANGES': [r"ooc.*clamp state"]
}
dict_errors_status = {
    'MMX_ERROS': [
        r"error dump|Out of interrupt|can't.*mount|Check Failed|mmu fault|preempt|Created log file|free malloc object"],
    'MMX_CBC': [r"test_cbc:(timeout|.*test_cbc)|dumping context info"],
    'MMX_PCI': [r"PCI.*port|Unable to init.*devn"],
    'MMX_USB': [r"Firmware reinit"],
    'MMX_HMI': [r"slay.*j9|Unhandled exception|LOCATION of error|thread hanging|suicidei|j9heapdump.txt"],
    'MMX_DISPLAY_MANAGER': [r"MIB_DM_watchdog"],
    'MMX_RSTP': [r"RSTP Watchdog ERROR"],
    'MMX_SM_ERRORS': [r"SM blocked|executeOnReset|\[SM.*(send|mutex)"],
    'MMX_KERNEL': [r"QNX Version|Kernel dump start"],
    'MMX_POWER_MANAGEMENT': [r"OOC:AAP:WRN"],
    'MMX_CRASHES': [r"dumping to.*core|terminated SIG|corechecker.*Renamed"]
}
dict_performance = {
    'MMX_LASTMODE': [r"Last mode source|LastmodeApp|LastmodeAudio"]
}

dict_mmx = {
    'Startup': dict_startup,
    'CPU and memory': dict_cpu_memory,
    'Reset and Shutdown': dict_reset_shutdown,
    'Important Info': dict_importaint_info,
    'ERRORs and Status': dict_errors_status,
    'Performance': dict_performance
}


# A15 grep constants
dict_a = {
    'A15_STARTUP_COLD': [r"IPL\!"],
    'A15_STARTUP_WARM': [r"Process reboot"],
    'A15_CBC_PROBLEMS_PCI': [r"PCIe WD|block in.*carsensordata"],
    'A15_CBC_PROBLEMS_UART': [r"GPIO_PORT_UART1_RTS"],
    'A15_CRASH_EXCEPTION': [r"CATCH the SIGNAL|SIGSEGV|Exception occurred|Stored core file"]
}

dict_a15 = {
    'A15': dict_a
}

# M4 grep constants
dict_m4 = {
    'M4': {
        'A15_RESET_WD': [r"IPC WD.*REBOOT|Reset for Safe Shutdown|fast.*shutdown|WD Reset|WDInfo"]
    }
}

# SubCpu grep constants
dict_subcpu = {
    'SubCpu': {
        'SUBCPU_RESET': [r"Reset Src"]
    }
}

dict_all_grep_words = {
    'MMX': dict_mmx,
    'A15': dict_a15,
    'M4': dict_m4,
    'SubCpu': dict_subcpu
}
def parse_all_files(list_of_files):
    """parses all of the files

    Args:
        list of files (dict): list of log files in a form of dictionary key is associative name for each file

    Todo:
        * how to print/store/return the results
    """
    for key in list_of_files.keys():
        print('{0} file: {1}'.format(list_of_files[key], key))
        goThroughFile(list_of_files[key], dict_all_grep_words[key])


def goThroughFile(file, double_dict_regex_end):
    """Goes through file by groups

    Groups have a list of regex for them
    """

    for key in double_dict_regex_end:
        print('{0}-START'.format(key.__str__()))
        for second_key in double_dict_regex_end[key]:
            print(second_key + ':')
            parseFile(file, double_dict_regex_end[key][second_key])
        print('{0}-END'.format(key.__str__()))


def parseFile(file, list_of_regex):
    """Parse individual file with some regexes"""
    for regex in list_of_regex:
        with open(file, 'r', encoding='utf8', errors='ignore') as fp:
            for line_number, line in enumerate(iter(fp.readline, '')):
                line = line.rstrip()
                if re.search(regex, line) is not None:
                    print('[{0}]: {1}'.format(line_number.__str__(), line))
        print('-----------------------------------------------------------')


def parseMMX(mmx_file):
    goThroughFile(mmx_file, dict_mmx)