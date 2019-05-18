#!/usr/bin/env node
const ethUtil = require('ethereumjs-util')
const BN = ethUtil.BN

var Buffer = require('safe-buffer').Buffer // use for Node.js <4.5.0
var VM = require('./index.js')
var argv = require('yargs').argv

var code=''
code=argv.code

var sig=argv.sig


// create a new VM instance
var vm = new VM()

vm.on('step', function (e) {
    let hexStack = []
    hexStack = e.stack.map(item => {
        return '0x' + new BN(item).toString(16, 0)
    })

    var opTrace = {
        'pc': e.pc,
        'op': e.opcode.opcode,
        'gas': '0x' + e.gasLeft.toString('hex'),
        'gasCost': '0x' + e.opcode.fee.toString(16),
        // 'memory': '0x'+new BN(e.memory).toString(16),
        // 'memsize': e.memory.memsize,
        'stack': hexStack,
        'depth': e.depth,
        'opName': e.opcode.name
    }
    // console.log(opTrace)
    opTrace_json = JSON.stringify(opTrace)
    console.log(opTrace_json)
})

if(sig==undefined){
    vm.runCode({
        code: Buffer.from(code, 'hex'),
        gasLimit: Buffer.from('ffffffff', 'hex'),

        // value:new BN(1),
    }, function (err, results) {
        var ret = {
            'output':results.return.toString('hex'),
            'gasUsed':'0x'+results.gasUsed.toString('hex')
        }
        ret_json = JSON.stringify(ret)
        console.log(ret_json)
    })

}

else{
    sig=sig.toString(16)
    sig=sig.toString('hex')
    if(sig.charAt(0)== "0" && sig.charAt(1)== "x"){
        sig=sig.slice(2)
    }

    // sig=new Buffer(sig,"utf-8").toString();

    vm.runCode({
        code: Buffer.from(code, 'hex'),
        gasLimit: Buffer.from('ffffffff', 'hex'),
        data:Buffer.from(sig, 'hex'),
        // value:new BN(1),
    }, function (err, results) {
        var ret = {
            'output':results.return.toString('hex'),
            'gasUsed':'0x'+results.gasUsed.toString('hex')
        }
        ret_json = JSON.stringify(ret)
        console.log(ret_json)

    })
}
