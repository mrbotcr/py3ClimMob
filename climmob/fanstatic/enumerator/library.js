function showAddEnumerator(url,windowTitle,buttonCaption)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = windowTitle;
    document.getElementById("modalmainbutton").innerHTML = buttonCaption;
    document.getElementById("modalmainbutton").style.cssText = "";
    $('#modal1').modal('show');
}

function showModifyEnumerator(url,windowTitle,buttonCaption)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = windowTitle;
    document.getElementById("modalmainbutton").innerHTML = buttonCaption;
    document.getElementById("modalmainbutton").style.cssText = "color: transparent; background-color: transparent; border: none;";
    $('#modal1').modal('show');
}

function showDeleteEnumerator(url,windowTitle,buttonCaption)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = windowTitle;
    document.getElementById("modalmainbutton").innerHTML = buttonCaption;
    document.getElementById("modalmainbutton").style.cssText = "";
    $('#modal1').modal('show');
}


function closeModal() {
    $('#modal1').modal('hide');
}

