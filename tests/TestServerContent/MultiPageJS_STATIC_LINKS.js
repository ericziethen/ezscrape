function gotoPage(num) {
    url = "MultiPageJS_STATIC_LINKS_" + num + ".html"
    console.log("SET URL: " + url)
    window.open(url, "_self")
}

function loadContent(num) {
    document.getElementById("content").innerHTML = "THIS IS PAGE " + num + "/3";
}


