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
        	}
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
				["Point", "Real", "Imag"]
			];

			var timePerSample = 1000.0 / params.srate; // in milliseconds

			for (var pos = 0; pos < realData.length; ++pos) {
				formattedData.push([ pos * timePerSample, realData[pos], imagData[pos]]);
			}

			var dataTable = google.visualization.arrayToDataTable(formattedData);
			self.chart.draw(dataTable, self.options);
		});
	};

}
