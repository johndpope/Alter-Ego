const { 
    series, parallel, watch,
    src, dest} = require('gulp')
const settings = require('./project-settings.json')
const ftp = require('vinyl-ftp')
const merge = require('merge-stream')
const {argv} = require('yargs')

// Used to redirect tasks based on additional arguments, two input or output pi or both

function targetPiByArgs(task, cb){
    const hasArguments = Object.keys(argv).length > 2
    if (hasArguments){
        if (argv.in){
            if (cb == undefined){
                return task('input-pi')
            } else {
                task('input-pi', cb)
            }
        } else if (argv.out){
            if (cb == undefined){
                return task('output-pi')
            } else {
                task('output-pi', cb)
            } 
        }
    } else {
        if (cb == undefined){
            return merge(task('input-pi'), task('output-pi'))
        } else {
            task('input-pi', cb)
            task('output-pi', cb)
        }
    }
}

// Tasks by Target

function connectToPi(target){
    const conn = ftp.create({
        host:     settings[target].ip,
        user:     settings[target].user,
        password: settings[target].password
    })
    return conn
}

function initPi(target){
    console.log("Initializing: ", target)
    const conn = connectToPi(target)
    return src("./virtual/" + target + "/**")
    .pipe(conn.dest("/home/pi"))
}

function cleanPi(target, cb){
    console.log("Cleaning: ", target)
    const conn = connectToPi(target)
    const targetDirectories = target == "output-pi" ? ["MyScripts", "MyPics", "MyVids"] : ["MyScripts", "MyPics"]
    for (const dir of targetDirectories){
        conn.rmdir("/home/pi/" + dir, cb)
    }
    cb()
}

function deployToPi(target){
    console.log("Deploying: ", target)
    return copyScriptsToPi(target)
}

function copyScriptsToPi(target){
    const conn = connectToPi(target)
    const globs = ['./virtual/' + target + '/MyScripts/**', './modules/util/*', 'project-settings.json', './virtual/*.py']
    return src(globs)
        .pipe(conn.newer('/home/pi/MyScripts/'))
        .pipe(conn.dest('/home/pi/MyScripts/'))
}

function test(pi, cb){
    console.log(pi)
    cb()
}

// Final Tasks

function testTask(cb){
    console.log("This is a test output for Gulp. Everything seems to work fine!")
    targetPiByArgs(test, cb)
}

function watchScripts(){
    watch(["./virtual/**/*.py", "./project-settings.json", "./modules/util/*"], series(deployTask, watchScripts))
}

function deployTask(){
    return targetPiByArgs(deployToPi)
}

function initTask(){
    return targetPiByArgs(initPi)
}

function cleanTask(cb){
    targetPiByArgs(cleanPi, cb)
}

exports.test = testTask
exports.watch = watchScripts
exports.deploy = deployTask
exports.init = initTask
exports.clean = cleanTask

exports.default = series(cleanTask, initTask, deployTask, watchScripts)