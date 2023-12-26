# Dictionary Attack
A Python program that loads words from a file, caculates their respective hashes according to the Hash Algorithm Provided and then compares with the feeded Hashes to implement a Dictionary Attack, hence attempting to crack the given hashes.

## Requirements
Language Used = Python3<br />
Modules/Packages used:
* hashlib
* pathlib
* datetime
* optparse
* colorama
* time
<!-- -->
Install the dependencies:
```bash
pip install -r requirements.txt
```

## Input
It takes the following command line arguments:
* '-l', "--load": List of Wordlists (seperated by ',')
* '-H', "--hash": Hashes/Hash Files to Load (seperated by ',')
* '-a', "--hashing-algorithm": Hashing Algorithm (md5,sha1,sha224,sha256,sha384,sha3_224,sha3_256,sha3_384,sha3_512,sha512)
* '-w', "--write": "Name of the File for the data to be dumped (default=current data and time)"
* '-t', "--save-type": File type to dump the data into (text, csv, json, pickle, Default=text)

### Note
For Large Wordlists, the program may give memory error as it may not be able to load all the passwords at once into the memory. To overcome this, we can use *split* command in linux to split the Wordlist into smaller files. <br />
For example: **-l** argument of *split* divided the file into small files each containing lines equal to the value provided in the **-l** argument (the last file would have lines equal to the total number of lines present in the initial wordlist modulus value provided in the **-l** argument)
```bash
split -l {lines} {name_of_the_file}
```