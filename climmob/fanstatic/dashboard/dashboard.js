

function showAddProject(url)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = "Add new project";
    document.getElementById("modalmainbutton").innerHTML = "Add project";
    document.getElementById("modalmainbutton").style.cssText = "";
    $('#modal1').modal('show');
}

function showModifyProject(url)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = "Modify project";
    document.getElementById("modalmainbutton").innerHTML = "Modify project";
    document.getElementById("modalmainbutton").style.cssText = "";
    $('#modal1').modal('show');
}

function showDeleteProject(url)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = "Delete project";
    document.getElementById("modalmainbutton").style.cssText = "color: transparent; background-color: transparent; border: none;";
    $('#modal1').modal('show');
}

function showRegistry(url)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = "Prepare participant registration";
    document.getElementById("modalmainbutton").style.cssText = "color: transparent; background-color: transparent; border: none;";
    $('#modal1').modal('show');
}

function showAssessment(url)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = "Prepare data collection";
    document.getElementById("modalmainbutton").style.cssText = "color: transparent; background-color: transparent; border: none;";
    $('#modal1').modal('show');
}

function showTechnologies(url)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = "Select treatments";
    document.getElementById("modalmainbutton").style.cssText = "color: transparent; background-color: transparent; border: none;";
    $('#modal1').modal('show');
}

function showEnumerators(url)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = "Assign field agents";
    document.getElementById("modalmainbutton").style.cssText = "color: transparent; background-color: transparent; border: none;";
    $('#modal1').modal('show');
}

function showUpload(url)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = "Upload data";
    document.getElementById("modalmainbutton").style.cssText = "color: transparent; background-color: transparent; border: none;";
    $('#modal1').modal('show');
}

function showAnalysis(url)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = "Create Analysis";
    document.getElementById("modalmainbutton").style.cssText = "color: transparent; background-color: transparent; border: none;";
    $('#modal1').modal('show');
}

function showCombinations(url)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = "Combinations and packages";
    document.getElementById("modalmainbutton").style.cssText = "color: transparent; background-color: transparent; border: none;";
    $('#modal1').modal('show');
}

function showCancelRegistry(url)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = "Cancel the registration of participants";
    document.getElementById("modalmainbutton").style.cssText = "color: transparent; background-color: transparent; border: none;";
    $('#modal1').modal('show');
}

function showCloseRegistry(url)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = "Finish the registration of participants";
    document.getElementById("modalmainbutton").style.cssText = "color: transparent; background-color: transparent; border: none;";
    $('#modal1').modal('show');
}

function showStartAssessments(url)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = "Start the data collection";
    document.getElementById("modalmainbutton").style.cssText = "color: transparent; background-color: transparent; border: none;";
    $('#modal1').modal('show');
}

function closeModal() {

    var iframe = document.getElementById("modaliframe");

    iframe.contentWindow.location.href = 'about:blank';
    setTimeout(function(){
    $('#modal1').modal('hide');
    }, 1000);
}

function showCancelAssessments(url)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = "Cancel the data collection";
    document.getElementById("modalmainbutton").style.cssText = "color: transparent; background-color: transparent; border: none;";
    $('#modal1').modal('show');
}

function showCloseAssessment(url)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = "Close data collection";
    document.getElementById("modalmainbutton").style.cssText = "color: transparent; background-color: transparent; border: none;";
    $('#modal1').modal('show');
}

function showCancelAssessment(url)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = "Cancel data collection";
    document.getElementById("modalmainbutton").style.cssText = "color: transparent; background-color: transparent; border: none;";
    $('#modal1').modal('show');
}




jQuery(document).ready(function() {

    $('#modal1').on('hidden.bs.modal', function () {
        window.top.location.reload();
    });

    /*window.oncontextmenu = function() {
    return false;
    }

    $(window).on('keydown',function(event)
    {

        if(event.ctrlKey && event.shiftKey && event.keyCode==73)
        {
            //alert('Entered ctrl+shift+i')
            return false;  //Prevent from ctrl+shift+i
        }
     })*/


});