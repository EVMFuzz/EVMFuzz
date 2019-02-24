EVMFuzz
======

*An Detection Tool for Ethereum Virtual Machine (EVM).*

## Folder Structure

**Dependency Libraries：**

\> `Py-EVM`  Source code of EVM written in Python.

\> `aleth`  Source code of EVM written in CPP.

\> `jsEVM`  Source code of EVM written in JavaScript.

\> `geth`  Source code of EVM written in Golang.

**Code Folders：**

\> `example`  Some examples.

\> `mutate`  Script files for contract mutation.

**Executable scripts：**

\> `EVMFuzz-Run` 



## Quick Start

To start the work, install all dependent libraries and platforms.

Guidance can be found in the following repositories:

[py-evm](https://github.com/pipermerriam/py-evm)   [aleth](https://github.com/ethereum/aleth)   [js-evm](https://github.com/ethereumjs/ethereumjs-vm)   [geth](https://github.com/ethereum/go-ethereum)

Execute a python virtualenv 

```
python -m virtualenv env
source env/bin/activate
```

The runtime environment is python3, and just run:

```
$ python3 EVMFuzz-Run.py
```

You are done! 
