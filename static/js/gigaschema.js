function dispatcher (guard, func) {
    dispatcher.path_func = dispatcher.path_func || []
    if (func) {
        dispatcher.path_func.push([guard, func]);
        return;
    }
    dispatcher.path_func.forEach(function(pair) {
        var guard = pair[0];
        var func = pair[1];

        // TODO: when guard is a function
        $(guard).length > 0 && func();
    });
};

dispatcher('body#schema', function() {
    $.jqplot('chartdiv',
             [[['2009/07/01 18:00:00',2], ['2009/09/08 18:30:00',11], ['2009/09/08 18:40:00',15], ['2010/01/02',3],['2010/01/03',6],['2010/02/01',3]]], {
                 title:'雪が降ってうれしい',
                 axes: {
                     xaxis: {
                         renderer: $.jqplot.DateAxisRenderer
                     }
                 }
             });
});

$(function() {
    dispatcher();
});