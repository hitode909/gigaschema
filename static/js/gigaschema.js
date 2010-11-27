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
window.gigaschema.plotGraph = function(id, title, data) {
    $.jqplot('chartdiv',
             data, {
                 title:title,
                 axes: {
                     xaxis: {
                         renderer: $.jqplot.DateAxisRenderer
                     }
                 }
             });
}

window.gigaschema.dispatcher('body#schema', function() {
    var from = window.gigaschema.currentSchema;
    var to = [];
    from.data.forEach(function(row) {
        // TODO: validation
        to.push([row.timestamp, parseInt(row.value, 10)]);
    });
    window.gigaschema.plotGraph('chartdiv', from.name, [to]);
});

$(function() {
    window.gigaschema.dispatcher();
});