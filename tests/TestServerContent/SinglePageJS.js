function loadContent(waitMs) {
    var a = document.createElement('p');
    var linkText = document.createTextNode("Waited " + waitMs + "ms for page to load");
    a.id = 'wait-text'
    a.appendChild(linkText);
    document.body.appendChild(a);

    if(waitMs != null){
        sleep(waitMs)
    }
    document.getElementById("content").innerHTML = "LOADED-Javascript Line";
}

function sleep(milliseconds) {

    var start = new Date().getTime();
    for (var i = 0; i < 1e7; i++) {
        if ((new Date().getTime() - start) > milliseconds){
            break;
        }
    }
}