function setUrl(pageNum, title, id) {
    var a = document.createElement('a');
    var linkText = document.createTextNode(title);
    a.appendChild(linkText);
    a.title = id;
    if(pageNum != null){
        url = "MultiPageJS_STATIC_LINKS_" + pageNum + ".html"
        a.href = url
        console.log("URL: " + url)
    }
    document.body.appendChild(a);
}

function loadContent(currentPage) {
    max_pages = 4
    document.getElementById("content").innerHTML = "THIS IS PAGE " + currentPage + "/" + max_pages;
    document.getElementById("content2").innerHTML = "LOADED-Javascript Line";

    if(currentPage <= 1) {
        setUrl(null, "prev", "prev")
    }
    else {
        setUrl(currentPage-1, "prev", "prev")
    }
    setUrl(1, "1", "page1");
    setUrl(2, "2", "page2");
    setUrl(3, "3", "page3");
    setUrl(4, "4", "page4");
    if(currentPage >= max_pages) {
        setUrl(null, "next", "next")
    }
    else {
        setUrl(currentPage+1, "next", "next")
    }
}


