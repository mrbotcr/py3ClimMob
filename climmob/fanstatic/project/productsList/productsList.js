
var call_refresh = true;

jQuery(document).ready(function()
{

    /*setInterval(function(){
        if (call_refresh) {
            //console.log("Calling...");
            call_refresh = false;
            refresh();
        }
        // else
        //     console.log("Not Calling");
    }, 20000);*/



    //alert("llega")

    /*$(".btn_datadesk").click(function()
    {
        object = $(this)
        idcomplet = $(this).attr("id").split("$#%%#$")
        id = idcomplet[0]
		$.post("/downloadJson/"+id,{'csrf_token': $('#csrf_token').val()}, function(result){

		    var dictstring = JSON.stringify(result);
		    file = new Blob([dictstring], {type: "application/json"});
		    filename = idcomplet[1]
		    if(file.size > 1024*1024)
		    {
			    alert('Please choose files smaller than 1mb, otherwise you may crash your browser. \nThis is a known issue. See the tutorial.');
			    return;
		    }
		    else
		    {

		        //alert("Siga")
		        encryptar(object,file, filename)
		        //alert("sale")
		    }

		});

    })*/

    array = [];
    $('.btn_datadesk').each(function()
    {
        array.push($(this))
    });

    procedimientoRecursivo(0, array.length-1)
})

function procedimientoRecursivo(posicion, maximo)
{
    if (posicion <= maximo)
    {
        //alert("va el "+posicion)
        object = array[posicion];
        idcomplet = object.attr("id").split("$#%%#$");
        id = idcomplet[0];
        $.post("/downloadJson/"+id,{'csrf_token': $('#csrf_token').val()}, function(result){

            var dictstring = JSON.stringify(result);
            file = new Blob([dictstring], {type: "application/json"});
            filename = idcomplet[1]
            if(file.size > 1024*1024)
            {
                alert('Please choose files smaller than 1mb, otherwise you may crash your browser. \nThis is a known issue. See the tutorial.');
                return;
            }
            else
            {

                //alert("Siga")
                encryptarRecursivo(object,file, filename, posicion, maximo)
                //alert("sale")
            }

        });
    }
    else
    {
        //alert("Ya termina")
        $('#content_product').css('display','block')
    }
}

function encryptarRecursivo(object, file, filename, posicion, maximo)
{
    var reader = new FileReader();

    // Encrypt the file!

    reader.onload = function(e){


        // Use the CryptoJS library and the AES cypher to encrypt the
        // contents of the file, held in e.target.result, with the password

        var encrypted = CryptoJS.AES.encrypt(e.target.result, "Bioversity2015");

        // The download attribute will cause the contents of the href
        // attribute to be downloaded when clicked. The download attribute
        // also holds the name of the file that is offered for download.

        a = object;
        a.attr('download', filename + '.encrypted');
        a.attr('href', 'data:application/octet-stream,' + encrypted);
        a.off("click")
        procedimientoRecursivo(posicion+1, maximo)
        //alert("termina")


    };

    // This will encode the contents of the file into a data-uri.
    // It will trigger the onload handler above, with the result

    reader.readAsDataURL(file);
}


function encryptar(object, file, filename)
{
    var reader = new FileReader();

    // Encrypt the file!

    reader.onload = function(e){


        // Use the CryptoJS library and the AES cypher to encrypt the
        // contents of the file, held in e.target.result, with the password

        var encrypted = CryptoJS.AES.encrypt(e.target.result, "Bioversity2015");

        // The download attribute will cause the contents of the href
        // attribute to be downloaded when clicked. The download attribute
        // also holds the name of the file that is offered for download.

        a = object;
        a.attr('download', filename + '.encrypted');
        a.attr('href', 'data:application/octet-stream,' + encrypted);
        a.off("click")
        //alert("termina")


    };

    // This will encode the contents of the file into a data-uri.
    // It will trigger the onload handler above, with the result

    reader.readAsDataURL(file);
}


function refresh()
{
    // console.log("Querying products");
    $('#content_product').css('display','none');
    jQuery.ajax(
    {
        url     : 'dataProductsList',
        data :{
        'csrf_token': $('#csrf_token').val()
        },
        type    : 'post',
        async:true,
        success : function(data){
            $('#content_product').html(data);
            array = [];
            $('.btn_datadesk').each(function()
            {
                array.push($(this))
            });
            procedimientoRecursivo(0, array.length-1);
            call_refresh = true;
        },
        error: function (request, error) {
            console.log(" Can't get data: " + error);
            console.log(arguments);
        }
    });
}


/*function fun_download(product_id,csrf_token)
{
    jQuery.ajax(
    {
        url     : product_id,
        data :{
        'csrf_token': csrf_token
        },
        type    : 'post',
        success : function(data)
        {
            var blob=new Blob([data],{type: 'application/pdf'});
            alert(blob)
            var link=document.createElement('a');
            link.href=window.URL.createObjectURL(blob);
            link.download="SearchedResults.pdf";
            link.click();
            window.location.href = data
        },
        error: function (request, error) {
            console.log(arguments);
            alert(" Can't do because: " + error);
        }
    });
}*/