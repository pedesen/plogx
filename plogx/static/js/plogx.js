$(document).ready(function(){
    var day_stats;

    var generate_stats_per_month = function(data){
        var chart_visits = new Array();
        var chart_page_impr = new Array();

        day_stats = data["day_stats"];
        for (var i = 0; i < day_stats.length; i++) {
            chart_visits.push([i+1, day_stats[i]["num_visits"]])
            chart_page_impr.push([i+1, day_stats[i]["num_page_impressions"]])
        }

        var dataset = [{
          label: "Page Impressions",
          data: chart_page_impr,
          lines: { show: false },
          color: "#8db9cc",
          bars: {
            show: true,
            barWidth: 0.8,
            align: "center",
            fill:1
          }
        },{
          label: "Visitors",
          data: chart_visits,
          lines: { show: false },
          color: "#14568a",
          bars: {
            show: true,
            barWidth: 0.4,
            align: "center",
            fill:1
          }
        }]

        var plot = $.plot(month_stats, dataset, {
          xaxis: {
            tickSize: 1
          },
          grid: {
            clickable: true
          }
        });
    }

    $.getJSON( "/stats_per_month", generate_stats_per_month);

    $("#month_stats").bind("plotclick", function(event, pos, item){
      if (item){
        day = new Date(day_stats[item["dataIndex"]]["day"]["$date"]);

        $.getJSON("/stats_per_day/" + moment(day).format("YYYYMMDD"), function(data){
          console.log(data);
          var paths = "";
          for (i=0; i< data["path_stats"].length; i++){
            path_stats = data["path_stats"][i];
            paths+=path_stats["num_visits"]+"x "+path_stats["path"]+"<br/>"
          }

          $("#day_stats").html("Stats for "+ moment(day).format("MMMM Do YYYY")+":<br/>"+
            "Page Impressions: "+data["num_page_impressions"]+"<br/>"+
            "Visitors: "+data["num_visits"]+"<br/>"+
            "<a href='/raw_logs_per_day/"+moment(day).format("YYYYMMDD")+"'>Raw Log Data</a><br/><br/>"+
            "Paths:<br/>"+paths
          );
        })
      }
    })
});
