
import random;
from datetime import datetime;

# Initial Permutation
INIT_PERM = [
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7,
    56, 48, 40, 32, 24, 16, 8, 0,
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6
]

# Intermediary Permutation
P_BOX = [
    15, 6, 19, 20, 28, 11, 27, 16,
    0, 14, 22, 25, 4, 17, 30, 9,
    1, 7, 23, 13, 31, 26, 2, 8,
    18, 12, 29, 5, 21, 10, 3, 24
]

# Final Permutation
FINAL_PERM = [
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25,
    32, 0, 40, 8, 48, 16, 56, 24
]

# Expansion Permutation
EXPAND = [
    31, 0, 1, 2, 3, 4,
    3, 4, 5, 6, 7, 8,
    7, 8, 9, 10, 11, 12,
    11, 12, 13, 14, 15, 16,
    15, 16, 17, 18, 19, 20,
    19, 20, 21, 22, 23, 24,
    23, 24, 25, 26, 27, 28,
    27, 28, 29, 30, 31, 0
]

# PC-1
PC1 = [
    56, 48, 40, 32, 24, 16, 8, 62, 54, 46, 38, 30, 22, 14,
    0, 57, 49, 41, 33, 25, 17, 6, 61, 53, 45, 37, 29, 21,
    9, 1, 58, 50, 42, 34, 26, 13, 5, 60, 52, 44, 36, 28,
    18, 10, 2, 59, 51, 43, 35, 20, 12, 4, 27, 19, 11, 3
]

# PC-2
PC2 = [
    13, 16, 10, 23, 0, 4,
    2, 27, 14, 5, 20, 9,
    22, 18, 11, 3, 25, 7,
    15, 6, 26, 19, 12, 1,
    40, 51, 30, 36, 46, 54,
    29, 39, 50, 44, 32, 47,
    43, 48, 38, 55, 33, 52,
    45, 41, 49, 35, 28, 31
]

# S-Boxes
S_BOX = [
    [
        14, 0, 4, 15, 13, 7, 1, 4, 2, 14, 15, 2, 11, 13, 8, 1,
        3, 10, 10, 6, 6, 12, 12, 11, 5, 9, 9, 5, 0, 3, 7, 8,
        4, 15, 1, 12, 14, 8, 8, 2, 13, 4, 6, 9, 2, 1, 11, 7,
        15, 5, 12, 11, 9, 3, 7, 14, 3, 10, 10, 0, 5, 6, 0, 13
    ],

    [
        15, 3, 1, 13, 8, 4, 14, 7, 6, 15, 11, 2, 3, 8, 4, 14,
        9, 12, 7, 0, 2, 1, 13, 10, 12, 6, 0, 9, 5, 11, 10, 5,
        0, 13, 14, 8, 7, 10, 11, 1, 10, 3, 4, 15, 13, 4, 1, 2,
        5, 11, 8, 6, 12, 7, 6, 12, 9, 0, 3, 5, 2, 14, 15, 9
    ],

    [
        10, 13, 0, 7, 9, 0, 14, 9, 6, 3, 3, 4, 15, 6, 5, 10,
        1, 2, 13, 8, 12, 5, 7, 14, 11, 12, 4, 11, 2, 15, 8, 1,
        13, 1, 6, 10, 4, 13, 9, 0, 8, 6, 15, 9, 3, 8, 0, 7,
        11, 4, 1, 15, 2, 14, 12, 3, 5, 11, 10, 5, 14, 2, 7, 12
    ],

    [
        7, 13, 13, 8, 14, 11, 3, 5, 0, 6, 6, 15, 9, 0, 10, 3,
        1, 4, 2, 7, 8, 2, 5, 12, 11, 1, 12, 10, 4, 14, 15, 9,
        10, 3, 6, 15, 9, 0, 0, 6, 12, 10, 11, 1, 7, 13, 13, 8,
        15, 9, 1, 4, 3, 5, 14, 11, 5, 12, 2, 7, 8, 2, 4, 14
    ],

    [
        2, 14, 12, 11, 4, 2, 1, 12, 7, 4, 10, 7, 11, 13, 6, 1,
        8, 5, 5, 0, 3, 15, 15, 10, 13, 3, 0, 9, 14, 8, 9, 6,
        4, 11, 2, 8, 1, 12, 11, 7, 10, 1, 13, 14, 7, 2, 8, 13,
        15, 6, 9, 15, 12, 0, 5, 9, 6, 10, 3, 4, 0, 5, 14, 3
    ],

    [
        12, 10, 1, 15, 10, 4, 15, 2, 9, 7, 2, 12, 6, 9, 8, 5,
        0, 6, 13, 1, 3, 13, 4, 14, 14, 0, 7, 11, 5, 3, 11, 8,
        9, 4, 14, 3, 15, 2, 5, 12, 2, 9, 8, 5, 12, 15, 3, 10,
        7, 11, 0, 14, 4, 1, 10, 7, 1, 6, 13, 0, 11, 8, 6, 13
    ],

    [
        4, 13, 11, 0, 2, 11, 14, 7, 15, 4, 0, 9, 8, 1, 13, 10,
        3, 14, 12, 3, 9, 5, 7, 12, 5, 2, 10, 15, 6, 8, 1, 6,
        1, 6, 4, 11, 11, 13, 13, 8, 12, 1, 3, 4, 7, 10, 14, 7,
        10, 9, 15, 5, 6, 0, 8, 15, 0, 14, 5, 2, 9, 3, 2, 12
    ],

    [
        13, 1, 2, 15, 8, 13, 4, 8, 6, 10, 15, 3, 11, 7, 1, 4,
        10, 12, 9, 5, 3, 6, 14, 11, 5, 0, 0, 14, 12, 9, 7, 2,
        7, 2, 11, 1, 4, 14, 1, 7, 9, 4, 12, 10, 14, 8, 2, 13,
        0, 15, 6, 12, 10, 9, 13, 0, 15, 3, 3, 5, 5, 6, 8, 11
    ],
]


# Pass input through scheduling table
def permute(inp, schedule):
    perm_msg = 0;
    for num, i in zip(schedule, range(len(schedule))):
        perm_msg = perm_msg | ((inp & 1 << num) >> num) << i;
    return perm_msg;


# Pass 48 bit inp through sboxes and return 32 bit output
def shrink(inp):
    shrink_msg = 0;
    for num, i in zip(range(0, 48, 6), range(0, 32, 4)):
        shrink_msg = shrink_msg | S_BOX[num//6][(inp & 0x3F << num) >> num] << i;
    return shrink_msg;


def DES(msg, key, enc):
    key56 = permute(key, PC1);
    perm_msg = permute(msg, INIT_PERM);

    # Rounds
    shift_value = 0;
    for i in range(16):
        # Cyclic shift based on round
        if (i == 0 or i == 1 or i == 8 or i == 15):
            shift_value += 1;
        else:
            shift_value += 2;
        # Split key into two halves
        shift_key_left = (key56 & 0xFFFFFFF0000000) >> 28;
        shift_key_right = key56 & 0x0000000FFFFFFF;
        if(enc):
            # Shift halves through round keys forward
            shift_key_left = ((shift_key_left << shift_value) | (shift_key_left >> 28-shift_value)) & 0xFFFFFFF;
            shift_key_right = ((shift_key_right << shift_value) | (shift_key_right >> 28-shift_value)) & 0xFFFFFFF;
        else:
            # Shift halves through round keys backwards
            shift_key_left = ((shift_key_left << (29-shift_value)) | (shift_key_left >> 28-(29-shift_value))) & 0xFFFFFFF;
            shift_key_right = ((shift_key_right << (29-shift_value)) | (shift_key_right >> 28-(29-shift_value))) & 0xFFFFFFF;
        # Combine halves
        shift_key = ((shift_key_left & 0x0000000FFFFFFF) << 28) | shift_key_right;
        # Pass shift_key through PC2 for round_key
        round_key = permute(shift_key, PC2);

        # Split msg into two halves
        lhalf = (perm_msg & 0xFFFFFFFF00000000) >> 32;
        rhalf = perm_msg & 0x00000000FFFFFFFF;

        # new_lhalf is old rhalf
        new_lhalf = rhalf << 32;

        # Expand new_rhalf
        new_rhalf = permute(rhalf, EXPAND);

        # XOR new_rhalf with round_key
        new_rhalf = new_rhalf ^ round_key;

        # Pass previous value through sboxes
        new_rhalf = shrink(new_rhalf);

        # Pass sbox results through pbox
        new_rhalf = permute(new_rhalf, P_BOX);

        # XOR lhalf with new_rhalf
        new_rhalf = new_rhalf ^ lhalf;

        # Combine new halves
        perm_msg = new_lhalf | new_rhalf;

    # Swap Halves
    new_lhalf = (perm_msg & 0x00000000FFFFFFFF) << 32;
    new_rhalf = (perm_msg & 0xFFFFFFFF00000000) >> 32;
    msg = new_lhalf | new_rhalf;
    return permute(msg, FINAL_PERM);


# Encrypts msg using 3DES
# Takes string of any length and 192 bit key
def encrypt(msg, key):
    # Split 192 bit key into 3 64 bit keys
    key1 = (key & 0xFFFFFFFFFFFFFFFF00000000000000000000000000000000) >> 128;
    key2 = (key & 0x0000000000000000FFFFFFFFFFFFFFFF0000000000000000) >> 64;
    key3 = (key & 0x00000000000000000000000000000000FFFFFFFFFFFFFFFF);
    # Pad msg to be multiple of 8 bytes
    for i in range(len(msg) % 8):
        msg = "\0" + msg;
    # Encrypt in 8 byte chunks
    encrypted = "";
    for i in range(0, len(msg), 8):
        substr = msg[i:i+8];
        # Convert characters to binary
        int64 = "";
        for c in substr:
            int64 += bin(ord(c))[2:].zfill(8);
        int64 = int(int64, 2);
        # E(D(E(msg, key1), key2), key3)
        int64 = DES(DES(DES(int64, key1, True), key2, False), key3, True);
        for j in range(56, -1, -8):
            # Convert binary to characters
            encrypted += chr((int64 & 0xFF << j) >> j);
    return encrypted;


# Decrypts msg using 3DES
# Takes string of any length and 192 bit key
def decrypt(msg, key):
    # Split 192 bit key into 3 64 bit keys
    key1 = (key & 0xFFFFFFFFFFFFFFFF00000000000000000000000000000000) >> 128;
    key2 = (key & 0x0000000000000000FFFFFFFFFFFFFFFF0000000000000000) >> 64;
    key3 = (key & 0x00000000000000000000000000000000FFFFFFFFFFFFFFFF);
    decrypted = "";
    for i in range(0, len(msg), 8):
        substr = msg[i:i+8];
        int64 = "";
        for c in substr:
            # Convert characters to binary
            int64 += bin(ord(c))[2:].zfill(8);
        int64 = int(int64, 2);
        # D(E(D(msg, key3), key2), key1)
        int64 = DES(DES(DES(int64, key3, False), key2, True), key1, False);
        for j in range(56, -1, -8):
            # Convert binary to characters
            decrypted += chr((int64 & 0xFF << j) >> j);
    # Return unpadded message
    return decrypted.replace("\0", "");


# For testing purposes
if __name__ == '__main__':
    key = 0x9474B8E8C73BCA7D;
    print(hex(key));
    for i in range(16):
        if ((i) % 2 == 0):
            key = DES(key, key, True);
        else:
            key = DES(key, key, False);
        print(hex(key));
    random.seed(datetime.now());
    x = input('Enter text to encrypt ("Exit" to quit): ');
    while(x != "Exit"):
        key = random.getrandbits(64);
        enc_msg = encrypt(x, int(key));
        dec_msg = decrypt(enc_msg, int(key));
        print("Encrypted text: " + enc_msg + "\nDecrypted Text: " + dec_msg);
        x = input('Next text ("Exit" to quit): ');
