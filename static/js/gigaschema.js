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

window.gigaschema.roundDateTime = function(dtstr) {
    var date = new Date(Date.parse(dtstr.split('.')[0]));
    return [date.getFullYear(), date.getMonth() + 1, date.getDate()].join('-');
}

window.gigaschema.dispatcher('body#schema', function() {
    var path = location.pathname + '.json';
    $.getJSON(path, function(data) {
        var self = window.gigaschema;

        var nums = [];
        var post_at = { };

        data.data.forEach(function(row) {
            var created_on = row.timestamp;
            var value = row.value;
            var num_value = parseInt(value, 10);

            var key = self.roundDateTime(created_on);
            post_at[key] = (post_at[key] || 0) + 1;

            if (! isNaN(num_value)) {
                nums.push([created_on, num_value]);
            }
        });
        if (nums.length == 0) {
            for(var day in post_at) if (post_at.hasOwnProperty(day)) {
                nums.push([day, post_at[day]]);
            }
        }
        console.log(nums);
        window.gigaschema.plotGraph('chartdiv', [nums]);
    });
});

window.gigaschema.dispatcher('body', function() {
    $('.data-item:even').addClass('odd');
});

$(function() {
    window.gigaschema.dispatcher();
});