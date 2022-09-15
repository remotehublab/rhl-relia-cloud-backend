function Relia() {
}

function ReliaTimeSink (divIdentifier, deviceIdentifier, blockIdentifier) {
	var self = this;

        this.chart = new google.visualization.LineChart(document.getElementById(divIdentifier));
	this.options = {
		title: 'Time',
		curveType: 'function',
		legend: { position: 'bottom' },
		hAxis: {
			title: 'Time (milliseconds)'
		},
		vAxis: {
			title: 'Amplitude',
        	},
        explorer: {
        	actions: ['dragToZoom', 'rightClickToReset'],
        	axis: 'horizontal',
        	keepInBounds: true,
        	maxZoomIn: 4.0,
        },
        colors: ['#e2431e', '#000000'],
	};

	this.url = window.API_BASE_URL + "data/current/" + deviceIdentifier + "/blocks/" + blockIdentifier;

	this.redraw = function() {
		$.get(self.url).done(function (data) {
			setTimeout(function () {
				self.redraw();
			});

			if (!data.success) {
				console.log("Error: " + data.message);
				return;
			}

			if (data.data == null) {
				console.log("No data");
				return;
			}

			var params = data.data.params;

			console.log(data.data.block_type);
			console.log(data.data.type);
			console.log(params);
			console.log(data.data.data);

			var realData = data.data.data.streams['0']['real'];
			var imagData = data.data.data.streams['0']['imag'];
			$.each(realData, function (pos, value) {
				realData[pos] = parseFloat(value);
			});
			$.each(imagData, function (pos, value) {
				imagData[pos] = parseFloat(value);
			});

			var enableReal;
        	if($("#time-sink-real-checkbox").is(':checked'))  {
        		enableReal = true; }
        	else { 
        		enableReal = false; 
        		realData= new Array(realData.length).fill(null);
        	}
        		
			var enableImag;
        	if($("#time-sink-imag-checkbox").is(':checked'))  {
        		enableImag = true; }
        	else { 
        		enableImag = false; 
//        	 	imagData=Array(realData.length).fill(null);
        	 }
			if (!enableReal && !enableImag) {
				console.log("Error: activate real or imag");
				return;
			}
        		
			var columns = ["Point"];
		        self.options['series'] = {};

			var counter = 0;

			if (enableReal) {
				columns.push("Real");
				self.options.series[counter] = '#e2431e';
				counter++;
			}	
			if (enableImag) {
				columns.push("Imag");
				self.options.series[counter] = '#1c91c0';
			}

			console.log(self.options);

			var formattedData = [
				columns
			];
			
			var temp = document.getElementById("TimeSink_NumberOfPoints2Plot");
			var Number2plot=temp.value


			var timePerSample = 1000.0 / params.srate; // in milliseconds

			for (var pos = 0; pos < Number2plot	; ++pos) {
				var currentRow = [pos * timePerSample];
				if (enableReal)
					currentRow.push(realData[pos]);
				if (enableImag)
					currentRow.push(imagData[pos]);
				formattedData.push(currentRow);
			}

			var dataTable = google.visualization.arrayToDataTable(formattedData);
			self.chart.draw(dataTable, self.options);
		});
	};

}

function ReliaConstellationSink (divIdentifier, deviceIdentifier, blockIdentifier) {
	var self = this;

        this.chart = new google.visualization.ScatterChart(document.getElementById(divIdentifier));
	this.options = {
		title: 'Constellation Plot',
		pointSize: 3,
		curveType: 'function',
		legend: { position: 'bottom' },
		hAxis: {
			title: 'In - phase'
		},
		vAxis: {
			title: 'Quadrature',
        	},
        explorer: {
        	actions: ['dragToZoom', 'rightClickToReset'],
        	axis: 'horizontal',
        	keepInBounds: true,
        	maxZoomIn: 4.0,
        },
	};

	this.url = window.API_BASE_URL + "data/current/" + deviceIdentifier + "/blocks/" + blockIdentifier;

	this.redraw = function() {
		$.get(self.url).done(function (data) {
			setTimeout(function () {
				self.redraw();
			});

			if (!data.success) {
				console.log("Error: " + data.message);
				return;
			}

			if (data.data == null) {
				console.log("No data");
				return;
			}

			var params = data.data.params;

			console.log(data.data.block_type);
			console.log(data.data.type);
			console.log(params);
			console.log(data.data.data);

			var realData = data.data.data.streams['0']['real'];
			var imagData = data.data.data.streams['0']['imag'];
			$.each(realData, function (pos, value) {
				realData[pos] = parseFloat(value);
			});
			$.each(imagData, function (pos, value) {
				imagData[pos] = parseFloat(value);
			});

			var formattedData = [
				["", ""]
			];

			var temp = document.getElementById("ConstSink_NumberOfPoints2Plot");
			var Number2plot=temp.value

			for (var pos = 0; pos < Number2plot; ++pos) {
				formattedData.push([ realData[pos], imagData[pos]]);
			}

			var dataTable = google.visualization.arrayToDataTable(formattedData);
			self.chart.draw(dataTable, self.options);
		});
	};

}




