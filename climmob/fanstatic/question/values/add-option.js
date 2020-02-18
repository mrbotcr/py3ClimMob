/**
 * Created by brandon on 27/06/16.
 */

$(document).ready(function()
{
    
    var objOther = $("#ckb_other");
    var other = 0;
    if (objOther.is(':checked'))
        other = 1;

    var vNA = 0;
    var objNA = $("#ckb_na");
    if (objNA.is(':checked'))
        vNA = 1;

    if(other == 1)
        objOther.bootstrapSwitch('state',true);
    else
        objOther.bootstrapSwitch('state',false);

    if (vNA == 1)
        objNA.bootstrapSwitch('state',true);
    else
        objNA.bootstrapSwitch('state',false);



});


$("#ckb_other").on('switchChange.bootstrapSwitch', function(event, state) {
    if($(this).is(':checked')) {
        $("#ckb_na").bootstrapSwitch('state', false);
    }
});

$("#ckb_na").on('switchChange.bootstrapSwitch', function(event, state) {
    if($(this).is(':checked')) {
        $("#ckb_other").bootstrapSwitch('state', false);
    }
});


