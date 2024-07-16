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
