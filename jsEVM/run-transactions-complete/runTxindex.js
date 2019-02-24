
var Buffer = require('safe-buffer').Buffer // use for Node.js <4.5.0
var async = require('async')
var VM = require('./../index.js')
var Account = require('ethereumjs-account')
var Transaction = require('ethereumjs-tx')
var Trie = require('merkle-patricia-tree')
var rlp = require('rlp')
var utils = require('ethereumjs-util')
var argv = require('yargs').argv

// var code=argv.code
// var txdata=argv.txdata
// var value=argv.value
// console.log(code)
// console.log(txdata)
// console.log(value)


var stateTrie = new Trie()

// create a new VM instance
var vm = new VM({state: stateTrie})

var keyPair = require('./key-pair')

var createdAddress

var rawTx1 = require('./raw-tx1')


var rawTx2 = require('./raw-tx2')

// sets up the initial state and runs the callback when complete
function setup (cb) {
  // the address we are sending from
  var publicKeyBuf = Buffer.from(keyPair.publicKey, 'hex')
  var address = utils.pubToAddress(publicKeyBuf, true)

  // create a new account
  var account = new Account()

  // give the account some wei.
  //    Note: this needs to be a `Buffer` or a string. All
  //      strings need to be in hex.
  account.balance = '0xf00000000000000001'

  // store in the trie
  stateTrie.put(address, account.serialize(), cb)
}

function createContract(cb) {
    const rawDeployTransaction = {
        nonce: '0x00',
        gasPrice: '0x09184e72a001',
        gasLimit: '0xffffff',
        data: '0x'+code,
    }
    var tx = new Transaction(rawDeployTransaction)
    tx.sign(Buffer.from(keyPair.secretKey, 'hex'))
    vm.on('step', function (data) {
        // let hexStack = []
        // hexStack = data.stack.map(item => {
        //     return '0x' + new BN(item).toString(16, 0)
        // })

        var opTrace = {
            'pc': data.pc,
            'op': data.opcode.opcode,
            'gas': '0x' + data.gasLeft.toString('hex'),
            'gasCost': '0x' + data.opcode.fee.toString(16),
            // 'memory': '0x'+new BN(data.memory).toString(16),
            // 'memsize': e.memory.memsize,
            // 'stack': hexStack,
            'depth': data.depth,
            'opName': data.opcode.name
        }
        opTrace_json = JSON.stringify(opTrace)
        console.log(opTrace_json)
    })

    vm.runTx({
        tx: tx
    }, function (err, results) {
        createdAddress = results.createdAddress
        // log some results
        console.log('gas used: ' + '0x'+results.gasUsed.toString(16))
        console.log('returned: ' + results.vm.return.toString('hex'))
        if (createdAddress) {
            console.log('address created: ' +
                createdAddress.toString('hex'))
        }

        cb(err)
    })

}

function runTxdata(cb) {
    const rawCallFuncTransaction = {
        nonce: '0x01',
        gasPrice: '0x09184e72a000',
        gasLimit: '0x20710',
        to:'0x'+createdAddress.toString('hex'),
        // value: value,
        data: txdata,
    }
    var tx = new Transaction(rawCallFuncTransaction)
    tx.sign(Buffer.from(keyPair.secretKey, 'hex'))
    vm.on('step', function (data) {
        // let hexStack = []
        // hexStack = data.stack.map(item => {
        //     return '0x' + new BN(item).toString(16, 0)
        // })

        var opTrace = {
            'pc': data.pc,
            'op': data.opcode.opcode,
            'gas': '0x' + data.gasLeft.toString('hex'),
            'gasCost': '0x' + data.opcode.fee.toString(16),
            // 'memory': '0x'+new BN(data.memory).toString(16),
            // 'memsize': e.memory.memsize,
            // 'stack': hexStack,
            'depth': data.depth,
            'opName': data.opcode.name
        }
        opTrace_json = JSON.stringify(opTrace)
        // console.log(opTrace_json)
    })

    vm.runTx({
        tx: tx
    }, function (err, results) {
        createdAddress = results.createdAddress
        // log some results
        console.log('gas used: ' + '0x'+results.gasUsed.toString(16))
        console.log('returned: ' + results.vm.return.toString('hex'))
        if (createdAddress) {
            console.log('address created: ' +
                createdAddress.toString('hex'))
        }

        cb(err)
    })

}
// runs a transaction through the vm
function runTx (raw, cb) {
  // create a new transaction out of the json
  var tx = new Transaction(raw)


  // tx.from
  tx.sign(Buffer.from(keyPair.secretKey, 'hex'))

  console.log('----running tx-------')
  // run the tx \o/
  vm.on('step', function (data) {
    // let hexStack = []
    // hexStack = data.stack.map(item => {
    //     return '0x' + new BN(item).toString(16, 0)
    // })

    var opTrace = {
        'pc': data.pc,
        'op': data.opcode.opcode,
        'gas': '0x' + data.gasLeft.toString('hex'),
        'gasCost': '0x' + data.opcode.fee.toString(16),
        // 'memory': '0x'+new BN(data.memory).toString(16),
        // 'memsize': e.memory.memsize,
        // 'stack': hexStack,
        'depth': data.depth,
        'opName': data.opcode.name
    }
    opTrace_json = JSON.stringify(opTrace)
    console.log(opTrace_json)
})

  vm.runTx({
    tx: tx
  }, function (err, results) {
    createdAddress = results.createdAddress
    // log some results
    console.log('gas used: ' + '0x'+results.gasUsed.toString(16))
    console.log('returned: ' + results.vm.return.toString('hex'))
    if (createdAddress) {
      console.log('address created: ' +
          createdAddress.toString('hex'))
    }

    cb(err)
  })
}

var storageRoot // used later

// Now lets look at what we created. The transaction
// should have created a new account for the contranct
// in the trie.Lets test to see if it did.
function checkResults (cb) {
  // fetch the new account from the trie.
  stateTrie.get(createdAddress, function (err, val) {
    var account = new Account(val)

    storageRoot = account.stateRoot // used later! :)
    console.log('------results------')
    console.log('nonce: ' + account.nonce.toString('hex'))
    console.log('balance in wei: ' + account.balance.toString('hex'))
    console.log('stateRoot: ' + storageRoot.toString('hex'))
    console.log('codeHash:' + account.codeHash.toString('hex'))
    console.log('-------------------')
    cb(err)
  })
}


function readStorage (cb) {
  // we need to create a copy of the state root
  var storageTrie = stateTrie.copy()

  // Since we are using a copy we won't change the
  // root of `stateTrie`
  storageTrie.root = storageRoot

  var stream = storageTrie.createReadStream()

  console.log('------Storage------')

  // prints all of the keys and values in the storage trie
  stream.on('data', function (data) {
    // remove the 'hex' if you want to see the ascii values
    console.log('key: ' + data.key.toString('hex'))
    console.log('Value: ' + rlp.decode(data.value).toString())
  })

  stream.on('end', cb)
}


async.series([
  setup,
  // createContract,
  // runTxdata,
  async.apply(runTx, rawTx1),
  async.apply(runTx, rawTx2),
  // runTx(rawTx1),
  checkResults,
  readStorage
])


