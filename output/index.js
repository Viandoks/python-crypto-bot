var i = 0;
google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);
function drawChart() {
    console.log()

    document.getElementById("last_call").innerText = 'Last call: '+lastcall

    var data = new google.visualization.DataTable();
    data.addColumn('date', 'Date');
    data.addColumn('number', 'LH,OC'); // low
    data.addColumn('number', 'Open');
    data.addColumn('number', 'Close');
    data.addColumn('number', 'High');
    data.addColumn('number', 'Order rate');
    data.addColumn('string', 'Order type');
    data.addColumn('number', 'Stop Loss');
    data.addColumn('number', 'Take Profit');
    data.addColumn('number', 'Exit Rate')
    data.addColumn('number', 'Order Number');
    data.addColumn('number', 'MA');

    Object.keys(dataRows).map(function(k) {
        data.addRow([
            new Date(k*1000),           // 0
            dataRows[k].low,            // 1
            dataRows[k].open,           // 2
            dataRows[k].close,          // 3
            dataRows[k].high,           // 4
            dataRows[k].rate,           // 5
            dataRows[k].direction,      // 6
            dataRows[k].stopLoss,       // 7
            dataRows[k].takeProfit,     // 8
            dataRows[k].exitRate,       // 9
            dataRows[k].orderNumber,    // 10
            dataRows[k].ma              // 11
        ]);
    });

    var view = new google.visualization.DataView(data);
    view.setColumns([0, 1, 2, 3, 4,
        {
            type: 'number',
            label: 'Buy Orders',
            calc: function (dt, row) {
                // rate is in column 5 and type in column 6
                if (dt.getValue(row, 5) && dt.getValue(row, 6) == 'BUY') {
                    return dt.getValue(row, 5);
                }
            }
        },
        {
            type: 'string',
            role: 'tooltip',
            calc: function (dt, row) {
                // tooltip for buy orders
                if (dt.getValue(row, 5) && dt.getValue(row, 6) == 'BUY') {
                    //Order number at column 10
                    text = "#"+dt.getValue(row, 10);
                    //date
                    text += " Buy Order: "+dt.getValue(row, 0)+"\n";
                    // stop loss and take profit are in columns 7 and 8
                    text += "Entry: "+dt.getValue(row, 5) + " SL:"+dt.getValue(row,7)+" TP:"+dt.getValue(row,8)+"\n";
                    // exit rate in column 9
                    if(dt.getValue(row,9) > 0){
                        text += 'Exit: '+dt.getValue(row,9)+' - ';
                        // exit rate and entry rate comparison
                        text+=(dt.getValue(row,9) > dt.getValue(row,5))?'Success':'Fail';
                    }
                    return text;
                }
            }
        },
        {
            type: 'number',
            label: 'Sell Orders',
            calc: function (dt, row) {
                // rate is in column 5 and type in column 6
                if (dt.getValue(row, 5) && dt.getValue(row, 6) == 'SELL') {
                    return dt.getValue(row, 5);
                }
            }
        },
        {
            type: 'string',
            role: 'tooltip',
            calc: function (dt, row) {
                // tooltip for sell orders
                if (dt.getValue(row, 5) && dt.getValue(row, 6) == 'SELL') {
                    //Order number at column 10
                    text = "#"+dt.getValue(row, 10);
                    //date
                    text += " Sell Order: "+dt.getValue(row, 0)+"\n";
                    // stop loss and take profit are in columns 7 and 8
                    text += "Entry: "+dt.getValue(row, 5) + ", SL:"+dt.getValue(row,7)+", TP:"+dt.getValue(row,8)+"\n";
                    // exit rate in column 9
                    if(dt.getValue(row,9) > 0){
                        text += 'Exit: '+dt.getValue(row,9)+' - ';
                        // exit rate and entry rate comparison
                        text+=(dt.getValue(row,9) < dt.getValue(row,5))?'Success':'Fail';
                    }
                    return text;
                }
            }
        },
    11]);

    var chart = new google.visualization.ComboChart(document.querySelector('#chart_div'));
    chart.draw(view, {
        chartArea: {
            left: '7%',
            width: '70%'
        },
        series: {
            0: {
                type: 'candlesticks'
            },
            1: { // buy orders
                type: 'scatter',
                color: '#27AE60',
                pointShape: 'triangle'
            },
            2: { // sell orders
                type: 'scatter',
                color: '#E74C3C',
                pointShape: {
                    type: 'triangle',
                    rotation: 180
                }
            },
            3: { // moving average
                type: 'line',
                color: 'blue'
            }
        },
        candlestick: {
            fallingColor: { strokeWidth: 0, fill: '#a52714' }, // red
            risingColor: { strokeWidth: 0, fill: '#0f9d58' }   // green
        },
        explorer: {
            actions: ['dragToZoom', 'rightClickToReset'],
            keepInBounds: true,
            maxZoomIn: 100.0
        }
    });

};
