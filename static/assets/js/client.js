/**
 * Created by jason on 15/12/21.
 */
function handle_tick(data) {
    data = eval("(" + data + ")");
    console.info(data);
    refresh();
    clock.value = data.clock;
}

function tick(number) {
    data = {
        num: number
    };
    $.post("/tick", data, handle_tick);
}

function ticktock_to_next_update() {
    $.post("/ticktock_to_next_update", handle_tick);
}
var tick_timer = 0;
var tick_interval = 10000;

function client_start() {
    client_stop()
    tick_timer = setInterval(function() {
        ticktock_to_next_update();
    }, tick_interval);
    var stop_b = document.getElementById("stop_clock_botton");
    var start_b = document.getElementById("start_clock_botton");
    var submit_b = document.getElementById("submit_botton");
    submit_b.disabled = "disabled";
    start_b.disabled = "disabled";
    stop_b.disabled = "";
}

function update_tick_interval() {
    tick_interval = input_tick_interval.valueAsNumber;
    if (tick_timer != 0) {
        client_start();
    }
    var start_b = document.getElementById("start_clock_botton");
    var submit_b = document.getElementById("submit_botton");
    submit_b.disabled = "disabled";
    start_b.disabled = "";
}

function client_stop() {
    clearInterval(tick_timer);
    tick_timer = 0;
    var submit_b = document.getElementById("submit_botton");
    var start_b = document.getElementById("start_clock_botton");
    var stop_b = document.getElementById("stop_clock_botton");
    stop_b.disabled = "disabled";
    start_b.disabled = "";
    submit_b.disabled = "";
}

function refresh() {
    $.post("/goal_values", function(data) {
        console.info(data);
        data = eval(data);
        xdata = [];
        for (i = 0; i < data[0].data.length; i++)
            xdata.push(i + 1)
        series = [];
        names = [];
        for (i = 0; i < data.length; i++) {
            series.push({
                name: data[i].name,
                type: 'line',
                data: data[i].data
            });
            names.push(data[i].name)
        }

        averages = [];
        variances = [];

        for (i=0; i < data.length; i++) {
            avg = 0;
            total = data[i].data;
            for (j=0;j<total.length;j++) {
                avg += total[j];
            }
            if (total.length != 0) {
                    avg /= total.length;
            }
            vrc = 0;
            for (j=0;j<total.length;j++) {
                vrc += (total[j]-avg)*(total[j]-avg);
            }
            vrc /= total.length;
            averages.push(avg.toFixed(4));
            variances.push(vrc.toFixed(4));

        }

        $("#property").html("");
        for(i=0;i<data.length;i++) {
            txt = "<tr> <td>"+names[i]+"</td> <td>"+averages[i]+"</td> <td>"+variances[i]+"</td> </tr>";
            $("#property").append(txt);
        }

        var option2 = {
            title: {
                text: 'Goal Satisfaction Degree'
            },
            tooltip: {
                trigger: 'axis'
            },
            legend: {
                show: true,
                y: 'bottom',
                padding: 0,
                data: names
            },
            toolbox: {
                show: true,
                feature: {
                    mark: {
                        show: true
                    },
                    dataView: {
                        show: true,
                        readOnly: false
                    },
                    magicType: {
                        show: true,
                        type: ['line', 'bar']
                    },
                    restore: {
                        show: true
                    },
                    saveAsImage: {
                        show: true
                    }
                }
            },
            calculable: true,
            xAxis: [{
                type: 'category',
                name: 'clcok',
                boundaryGap: true,
                axisLabel: {
                    formatter: '{value}'
                },
                data: xdata
            }],
            yAxis: [{
                type: 'value',
                min: 0,
                max: 1,
                axisLabel: {
                    formatter: '{value}'
                }
            }],
            series: series
        };
        if (xdata.length > 0)
            myChart.hideLoading();
        myChart.setOption(option2);
    })

}
