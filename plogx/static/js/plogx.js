$(document).ready(function(){
    var day_stats;
    var current_year_month = $('#date').html();
    
    var generate_stats_per_month = function(data){
        var chart_visits = new Array();
        var chart_page_impr = new Array();
        
        var path_stats = data["path_stats"];
        day_stats = data["day_stats"];
        
        var current_date = moment(current_year_month, "YYYYMM");
        var path_stats_html = "<b>Stats for "+moment(current_date).format("MMMM YYYY")+":</b><br/>";
        for (var i = 0; i < path_stats.length; i++) {
            path_stats_html+=path_stats[i]["num_visits"]+"x "+path_stats[i]["path"]+"<br/>";
        }

        $("#month_stats").html(path_stats_html);

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

        var plot = $.plot(graph, dataset, {
          xaxis: {
            tickSize: 1
          },
          yaxis: {
            minTickSize: 5
          },
          grid: {
            clickable: true
          }
        });
    }

    
    var current_date = moment(current_year_month, "YYYYMM");
    $('#current_month').html(current_date.format("MMMM YYYY"));
    $('#prev').attr("href", "/stats/"+current_date.subtract("M", 1).format("YYYYMM"));
    $('#next').attr("href", "/stats/"+current_date.add("M", 2).format("YYYYMM"));

    $.getJSON( "/stats_per_month/"+current_year_month, generate_stats_per_month);

    $("#graph").bind("plotclick", function(event, pos, item){
      if (item){
        day = new Date(day_stats[item["dataIndex"]]["day"]["$date"]);

        $.getJSON("/stats_per_day/" + moment(day).format("YYYYMMDD"), function(data){
          var paths = "";
          for (i=0; i< data["path_stats"].length; i++){
            path_stats = data["path_stats"][i];
            paths+=path_stats["num_visits"]+"x "+path_stats["path"]+"<br/>"
          }

          $("#day_stats").html("<b>Stats for "+ moment(day).format("MMMM Do YYYY")+":</b><br/>"+
            "Page Impressions: "+data["num_page_impressions"]+"<br/>"+
            "Visitors: "+data["num_visits"]+"<br/>"+
            "<a href='/raw_logs_per_day/"+moment(day).format("YYYYMMDD")+"'>Raw Log Data</a><br/><br/>"+
            "Paths:<br/>"+paths
          );
        })
      }
    })
});
