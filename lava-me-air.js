/* video lazyload */

function videoLazyload() {
    let videos = document.querySelectorAll('video');
    let videoSources = document.querySelectorAll('video source');
    let videoSrc;

    // 判定 D 版還 M 版
    if (screen.width > 575) videoSrc = 'src';
    else videoSrc = 'mSrc';

    if(videoSources){
        for(var i=0; i<videoSources.length; i++){
            videoSources[i].setAttribute('src', videoSources[i].dataset[videoSrc]);
            videos[i].load();
            console.log('Src loading Success.')
        }
    }
}

videoLazyload();

function gridImgTrigger(color){
    console.log('Start Grid Trigger')
    // let sec = document.querySelector('.section-6')
    // let grids = sec.querySelectorAll('.grid-trigger img');
    // document.querySelector('.tab-title.active').classList.remove('active');
    // this.classList.add('active');

    gridSilver = document.querySelectorAll('.grid-silver');
    gridDark = document.querySelectorAll('.grid-dark');

    if(color == 'silver'){
        for(var i=0; i<gridSilver.length; i++){
            gridSilver[i].classList.remove('show');
            gridSilver[i].classList.add('show');
            gridDark[i].classList.remove('show')
        }
    }
    else {
        for(var i=0; i<gridSilver.length; i++){
            gridDark[i].classList.remove('show');
            gridDark[i].classList.add('show');
            gridSilver[i].classList.remove('show')
        }
    }
}

function playEffect(effectNum){
    let tabSel = document.querySelectorAll('.section-11 .tab-box > div')[effectNum];
    let appSel = document.querySelectorAll('.section-11 .app-btn > div')[effectNum];
    let audioSel = document.querySelectorAll('.section-11 .app-btn audio')[effectNum];
    
    //點到正在播放的
    if(tabSel.classList.contains('selected')){
        tabSel.classList.remove('selected');
        appSel.classList.remove('selected');
        audioSel.classList.remove('selected');
        audioSel.pause();
        console.log('Selected Being Removed.')
    }

    //沒點到正在播放的
    else {
        //已有其他在播放
        if(document.querySelector('.section-11 .selected')){
            document.querySelector('.tab-box div.selected').classList.remove('selected');
            document.querySelector('.app-btn div.selected').classList.remove('selected');
            document.querySelector('.app-btn audio.selected').pause()
            document.querySelector('.app-btn audio.selected').classList.remove('selected');
        }
        tabSel.classList.add('selected');
        appSel.classList.add('selected');
        audioSel.classList.add('selected');
        audioSel.play()
        console.log('Selected is changed.');
    }
}

let tabSels = document.querySelectorAll('.section-11 .tab-box > div');
let appSels = document.querySelectorAll('.section-11 .app-btn > div');
for(var i=0; i<tabSels.length; i++){
    tabSels[i].setAttribute('onclick', `playEffect(${i})`);
    appSels[i].setAttribute('onclick', `playEffect(${i})`);
}
