
$(document).ready(function(){
    $('#newproject_tag').tagsinput({
        tagClass: 'label label-primary',
    });
    //ClimMobMaps.init();

    function isNumeric(value)
    {
        return /^\d+$/.test(value);
    }

    $('#newproject_code').on('input',function()
    {
        var value = $(this).val();
        if(isNumeric(value))
        {
            $(this).val("");
        }
        else
        {
            var value_without_space = value.replace(/[^a-z0-9]/gi,'')
            $(this).val(value_without_space);
        }
    });

    var ckb_localvariety = $("#ckb_localvariety");
    var localvariety = 0;
    if (ckb_localvariety.is(':checked'))
        localvariety = 1;

    if(localvariety == 1)
        ckb_localvariety.bootstrapSwitch('state',true);
    else
        ckb_localvariety.bootstrapSwitch('state',false);
});
