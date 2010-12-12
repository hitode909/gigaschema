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
        if (guard == true || $(guard).length > 0) {
            func();
        }
    });
};

// [['2009/07/01 18:00:00',2], ['2009/09/08 18:30:00',11], ['2009/09/08 18:40:00',15], ['2010/01/02',3],['2010/01/03',6],['2010/02/01',3]]
window.gigaschema.plotGraph = function(id, data) {
    $.jqplot(id,
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


window.gigaschema.dispatcher('#chart', function() {
    var path = location.pathname + '.json';
    $.getJSON(path, function(data) {
        var self = window.gigaschema;

        var nums = [];
        var post_at = { };

        data.data.forEach(function(row) {
            var created_on = row.created_on;
            var value = row.value;
            var num_value = parseFloat(value, 10);

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
        // console.log(nums);
        if (nums.length == 0) return;
        window.gigaschema.plotGraph('chart', [nums]);
    });
});

window.gigaschema.dispatcher(true, function() {
    $('form').submit(function() {
        $(this).find(':submit').attr('disabled', 'disabled');
    });
});

window.gigaschema.dispatcher('body#schema', function() {
    $('.api_key').click(function() {
        $(this).select();
    });

    $('#new-data textarea').focus(function() {
        $(this).attr({ rows: 6, cols: 80 });
    });

    var submit = $("#new-data :submit");
    console.log(submit);
    $('#new-data textarea').bind("keydown keyup click", function() {
        if ($(this).val().length > 0) {
            submit.attr('disabled', '');
        } else {
            submit.attr('disabled', 'disabled');
        }
    });
});

$(function() {
    window.gigaschema.dispatcher();
});

Deferred.define();

google.load("search", "1");
google.setOnLoadCallback(function() {
    if ($('body#index').length == 0) return;

    function getImage(keyword, d) {
        var search = new google.search.SearchControl();
        search.setResultSetSize(google.search.Search.LARGE_RESULTSET);
        search.addSearcher(new google.search.ImageSearch());
        search.draw();

        var deferred = new Deferred();
        search.setSearchCompleteCallback(this, function(sc, searcher) {
            var offset = Math.floor(Math.random() * searcher.results.length - 3);
            var urls = [];
            for (var i = 0; i < 3; i++) if (searcher.results[offset + i]) {
                urls.push(searcher.results[offset + i].url);
            }
            urls.forEach(function(url) {
                var img = $('<img>');
                img.attr( {src: url });
                img.hide();
                img.bind('load', function() {
                    if (deferred) {
                        deferred.call($(this));
                        deferred = null;
                    }
                });

            });
        });

        search.execute(keyword);
	return deferred;
    };

    // http://hail2u.net/blog/coding/shuffle-array-in-javascript.html
    function shuffle(list) {
        var i = list.length;

        while (--i) {
            var j = Math.floor(Math.random() * (i + 1));
            if (i == j) continue;
            var k = list[i];
            list[i] = list[j];
            list[j] = k;
        }

        return list;
    }

    $.getJSON('http://gigaschema.appspot.com/hitode909/keyword.json', function(schema) {
        var keywords = shuffle(schema.data).map(function(data) { return data.value });

        results = [];
        loop(3, function (i) {
            return getImage(keywords[i]).next(function(url) {
                results.push([keywords[i], url]);
            });
        }).
            next(function () {
                var copy = [];
                results.forEach(function(pair) {
                    var keyword = pair[0];
                    var img = pair[1];
                    $('#welcome').append(img);
                    img.show();
                    copy.push(keyword);
                });
                $('#welcome #dummy').remove();
                $('#welcome').css({opacity: 0.1}).animate({opacity: 1.0}, 1000);
                $('#welcome #copy').text(copy.join('、') + '。');
            });

    });

});


