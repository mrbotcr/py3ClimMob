/**
 * Created by acoto on 11/07/17.
 */

function msj(flag) {

    if (flag == 2) {
        toastr.options = {
            closeButton: true,
            progressBar: true,
            showMethod: 'slideDown',
            timeOut: 4000
        };
        toastr.error("Seleccione al menos una columna");

    }

    if (flag == 1) {
        swal({title: "Listo!", text: "Sus cambios fueron guardados en la base de datos", type: "success"});
    }

    if (flag == 0) {
        swal({
            title: "Error!",
            text: "Sucedio un error al actualizar sus datos, por favor intentelo de nuevo",
            type: "error"
        });
    }

}

function drawtable(data_fill) {

    var vals = JSON.parse(data_fill);
    //$('#byC').trigger('click');

    $.jgrid.defaults.width = 780;
    $.jgrid.defaults.responsive = true;
    $.jgrid.defaults.styleUI = 'Bootstrap';

    var mydata = vals['data'];
    // Configuration for jqGrid Example 2
    var queValido = ""
    var enQueFila = ""
    var queValor  = ""

    validateText = function (value, colname)
    {
        /*vals['colModel'].forEach(function(element)
        {
            if(queValido == element.name)
            {
                enEstaPosicionEstaElQueOcupo = vals['colModel'].indexOf(element)
            }
        })

        var cell = $('#jqGrid').jqGrid('getCell',enQueFila,enEstaPosicionEstaElQueOcupo)

        if (queValor == cell)
            return [false,"La mejor y la peor no pueden ser la misma opción."];
        else
            return [true]*/

        cuantosRepetidos = 0
        queTengoQueValidar = queValido.split("*****")
        queTengoQueValidar.forEach(function(elementValidar)
        {
            vals['colModel'].forEach(function(element)
            {
                if(elementValidar == element.name)
                {
                    enEstaPosicionEstaElQueOcupo = vals['colModel'].indexOf(element)
                }
            })

            var cell = $('#jqGrid').jqGrid('getCell',enQueFila,enEstaPosicionEstaElQueOcupo)
            if(queValor == cell)
            {
                cuantosRepetidos = cuantosRepetidos + 1
            }
        })

        //alert(cuantosRepetidos)

        if (cuantosRepetidos>0)
            return [false,"Revise que el valor no se duplique en otra columna."];
        else
            return [true]
    };

    vals['colModel'].forEach(function(element)
    {
        index = vals['colModel'].indexOf(element)
        if (vals['colModel'][index]["validation"] != "" && vals['colModel'][index]["validation"] != undefined)
        {
            vals['colModel'][index]["editrules"]= {"custom":true,"custom_func":validateText}
        }
    });

    $("#jqGrid").jqGrid({
        data: mydata,
        datatype: "local",
        height: 'auto',
        autowidth: true,
        pager: "#pager_list_2",
        //colNames: vals['colNames'],
        colModel: vals['colModel'],
        caption: "Tabla de edicion",
        hidegrid: false,
        cellEdit: true,
        cellsubmit: 'clientArray',
        onCellSelect: bandera,
        loadonce: true,
        viewrecords: true,
        editurl: 'clientArray'

    });

    function getJson() {
        var allRowsInGrid = $('#jqGrid').jqGrid('getGridParam', 'data');
        console.log(JSON.stringify(allRowsInGrid));
        $('#json_data').val(JSON.stringify(allRowsInGrid));
        $("#save_jq").attr("disabled", false);
    }

    function bandera(rowid, iCol, cellcontent, e)
    {
        $("#save_jq").attr("disabled", true);
        $('#jqGrid').jqGrid('setCell', rowid, 'flag_update', true);
    }

    $("#jqGrid").bind("jqGridAfterSaveCell", function (e, rowid, orgClickEvent) {
        getJson();
    });

    $("#jqGrid").bind("jqGridBeforeSaveCell",function(event, rowid, cellname, value, iRow, iCol)
    {
        enQueFila = rowid
        queValor  = value

        var cm = $('#jqGrid').jqGrid('getGridParam','colModel')
        cm.forEach(function(element)
        {
            if(element.name == cellname)
            {
                queValido = element["validation"]
            }
        })
    });


    //--------------------
    grid = $("#jqGrid");
    var flag, flag2 = true;

    onclickSubmitLocal = function (options, postdata) {


        var grid_p = grid[0].p,
            idname = grid_p.prmNames.id,
            grid_id = grid[0].id,
            id_in_postdata = grid_id + "_id",
            rowid = postdata[id_in_postdata],
            addMode = rowid === "_empty",
            oldValueOfSortColumn;

        if (addMode) {
            // generate new id
            var new_id = grid_p.records + 1;
            while ($("#" + new_id).length !== 0) {
                new_id++;
            }
            postdata[idname] = String(new_id);
        } else if (typeof(postdata[idname]) === "undefined") {
            // set id property only if the property not exist
            postdata[idname] = rowid;
        }
        delete postdata[id_in_postdata];

        // prepare postdata for tree grid
        if (grid_p.treeGrid === true) {
            if (addMode) {
                var tr_par_id = grid_p.treeGridModel === 'adjacency' ? grid_p.treeReader.parent_id_field : 'parent_id';
                postdata[tr_par_id] = grid_p.selrow;
            }

            $.each(grid_p.treeReader, function (i) {
                if (postdata.hasOwnProperty(this)) {
                    delete postdata[this];
                }
            });
        }

        // decode data if there encoded with autoencode
        if (grid_p.autoencode) {
            $.each(postdata, function (n, v) {
                postdata[n] = $.jgrid.htmlDecode(v); // TODO: some columns could be skipped
            });
        }

        // save old value from the sorted column
        oldValueOfSortColumn = grid_p.sortname === "" ? undefined : grid.jqGrid('getCell', rowid, grid_p.sortname);
        grid.jqGrid('setCell', rowid, 'flag_update', true);
        // save the data in the grid
        if (grid_p.treeGrid === true) {
            if (addMode) {
                grid.jqGrid("addChildNode", rowid, grid_p.selrow, postdata);
            } else {
                grid.jqGrid("setTreeRow", rowid, postdata);
            }
        } else {
            if (addMode) {
                grid.jqGrid("addRowData", rowid, postdata, options.addedrow);
            } else {
                grid.jqGrid("setRowData", rowid, postdata);
            }
        }


        if (flag) {

            if ((addMode && options.closeAfterAdd) || (!addMode && options.closeAfterEdit)) {
                // close the edit/add dialog
                $.jgrid.hideModal("#editmod" + grid_id,
                    {gb: "#gbox_" + grid_id, jqm: options.jqModal, onClose: options.onClose});
            }


        }

        if (postdata[grid_p.sortname] !== oldValueOfSortColumn) {
            // if the data are changed in the column by which are currently sorted
            // we need resort the grid
            setTimeout(function () {
                grid.trigger("reloadGrid", [{current: true}]);
            }, 100);
        }

        // !!! the most important step: skip ajax request to the server
        options.processing = true;
        flag = true
        getJson();

        return {};
    };

    //--------------------

    $("#jqGrid").jqGrid('navGrid', '#pager_list_2',
        {edit: true, add: false, del: false, search: true},
        //edit
        {
            editCaption: "The Edit Dialog",
            reloadAfterSubmit: true,
            closeOnEscape: true,
            savekey: [false, 13],
            closeAfterEdit: true,
            onclickSubmit: onclickSubmitLocal,
            width: 500,
            height: 'auto',
            viewPagerButtons: true,
            recreateForm: true,
            bCancel: "Cancel",
            bSubmit: "Save",
            jqModal: true,
            beforeShowForm: function (formid) {
                flag2 = false;
                flag = false;
                $("[role=select ]").width('80%').addClass("form-control")
                $("[role=textbox ]").addClass("form-control").width('77%');

                $("#pData span").addClass('fa fa-4x');
                $("#nData span").addClass('fa fa-4x');//.css({'width':'25px', 'height':'25px'})


            },
            onclickPgButtons: function (whichbutton, formid, rowid) {
                flag = false;
                $('#sData').click();
            },
            onClose: function () {
                flag2 = true;
                flag = true;
            }
        },
        //adds
        {
            width: 500,
            closeAfterAdd: true,
            recreateForm: true,
            reloadAfterSubmit: false,
            savekey: [true, 13],
            closeOnEscape: true,
            closeAfterAdd: true,
        },
        {},
        {multipleSearch: true}
    );
    $('.ui-state-error').hide()

    // Add responsive to jqGrid
    $(window).bind('resize', function () {
        var width = $('.jqGrid_wrapper').width();
        $('#jqGrid').setGridWidth(width);
    });


    //create editable row
    var lastSelection;

    function editRow(id) {

        if (flag2) {

            if (id && id !== lastSelection) {
                var grid = $("#jqGrid");
                grid.jqGrid('saveRow', lastSelection);
                grid.jqGrid('restoreRow', lastSelection);
                grid.jqGrid('editRow', id, {keys: true, focusField: 4});
                grid.jqGrid('setCell', id, 'flag_update', true);
                lastSelection = id;

            }
        }
        //$("[role=textbox ]").addClass("form-control");


    }

    grid.bind("jqGridAddEditAfterSelectUrlComplete‌​", function (e, elem) {
        console.log('scacsac')
    });


    //validate if jqgrid has changed before send post cancel_jq
    $("#jqEditTable").submit(function (e) {

        //console.log(document.activeElement.id); // name of submit button
        if ($('#json_data').val() != '') {

            if (document.activeElement.id == 'cancel_jq') {
                e.preventDefault();
                swal({
                        title: "Hay cambios sin guardar!",
                        text: "Desea guardar los cambios realizados en la base de datos?",
                        type: "warning",
                        showCancelButton: true,
                        confirmButtonColor: "#DD6B55",
                        confirmButtonText: "Si, deseo guardarlos!",
                        cancelButtonText: "No, deseo cancelar!",
                        closeOnConfirm: false,
                        closeOnCancel: false
                    },
                    function (isConfirm) {
                        if (isConfirm) {
                            //"#jqEditTable").off('submit').submit();
                            $("#jqEditTable").off('submit').submit()
                        } else {
                            $('#json_data').val('');
                            swal({
                                title: "Cancelado",
                                text: "Sus cambios no se almacenaran en la base de datos)",
                                type: "error"
                            }, function () {
                                $("#jqEditTable").off('submit').submit()
                            });
                        }
                    });
                //e.preventDefault();
            }
        }

    });

}

$(document).ready(function () {

    $('.i-checks').iCheck({
        checkboxClass: 'icheckbox_square-green',
        radioClass: 'iradio_square-green',
    });

    $('.checkpadre').on('ifChanged', function(e)
    {
        id = e.target.id;
        if ($(this).prop('checked')) {
            $('.'+id).iCheck('check');
        } else
        {
            $('.'+id).iCheck('uncheck');
        }
    });

});
