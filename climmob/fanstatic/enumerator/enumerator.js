jQuery(document).ready(function()
{
    if ($('#ckb_modify_status').prop('checked'))
        $("[name='ckb_modify_status']").bootstrapSwitch('state',true);
    else
        $("[name='ckb_modify_status']").bootstrapSwitch('state',false);
});