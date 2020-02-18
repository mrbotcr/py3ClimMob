/**
 * Created by brandon on 27/06/16.
 */

$(document).ready(function()
{
	// $('#SearchInTable').keyup(function()
	// {
	// 	searchTable($(this).val());
	// });
    //
	// $('#SearchInTable2').keyup(function()
	// {
	// 	searchTable2($(this).val());
	// });

    $('.dataTables-example').DataTable({
                pageLength: 25,
                responsive: true,


            });

});

/*function showIFrame(url,windowTitle,buttonCaption)
{
    document.getElementById('modaliframe').src = url;
    document.getElementById("modaltitle").innerHTML = windowTitle;
    document.getElementById("modalmainbutton").innerHTML = buttonCaption;
    document.getElementById("modalmainbutton").style.cssText = "color: transparent; background-color: transparent; border: none;";
    //document.getElementById("modaliframecont").style.cssText = "min-height: 650px;";
    //document.getElementById("modaliframecont").style.cssText = "min-width: 900px;";
    $('#modal1').modal('show');
}

function closeModal() {
    $('#modal1').modal('hide');
}

$('#modal1').on('hidden.bs.modal', function () {
  location.reload();
});
*/
/*

function searchTable(searching)
{
    var table = $('#tabletechnologies');
    table.find('tr').each(function(index, row)
    {
        var allCells = $(row).find('td');

        if(allCells.length > 0)
        {
            var found = false;
            allCells.each(function(index, td)
            {
                var regExp = new RegExp(searching, 'i');

                if(regExp.test($(td).text()))
                {
                    found = true;
                    return false;
                }
            });
            if(found == true)
                $(row).show();
            else {
                if (row.className != "clm-option")
            		$(row).hide();
            }
        }
    });
}

function searchTable2(searching)
{
    var table = $('#tabletechnologies2');
    table.find('tr').each(function(index, row)
    {
        var allCells = $(row).find('td');

        if(allCells.length > 0)
        {
            var found = false;
            allCells.each(function(index, td)
            {
                var regExp = new RegExp(searching, 'i');

                if(regExp.test($(td).text()))
                {
                    found = true;
                    return false;
                }
            });
            if(found == true)
                $(row).show();
            else {
                if (row.className != "clm-option")
            		$(row).hide();
            }
        }
    });
}*/

