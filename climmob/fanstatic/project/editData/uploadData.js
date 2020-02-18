
$(document).ready(function () {

});

var file =""
function cargar_json(sender)
{
    $("#dataUpload").val("")
    $("#dataNeccessaryUpload").val("")
    $("#btn_uploadData").css("display","none")
    var validExts = new Array(".encrypted");
    var fileExt = sender.value;
    fileExt = fileExt.substring(fileExt.lastIndexOf('.'));
    if (validExts.indexOf(fileExt) < 0)
    {
        alert("Archivo no valido.")
    }
    else
    {
        var archivos = document.getElementById("inputFile");
        var archivo = archivos.files;
        leerArchivo(archivo[0]);

        //leerArchivo(sender);
    }
}

function leerArchivo(archivo)
{

    file = archivo
    decrypt()
}

function decrypt()
{
	var reader = new FileReader();
	reader.onload = function(e){

		var decrypted = CryptoJS.AES.decrypt(e.target.result, "Bioversity2015").toString(CryptoJS.enc.Latin1);

		if(!/^data:/.test(decrypted)){
			alert("Invalid pass phrase or file! Please try again.");
			return false;
		}
		json = atob(decrypted.split(',')[1])
		var vals = JSON.parse(json);
		$("#dataUpload").val(json)
		$("#dataNeccessaryUpload").val(JSON.stringify(vals["data"]))
		$("#btn_uploadData").css("display","block")

	};

	reader.readAsText(file);
}