#!/usr/bin/env node

var jsonDiff = require('json-diff')
var argv = require('yargs').argv
var rf=require("fs")
var wf=require("fs")

var js_file=argv.js_file
var py_file=argv.py_file
var cpp_file=argv.cpp_file
var resfile=argv.resfile
var ret_dir=argv.ret_dir
var txdata=argv.txdata
// console.log(txdata)
// console.log(txdata.toString(16))



// var difffile=ret_dir+'/'+'diff.log'
var difffile=ret_dir
var opcodeDiff=0
var gasusedDiff=0
var totalDiff=0

var js_file_data=rf.readFileSync(js_file,"utf-8")
var cpp_file_data=rf.readFileSync(cpp_file,"utf-8")
var py_file_data=rf.readFileSync(py_file,"utf-8")

var js_py_conflict=""
var py_cpp_conflict=""
var js_cpp_conflict=""

js_file_data=js_file_data.split('\n')
// console.log(js_file_data.length)
cpp_file_data=cpp_file_data.split('\n')
// console.log(cpp_file_data.length)
py_file_data=py_file_data.split('\n')
// console.log(py_file_data.length)

opcodeDiff=Math.abs(js_file_data.length-cpp_file_data.length)+
    Math.abs(js_file_data.length-py_file_data.length)+
    Math.abs(py_file_data.length-cpp_file_data.length)
// console.log(opcodeDiff)

var js_json =JSON.parse(js_file_data[js_file_data.length-2])
js_gas=js_json.gasUsed
js_output=js_json.output

var py_json =JSON.parse(py_file_data[py_file_data.length-2])
py_gas=py_json.gasUsed
py_output=py_json.output

var cpp_json =JSON.parse(cpp_file_data[cpp_file_data.length-2])
cpp_gas=cpp_json.gasUsed
cpp_output=cpp_json.output

gasusedDiff=Math.abs(js_gas-py_gas)+
    Math.abs(cpp_gas-py_gas)+
    Math.abs(js_gas-cpp_gas)
// console.log(gasusedDiff)
totalDiff=gasusedDiff+opcodeDiff
// const diff_file_data = rf.readFileSync(difffile, 'utf-8')
// var oldDiff = diff_file_data.trim()
// oldDiff=oldDiff*1
totalDiff=totalDiff*1
// totalDiff+=oldDiff

wf.writeFileSync(difffile,totalDiff+"\n")


if(js_output!=py_output ||js_gas!= py_gas ){
    error='js&py_'
    if(js_output!=py_output && js_gas!= py_gas ){
        error+='output+gas'
    }
    else if(js_output!=py_output && js_gas== py_gas){
        error+='output'
    }
    else if(js_gas!= py_gas && js_output==py_output){
        error+='gas'
    }
    var ret={
        'error':error,
        'js_output':js_output,
        'py_output':py_output,
        'js_gasUsed':js_gas,
        'py_gasUsed':py_gas,
        'txdata':txdata.toString(16),


    }

    wf.appendFileSync(resfile,JSON.stringify(ret)+" \n")
}

if(js_output!=cpp_output || js_gas!= cpp_gas){
    error='js&cpp_'
    if(js_output!=cpp_output && js_gas!= cpp_gas ){
        error+='output+gas'
    }
    else if(js_output!=cpp_output && js_gas == cpp_gas){
        error+='output'
    }
    else if(js_gas!= cpp_gas &&  js_output== cpp_output){
        error+='gas'
    }

    var ret={
        'error':error,
        'js_output':js_output,
        'cpp_output':cpp_output,
        'js_gasUsed':js_gas,
        'cpp_gasUsed':cpp_gas,
        'txdata':txdata.toString(16),


    }

    wf.appendFileSync(resfile,JSON.stringify(ret)+" \n")
}
if(cpp_output!=py_output || cpp_gas!= py_gas){
    error='cpp&py_'
    if(cpp_output!=py_output && cpp_gas!= py_gas ){
        error+='output+gas'
    }
    else if(py_output!=cpp_output && cpp_gas== py_gas ){
        error+='output'
    }
    else if(py_gas!= cpp_gas && py_output==cpp_output ){
        error+='gas'
    }

    var ret={
        'error':error,
        'cpp_output':cpp_output,
        'py_output':py_output,
        'cpp_gasUsed':cpp_gas,
        'py_gasUsed':py_gas,
        'txdata':txdata.toString(16),


    }

    wf.appendFileSync(resfile,JSON.stringify(ret)+" \n")
}


// js_geth_cmp(js_file_data,geth_file_data)
// js_py_cmp(js_file_data,py_file_data)
// geth_py_cmp(geth_file_data,py_file_data)

function js_geth_cmp(js_file_data,geth_file_data){
    if(js_file_data.length!=geth_file_data.length){
        wf.appendFileSync(resfile1,"file length inconsistent! \n");
        js_geth_conflict+="file length inconsistent! \n"

    }
    else{
        var len=js_file_data.length<=geth_file_data.length?js_file_data.length: geth_file_data
        for(i=0;i<len-2;i++){
            var js_json =JSON.parse(js_file_data[i])
            var geth_json =JSON.parse(geth_file_data[i])

            js_json.depth+=1
            delete js_json.gas
            delete js_json.stack

            delete geth_json.memory
            delete geth_json.memSize
            delete geth_json.error
            delete geth_json.gas
            delete geth_json.stack

            var cmp=jsonDiff.diff(js_json,geth_json)
            if(cmp !=undefined){
                var temp=(i+1)+' '+JSON.stringify(cmp)+' '
                var keys= Object.keys(cmp)
                console.log(keys)
                for(j=0;j<keys.length;j++){
                    key=keys[j]
                    if(key=="gasCost"){
                        temp+=" opName: "+js_json.opName
                    }
                    else{
                        temp+=" js: "+js_json[key]+" geth: "+geth_json[key]
                    }

                }
                temp+='\n'
                wf.appendFileSync(resfile1,temp);
                js_geth_conflict+=temp
            }
            else{
                // console.log(i+1)
                wf.appendFileSync(resfile1,(i+1)+' \n');
            }

        }
        // i=js_file_data.length-2
        var js_json =JSON.parse(js_file_data[i])
        var geth_json =JSON.parse(geth_file_data[i])


        delete geth_json.time

        cmp=jsonDiff.diff(js_json,geth_json)
        if(cmp!=undefined){
            var keys= Object.keys(cmp)
            for(j=0;j<keys.length;j++){
                key=keys[j]
                if(key=="gasUsed"){
                    temp=(i+1)+" js gasUsed: "+js_json[key]+" geth gasUsed: "+geth_json[key]+'\n'
                }


            }
            wf.appendFileSync(resfile1,temp);
            js_geth_conflict+=temp
        }
        else{
            wf.appendFileSync(resfile1,(i+1))
        }

    }


    wf.appendFileSync(totalresfile,"js_geth_conflict\n "+js_geth_conflict.toString());




}

function js_py_cmp(js_file_data,py_file_data) {
    if(js_file_data.length!=py_file_data.length){
        wf.appendFileSync(ret_file,"file length inconsistent! \n");
        js_py_conflict+="file length inconsistent! \n"

    }
    else {
        var len = js_file_data.length <= py_file_data.length ? js_file_data.length : py_file_data
        for(i=0;i<len-2;i++){
            var js_json =JSON.parse(js_file_data[i])
            var py_json =JSON.parse(py_file_data[i])

            delete py_json.gas
            delete py_json.error
            delete py_json.stack


            delete js_json.gas
            delete js_json.stack

            var cmp=jsonDiff.diff(js_json,py_json)
            if(cmp !=undefined){
                var temp=(i+1)+' '+JSON.stringify(cmp)+' '
                var keys= Object.keys(cmp)
                console.log(keys)
                for(j=0;j<keys.length;j++){
                    key=keys[j]
                    if(key=="gasCost"){
                        temp+=" opName: "+js_json.opName
                    }
                    else{
                        temp+=" js: "+js_json[key]+" python: "+py_json[key]
                    }

                }
                temp+='\n'
                wf.appendFileSync(ret_file,temp);
                js_py_conflict+=temp
            }
            else{
                // console.log(i+1)
                wf.appendFileSync(ret_file,(i+1)+' \n');
            }
        }
        // i=js_file_data.length-2
        var js_json =JSON.parse(js_file_data[i])
        // var py_json =JSON.parse(py_file_data[i])
        var js_gasused=js_json.gasUsed
        // var le=js_gasused.length-1
        var py_gasused=py_file_data[i].split(',')[py_file_data[i].split(',').length-1].split(':')[1].split('}')[0].split("\"")[1]
        if(js_gasused!=py_gasused){
            wf.appendFileSync(ret_file,(i+1)+" js gasUsed: "+js_gasused+" py gasUsed: "+py_gasused+'\n')
            js_py_conflict+=(i+1)+" js gasUsed: "+js_gasused+" py gasUsed: "+py_gasused+'\n'
        }



    }


    wf.appendFileSync(ret_file,"js_py_conflict\n "+js_py_conflict.toString());

}

function geth_py_cmp(geth_file_data,py_file_data) {
    if(geth_file_data.length!=py_file_data.length){
        wf.appendFileSync(resfile2,"file length inconsistent! \n");
        py_geth_conflict+="file length inconsistent! \n"

    }
    else{
        var len = geth_file_data.length <= py_file_data.length ? geth_file_data.length : py_file_data
        for (i = 0; i < len - 2; i++) {
            var geth_json = JSON.parse(geth_file_data[i])
            var py_json = JSON.parse(py_file_data[i])
            py_json.depth += 1
            delete py_json.gas
            delete py_json.error
            delete py_json.stack

            delete geth_json.memory
            delete geth_json.memSize
            delete geth_json.error
            delete geth_json.gas
            delete geth_json.stack

            var cmp = jsonDiff.diff(py_json,geth_json)
            if (cmp != undefined) {
                var temp = (i + 1) + ' ' + JSON.stringify(cmp) + ' '
                var keys = Object.keys(cmp)
                console.log(keys)
                for (j = 0; j < keys.length; j++) {
                    key = keys[j]
                    if (key == "gasCost") {
                        temp += " opName: " + py_json.opName
                    }
                    else {
                        temp += " geth: " + geth_json[key] + " python: " + py_json[key]
                    }

                }
                temp += '\n'
                wf.appendFileSync(resfile2, temp);
                py_geth_conflict+=temp
            }
            else {
                // console.log(i+1)
                wf.appendFileSync(resfile2, (i + 1) + ' \n');
            }

        }
        var geth_json = JSON.parse(geth_file_data[i])
        // var py_json = JSON.parse(py_file_data[i])
        var geth_gasused=geth_json.gasUsed
        var py_gasused=py_file_data[i].split(',')[py_file_data[i].split(',').length-1].split(':')[1].split('}')[0].split("\"")[1]

        if(geth_gasused!=py_gasused){
            wf.appendFileSync(resfile2,(i+1)+" py gasUsed: "+py_gasused+" geth gasUsed: "+geth_gasused+'\n')
            py_geth_conflict+=(i+1)+" py gasUsed: "+py_gasused+" geth gasUsed: "+geth_gasused+'\n'
        }


    }


    wf.appendFileSync(totalresfile,"py_geth_conflict\n "+py_geth_conflict.toString());


}






