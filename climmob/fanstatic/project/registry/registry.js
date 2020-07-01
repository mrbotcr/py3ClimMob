/**
 * Created by brandon on 17/05/17.
 */

var updateOutput = function (e,enableButtons) {
    enableButtons = typeof enableButtons !== 'undefined' ? enableButtons : true;
    var list = e.length ? e : $(e.target),
        output = list.data('output');
    if (window.JSON) {
        output.val(window.JSON.stringify(list.nestable('serialize')));//, null, 2));
    } else {
        output.val('JSON browser support required for this demo.');
    }

    $(".clm-actions").prop('disabled', !enableButtons);
    $(".clm-grpactions").prop('disabled', enableButtons);
};

function deleteQuestion(id)
{
    $('#nestable').nestable('remove', id);
    updateOutput($('#nestable').data('output', $('#nestable-output')));
}

$(document).ready(function(){

    $('#nestable').nestable({
        group: 1,
        onDragStart: function (l, e) {
            // get type of dragged element
            var type = $(e).data('type');

            // based on type of dragged element add or remove no children class
            switch (type) {
                case 'question':
                    // A question can be part of a group
                    l.find("[data-type=group]").removeClass('dd-nochildren');
                    break;
                case 'group':
                    // A group cannot be part of another group
                    l.find("[data-type=group]").addClass('dd-nochildren');
                    break;
                default:
                    console.error("Invalid type");
            }
        }
    }).on('change', updateOutput);
    updateOutput($('#nestable').data('output', $('#nestable-output')),false);
    $('#carlos').attr("disabled", true);
});

