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
    $("#" + id).empty();
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

window.gigaschema.roundDateTime = function(dt) {
    var timezone_offset = (new Date).getTimezoneOffset() * 60;
    dt -= timezone_offset;
    var round = 60 * 60 * 24;
    return Math.floor(dt / round) * round + timezone_offset;
}

var plotChart = function() {
    var path = location.pathname + '.json';
    $.getJSON(path, function(data) {
        var self = window.gigaschema;

        var nums = [];
        var post_at = { };
        var as_total = $('input[name="as_total"]').attr('checked');

        var last_value_post_at = 0;
        data.data.reverse().forEach(function(row) {
            var created_on = row.created_on;
            var value = row.value;
            var num_value = parseFloat(value, 10);

            var key = self.roundDateTime(created_on);
            if (!as_total) {
                last_value_post_at = (post_at[key] || 0);
            }
            last_value_post_at++;
            post_at[key] = last_value_post_at;

            if (! isNaN(num_value)) {
                if (as_total) {
                    var last_value = 0.0;
                    if (nums.length > 0) {
                        last_value += nums[nums.length-1][1];
                    }
                    nums.push([created_on * 1000, last_value + num_value]);
                } else {
                    nums.push([created_on * 1000, num_value]);
                }
            }
        });

        var nums_by_day = [];
        for(var day in post_at) if (post_at.hasOwnProperty(day)) {
            nums_by_day.push([day * 1000, post_at[day]]);
        }

        var nums_for_plot = nums.length >= nums_by_day.length ? nums : nums_by_day;
        if (nums_for_plot.length == 0) return;
        window.gigaschema.plotGraph('chart', [nums_for_plot]);
    });
}

window.gigaschema.dispatcher('#chart', function() {
    plotChart();
    $('input[name="as_total"]').change(function() {
        plotChart();
    });
});

window.gigaschema.dispatcher('body#schema', function() {
    $('.api_key').click(function() {
        $(this).select();
    });

    var submit = $("#new-data :submit");
    $('#new-data textarea').bind("keydown keyup click touch", function() {
        if ($(this).val().length > 0) {
            submit.attr('disabled', '');
        } else {
            submit.attr('disabled', 'disabled');
        }
    });
});

window.gigaschema.dispatcher(true, function() {
    $('form').submit(function(event) {
        $(this).find(':submit').attr('disabled', 'disabled');
        if ($(this).attr('data-confirm')) {
            if (!confirm($(this).attr('data-confirm'))) {
                $(this).find(':submit').attr('disabled', '');
                event.preventDefault();
                return false;
            }
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
            var results = [];
            for (var i = 0; i < 3; i++) if (searcher.results[offset + i]) {
                results.push(searcher.results[offset + i]);
            }
            results.forEach(function(result) {
                var img = $('<img>');
                img.attr( {src: result.url, title: keyword });
                img.hide();
                img.bind('load', function() {
                    if (deferred) {
                        deferred.call($(this));
                        deferred = null;
                    }
                });
            });
            setTimeout(function() {
                if (deferred) {
                    var img = $('<img>');
                    img.attr({src: searcher.results[0].tbUrl, title: keyword });
                    img.hide();
                    deferred.call(img);
                    deferred = null;
                }
            }, 1000);
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
                    $('#welcome #images').append(img);
                    img.show();
                    copy.push(keyword);
                });
                $('#welcome #dummy').remove();
                $('#welcome').css({opacity: 0.1}).animate({opacity: 1.0}, 1000);
                $('#welcome #copy').text(copy.join('、') + '。');
                $('#welcome p').css({opacity: 0.1, visibility: 'visible'}).animate({opacity: 1.0}, 1000);
            });

    });

});
Hatena.Star.SiteConfig = {
  entryNodes: {
    'div.data-item': {
      uri: '.info .star-permalink',
      title: '.info .star-title',
      container: '.info .star-container'
    }
  }
};


