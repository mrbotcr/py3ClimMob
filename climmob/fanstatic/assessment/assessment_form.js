$(document).ready(function(){
    var ckb_localvariety = $("#ckb_final");
    var localvariety = 0;
    if (ckb_localvariety.is(':checked'))
        localvariety = 1;

    if(localvariety == 1)
        ckb_localvariety.bootstrapSwitch('state',true);
    else
        ckb_localvariety.bootstrapSwitch('state',false);
});