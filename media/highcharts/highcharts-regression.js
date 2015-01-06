(function (H) {


    H.wrap(H.Chart.prototype, 'init', function (proceed) {
        var series = arguments[1].series ;
        var extraSeries = [];
        var i = 0;
        for (i = 0 ; i < series.length ; i++){
            var s = series[i];
            s.regression = s.regression || '';
            if ( s.regression == 'true' ) {
                s.regressionSettings =  s.regressionSettings || {};
                var regressionType = s.regressionSettings.type || 'linear';
                var regression;
                var extraSerie = {
                        data:[],
                        yAxis: s.yAxis,
                        lineWidth: 2,
                        marker: {enabled: false},
                        isRegressionLine: true,
                        name: s.regressionSettings.label || "R2: %r2<br>%eq",
                        color: s.regressionSettings.color || ''
                };

                if (regressionType == "linear") {
                    regression = _linear(s.data) ;
                    extraSerie.type = "line";
                    extraSerie.data = regression.points;
                    extraSerie.name = extraSerie.name.replace("%r2", regression.rSquared);
                    extraSerie.name = extraSerie.name.replace("%eq", regression.string);
                }
                if (regressionType == "exponential") {
                    regression = _exponential(s.data);
                    extraSerie.type = "spline";
                    extraSerie.data = regression.points;
                    extraSerie.name = extraSerie.name.replace("%r2", regression.rSquared);
                    extraSerie.name = extraSerie.name.replace("%eq", regression.string);
                }
                if (regressionType == "polynomial"){
                    regression = _polynomial(s.data, 2);
                    extraSerie.type = "spline";
                    extraSerie.data = regression.points;
                    extraSerie.name = extraSerie.name.replace("%r2", regression.rSquared);
                    extraSerie.name = extraSerie.name.replace("%eq", regression.string);
                }
                if (regressionType == "logarithmic"){
                    regression = _logarithmic(s.data);
                    extraSerie.type = "spline";
                    extraSerie.data = regression.points;
                    extraSerie.name = extraSerie.name.replace("%r2", regression.rSquared);
                    extraSerie.name = extraSerie.name.replace("%eq", regression.string);
                }
                if (regressionType == "power"){
                    regression = _power(s.data);
                    extraSerie.type = "spline";
                    extraSerie.data = regression.points;
                    extraSerie.name = extraSerie.name.replace("%r2", regression.rSquared);
                    extraSerie.name = extraSerie.name.replace("%eq", regression.string);
                }

                extraSerie.regressionOutputs = regression;
                extraSeries.push(extraSerie);
                arguments[1].series[i].rendered = true;
            }
        }

        arguments[1].series = series.concat(extraSeries);
        proceed.apply(this, Array.prototype.slice.call(arguments, 1));
    });

    function _exponential(data) {
        var sum = [0, 0, 0, 0, 0, 0], results = [];

        for (var n = 0; n < data.length; n++) {
            sum[0] += data[n][0]; // X
            sum[1] += data[n][1]; // Y
            sum[2] += data[n][0] * data[n][0] * data[n][1]; // XXY
            sum[3] += data[n][1] * Math.log(data[n][1]); // Y Log Y
            sum[4] += data[n][0] * data[n][1] * Math.log(data[n][1]); //YY Log Y
            sum[5] += data[n][0] * data[n][1]; //XY
        }

        var denominator = (sum[1] * sum[2] - sum[5] * sum[5]);
        var A = Math.pow(Math.E, (sum[2] * sum[3] - sum[5] * sum[4]) / denominator);
        var B = (sum[1] * sum[4] - sum[5] * sum[3]) / denominator;

        for (var i = 0, len = data.length; i < len; i++) {
            var coordinate = [data[i][0], A * Math.pow(Math.E, B * data[i][0])];
            results.push(coordinate);
        }

        results.sort(function(a,b){
           if(a[0] > b[0]){ return 1}
            if(a[0] < b[0]){ return -1}
              return 0;
        });

        var rSquared = coefficientOfDetermination(data, results);
        var string = 'y = ' + A.toFixed(4) + 'e^(' + B.toFixed(4) + 'x)';

        return {points: results, string: string, rSquared: rSquared.toFixed(3)};
    }

    function _linear(data) {
        var sum = [0, 0, 0, 0, 0], results = [], N = data.length;

        for (var n = 0; n < data.length; n++) {
            sum[0] += data[n][0]; //Î£(X)
            sum[1] += data[n][1]; //Î£(Y)
            sum[2] += data[n][0] * data[n][0]; //Î£(X^2)
            sum[3] += data[n][0] * data[n][1]; //Î£(XY)
            sum[4] += data[n][1] * data[n][1]; //Î£(Y^2)
        }

        var gradient = (N * sum[3] - sum[0] * sum[1]) / (N * sum[2] - sum[0] * sum[0]);
        var intercept = (sum[1] / N) - (gradient * sum[0]) / N;

        for (var i = 0, len = data.length; i < len; i++) {
            var coordinate = [data[i][0], data[i][0] * gradient + intercept];
            results.push(coordinate);
        }

        results.sort(function(a,b){
           if(a[0] > b[0]){ return 1}
            if(a[0] < b[0]){ return -1}
              return 0;
        });

        var rSquared = coefficientOfDetermination(data, results);
        var string = 'y = ' + gradient.toFixed(4) + 'x + ' + intercept.toFixed(4);

        return {points: results, string: string, rSquared: rSquared.toFixed(3)};
    }

    function _logarithmic(data) {
        var sum = [0, 0, 0, 0], results = [], N = data.length;

        for (var n = 0; n < data.length; n++) {
            sum[0] += Math.log(data[n][0]);
            sum[1] += data[n][1] * Math.log(data[n][0]);
            sum[2] += data[n][1];
            sum[3] += Math.pow(Math.log(data[n][0]), 2);
        }

        var B = (N * sum[1] - sum[2] * sum[0]) / (N * sum[3] - sum[0] * sum[0]);
        var A = (sum[2] - B * sum[0]) / N;

        for (var i = 0, len = data.length; i < len; i++) {
            var coordinate = [data[i][0], A + B * Math.log(data[i][0])];
            results.push(coordinate);
        }

        results.sort(function(a,b){
           if(a[0] > b[0]){ return 1}
            if(a[0] < b[0]){ return -1}
              return 0;
        });

        var rSquared = coefficientOfDetermination(data, results);
        var string = 'y = ' + A.toFixed(3) + ' + ' + B.toFixed(3) + ' ln(x)';

        return {points: results, string: string, rSquared: rSquared.toFixed(3)};
    }

    function _power(data) {
        var sum = [0, 0, 0, 0], results = [], N = data.length;

        for (var n = 0; n < data.length; n++) {
            sum[0] += Math.log(data[n][0]);
            sum[1] += Math.log(data[n][1]) * Math.log(data[n][0]);
            sum[2] += Math.log(data[n][1]);
            sum[3] += Math.pow(Math.log(data[n][0]), 2);
        }

        var B = (N * sum[1] - sum[2] * sum[0]) / (N * sum[3] - sum[0] * sum[0]);
        var A = Math.pow(Math.E, (sum[2] - B * sum[0]) / N);

        for (var i = 0, len = data.length; i < len; i++) {
            var coordinate = [data[i][0], A * Math.pow(data[i][0] , B)];
            results.push(coordinate);
        }

        results.sort(function(a,b){
           if(a[0] > b[0]){ return 1}
            if(a[0] < b[0]){ return -1}
              return 0;
        });

        var rSquared = coefficientOfDetermination(data, results);
        var string = 'y = ' + A.toFixed(4) + 'x^' + B.toFixed(4);

        return {points: results, string: string, rSquared: rSquared.toFixed(3)};
    }

    function _polynomial(data, order) {
        var lhs = [], rhs = [], results = [], a = 0, b = 0, i = 0, k = order + 1;

        for (; i < k; i++) {
            for (var l = 0; l < data.length; l++) {
                if (data[l][1]) {
                    a += Math.pow(data[l][0], i) * data[l][1];
                }
            }
            lhs.push(a);
            a = 0;
                var c = [];
                for (var j = 0; j < k; j++) {
                    for (l = 0; l < data.length; l++) {
                        if (data[l][1]) {
                            b += Math.pow(data[l][0], i + j);
                        }
                    }
                    c.push(b);
                    b = 0;
                }
                rhs.push(c);
        }
        rhs.push(lhs);

        var equation = gaussianElimination(rhs, k);

        for (i = 0; i < data.length; i++) {
            var answer = 0;
            for (var w = 0; w < equation.length; w++) {
                answer += equation[w] * Math.pow(data[i][0], w);
            }
            results.push([data[i][0], answer]);
        }

        results.sort(function(a,b){
           if(a[0] > b[0]){ return 1}
            if(a[0] < b[0]){ return -1}
              return 0;
        });

        var string = 'y = ';

        for(i = equation.length-1; i >= 0; i--){
            if(i > 1) string += equation[i].toFixed(4) + 'x^' + i + ' + ';
            else if (i == 1) string += equation[i].toFixed(4) + 'x' + ' + ';
            else string += equation[i].toFixed(4);
        }

        var rSquared = coefficientOfDetermination(data, results);
        return {points: results, string: string, rSquared: rSquared.toFixed(3)};
    }

    function  gaussianElimination(a, o) {
        var j = 0, k = 0, tmp = 0, n = a.length - 1, x = new Array(o);
        for (var i = 0; i < n; i++) {
           var maxrow = i;
           for (j = i + 1; j < n; j++) {
              if (Math.abs(a[i][j]) > Math.abs(a[i][maxrow]))
                 maxrow = j;
           }
           for (k = i; k < n + 1; k++) {
              tmp = a[k][i];
              a[k][i] = a[k][maxrow];
              a[k][maxrow] = tmp;
           }
           for (j = i + 1; j < n; j++) {
              for (k = n; k >= i; k--) {
                 a[k][j] -= a[k][i] * a[i][j] / a[i][i];
              }
           }
        }
        for (j = n - 1; j >= 0; j--) {
           tmp = 0;
           for (k = j + 1; k < n; k++)
              tmp += a[k][j] * x[k];
           x[j] = (a[n][j] - tmp) / a[j][j];
        }
        return (x);
     }

    function coefficientOfDetermination(data, pred) {
        var mean = 0, SStot = 0, SSexp = 0;

        // Calc the mean
        for (var i = 0; i < data.length; i++ ){
            mean +=  data[i][1] / data.length;
        }

        // Calc the coefficent of determination
        for (i = 0; i < data.length; i++ ){
            SStot +=  Math.pow( data[i][1] - mean, 2);
            SSexp +=  Math.pow( pred[i][1] - mean, 2);
        }
        return  SSexp / SStot;
    }
}(Highcharts));
