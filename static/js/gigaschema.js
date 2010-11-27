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
             [[[1, 2],[3,5.12],[5,13.1],[7,33.6],[9,85.9],[11,219.9]]],
             { title:'Exponential Line',
               axes:{yaxis:{min:-10, max:240}},
               series:[{color:'#5FAB78'}]
             });
});

$(function() {
    dispatcher();
});