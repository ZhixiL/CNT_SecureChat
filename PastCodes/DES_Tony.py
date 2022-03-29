# Tony Drouillard | TLD19B | 11/12/21 | "The program in this file is the individual work of Tony Drouillard.

import random;
from datetime import datetime;

# Initial Permutation
init_perm = [
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7,
    56, 48, 40, 32, 24, 16, 8, 0,
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6
]

# PC-2
pc2 = [
    13, 16, 10, 23, 0, 4,
    2, 27, 14, 5, 20, 9,
    22, 18, 11, 3, 25, 7,
    15, 6, 26, 19, 12, 1,
    40, 51, 30, 36, 46, 54,
    29, 39, 50, 44, 32, 47,
    43, 48, 38, 55, 33, 52,
    45, 41, 49, 35, 28, 31
]

# Expansion Permutation
expand = [
    31, 0, 1, 2, 3, 4,
    3, 4, 5, 6, 7, 8,
    7, 8, 9, 10, 11, 12,
    11, 12, 13, 14, 15, 16,
    15, 16, 17, 18, 19, 20,
    19, 20, 21, 22, 23, 24,
    23, 24, 25, 26, 27, 28,
    27, 28, 29, 30, 31, 0
]

# S-Box
s_box = [
    14, 0, 4, 15, 13, 7, 1, 4, 2, 14, 15, 2, 11, 13, 8, 1,
    3, 10, 10, 6, 6, 12, 12, 11, 5, 9, 9, 5, 0, 3, 7, 8,
    4, 15, 1, 12, 14, 8, 8, 2, 13, 4, 6, 9, 2, 1, 11, 7,
    15, 5, 12, 11, 9, 3, 7, 14, 3, 10, 10, 0, 5, 6, 0, 13
]

# Intermediary Permutation
inter_perm = [
    15, 6, 19, 20, 28, 11, 27, 16,
    0, 14, 22, 25, 4, 17, 30, 9,
    1, 7, 23, 13, 31, 26, 2, 8,
    18, 12, 29, 5, 21, 10, 3, 24
]

# Final Permutation
final_perm = [
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25,
    32, 0, 40, 8, 48, 16, 56, 24
]


def permute(inp, schedule):
    perm_msg = 0;
    for num, i in zip(schedule, range(len(schedule))):
        perm_msg = perm_msg | ((inp & 1 << num) >> num) << i;
    return perm_msg;


def shrink(inp, sBox):
    shrink_msg = 0;
    for num, i in zip(range(0, 48, 6), range(0, 32, 4)):
        shrink_msg = shrink_msg | sBox[(inp & 0x3F << num) >> num] << i;
    return shrink_msg;


def DES(msg, key, enc):

    perm_msg = permute(msg, init_perm);

    # Rounds
    for i in range(16):

        # Cyclic shift
        if(enc):
            shift_key = ((key << (i+1)) | (key >> 56-(i+1))) & 0xFFFFFFFFFFFFFF;
        else:
            shift_key = ((key << (16-i)) | (key >> 56-(16-i))) & 0xFFFFFFFFFFFFFF;

        round_key = permute(shift_key, pc2);

        # Split msg into two halves
        lhalf = (perm_msg & 0xFFFFFFFF00000000) >> 32;
        rhalf = perm_msg & 0x00000000FFFFFFFF;

        new_lhalf = rhalf << 32;

        new_rhalf = permute(rhalf, expand);

        # XOR new_rhalf with round_key
        new_rhalf = new_rhalf ^ round_key;

        rhalf = new_rhalf;
        new_rhalf = shrink(rhalf, s_box);

        rhalf = new_rhalf;
        new_rhalf = permute(rhalf, inter_perm);

        # XOR lhalf with new_rhalf
        new_rhalf = new_rhalf ^ lhalf;

        perm_msg = new_lhalf | new_rhalf;

    # Swap Halves
    new_lhalf = (perm_msg & 0x00000000FFFFFFFF) << 32;
    new_rhalf = (perm_msg & 0xFFFFFFFF00000000) >> 32;
    msg = new_lhalf | new_rhalf;

    perm_msg = permute(msg, final_perm);

    return perm_msg;


def encrypt(msg, key):

    # Padding
    for i in range(len(msg) % 8):
        msg = "\0" + msg;

    encrypted = "";
    for i in range(0, len(msg), 8):
        substr = msg[i:i+8];
        int64 = "";
        for c in substr:
            int64 += bin(ord(c))[2:].zfill(8);
        int64 = DES(int(int64, 2), key, True);
        for j in range(56, -1, -8):
            encrypted += chr((int64 & 0xFF << j) >> j);

    return encrypted;


def decrypt(msg, key):

    decrypted = "";
    for i in range(0, len(msg), 8):
        substr = msg[i:i+8];
        int64 = "";
        for c in substr:
            int64 += bin(ord(c))[2:].zfill(8);
        int64 = DES(int(int64, 2), key, False);
        for j in range(56, -1, -8):
            decrypted += chr((int64 & 0xFF << j) >> j);

    return decrypted.replace("\0", "");


if __name__ == '__main__':
    random.seed(datetime.now());
    x = input('Enter text to encrypt ("Exit" to quit): ');
    while(x != "Exit"):
        key = random.getrandbits(56);
        enc_msg = encrypt(x, key);
        dec_msg = decrypt(enc_msg, key);
        print("Encrypted text: " + enc_msg + "\nDecrypted Text: " + dec_msg);
        x = input('Next text ("Exit" to quit): ');
