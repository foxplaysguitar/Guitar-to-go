/* Crawl Sitemap - 放置index */  

    //宣告

    var arrSitemap = 'https://guitartogo-music.com/page-sitemap.xml';                           //Sitemap Index 網址放這
    

    //抓每一Sitemap的內容

    function checkSitemapUrls(arrSitemap){
        let urls = document.querySelectorAll('td a');
        let arrHrefs = [];                                  //紀錄網頁
        for(var i=0; i<urls.length; i++){
            arrHrefs.push(urls[i].innerText)
        }
        return arrHrefs
    }

    let urls = checkSitemapUrls(arrSitemap)

/* Main Function */

    var s1 = document.createElement('script');                      //引入 file-saver 模組
    var s2 = document.createElement('script');                      //引入 exceljs
    s1.src = "https://cdn.jsdelivr.net/npm/file-saver@2.0.5";
    s2.src = "https://unpkg.com/exceljs/dist/exceljs.min.js";
    document.querySelector('head').append(s1);
    document.querySelector('head').append(s2);

    async function crawlPages() {

        let problemUrl = []

        for (var i = 0; i < urls.length; i++) {
            var url = urls[i];
            await fetch(url).then(res => {
                if (/4.*/.test(res.status)) { //4XX Test

                } else if (/5.*/.test(res.status)) { //5XX Test

                } else if (/301/.test(res.status)) { //301 Test

                    return res.text();

                } else if (/302/.test(res.status)) { //301 Test

                    return res.text();
                } else {                             //200 Test

                    return res.text();
                }
            }).catch(() => {
                console.log('failed to fetch');
            }).then(html => {
                var parser = new DOMParser();
                var doc = parser.parseFromString(html, 'text/html');
            
                // What you want to do
                
                if (!doc.querySelector('link[data-will]')){
                    problemUrl.push(url);
                    console.log("找到問題網頁")
                }
                else {
                    console.log("網頁沒問題")
                }
            })
        }

        console.log(problemUrl.join('\n'))
    }

    crawlPages();
                

    //     /* 輸出 */

    //     //宣告

    //     var workbook = new ExcelJS.Workbook();
    //     var w1 = workbook.addWorksheet('A1');
    //     var w2 = workbook.addWorksheet('A2');

    //     //audit1
        
    //     w1.addRow(auditItem);
    //     var a1Keys = Object.keys(audit);
    //     for(var k=0; k<a1Keys.length; k++){
    //         w1.addRow([a1Keys[k]].concat(audit[a1Keys[k]]))
    //     }

    //     //audit2

    //     var a2Keys = Object.keys(audit2);
    //     for(var i=0; i<a2Keys.length; i++){
    //         w2.addRow([a2Keys[i]]);
    //         w2.addRow(['網頁','問題連結']);        
    //         var a2KeysInner = Object.keys(audit2[a2Keys[i]]);
    //         var a2ValuesInner = Object.values(audit2[a2Keys[i]]);
    //         for(var l = 0; l<a2KeysInner.length; l++){
    //             w2.addRow([a2KeysInner[l]].concat(a2ValuesInner[l]));
    //         }
    //         w2.addRow([])
    //     }

    //     //audit3

    //     var a3Keys = Object.keys(audit3);
    //     var a3Values = Object.values(audit3).map(v => v instanceof Set ? Array.from(v) : v);;
    //     for(var i=0; i<a3Keys.length; i++){
    //         w2.addRow([a3Keys[i]]);
    //         w2.addRow(a3Values[i]);
    //         w2.addRow([]);
    //     }

    //     //樣式設定

    //     w1.getRow(1).font = {name: '微軟正黑體' ,bold: true, size: 13};
    //     w1.views = [{
    //         state:'frozen',
    //         xSplit: 1,
    //         ySplit: 1,
    //     }]

    //     w1.getColumn('A').eachCell(cell => {
    //         if(/^https?:\/\//.test(cell)){
    //             cell.value = {
    //                 text: cell.value,
    //                 hyperlink: cell.value
    //             };
    //             cell.font = {
    //                 color: { argb: '3366ff'}
    //             }
    //         }

    //     })

    //     w2.getColumn('A').eachCell(cell => {
    //         if(/^https?:\/\//.test(cell)){
    //             cell.value = {
    //                 text: cell.value,
    //                 hyperlink: cell.value
    //             };
    //             cell.font = {
    //                 color: { argb: '3366ff'}
    //             }
    //         }

    //     })

    //     w1.columns[0].width = 60;
    //     w2.columns[0].width = 60;

    //     //存檔

    //     workbook.xlsx.writeBuffer().then(data => {
    //         var blob = new Blob([data],{ type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    //         var webName = window.location.origin.replace(/http(s)?:\/\/(.+\.)?(.+)\..*/,'$3');
    //         saveAs(blob,webName + ' seo-audit.xlsx')
    //     })

    // }
