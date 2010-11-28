window.gigaschema = {  };

window.gigaschema.dispatcher = function(guard, func) {
    window.gigaschema.dispatcher.path_func = window.gigaschema.dispatcher.path_func || []
    if (func) {
        window.gigaschema.dispatcher.path_func.push([guard, func]);
        return;
    }
    window.gigaschema.dispatcher.path_func.forEach(function(pair) {
        var guard = pair[0];
        var func = pair[1];

        // TODO: when guard is a function
        $(guard).length > 0 && func();
    });
};

// [['2009/07/01 18:00:00',2], ['2009/09/08 18:30:00',11], ['2009/09/08 18:40:00',15], ['2010/01/02',3],['2010/01/03',6],['2010/02/01',3]]
window.gigaschema.plotGraph = function(id, data) {
    $.jqplot('chartdiv',
             data, {
                 // title:title,
                 axes: {
                     xaxis: {
                         renderer: $.jqplot.DateAxisRenderer
                     }
                 }
             });
}

window.gigaschema.dispatcher('body#schema', function() {
    if ($('#chartdiv').length == 0) return;
    var to = [];
    $('.data-item').each(function() {
        var created_on = $(this).attr('data-created-on');
        var value = parseInt($(this).attr('data-value'), 10);
        if (! isNaN(value)) {
            to.push([created_on, value]);
        }
    });
    window.gigaschema.plotGraph('chartdiv', [to]);
});

$(function() {
    window.gigaschema.dispatcher();
});