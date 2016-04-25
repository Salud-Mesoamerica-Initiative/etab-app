//for each meta_series
//grab the percent passing and add it to the top
//add each other series to its graph

var months = ["January", "February", "March", "April", "May", "June", "July", "August",
  "September", "October", "November", "December"];
var $container = $('#container-p');
var $content = $('#visualize-content');
var $indicatorChart = $(".indicator-chart");
var currentDimension = null;
var noDimensions = "-1";
var seriesData = {};

orchid_vis = {
  locations: [],
  location_cursor: null,
  month: months,
  get_chart_by_id: function (id) {
    var index = $("#container-" + id).data('highchartsChart');
    return Highcharts.charts[index];
  },
  clearCharts: function () {
    $indicatorChart.each(function () {
      orchid_vis.clearChart($(this));
    });
  },
  clearChart: function ($el) {
    try {
      $el.highcharts().destroy();
    } catch (e) {
      // console.log(e);
    }
    $el.hide();
    // orchid_vis.apply_chart($el, [], $el.data("indicator-title"), true);
  },
  apply_chart: function (dom_object, series_data_blob, chart_title, legend_enabled) {
    return dom_object.highcharts({
      chart: {
        type: 'spline'
      },
      title: {
        text: chart_title
      },
      subtitle: {
        text: 'Click legend to select lines.'
      },
      exporting: {
        sourceWidth: 1024,
        sourceHeight: 786
      },
      xAxis: {
        type: 'datetime',
        tickInterval: 30 * 24 * 3600 * 1000,
        dateTimeLabelFormats: { // don't display the dummy year
          month: '%e. %b',
          year: '%b'
        },
        title: {
          text: 'Date'
        }
      },
      yAxis: {
        title: {
          text: 'Score (%)'
        },
        min: 0,
        max: 100
      },
      legend: {
        enabled: legend_enabled
      },
      tooltip: {
        headerFormat: '<b>{series.name}</b><br>',
        pointFormat: '{point.x: %b %Y}: {point.y:.2f}%'
      },
      series: series_data_blob
    });

  },
  load_next_location: function (dimension) {
    if (dimension != currentDimension) {
      return;
    }

    if (orchid_vis.location_cursor == null) {
      orchid_vis.location_cursor = 0;
    }
    else {
      //update the cursor
      orchid_vis.location_cursor += 1;
    }
    if (orchid_vis.location_cursor < orchid_vis.locations.length) {
      var next_location_id = orchid_vis.locations[orchid_vis.location_cursor].id;
      //load the location's json
      var url = "location/" + String(next_location_id) + "/visualize";
      $.getJSON(url, {dimension: dimension}, function (data) {
        for (var q in data.series) {
          var s = data.series[q];
          if (s.id != undefined) {
            // var $el = $("#container-" + s.id);
            // $el.show();
            // var loading_chart = orchid_vis.get_chart_by_id(s.id);
            //adjust dates in data
            var newData = [];
            for (var d in s.data) {
              var this_data = s.data[d];
              newData.push([
                new Date(this_data[0]).getTime(),
                parseInt(this_data[1]),
                this_data[2],
                this_data[3]
              ]);
            }
            var title = "";
            if (data.noun) {
              title = data.noun.title;
            }

            if (!seriesData[s.id]) {
              seriesData[s.id] = [];
            }

            seriesData[s.id].push({
              name: title,
              data: newData
            });

            // loading_chart.addSeries({
            //   name: title,
            //   data: newData
            // });
            // var $chart = $el.highcharts();
            // $chart.setSize($el.width(), $chart.chartHeight, doAnimation = true);
          }
        }
        var txt = String(orchid_vis.location_cursor + 1) + "/" +
          String(orchid_vis.locations.length) + " Loaded";
        $('#loaded_counter').html(txt);
        orchid_vis.load_next_location(dimension);
      });
    } else {
      for (var sid in seriesData) {
        var $el = $("#container-" + sid);
        $el.show();
        orchid_vis.apply_chart($el, seriesData[sid], $el.data("indicator-title"), true);
        // var loading_chart = orchid_vis.get_chart_by_id(s.id);
      }
    }

  }
};

$('#dimensions').on('change', function (e) {
  var $this = $(this);
  var value = $this.val();
  seriesData = {};
  if (value == noDimensions) {
    $content.hide();
  } else {
    $content.show();
    currentDimension = value;
    drawLocationsByDimension(currentDimension);
  }
});

function drawLocationsByDimension(dimension) {
  orchid_vis.locations = [];
  orchid_vis.location_cursor = null;
  orchid_vis.clearCharts();

  $.getJSON("location/list/plain", {dimension: dimension}, function (data) {
    // is still the same dimension?
    if (dimension == currentDimension) {
      $.each(data.locations, function (key, val) {
        orchid_vis.locations.push(val);
      });
      $('#loaded_counter').html("0/" + String(orchid_vis.locations.length) + " Loaded");
      orchid_vis.load_next_location(dimension);
    }
  });
}


// I do not what this does
orchid_vis.apply_chart($container, [], "Percent Of Goals Met", true);
var index = $container.data('highchartsChart');
// var mychart = Highcharts.charts[index];
//
// mychart.setTitle("hello!");

$indicatorChart.each(function () {
  orchid_vis.apply_chart($(this), [], $(this).data("indicator-title"), true);
});
